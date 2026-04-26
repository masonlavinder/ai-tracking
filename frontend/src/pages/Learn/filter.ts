interface ArticleLike {
  category: string;
  title: string;
  source: string;
  summary: string;
  why?: string;
}

interface TermLike {
  term: string;
  definition: string;
}

export function articleMatches(article: ArticleLike, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    article.category.toLowerCase().includes(q) ||
    article.title.toLowerCase().includes(q) ||
    article.source.toLowerCase().includes(q) ||
    article.summary.toLowerCase().includes(q) ||
    (article.why?.toLowerCase().includes(q) ?? false)
  );
}

export function termMatches(term: TermLike, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    term.term.toLowerCase().includes(q) ||
    term.definition.toLowerCase().includes(q)
  );
}
