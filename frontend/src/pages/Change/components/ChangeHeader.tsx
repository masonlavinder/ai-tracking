import { Link } from "react-router-dom";
import { TagBadge } from "@components/TagBadge";
import type { ChangeDetail } from "@types";

export function ChangeHeader({ change }: { change: ChangeDetail }) {
  return (
    <header>
      <Link
        to={`/companies/${change.company_slug}`}
        className="text-xs text-slate-500 hover:underline"
      >
        ← {change.company_name}
      </Link>
      <h1 className="mt-1 text-2xl font-semibold text-slate-900">
        {change.policy_label}
      </h1>
      <div className="mt-1 text-sm text-slate-600">
        {change.from_date} → {change.to_date}
      </div>
      {change.url && (
        <a
          className="mt-2 inline-block text-sm text-sky-700 underline"
          href={change.url}
          target="_blank"
          rel="noreferrer noopener"
        >
          Source page
        </a>
      )}
      {change.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {change.tags.map((t) => (
            <TagBadge key={t} tag={t} />
          ))}
        </div>
      )}
    </header>
  );
}
