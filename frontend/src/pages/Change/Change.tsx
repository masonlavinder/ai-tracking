// Change detail page: diff blocks, tags, source link, score breakdown.

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { DiffViewer } from "../../components/DiffViewer";
import { ScoreBadge } from "../../components/ScoreBadge";
import { TagBadge } from "../../components/TagBadge";
import { loadChangeDetail } from "../../lib/data";
import type { ChangeDetail } from "../../lib/types";

const SCORE_ROW_LABELS: Record<string, string> = {
  content: "Real content (not boilerplate)",
  tags: "Per-tag credit (2 × tags)",
  add_only: "Only adds paragraphs",
  heading_keyword: "Keyword in a nearby heading",
};

export function Change() {
  const { id = "" } = useParams<{ id: string }>();
  const [change, setChange] = useState<ChangeDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    loadChangeDetail(id)
      .then((data) => {
        if (!cancelled) {
          setChange(data);
          setLoading(false);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return <div className="text-sm text-slate-500">Loading…</div>;
  }
  if (error || !change) {
    return (
      <div className="rounded-md border border-rose-300 bg-rose-50 p-4 text-sm text-rose-900">
        {error ?? "Change not found."}{" "}
        <Link to="/" className="underline">
          Back to timeline
        </Link>
        .
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <Link
          to={`/companies/${change.company_slug}`}
          className="text-xs text-slate-500 hover:underline"
        >
          ← {change.company_name}
        </Link>
        <h1 className="mt-1 text-2xl font-semibold text-slate-900">
          {change.policy_label}
        </h1>
        <div className="mt-1 text-sm text-slate-600">
          {change.from_date} → {change.to_date}
        </div>
        {change.url && (
          <a
            className="mt-2 inline-block text-sm text-sky-700 underline"
            href={change.url}
            target="_blank"
            rel="noreferrer noopener"
          >
            Source page
          </a>
        )}
        {change.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {change.tags.map((t) => (
              <TagBadge key={t} tag={t} />
            ))}
          </div>
        )}
      </header>

      {change.llm_summary && (
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            In plain English
          </h2>
          <div className="mt-2 rounded-md border border-sky-200 bg-sky-50 p-4 text-sm text-slate-800">
            <p className="whitespace-pre-wrap leading-relaxed">
              {change.llm_summary}
            </p>
            <p className="mt-3 text-xs text-slate-500">
              AI-generated summary (gpt-4o-mini via GitHub Models).
              Verify against the diff below before citing. Not legal advice.
            </p>
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Significance score
        </h2>
        <div className="mt-2 rounded-md border border-slate-200 bg-white p-4 text-sm">
          <ScoreBadge score={change.score} outOf={10} size="lg" showLabel />
          <ul className="mt-3 space-y-1 text-slate-700">
            {Object.entries(SCORE_ROW_LABELS).map(([key, label]) => {
              const value =
                (change.score_breakdown as unknown as Record<string, number>)[
                  key
                ] ?? 0;
              return (
                <li key={key} className="flex justify-between">
                  <span>{label}</span>
                  <span className="font-mono">
                    {value > 0 ? `+${value}` : value}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Diff
        </h2>
        <div className="mt-2">
          <DiffViewer change={change} />
        </div>
      </section>
    </div>
  );
}
