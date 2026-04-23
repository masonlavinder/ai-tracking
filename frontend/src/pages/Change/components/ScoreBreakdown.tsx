import { ScoreBadge } from "@components/ScoreBadge";
import type { ChangeDetail } from "@types";

const SCORE_ROW_LABELS: Record<string, string> = {
  content: "Real content (not boilerplate)",
  tags: "Per-tag credit (2 × tags)",
  add_only: "Only adds paragraphs",
  heading_keyword: "Keyword in a nearby heading",
};

export function ScoreBreakdown({ change }: { change: ChangeDetail }) {
  const breakdown = change.score_breakdown as unknown as Record<string, number>;
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Significance score
      </h2>
      <div className="mt-2 rounded-md border border-slate-200 bg-white p-4 text-sm">
        <ScoreBadge score={change.score} outOf={10} size="lg" showLabel />
        <ul className="mt-3 space-y-1 text-slate-700">
          {Object.entries(SCORE_ROW_LABELS).map(([key, label]) => {
            const value = breakdown[key] ?? 0;
            return (
              <li key={key} className="flex justify-between">
                <span>{label}</span>
                <span className="font-mono">
                  {value > 0 ? `+${value}` : value}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
