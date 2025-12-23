// Lightweight similarity to bias sort after each new search
export function similarityScore(
  query: string,
  name?: string | null,
  brand?: string | null,
) {
  const q = query.trim().toLowerCase();
  if (!q) return 0;
  const hay = `${name ?? ""} ${brand ?? ""}`.toLowerCase();

  if (hay.includes(q)) return 100;
  if (name?.toLowerCase().startsWith(q) || brand?.toLowerCase().startsWith(q))
    return 80;

  const qTokens = q.split(/\s+/).filter(Boolean);
  const hits = qTokens.filter((t) => hay.includes(t)).length;
  return Math.min(60, hits * 15);
}
