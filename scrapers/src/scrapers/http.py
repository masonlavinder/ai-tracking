"""Shared HTTP client and politeness helpers.

Provides a single `PoliteClient` that:

- sends a descriptive User-Agent
- consults `robots.txt` before each fetch
- enforces a per-host minimum delay between requests
- retries with exponential backoff on 429 and 5xx responses
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Final
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx

from .config import PROJECT_USER_AGENT

log = logging.getLogger(__name__)

DEFAULT_MIN_HOST_DELAY_SECONDS: Final = 2.0
DEFAULT_TIMEOUT_SECONDS: Final = 30.0
DEFAULT_MAX_RETRIES: Final = 4


class RobotsDisallowedError(RuntimeError):
    """Raised when robots.txt disallows fetching a URL."""


@dataclass
class PoliteClient:
    """Minimal polite HTTP client wrapping httpx.Client.

    The client is stateless apart from the per-host last-fetch timestamps and
    the robots.txt cache, so it is safe to construct one per scraper run.
    """

    user_agent: str = PROJECT_USER_AGENT
    min_host_delay: float = DEFAULT_MIN_HOST_DELAY_SECONDS
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    respect_robots: bool = True

    _last_fetch_at: dict[str, float] = field(default_factory=dict, init=False, repr=False)
    _robots: dict[str, RobotFileParser | None] = field(
        default_factory=dict, init=False, repr=False
    )
    _client: httpx.Client | None = field(default=None, init=False, repr=False)

    def __enter__(self) -> "PoliteClient":
        self._client = httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    def __exit__(self, *exc: object) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # --- robots.txt ---------------------------------------------------------

    def _robots_for(self, url: str) -> RobotFileParser | None:
        parts = urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        if host in self._robots:
            return self._robots[host]

        robots_url = f"{host}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            assert self._client is not None
            resp = self._client.get(robots_url)
            if resp.status_code >= 400:
                # Per RFC 9309, treat 4xx as "allow all" and 5xx as "disallow all".
                # We conservatively treat both as allow to avoid over-blocking on
                # transient errors, but log 5xx.
                if resp.status_code >= 500:
                    log.warning("robots.txt for %s returned %s", host, resp.status_code)
                self._robots[host] = None
                return None
            parser.parse(resp.text.splitlines())
        except httpx.HTTPError as err:
            log.warning("Failed to fetch robots.txt for %s: %s", host, err)
            self._robots[host] = None
            return None

        self._robots[host] = parser
        return parser

    def allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parser = self._robots_for(url)
        if parser is None:
            return True
        return parser.can_fetch(self.user_agent, url)

    # --- fetch --------------------------------------------------------------

    def _wait_for_host(self, url: str) -> None:
        host = urlsplit(url).netloc
        last = self._last_fetch_at.get(host)
        if last is None:
            return
        elapsed = time.monotonic() - last
        if elapsed < self.min_host_delay:
            time.sleep(self.min_host_delay - elapsed)

    def _record_fetch(self, url: str) -> None:
        host = urlsplit(url).netloc
        self._last_fetch_at[host] = time.monotonic()

    def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Fetch a URL politely. Raises for robots disallow and HTTP errors."""
        assert self._client is not None, "Use PoliteClient as a context manager"

        if not self.allowed(url):
            raise RobotsDisallowedError(f"robots.txt disallows {url}")

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            self._wait_for_host(url)
            try:
                resp = self._client.get(url, params=params)
            except httpx.HTTPError as err:
                last_exc = err
                self._record_fetch(url)
            else:
                self._record_fetch(url)
                if resp.status_code < 400:
                    return resp
                if resp.status_code not in (429, 500, 502, 503, 504):
                    resp.raise_for_status()
                last_exc = httpx.HTTPStatusError(
                    f"retryable status {resp.status_code} for {url}",
                    request=resp.request,
                    response=resp,
                )

            if attempt < self.max_retries:
                backoff = (2**attempt) + random.uniform(0, 0.5)
                log.info(
                    "Retrying %s in %.1fs (attempt %d/%d): %s",
                    url,
                    backoff,
                    attempt + 1,
                    self.max_retries,
                    last_exc,
                )
                time.sleep(backoff)

        assert last_exc is not None
        raise last_exc
