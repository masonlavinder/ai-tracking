// Change detail page: diff blocks, tags, source link, score breakdown.

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { loadChangeDetail } from "@api";
import type { ChangeDetail } from "@types";
import { ChangeHeader } from "./components/ChangeHeader";
import { SummaryBox } from "./components/SummaryBox";
import { ScoreBreakdown } from "./components/ScoreBreakdown";
import { DiffViewer } from "./components/DiffViewer";

export const Change = () => {
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
      <ChangeHeader change={change} />
      {change.llm_summary && <SummaryBox summary={change.llm_summary} />}
      <ScoreBreakdown change={change} />
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
