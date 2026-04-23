// Per-company page: corporate + stock links, policy index, change history
// filterable by policy type, and the tag summary we can derive without
// editorializing.

import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { loadChanges, loadCompanies } from "@api";
import type { ChangeSummary, CompanySummary } from "@types";
import { CompanyHeader } from "./components/CompanyHeader";
import { PoliciesGrid } from "./components/PoliciesGrid";
import { TagSummary } from "./components/TagSummary";
import { ChangeHistorySection } from "./components/ChangeHistorySection";

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

  const policyKindOptions = useMemo<[string, string][]>(() => {
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
      <CompanyHeader company={company} />
      <PoliciesGrid policies={company.policies} />
      <TagSummary companyName={company.name} tags={tagsAcrossHistory} />
      <ChangeHistorySection
        allChanges={changes}
        filteredChanges={filteredChanges}
        policyKindOptions={policyKindOptions}
        policyFilter={policyFilter}
        setPolicyFilter={setPolicyFilter}
      />
    </div>
  );
}
