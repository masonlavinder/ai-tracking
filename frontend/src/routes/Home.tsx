// Home: timeline of significant changes with company + tag filters, plus a
// row of company summary cards so visitors can jump straight to a company.

import { useEffect, useMemo, useState } from "react";
import { CompanyCard } from "../components/CompanyCard";
import { Timeline } from "../components/Timeline";
import { loadCompanies, loadTimeline } from "../lib/data";
import type {
  ChangeSummary,
  CompanySummary,
  TimelineFile,
} from "../lib/types";

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

  return (
    <div className="flex flex-col gap-8">
      <section>
        <h1 className="text-2xl font-semibold text-slate-900">
          How policies change around AI
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          Daily-updated diffs of privacy policies and terms from Meta, OpenAI,
          Anthropic, Google, and Microsoft. The timeline below shows changes
          our rule-based classifier rated significance ≥
          {timeline ? ` ${timeline.threshold}` : " 4"}.
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
