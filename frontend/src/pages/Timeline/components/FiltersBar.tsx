import type { CompanySummary } from "@types";

interface Props {
  companies: CompanySummary[];
  allTags: string[];
  companyFilter: string;
  setCompanyFilter: (value: string) => void;
  tagFilter: string;
  setTagFilter: (value: string) => void;
}

export function FiltersBar({
  companies,
  allTags,
  companyFilter,
  setCompanyFilter,
  tagFilter,
  setTagFilter,
}: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      <label className="flex items-center gap-1 text-xs text-slate-600">
        Company
        <select
          value={companyFilter}
          onChange={(e) => setCompanyFilter(e.target.value)}
          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
        >
          <option value="all">All</option>
          {companies.map((c) => (
            <option key={c.slug} value={c.slug}>
              {c.name}
            </option>
          ))}
        </select>
      </label>
      <label className="flex items-center gap-1 text-xs text-slate-600">
        Tag
        <select
          value={tagFilter}
          onChange={(e) => setTagFilter(e.target.value)}
          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-sm"
        >
          <option value="all">All</option>
          {allTags.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
