// Vertical stacked list of ChangeCards used on home and company pages.

import type { ChangeSummary } from "../lib/types";
import { ChangeCard } from "./ChangeCard";

interface Props {
  changes: ChangeSummary[];
  hideCompany?: boolean;
  emptyMessage?: string;
}

export function Timeline({
  changes,
  hideCompany = false,
  emptyMessage = "No changes detected yet.",
}: Props) {
  if (changes.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        {emptyMessage}
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-3">
      {changes.map((change) => (
        <ChangeCard
          key={change.id}
          change={change}
          hideCompany={hideCompany}
        />
      ))}
    </div>
  );
}
