import { Timeline } from "@components/Timeline";
import type { ChangeSummary } from "@types";

interface Props {
  allChanges: ChangeSummary[];
  filteredChanges: ChangeSummary[];
  policyKindOptions: [string, string][];
  policyFilter: string;
  setPolicyFilter: (value: string) => void;
}

export function ChangeHistorySection({
  allChanges,
  filteredChanges,
  policyKindOptions,
  policyFilter,
  setPolicyFilter,
}: Props) {
  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Change history
          {policyFilter !== "all" && (
            <span className="ml-2 text-xs font-normal text-slate-500">
              · {filteredChanges.length} of {allChanges.length}
            </span>
          )}
        </h2>
        {policyKindOptions.length > 1 && (
          <label className="flex items-center gap-1 text-xs text-slate-600">
            Policy
            <select
              value={policyFilter}
              onChange={(e) => setPolicyFilter(e.target.value)}
              className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
            >
              <option value="all">All</option>
              {policyKindOptions.map(([kind, label]) => (
                <option key={kind} value={kind}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      <div className="mt-3">
        <Timeline
          changes={filteredChanges}
          hideCompany
          emptyMessage={
            allChanges.length === 0
              ? "No changes have been detected for this company yet."
              : "No changes match the selected policy."
          }
        />
      </div>
    </section>
  );
}
