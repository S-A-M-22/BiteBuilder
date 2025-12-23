import { useState } from "react";
import type { Product } from "@/schema/zodSchema";
import { productService } from "@/services/product_service";
import { similarityScore } from "@/lib/similarity";

type WithFlags<T> = T & { __qty?: number; __score?: number; __selected?: boolean; __saved?: boolean };

export function useMealProductSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<WithFlags<Partial<Product>>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const safeKey = (p: Partial<Product>) =>
    (p as any).id ?? (p as any).barcode ?? (p as any).gtin ?? (p as any).code ?? JSON.stringify(p);

  const mergeAppend = (
    current: WithFlags<Partial<Product>>[],
    incoming: Partial<Product>[],
    q: string
  ) => {
    const map = new Map<string, WithFlags<Partial<Product>>>();
    for (const c of current) map.set(String(safeKey(c)), c);
    for (const it of incoming) {
      const k = String(safeKey(it));
      if (!k) continue;
      const prev = map.get(k);
      map.set(k, {
        ...(prev ?? {}),
        ...it,
        __qty: prev?.__qty ?? 100,
        __score: similarityScore(q, it.name ?? "", it.brand ?? ""),
      });
    }
    return Array.from(map.values());
  };

  const handleSearch = async (q: string) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuery(trimmed);
    setLoading(true);
    setError(null);

    try {
      const res = await productService.search(trimmed);
      const newResults = mergeAppend([], res.items ?? [], trimmed);
      setResults(newResults);
    } catch (err) {
      console.error("Search failed:", err);
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  };

  const setQty = (key: string, qty: number) => {
    setResults((prev) =>
      prev.map((it) =>
        String(safeKey(it)) === key ? { ...it, __qty: Math.max(1, qty) } : it
      )
    );
  };

  return {
    query,
    setQuery,
    results,
    setResults,
    loading,
    error,
    handleSearch,
    setQty,
  };
}
