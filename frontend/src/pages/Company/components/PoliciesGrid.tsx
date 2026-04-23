import type { CompanySummary } from "@types";

export function PoliciesGrid({ policies }: { policies: CompanySummary["policies"] }) {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        Tracked policies
      </h2>
      {policies.length === 0 ? (
        <div className="mt-2 rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-500">
          No snapshots captured yet.
        </div>
      ) : (
        <ul className="mt-2 grid gap-2 sm:grid-cols-2">
          {policies.map((p) => (
            <li
              key={p.policy_id}
              className="rounded-md border border-slate-200 bg-white p-3 text-sm"
            >
              <div className="font-medium text-slate-900">{p.label}</div>
              {p.url && (
                <a
                  className="break-all text-xs text-sky-700 underline"
                  href={p.url}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  {p.url}
                </a>
              )}
              <div className="mt-1 text-xs text-slate-500">
                Latest snapshot: {p.latest_snapshot_date || "—"}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
