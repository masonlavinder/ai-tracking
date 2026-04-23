// Renders a ChangeDetail as side-by-side paragraph blocks.
//
// We intentionally avoid unified diffs / diff2html: the analysis pipeline
// already produces paragraph-granularity additions, removals, and
// (before, after) modification pairs. A semantic green/red presentation
// is more readable for policy language than line-numbered hunks.

import type { ChangeDetail } from "@types";

function Block({
  kind,
  text,
}: {
  kind: "added" | "removed" | "before" | "after";
  text: string;
}) {
  const styles: Record<typeof kind, string> = {
    added: "border-emerald-300 bg-emerald-50 text-emerald-700",
    removed: "border-rose-300 bg-rose-50 text-rose-700 line-through decoration-rose-400/60",
    before: "border-rose-300 bg-rose-50 text-rose-700",
    after: "border-emerald-300 bg-emerald-50 text-emerald-700",
  };
  return (
    <div
      className={`whitespace-pre-wrap rounded-md border px-3 py-2 text-sm leading-relaxed ${styles[kind]}`}
    >
      {text}
    </div>
  );
}

function SectionLabel({ label, count }: { label: string; count: number }) {
  return (
    <h3 className="mt-6 flex items-baseline gap-2 text-sm font-semibold uppercase tracking-wide text-slate-700">
      {label}
      <span className="text-xs font-normal text-slate-500">({count})</span>
    </h3>
  );
}

export function DiffViewer({ change }: { change: ChangeDetail }) {
  const hasAnyContent =
    change.added_paragraphs.length +
      change.removed_paragraphs.length +
      change.modified_paragraphs.length >
    0;

  if (!hasAnyContent) {
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-500">
        No textual diff content recorded for this change.
      </div>
    );
  }

  return (
    <div>
      {change.added_paragraphs.length > 0 && (
        <>
          <SectionLabel label="Added" count={change.added_paragraphs.length} />
          <div className="mt-2 flex flex-col gap-2">
            {change.added_paragraphs.map((p, i) => (
              <Block key={`add-${i}`} kind="added" text={p} />
            ))}
          </div>
        </>
      )}

      {change.modified_paragraphs.length > 0 && (
        <>
          <SectionLabel
            label="Modified"
            count={change.modified_paragraphs.length}
          />
          <div className="mt-2 flex flex-col gap-4">
            {change.modified_paragraphs.map((pair, i) => (
              <div
                key={`mod-${i}`}
                className="grid gap-2 md:grid-cols-2"
              >
                <Block kind="before" text={pair.before} />
                <Block kind="after" text={pair.after} />
              </div>
            ))}
          </div>
        </>
      )}

      {change.removed_paragraphs.length > 0 && (
        <>
          <SectionLabel
            label="Removed"
            count={change.removed_paragraphs.length}
          />
          <div className="mt-2 flex flex-col gap-2">
            {change.removed_paragraphs.map((p, i) => (
              <Block key={`rem-${i}`} kind="removed" text={p} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
