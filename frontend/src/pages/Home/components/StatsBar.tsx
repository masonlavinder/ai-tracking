interface Props {
  companyCount: number;
  totalChanges: number;
  lastUpdated: string;
}

export function StatsBar({ companyCount, totalChanges, lastUpdated }: Props) {
  return (
    <section>
      <dl className="flex flex-wrap items-baseline gap-x-10 gap-y-3 rounded-lg border border-slate-200 bg-white px-5 py-4 text-sm">
        <div className="flex items-baseline gap-2">
          <dt className="uppercase tracking-wide text-slate-500 text-xs">
            Companies tracked
          </dt>
          <dd className="text-xl font-semibold tabular-nums text-slate-900">
            {companyCount}
          </dd>
        </div>
        <div className="flex items-baseline gap-2">
          <dt className="uppercase tracking-wide text-slate-500 text-xs">
            Significant changes
          </dt>
          <dd className="text-xl font-semibold tabular-nums text-slate-900">
            {totalChanges}
          </dd>
        </div>
        <div className="flex items-baseline gap-2">
          <dt className="uppercase tracking-wide text-slate-500 text-xs">
            Last updated
          </dt>
          <dd className="font-mono text-slate-900">{lastUpdated}</dd>
        </div>
      </dl>
    </section>
  );
}
