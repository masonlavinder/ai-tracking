import type { ChangeSummary } from "@types";

const COLUMNS: ReadonlyArray<{ key: keyof ChangeSummary | "tags"; label: string }> = [
  { key: "date", label: "date" },
  { key: "from_date", label: "from_date" },
  { key: "to_date", label: "to_date" },
  { key: "company_name", label: "company" },
  { key: "company_slug", label: "company_slug" },
  { key: "policy_label", label: "policy" },
  { key: "policy_kind", label: "policy_kind" },
  { key: "source_type", label: "source_type" },
  { key: "score", label: "score" },
  { key: "added_count", label: "added" },
  { key: "removed_count", label: "removed" },
  { key: "modified_count", label: "modified" },
  { key: "tags", label: "tags" },
  { key: "url", label: "url" },
  { key: "id", label: "id" },
];

function escapeCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  const str = Array.isArray(value) ? value.join("; ") : String(value);
  if (/[",\n\r]/.test(str)) return `"${str.replace(/"/g, '""')}"`;
  return str;
}

export function downloadChangesCsv(changes: ChangeSummary[], filename: string): void {
  const header = COLUMNS.map((c) => c.label).join(",");
  const rows = changes.map((c) =>
    COLUMNS.map((col) => escapeCell((c as unknown as Record<string, unknown>)[col.key])).join(","),
  );
  // BOM so Excel reads UTF-8 correctly.
  const csv = "﻿" + [header, ...rows].join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
