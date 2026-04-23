// Summary tile used on the home timeline and company pages.

import { Link } from "react-router-dom";
import type { ChangeSummary } from "@types";
import { ScoreBadge } from "./ScoreBadge";
import { TagBadge } from "./TagBadge";

interface Props {
  change: ChangeSummary;
  hideCompany?: boolean;
}

export function ChangeCard({ change, hideCompany = false }: Props) {
  return (
    <Link
      to={`/changes/${encodeURIComponent(change.id)}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:border-slate-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {!hideCompany && (
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              {change.company_name}
            </div>
          )}
          <div className="mt-1 truncate text-base font-medium text-slate-900">
            {change.policy_label}
          </div>
          <div className="mt-1 text-sm text-slate-600">
            {change.from_date} → {change.to_date}
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <ScoreBadge score={change.score} />
          <div className="flex items-center gap-2 text-xs font-medium tabular-nums">
            <span className="text-emerald-700">+{change.added_count}</span>
            <span className="text-slate-500">~{change.modified_count}</span>
            <span className="text-rose-700">−{change.removed_count}</span>
          </div>
        </div>
      </div>
      {change.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {change.tags.map((tag) => (
            <TagBadge key={tag} tag={tag} />
          ))}
        </div>
      )}
    </Link>
  );
}
