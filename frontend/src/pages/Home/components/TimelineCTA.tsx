import { Link } from "react-router-dom";

export const TimelineCTA = () => {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-700">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Full change history
          </h2>
          <p className="mt-1">
            See every significant change, newest first, with company and
            tag filters.
          </p>
        </div>
        <Link
          to="/timeline"
          className="inline-flex items-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-brand-700"
        >
          Open the timeline →
        </Link>
      </div>
    </section>
  );
}
