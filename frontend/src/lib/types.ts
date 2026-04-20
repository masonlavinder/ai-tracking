// Mirrors the JSON schemas produced by the analysis pipeline.
// Keep in sync with analysis/src/analysis/models.py.

export type SourceType = "policy";

export interface ParagraphChange {
  before: string;
  after: string;
}

export interface ChangeSummary {
  id: string;
  company_slug: string;
  company_name: string;
  source_type: SourceType;
  policy_kind: string;
  policy_label: string;
  url: string;
  from_date: string;
  to_date: string;
  date: string;
  tags: string[];
  score: number;
  added_count: number;
  removed_count: number;
  modified_count: number;
}

export interface ScoreBreakdown {
  content: number;
  tags: number;
  add_only: number;
  heading_keyword: number;
  total: number;
}

export interface ChangeDetail extends Omit<ChangeSummary, "added_count" | "removed_count" | "modified_count"> {
  added_paragraphs: string[];
  removed_paragraphs: string[];
  modified_paragraphs: ParagraphChange[];
  score_breakdown: ScoreBreakdown;
}

export interface PolicyEntry {
  policy_id: string;
  label: string;
  url: string;
  latest_snapshot_date: string;
}

export interface CompanySummary {
  slug: string;
  name: string;
  ticker: string | null;
  sec_cik: string | null;
  homepage_url: string | null;
  stock_url: string | null;
  latest_snapshot_date: string | null;
  total_changes: number;
  recent_change_ids: string[];
  policies: PolicyEntry[];
}

export interface CompaniesFile {
  generated_at: string;
  companies: CompanySummary[];
}

export interface ChangesFile {
  generated_at: string;
  changes: ChangeSummary[];
}

export interface TimelineFile {
  generated_at: string;
  threshold: number;
  changes: ChangeSummary[];
}
