import { Link } from "react-router-dom";
import Logo from "@components/Logo";

const destinations: { to: string; label: string; description: string }[] = [
  {
    to: "/",
    label: "Home",
    description: "The latest changes across all tracked companies.",
  },
  {
    to: "/timeline",
    label: "Timeline",
    description: "Filterable history of every detected change.",
  },
  {
    to: "/learn",
    label: "Learn",
    description: "Plain-language glossary and curated explainers.",
  },
  {
    to: "/about",
    label: "About",
    description: "Methodology, scoring, and limitations.",
  },
];

export const NotFound = () => {
  return (
    <div className="flex flex-col gap-6">
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-brand-100 via-white to-white px-6 py-10 sm:px-10 sm:py-14">
        <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:gap-8">
          <Logo size="xl" className="shrink-0 opacity-60 drop-shadow-sm" />
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-brand-700">
              404
            </p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
              No record of this page in the diff.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-700">
              The page you're looking for may have been moved, renamed, or
              never existed. Either way, it isn't here. Even watchers miss
              things sometimes.
            </p>
          </div>
        </div>
      </section>

      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Try one of these
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {destinations.map((d) => (
            <Link
              key={d.to}
              to={d.to}
              className="group rounded-xl border border-slate-200 bg-white p-4 transition hover:border-brand-300 hover:shadow-sm"
            >
              <h3 className="text-base font-semibold text-slate-900 group-hover:text-brand-800">
                {d.label} →
              </h3>
              <p className="mt-1 text-sm text-slate-600">{d.description}</p>
            </Link>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-500">
        Think this is a broken link?{" "}
        <a
          href="https://github.com/masonlavinder/ai-tracking/issues"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-brand-700"
        >
          Open an issue on GitHub
        </a>
        .
      </p>
    </div>
  );
}
