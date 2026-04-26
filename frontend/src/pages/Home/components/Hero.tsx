import Logo from "@components/Logo";

export function Hero() {
  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-gradient-to-br from-brand-100 via-white to-white px-6 py-10 sm:px-10 sm:py-14">
      <div className="flex flex-col items-start gap-5 sm:flex-row sm:items-center sm:gap-8">
        <Logo size="xl" className="shrink-0 drop-shadow-sm" />
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
            Watch the Diff
          </h1>
          <p className="mt-2 text-lg font-medium text-brand-700">
            Track the trackers.
          </p>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-700">
            Daily, automated diffs of privacy policies and terms from the
            largest AI companies. Every material change is detected,
            classified, scored, and dated — so you can see exactly how
            AI data-use language shifts over time.
          </p>
        </div>
      </div>
    </section>
  );
}
