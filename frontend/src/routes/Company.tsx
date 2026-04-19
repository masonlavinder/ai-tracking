// Per-company page: policy index, full change history, and the known
// facts we can derive about AI data use without editorializing.

import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Timeline } from "../components/Timeline";
import { loadChanges, loadCompanies } from "../lib/data";
import type { ChangeSummary, CompanySummary } from "../lib/types";

export function Company() {
  const { slug = "" } = useParams<{ slug: string }>();
  const [company, setCompany] = useState<CompanySummary | null>(null);
  const [changes, setChanges] = useState<ChangeSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([loadCompanies(), loadChanges()])
      .then(([co, ch]) => {
        if (cancelled) return;
        const match = co.companies.find((c) => c.slug === slug) ?? null;
        setCompany(match);
        setChanges(ch.changes.filter((c) => c.company_slug === slug));
        setLoading(false);
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  const tagsAcrossHistory = useMemo(() => {
    const set = new Set<string>();
    for (const c of changes) c.tags.forEach((t) => set.add(t));
    return Array.from(set).sort();
  }, [changes]);

  if (loading) {
    return <div className="text-sm text-slate-500">Loading…</div>;
  }
  if (error) {
    return (
      <div className="rounded-md border border-rose-300 bg-rose-50 p-4 text-sm text-rose-900">
        Failed to load data: {error}
      </div>
    );
  }
  if (!company) {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        Unknown company. <Link to="/" className="underline">Back to timeline</Link>.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <header>
        <Link to="/" className="text-xs text-slate-500 hover:underline">
          ← All companies
        </Link>
        <h1 className="mt-1 text-2xl font-semibold text-slate-900">
          {company.name}
        </h1>
        <div className="mt-1 text-sm text-slate-600">
          {company.ticker ? `NASDAQ: ${company.ticker} · ` : ""}
          {company.total_changes} detected changes
          {company.latest_snapshot_date
            ? ` · latest snapshot ${company.latest_snapshot_date}`
            : ""}
        </div>
      </header>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Tracked policies
        </h2>
        {company.policies.length === 0 ? (
          <div className="mt-2 rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-500">
            No snapshots captured yet.
          </div>
        ) : (
          <ul className="mt-2 grid gap-2 sm:grid-cols-2">
            {company.policies.map((p) => (
              <li
                key={p.policy_id}
                className="rounded-md border border-slate-200 bg-white p-3 text-sm"
              >
                <div className="font-medium text-slate-900">{p.label}</div>
                {p.url && (
                  <a
                    className="text-xs text-sky-700 underline"
                    href={p.url}
                    target="_blank"
                    rel="noreferrer noopener"
                  >
                    {p.url}
                  </a>
                )}
                <div className="mt-1 text-xs text-slate-500">
                  Latest snapshot: {p.latest_snapshot_date || "—"}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          What we've seen change
        </h2>
        {tagsAcrossHistory.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">
            No classified changes yet. This is not a statement about{" "}
            {company.name}'s data practices — only about what has changed in
            the tracked snapshots.
          </p>
        ) : (
          <p className="mt-2 text-sm text-slate-600">
            Historical changes have touched: {tagsAcrossHistory.join(", ")}.
          </p>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Full change history
        </h2>
        <div className="mt-3">
          <Timeline
            changes={changes}
            hideCompany
            emptyMessage="No changes have been detected for this company yet."
          />
        </div>
      </section>
    </div>
  );
}
