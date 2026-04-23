// Company summary tile shown on the home page.

import { Link } from "react-router-dom";
import type { CompanySummary } from "@types";

export function CompanyCard({ company }: { company: CompanySummary }) {
  return (
    <Link
      to={`/companies/${company.slug}`}
      className="block rounded-md border border-slate-200 bg-white px-3 py-2 shadow-sm transition hover:border-slate-300 hover:shadow-md"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-slate-900">
            {company.name}
          </div>
          {company.ticker && (
            <div className="text-[10px] uppercase tracking-wide text-slate-500">
              {company.ticker}
            </div>
          )}
        </div>
        <div className="shrink-0 text-right">
          <div className="text-lg font-semibold leading-none text-slate-900">
            {company.total_changes}
          </div>
          <div className="mt-0.5 text-[10px] text-slate-500">changes</div>
        </div>
      </div>
    </Link>
  );
}
