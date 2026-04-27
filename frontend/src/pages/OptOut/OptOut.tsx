import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { loadCompanies } from "@api";
import type { CompanySummary } from "@types";
import { companyContent } from "@data/companyContent";
import type { OptOutInfo, OptOutLink } from "@data/companyContent";
import Logo from "@components/Logo";

interface CompanyEntry {
  company: CompanySummary;
  optOut: OptOutInfo;
}

const ExternalLink = ({ link }: { link: OptOutLink }) => {
  return (
    <div>
      <a
        href={link.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-sm font-medium text-brand-700 hover:underline"
      >
        {link.label} ↗
      </a>
      {link.notes && (
        <p className="mt-1 text-xs italic text-slate-500">{link.notes}</p>
      )}
    </div>
  );
}

interface CardProps extends CompanyEntry {
  isHighlighted: boolean;
}

const CompanyOptOutCard = ({ company, optOut, isHighlighted }: CardProps) => {
  return (
    <section
      id={`company-${company.slug}`}
      className={`scroll-mt-20 rounded-xl border bg-white p-5 transition ${
        isHighlighted
          ? "border-brand-400 ring-2 ring-brand-200"
          : "border-slate-200"
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">
          {company.name}
        </h2>
        <Link
          to={`/companies/${company.slug}`}
          className="text-xs font-medium text-slate-500 hover:text-brand-700 hover:underline"
        >
          Change history →
        </Link>
      </div>

      <dl className="mt-4 grid gap-5 sm:grid-cols-2">
        <div className="rounded-lg bg-brand-50 p-4 ring-1 ring-brand-200 sm:col-span-2">
          <dt className="text-xs font-semibold uppercase tracking-wide text-brand-800">
            AI training opt-out
          </dt>
          <dd className="mt-2">
            {optOut.trainingOptOut ? (
              <ExternalLink link={optOut.trainingOptOut} />
            ) : (
              <p className="text-sm leading-relaxed text-slate-700">
                {optOut.trainingOptOutNote ??
                  "No formal training opt-out is exposed."}
              </p>
            )}
          </dd>
        </div>

        {optOut.settingsUrl && (
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Privacy & account settings
            </dt>
            <dd className="mt-2">
              <a
                href={optOut.settingsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="break-all text-sm font-medium text-brand-700 hover:underline"
              >
                {optOut.settingsUrl} ↗
              </a>
            </dd>
          </div>
        )}

        {optOut.deletion && (
          <div>
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Account / data deletion
            </dt>
            <dd className="mt-2">
              <ExternalLink link={optOut.deletion} />
            </dd>
          </div>
        )}

        {optOut.notes && (
          <div className="sm:col-span-2">
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Worth knowing
            </dt>
            <dd className="mt-2 text-sm leading-relaxed text-slate-700">
              {optOut.notes}
            </dd>
          </div>
        )}
      </dl>
    </section>
  );
}

function scrollToCompany(slug: string) {
  const el = document.getElementById(`company-${slug}`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export const OptOut = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const targetSlug = searchParams.get("company");
  const [companies, setCompanies] = useState<CompanySummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    loadCompanies()
      .then((file) => {
        if (!cancelled) {
          setCompanies(file.companies);
          setLoading(false);
        }
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
  }, []);

  const entries = useMemo<CompanyEntry[]>(() => {
    return companies
      .map((company) => {
        const optOut = companyContent[company.slug]?.optOut;
        return optOut ? { company, optOut } : null;
      })
      .filter((e): e is CompanyEntry => e !== null)
      .sort((a, b) => a.company.name.localeCompare(b.company.name));
  }, [companies]);

  useEffect(() => {
    if (loading || !targetSlug) return;
    const id = window.setTimeout(() => scrollToCompany(targetSlug), 50);
    return () => window.clearTimeout(id);
  }, [loading, targetSlug, entries.length]);

  return (
    <div className="flex flex-col gap-6">
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-brand-100 via-white to-white px-6 py-8 sm:px-10 sm:py-10">
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6">
          <Logo size="lg" className="shrink-0 drop-shadow-sm" />
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
              How to opt out
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-700">
              Privacy settings, AI training opt-outs, and account deletion
              tools for every company tracked on this site. One page, plain
              links.
            </p>
          </div>
        </div>
      </section>

      <div className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        <strong className="font-semibold">Verify before acting.</strong>{" "}
        These pages, toggle names, and URLs change as companies redesign
        their privacy interfaces. The links here are best-effort and
        accurate at time of writing. If a link 404s or a setting has moved,
        the company's privacy page is the canonical source.
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : error ? (
        <div className="rounded-md border border-rose-300 bg-rose-50 p-4 text-sm text-rose-900">
          Failed to load company list: {error}
        </div>
      ) : (
        <>
          <nav className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Jump to
            </p>
            <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm">
              {entries.map(({ company }) => (
                <li key={company.slug}>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchParams(
                        { company: company.slug },
                        { replace: true },
                      );
                      scrollToCompany(company.slug);
                    }}
                    className="text-brand-700 hover:underline"
                  >
                    {company.name}
                  </button>
                </li>
              ))}
            </ul>
          </nav>

          <div className="flex flex-col gap-4">
            {entries.map((entry) => (
              <CompanyOptOutCard
                key={entry.company.slug}
                company={entry.company}
                optOut={entry.optOut}
                isHighlighted={entry.company.slug === targetSlug}
              />
            ))}
          </div>
        </>
      )}

      <p className="mt-2 text-xs italic text-slate-500">
        Not legal advice. Opt-out commitments differ by region — EU and
        California users typically have stronger statutory rights than the
        defaults shown here.
      </p>
    </div>
  );
}
