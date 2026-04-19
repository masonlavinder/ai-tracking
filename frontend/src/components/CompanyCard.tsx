// Company summary tile shown on the home page.

import { Link } from "react-router-dom";
import type { CompanySummary } from "../lib/types";

export function CompanyCard({ company }: { company: CompanySummary }) {
  return (
    <Link
      to={`/companies/${company.slug}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:border-slate-300 hover:shadow-md"
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-base font-semibold text-slate-900">
            {company.name}
          </div>
          {company.ticker && (
            <div className="text-xs uppercase tracking-wide text-slate-500">
              {company.ticker}
            </div>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-semibold text-slate-900">
            {company.total_changes}
          </div>
          <div className="text-xs text-slate-500">changes</div>
        </div>
      </div>
      {company.latest_snapshot_date && (
        <div className="mt-2 text-xs text-slate-500">
          Latest snapshot: {company.latest_snapshot_date}
        </div>
      )}
    </Link>
  );
}
