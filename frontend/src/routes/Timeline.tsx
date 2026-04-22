// Timeline: chronological list of every significant policy change,
// filterable by company and tag.

import { useEffect, useMemo, useState } from "react";
import { Timeline as TimelineList } from "../components/Timeline";
import { loadCompanies, loadTimeline } from "../lib/data";
import type {
  ChangeSummary,
  CompanySummary,
  TimelineFile,
} from "../lib/types";

export function TimelinePage() {
  const [timeline, setTimeline] = useState<TimelineFile | null>(null);
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [companyFilter, setCompanyFilter] = useState<string>("all");
  const [tagFilter, setTagFilter] = useState<string>("all");

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

  const threshold = timeline ? timeline.threshold : 4;

  return (
    <div className="flex flex-col gap-6">
      <section>
        <h1 className="text-2xl font-semibold text-slate-900">Timeline</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">
          Every policy change our rule-based classifier rated significance
          ≥ {threshold}, newest first. Filter by company or by tag to narrow
          in on a specific topic.
        </p>
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
          <TimelineList
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
