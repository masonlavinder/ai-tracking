// Home: timeline of significant changes with company + tag filters, plus a
// row of company summary cards so visitors can jump straight to a company.

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CompanyCard } from "../components/CompanyCard";
import { Timeline } from "../components/Timeline";
import { loadCompanies, loadTimeline } from "../lib/data";
import type {
  ChangeSummary,
  CompanySummary,
  TimelineFile,
} from "../lib/types";

function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toISOString().slice(0, 10);
}

const COMPANY_PREVIEW_LIMIT = 6;

export function Home() {
  const [timeline, setTimeline] = useState<TimelineFile | null>(null);
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [companyFilter, setCompanyFilter] = useState<string>("all");
  const [tagFilter, setTagFilter] = useState<string>("all");
  const [companyQuery, setCompanyQuery] = useState<string>("");
  const [companiesExpanded, setCompaniesExpanded] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;
    Promise.all([loadTimeline(), loadCompanies()])
      .then(([tl, co]) => {
        if (cancelled) return;
        setTimeline(tl);
        setCompanies(co.companies);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const allTags = useMemo(() => {
    if (!timeline) return [] as string[];
    const set = new Set<string>();
    for (const c of timeline.changes) c.tags.forEach((t) => set.add(t));
    return Array.from(set).sort();
  }, [timeline]);

  const matchedCompanies = useMemo(() => {
    const query = companyQuery.trim().toLowerCase();
    if (!query) return companies;
    return companies.filter(
      (c) =>
        c.name.toLowerCase().includes(query) ||
        (c.ticker ?? "").toLowerCase().includes(query),
    );
  }, [companies, companyQuery]);

  const isSearching = companyQuery.trim().length > 0;
  const visibleCompanies =
    isSearching || companiesExpanded
      ? matchedCompanies
      : matchedCompanies.slice(0, COMPANY_PREVIEW_LIMIT);
  const hasMoreCompanies =
    !isSearching &&
    !companiesExpanded &&
    matchedCompanies.length > COMPANY_PREVIEW_LIMIT;

  const filtered: ChangeSummary[] = useMemo(() => {
    if (!timeline) return [];
    return timeline.changes.filter((c) => {
      if (companyFilter !== "all" && c.company_slug !== companyFilter)
        return false;
      if (tagFilter !== "all" && !c.tags.includes(tagFilter)) return false;
      return true;
    });
  }, [timeline, companyFilter, tagFilter]);

  if (error) {
    return (
      <div className="rounded-md border border-rose-300 bg-rose-50 p-4 text-sm text-rose-900">
        Failed to load data: {error}
      </div>
    );
  }

  const totalChanges = timeline?.changes.length ?? 0;
  const lastUpdated = formatDate(timeline?.generated_at);
  const threshold = timeline ? timeline.threshold : 4;

  return (
    <div className="flex flex-col gap-8">
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-brand-50 via-white to-white px-6 py-10 sm:px-10 sm:py-14">
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:gap-8">
          <svg
            width="96"
            height="96"
            viewBox="0 0 64 64"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden
            className="shrink-0 drop-shadow-sm"
          >
            <rect width="64" height="64" rx="12" fill="#022c22" />
            <circle cx="32" cy="32" r="24" fill="#065f46" />
            <circle cx="32" cy="32" r="18" fill="#ecfdf5" />
            <circle cx="32" cy="32" r="12" fill="#0b6e4f" />
            <circle cx="32" cy="32" r="5" fill="#022c22" />
            <circle cx="34" cy="30" r="1.4" fill="#ecfdf5" />
          </svg>
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Nazar Watch
            </h1>
            <p className="mt-2 text-lg font-medium text-brand-700">
              Watching what watches you.
            </p>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-700">
              Daily, automated diffs of privacy policies and terms from the
              largest AI companies. Every material change is detected,
              classified, scored, and dated — so you can see exactly how
              AI data-use language shifts over time.
            </p>
          </div>
        </div>
      </section>

      <section>
        <dl className="flex flex-wrap items-baseline gap-x-10 gap-y-3 rounded-lg border border-slate-200 bg-white px-5 py-4 text-sm">
          <div className="flex items-baseline gap-2">
            <dt className="uppercase tracking-wide text-slate-500 text-xs">
              Companies tracked
            </dt>
            <dd className="text-xl font-semibold tabular-nums text-slate-900">
              {companies.length}
            </dd>
          </div>
          <div className="flex items-baseline gap-2">
            <dt className="uppercase tracking-wide text-slate-500 text-xs">
              Significant changes
            </dt>
            <dd className="text-xl font-semibold tabular-nums text-slate-900">
              {totalChanges}
            </dd>
          </div>
          <div className="flex items-baseline gap-2">
            <dt className="uppercase tracking-wide text-slate-500 text-xs">
              Last updated
            </dt>
            <dd className="font-mono text-slate-900">{lastUpdated}</dd>
          </div>
        </dl>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 text-sm leading-relaxed text-slate-700">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          How it works
        </h2>
        <p className="mt-2">
          Every day we scrape the published privacy and AI-data policies of
          each tracked company. When the text changes, a rule-based
          classifier compares paragraphs, tags the topics involved, and
          assigns a significance score. The timeline below lists every
          change rated ≥ {threshold}.{" "}
          <Link to="/about" className="font-medium text-brand-700 hover:text-brand-800 underline">
            Read the methodology
          </Link>{" "}
          or subscribe to the{" "}
          <a
            href="feed.xml"
            className="font-medium text-brand-700 hover:text-brand-800 underline"
          >
            RSS feed
          </a>
          .
        </p>
      </section>

      <section>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Companies
          </h2>
          <input
            type="search"
            value={companyQuery}
            onChange={(e) => setCompanyQuery(e.target.value)}
            placeholder="Search companies…"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm sm:w-64"
          />
        </div>
        {visibleCompanies.length === 0 ? (
          <div className="mt-3 rounded-md border border-dashed border-slate-300 bg-white p-4 text-center text-xs text-slate-500">
            No companies match &ldquo;{companyQuery}&rdquo;.
          </div>
        ) : (
          <div className="mt-3 grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {visibleCompanies.map((c) => (
              <CompanyCard key={c.slug} company={c} />
            ))}
          </div>
        )}
        {hasMoreCompanies && (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setCompaniesExpanded(true)}
              className="text-xs font-medium text-brand-700 hover:text-brand-800"
            >
              Show all {matchedCompanies.length} companies
            </button>
          </div>
        )}
        {companiesExpanded && !isSearching && (
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setCompaniesExpanded(false)}
              className="text-xs font-medium text-brand-700 hover:text-brand-800"
            >
              Show fewer
            </button>
          </div>
        )}
      </section>

      <section>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Significant changes
          </h2>
          <div className="flex flex-wrap gap-2">
            <label className="flex items-center gap-1 text-xs text-slate-600">
              Company
              <select
                value={companyFilter}
                onChange={(e) => setCompanyFilter(e.target.value)}
                className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
              >
                <option value="all">All</option>
                {companies.map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-1 text-xs text-slate-600">
              Tag
              <select
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
                className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
              >
                <option value="all">All</option>
                {allTags.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
        <div className="mt-3">
          <Timeline
            changes={filtered}
            emptyMessage={
              timeline && timeline.changes.length === 0
                ? "No significant changes have been detected yet. Check back after the daily scrape runs."
                : "No changes match the current filters."
            }
          />
        </div>
      </section>
    </div>
  );
}
