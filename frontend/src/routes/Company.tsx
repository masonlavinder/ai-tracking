// Per-company page: corporate + stock links, policy index, change history
// filterable by policy type, and the tag summary we can derive without
// editorializing.

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
  const [policyFilter, setPolicyFilter] = useState<string>("all");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setPolicyFilter("all");
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

  const policyKindOptions = useMemo(() => {
    const seen = new Map<string, string>();
    for (const c of changes) {
      if (!seen.has(c.policy_kind)) seen.set(c.policy_kind, c.policy_label);
    }
    return Array.from(seen.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [changes]);

  const filteredChanges = useMemo(() => {
    if (policyFilter === "all") return changes;
    return changes.filter((c) => c.policy_kind === policyFilter);
  }, [changes, policyFilter]);

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
          {company.total_changes} detected changes
          {company.latest_snapshot_date
            ? ` · latest snapshot ${company.latest_snapshot_date}`
            : ""}
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
          {company.homepage_url && (
            <a
              className="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-slate-700 hover:border-slate-400 hover:bg-slate-100"
              href={company.homepage_url}
              target="_blank"
              rel="noreferrer noopener"
            >
              Company site ↗
            </a>
          )}
          {company.stock_url && company.ticker && (
            <a
              className="rounded-md border border-emerald-300 bg-emerald-50 px-2.5 py-1 text-emerald-900 hover:border-emerald-400 hover:bg-emerald-100"
              href={company.stock_url}
              target="_blank"
              rel="noreferrer noopener"
              title={`${company.ticker} on Yahoo Finance`}
            >
              {company.ticker} ↗
            </a>
          )}
          {company.sec_cik && (
            <a
              className="rounded-md border border-slate-300 bg-white px-2.5 py-1 text-slate-700 hover:border-slate-400 hover:bg-slate-100"
              href={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${company.sec_cik}&type=10-K`}
              target="_blank"
              rel="noreferrer noopener"
              title="SEC EDGAR filings"
            >
              EDGAR ↗
            </a>
          )}
          {!company.ticker && (
            <span className="text-xs text-slate-500">private company</span>
          )}
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
                    className="break-all text-xs text-sky-700 underline"
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
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Change history
            {policyFilter !== "all" && (
              <span className="ml-2 text-xs font-normal text-slate-500">
                · {filteredChanges.length} of {changes.length}
              </span>
            )}
          </h2>
          {policyKindOptions.length > 1 && (
            <label className="flex items-center gap-1 text-xs text-slate-600">
              Policy
              <select
                value={policyFilter}
                onChange={(e) => setPolicyFilter(e.target.value)}
                className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
              >
                <option value="all">All</option>
                {policyKindOptions.map(([kind, label]) => (
                  <option key={kind} value={kind}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
          )}
        </div>
        <div className="mt-3">
          <Timeline
            changes={filteredChanges}
            hideCompany
            emptyMessage={
              changes.length === 0
                ? "No changes have been detected for this company yet."
                : "No changes match the selected policy."
            }
          />
        </div>
      </section>
    </div>
  );
}
