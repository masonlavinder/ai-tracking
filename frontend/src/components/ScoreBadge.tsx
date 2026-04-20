// Color-banded score pill shared by ChangeCard and the Change detail page.
//
// Bands reflect the v1 timeline threshold (4) and rising severity:
//   0–3  muted — below the timeline cut
//   4–5  amber — noteworthy but not severe
//   6–7  orange — significant
//   8–10 red — major

import type { FC } from "react";

type Size = "sm" | "md" | "lg";

const sizeClasses: Record<Size, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm",
  lg: "px-3 py-1.5 text-base",
};

export function scoreBandClasses(score: number): string {
  if (score >= 8) return "bg-rose-600 text-white";
  if (score >= 6) return "bg-orange-500 text-white";
  if (score >= 4) return "bg-amber-400 text-slate-900";
  return "bg-slate-400 text-white";
}

export function scoreBandLabel(score: number): string {
  if (score >= 8) return "Major";
  if (score >= 6) return "Significant";
  if (score >= 4) return "Noteworthy";
  return "Low signal";
}

interface Props {
  score: number;
  outOf?: number;
  size?: Size;
  showLabel?: boolean;
}

export const ScoreBadge: FC<Props> = ({
  score,
  outOf,
  size = "sm",
  showLabel = false,
}) => {
  const band = scoreBandClasses(score);
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md font-semibold ${sizeClasses[size]} ${band}`}
      title={`${scoreBandLabel(score)} (score ${score}${outOf ? `/${outOf}` : ""})`}
    >
      <span>{score}{outOf ? `/${outOf}` : ""}</span>
      {showLabel && (
        <span className="opacity-90 font-normal">{scoreBandLabel(score)}</span>
      )}
    </span>
  );
};
