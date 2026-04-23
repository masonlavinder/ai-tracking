import { useMemo, useState } from "react";
import type { CompanySummary } from "@types";
import { CompanyCard } from "./CompanyCard";

const COMPANY_PREVIEW_LIMIT = 8;

export function CompaniesSection({ companies }: { companies: CompanySummary[] }) {
  const [companyQuery, setCompanyQuery] = useState<string>("");
  const [companiesExpanded, setCompaniesExpanded] = useState<boolean>(false);

  const matchedCompanies = useMemo(() => {
    const query = companyQuery.trim().toLowerCase();
    if (!query) return companies;
    return companies.filter(
      (c) =>
        c.name.toLowerCase().includes(query) ||
        (c.ticker ?? "").toLowerCase().includes(query),
    );
  }, [companies, companyQuery]);

  const isSearching = companyQuery.trim().length > 0;
  const visibleCompanies =
    isSearching || companiesExpanded
      ? matchedCompanies
      : matchedCompanies.slice(0, COMPANY_PREVIEW_LIMIT);
  const hasMoreCompanies =
    !isSearching &&
    !companiesExpanded &&
    matchedCompanies.length > COMPANY_PREVIEW_LIMIT;

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Companies
        </h2>
        <div className="flex items-center gap-3">
          <input
            type="search"
            value={companyQuery}
            onChange={(e) => setCompanyQuery(e.target.value)}
            placeholder="Search companies…"
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm sm:w-64"
          />
          <span className="shrink-0 whitespace-nowrap text-xs text-slate-500">
            <a
              href={`https://github.com/masonlavinder/ai-tracking/issues/new?template=company-suggestion.yml${
                companyQuery.trim()
                  ? `&title=${encodeURIComponent(`Suggest: ${companyQuery.trim()}`)}`
                  : ""
              }`}
              target="_blank"
              rel="noreferrer noopener"
              className="font-medium text-brand-700 hover:text-brand-800 underline"
            >
              Suggest a company
            </a>
          </span>
        </div>
      </div>
      {visibleCompanies.length === 0 ? (
        <div className="mt-3 rounded-md border border-dashed border-slate-300 bg-white p-4 text-center text-xs text-slate-500">
          No companies match &ldquo;{companyQuery}&rdquo;.{" "}
          <a
            href={`https://github.com/masonlavinder/ai-tracking/issues/new?template=company-suggestion.yml&title=${encodeURIComponent(
              `Suggest: ${companyQuery.trim()}`,
            )}`}
            target="_blank"
            rel="noreferrer noopener"
            className="font-medium text-brand-700 hover:text-brand-800 underline"
          >
            Suggest it as an addition
          </a>{" "}
          (requires GitHub).
        </div>
      ) : (
        <div className="mt-3 grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {visibleCompanies.map((c) => (
            <CompanyCard key={c.slug} company={c} />
          ))}
        </div>
      )}
      {hasMoreCompanies && (
        <div className="mt-3">
          <button
            type="button"
            onClick={() => setCompaniesExpanded(true)}
            className="text-xs font-medium text-brand-700 hover:text-brand-800"
          >
            Show all {matchedCompanies.length} companies
          </button>
        </div>
      )}
      {companiesExpanded && !isSearching && (
        <div className="mt-3">
          <button
            type="button"
            onClick={() => setCompaniesExpanded(false)}
            className="text-xs font-medium text-brand-700 hover:text-brand-800"
          >
            Show fewer
          </button>
        </div>
      )}
    </section>
  );
}
