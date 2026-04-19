// Summary tile used on the home timeline and company pages.

import { Link } from "react-router-dom";
import type { ChangeSummary } from "../lib/types";
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
          <span
            className="rounded-md bg-slate-900 px-2 py-0.5 text-xs font-semibold text-white"
            title="Significance score"
          >
            Score {change.score}
          </span>
          <div className="text-xs text-slate-500">
            +{change.added_count} ~{change.modified_count} −{change.removed_count}
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
