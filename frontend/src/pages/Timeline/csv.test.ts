import { describe, expect, it } from "vitest";
import type { ChangeSummary } from "@types";
import { buildChangesCsv } from "./csv";

const BASE: ChangeSummary = {
  id: "acme-privacy_policy-us-2026-04-01-2026-04-15",
  company_slug: "acme",
  company_name: "Acme",
  source_type: "policy",
  policy_kind: "privacy_policy",
  policy_label: "Acme Privacy Policy",
  url: "https://acme.example/privacy",
  from_date: "2026-04-01",
  to_date: "2026-04-15",
  date: "2026-04-15",
  tags: ["ai-training-expansion", "third-party-sharing"],
  score: 7,
  added_count: 3,
  removed_count: 1,
  modified_count: 2,
};

describe("buildChangesCsv", () => {
  it("emits header + one row per change", () => {
    const csv = buildChangesCsv([BASE]);
    const lines = csv.replace(/^﻿/, "").split("\r\n");
    expect(lines).toHaveLength(2);
    expect(lines[0]).toMatch(/^date,from_date,to_date,company,/);
    expect(lines[1]).toContain("Acme");
  });

  it("joins tag arrays with a semicolon so Excel shows them in one cell", () => {
    const csv = buildChangesCsv([BASE]);
    expect(csv).toContain("ai-training-expansion; third-party-sharing");
  });

  it("quotes cells containing commas, quotes, or newlines", () => {
    const tricky: ChangeSummary = {
      ...BASE,
      policy_label: 'Acme, Inc. "Privacy"\nPolicy',
    };
    const csv = buildChangesCsv([tricky]);
    expect(csv).toContain('"Acme, Inc. ""Privacy""\nPolicy"');
  });

  it("prepends a UTF-8 BOM so Excel reads it as UTF-8", () => {
    const csv = buildChangesCsv([]);
    expect(csv.charCodeAt(0)).toBe(0xfeff);
  });

  it("emits only a header when given zero changes", () => {
    const csv = buildChangesCsv([]).replace(/^﻿/, "");
    expect(csv.split("\r\n")).toHaveLength(1);
  });

  it("preserves zero-valued numeric columns rather than dropping them", () => {
    const zeros: ChangeSummary = {
      ...BASE,
      score: 0,
      added_count: 0,
      removed_count: 0,
      modified_count: 0,
    };
    const csv = buildChangesCsv([zeros]);
    const row = csv.split("\r\n")[1];
    // score,added,removed,modified are columns 9–12; all four should be literal "0"
    const cols = row.split(",");
    expect(cols.slice(8, 12)).toEqual(["0", "0", "0", "0"]);
  });

  it("emits an empty cell for a change with no tags", () => {
    const noTags: ChangeSummary = { ...BASE, tags: [] };
    const csv = buildChangesCsv([noTags]);
    // The `tags` column is position 13 (0-indexed 12).
    const cols = csv.split("\r\n")[1].split(",");
    expect(cols[12]).toBe("");
  });
});
