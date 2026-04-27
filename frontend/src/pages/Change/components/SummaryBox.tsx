export const SummaryBox = ({ summary }: { summary: string }) => {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        In plain English
      </h2>
      <div className="mt-2 rounded-md border border-sky-200 bg-sky-50 p-4 text-sm text-slate-800">
        <p className="whitespace-pre-wrap leading-relaxed">{summary}</p>
        <p className="mt-3 text-xs text-slate-500">
          AI-generated summary (gpt-4o-mini via GitHub Models).
          Verify against the diff below before citing. Not legal advice.
        </p>
      </div>
    </section>
  );
}
