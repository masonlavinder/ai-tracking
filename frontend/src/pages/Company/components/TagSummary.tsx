interface Props {
  companyName: string;
  tags: string[];
}

export function TagSummary({ companyName, tags }: Props) {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        What we've seen change
      </h2>
      {tags.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">
          No classified changes yet. This is not a statement about{" "}
          {companyName}'s data practices — only about what has changed in
          the tracked snapshots.
        </p>
      ) : (
        <p className="mt-2 text-sm text-slate-600">
          Historical changes have touched: {tags.join(", ")}.
        </p>
      )}
    </section>
  );
}
