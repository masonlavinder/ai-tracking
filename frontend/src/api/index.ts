// Static-data fetch helpers. All requests go to files under /data/, which
// copy-data.mjs copies from data/processed/ at build time.
//
// Each helper memoises its result so multiple components sharing the same
// file don't re-fetch.

import type {
  ChangeDetail,
  ChangesFile,
  CompaniesFile,
  TimelineFile,
} from "@types";

const base = import.meta.env.BASE_URL; // e.g. "/ai-tracking/"

function url(path: string): string {
  const trimmedBase = base.endsWith("/") ? base.slice(0, -1) : base;
  return `${trimmedBase}${path}`;
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(url(path), { cache: "no-cache" });
  if (!res.ok) {
    throw new Error(`Failed to fetch ${path}: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

let companiesPromise: Promise<CompaniesFile> | null = null;
let changesPromise: Promise<ChangesFile> | null = null;
let timelinePromise: Promise<TimelineFile> | null = null;
const changeDetailCache = new Map<string, Promise<ChangeDetail>>();

export function loadCompanies(): Promise<CompaniesFile> {
  if (!companiesPromise) {
    companiesPromise = fetchJson<CompaniesFile>("/data/companies.json");
  }
  return companiesPromise;
}

export function loadChanges(): Promise<ChangesFile> {
  if (!changesPromise) {
    changesPromise = fetchJson<ChangesFile>("/data/changes.json");
  }
  return changesPromise;
}

export function loadTimeline(): Promise<TimelineFile> {
  if (!timelinePromise) {
    timelinePromise = fetchJson<TimelineFile>("/data/timeline.json");
  }
  return timelinePromise;
}

export function loadChangeDetail(id: string): Promise<ChangeDetail> {
  const existing = changeDetailCache.get(id);
  if (existing) return existing;
  const promise = fetchJson<ChangeDetail>(
    `/data/changes/${encodeURIComponent(id)}.json`,
  );
  changeDetailCache.set(id, promise);
  return promise;
}
