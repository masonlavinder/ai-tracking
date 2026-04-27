import { Link } from "react-router-dom";
import type { CompanySummary } from "@types";
import { companyContent } from "@data/companyContent";

export const CompanyHeader = ({ company }: { company: CompanySummary }) => {
  const hasOptOut = Boolean(companyContent[company.slug]?.optOut);
  return (
    <header>
      <Link to="/" className="text-xs text-slate-500 hover:underline">
        ← All companies
      </Link>
      <h1 className="mt-1 text-2xl font-semibold text-slate-900">
        {company.name}
      </h1>
      {company.latest_snapshot_date && (
        <div className="mt-1 text-sm text-slate-600">
          Latest snapshot {company.latest_snapshot_date}
        </div>
      )}
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
            Stock ↗
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
            SEC Reports ↗
          </a>
        )}
        {hasOptOut && (
          <Link
            to={`/opt-out?company=${company.slug}`}
            className="rounded-md border border-brand-300 bg-brand-50 px-2.5 py-1 font-medium text-brand-800 hover:border-brand-400 hover:bg-brand-100"
          >
            How to opt out →
          </Link>
        )}
        {!company.ticker && (
          <span className="text-xs text-slate-500">private company</span>
        )}
      </div>
      {company.policies.length > 0 && (
        <div className="mt-3 text-xs text-slate-500">
          <span className="font-semibold uppercase tracking-wide">Tracked:</span>{" "}
          {company.policies.map((p, i) => (
            <span key={p.policy_id}>
              {i > 0 && <span className="text-slate-300"> · </span>}
              {p.url ? (
                <a
                  href={p.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-slate-700 hover:text-brand-700 hover:underline"
                >
                  {p.label} ↗
                </a>
              ) : (
                <span className="text-slate-700">{p.label}</span>
              )}
            </span>
          ))}
        </div>
      )}
    </header>
  );
}
