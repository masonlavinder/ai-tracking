// Colored pill for classifier tags. Color is chosen deterministically from
// the tag string so the palette is stable across pages without a map.

import type { FC } from "react";

const PALETTE = [
  "bg-sky-100 text-sky-900 border-sky-200",
  "bg-emerald-100 text-emerald-900 border-emerald-200",
  "bg-amber-100 text-amber-900 border-amber-200",
  "bg-rose-100 text-rose-900 border-rose-200",
  "bg-violet-100 text-violet-900 border-violet-200",
  "bg-lime-100 text-lime-900 border-lime-200",
  "bg-cyan-100 text-cyan-900 border-cyan-200",
  "bg-fuchsia-100 text-fuchsia-900 border-fuchsia-200",
];

function hashString(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export const TagBadge: FC<{ tag: string }> = ({ tag }) => {
  const classes = PALETTE[hashString(tag) % PALETTE.length];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${classes}`}
    >
      {tag}
    </span>
  );
};
