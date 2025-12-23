import { useEffect, useMemo, useRef, useState } from "react";
import { productService } from "@/services/product_service";
import { Product, ProductWithProvenance } from "@/schema/zodSchema";
import { similarityScore } from "@/lib/similarity";
import { z } from "zod";
import { computeMetrics, normalizePricePerKg} from "@/lib/metrics";
type ScoredProduct = Partial<Product> & { __score?: number; __saved?: boolean };

export type SortKey =
  | "protein-efficiency"
  | "kcal-efficiency"
  | "protein-density"
  | "protein-to-fat"
  | "health-value"
  | "price-low-high"
  | "price-high-low"
  | "unitprice-low-high"
  | "unitprice-high-low"
  | "yield-high-low"      // ✅ NEW
  | "yield-low-high"      // ✅ NEW
  | "efficiency-high-low" // ✅ optional, explicit g/$
  | "density-high-low"    // ✅ optional, explicit g/100kcal
  | "saved-first"
  | "name"
  | "brand"
  | "relevance";


export default function useProductSearch() {
  const [saved, setSaved] = useState<Partial<Product>[]>([]);
  const [items, setItems] = useState<ScoredProduct[]>([]);
  const [sortKey, setSortKey] = useState<SortKey
>("relevance");

  const [lastQuery, setLastQuery] = useState("");
  const [selected, setSelected] = useState<Partial<Product> | null>(null);
  const [loading, setLoading] = useState(false);
  const initLoaded = useRef(false);
  const [store, setStore] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const PAGE_SIZE = 20;

  // Helper key
  const keyOf = (p: { barcode?: string | null; id?: string | null }) =>
    p.barcode ?? (p.id ? String(p.id) : "");

  // Load saved on mount (favourites)
  useEffect(() => {
    const load = async () => {
      try {
        const res = await productService.list();
        setSaved(res);
        // seed items with saved flagged so the UI can show saved-first initially
        setItems(res.map((p: any) => ({ ...p, __saved: true, __score: 0 })));
      } catch (e) {
        console.error("Failed to load saved products.", e);
        setError("Failed to load saved products.");
      } finally {
        initLoaded.current = true;
      }
    };
    load();
  }, []);

  // Defensive helpers for search response shapes
  const normalizeSearchResponse = (res: any) => {
    // items array
    const itemsArr: Partial<Product>[] = res?.items ?? res?.data ?? (Array.isArray(res) ? res : []);
    // detect a next cursor / token / url
    const next =
      res?.next_cursor ??
      res?.nextCursor ??
      res?.next_page_token ??
      res?.nextPageToken ??
      res?.next ??
      res?.meta?.next_cursor ??
      null;

    // also accept "page" offset style if present; convert page->cursor absent
    return { items: itemsArr ?? [], next: next ?? null };
  };

  // Merge & append (keeps scores & saved flag). If incoming contains duplicates keys, newest incoming wins.
  const mergeAppendMap = (
    current: ScoredProduct[],
    incoming: Partial<Product>[],
    q: string,
    savedSet: Set<string>,
  ) => {
    const map = new Map<string, ScoredProduct>();
    // preserve current items order/flags
    for (const c of current) {
      const k = keyOf(c);
      if (k) map.set(k, c);
    }
    // incoming replace / augment
    for (const it of incoming) {
      const k = keyOf(it);
      if (!k) continue;
      const score = similarityScore(q, it.name ?? "", it.brand ?? "");
      const prev = map.get(k);
      map.set(k, {
        ...(prev ?? {}),
        ...it,
        __score: score,
        __saved: savedSet.has(it.barcode ?? ""),
      });
    }
    return Array.from(map.values());
  };
  

  type WithDerived = ScoredProduct & {
    __metrics?: ReturnType<typeof computeMetrics> | null;
    __unitPrice?: number | null;
  };
  
  const safeDesc = (a: number | null | undefined, b: number | null | undefined) => {
    const A = a ?? -Infinity;
    const B = b ?? -Infinity;
    return B - A;
  };
  
  const safeAsc = (a: number | null | undefined, b: number | null | undefined) => {
    const A = a ?? Infinity;
    const B = b ?? Infinity;
    return A - B;
  };
  
  const sortItems = (arr: ScoredProduct[], mode: SortKey) => {
    // 1) Precompute once
    const prepared: WithDerived[] = arr.map((p) => ({
      ...p,
      __metrics: computeMetrics(p),
      __unitPrice: normalizePricePerKg(p), // $/kg
    }));
  
    // 2) Sort using precomputed values
    prepared.sort((a, b) => {
      const ma = a.__metrics;
      const mb = b.__metrics;
  
      const sa = a.__score ?? 0;
      const sb = b.__score ?? 0;
  
      switch (mode) {
        case "protein-efficiency":       // g/$
          return safeDesc(ma?.proteinPerDollar, mb?.proteinPerDollar);
  
        case "kcal-efficiency":          // kcal/$
          return safeDesc(ma?.kcalPerDollar, mb?.kcalPerDollar);
  
        case "protein-density":          // g / 100 kcal (use new density)
          return safeDesc(ma?.density_g_per_100kcal, mb?.density_g_per_100kcal);
  
        case "protein-to-fat":           // g:g
          return safeDesc(ma?.proteinToFatRatio, mb?.proteinToFatRatio);
  
        case "health-value":             // Health★ / $/kg
          return safeDesc(ma?.healthValue, mb?.healthValue);
  
        case "price-low-high":           // raw shelf price
          return safeAsc(a.price_current ?? null, b.price_current ?? null);
  
        case "price-high-low":
          return safeDesc(a.price_current ?? null, b.price_current ?? null);
  
        //  Unit price ($/kg) normalized
        case "unitprice-low-high":
          return safeAsc(a.__unitPrice, b.__unitPrice);
        case "unitprice-high-low":
          return safeDesc(a.__unitPrice, b.__unitPrice);
  
        //  NEW: Yield index
        case "yield-high-low":
          return safeDesc(ma?.yieldIndex, mb?.yieldIndex);
        case "yield-low-high":
          return safeAsc(ma?.yieldIndex, mb?.yieldIndex);
  
        // Optional explicit sorts for the new fields
        case "efficiency-high-low":      // g/$
          return safeDesc(ma?.efficiency_g_per_dollar, mb?.efficiency_g_per_dollar);
        case "density-high-low":         // g/100 kcal
          return safeDesc(ma?.density_g_per_100kcal, mb?.density_g_per_100kcal);
  
        case "saved-first":
          if (a.__saved && !b.__saved) return -1;
          if (!a.__saved && b.__saved) return 1;
          return 0;
  
        case "brand":
          return (a.brand ?? "").localeCompare(b.brand ?? "");
  
        case "name":
          return (a.name ?? "").localeCompare(b.name ?? "");
  
        case "relevance":
        default:
          if (sb !== sa) return sb - sa;
          return (a.name ?? "").localeCompare(b.name ?? "");
      }
    });
  
    return prepared;
  };
  

  const visible = useMemo(() => sortItems(items, sortKey), [items, sortKey]);

  // Search action: query (replace = true when new search; append = true when load-more)
  const performSearch = async (q: string, opts?: { append?: boolean; cursor?: string | null }) => {
    const query = q.trim();
    if (!query) return;
    const append = Boolean(opts?.append);
    const cursor = opts?.cursor ?? null;

    // setup
    if (!append) {
      setLoading(true);
      setError(null);
    } else {
      setLoadingMore(true);
    }

    try {
      // try to pass cursor/limit to productService.search, but fall back if it ignores extra params
      const arg2 = cursor || PAGE_SIZE ? { q: query, cursor, limit: PAGE_SIZE } : { q: query };
      // productService.search may accept (query, opts) or (query) — pass both defensively
      let res: any;
      try {
        res = await (productService as any).search(query, { cursor, limit: PAGE_SIZE });
      } catch (err) {
        // fallback to single-arg search
        res = await (productService as any).search(query);
      }

      const { items: found = [], next } = normalizeSearchResponse(res);

      // saved set (barcodes)
      const savedSet = new Set(saved.map((s) => s.barcode ?? ""));

      if (append) {
        // append to current items (merge by key)
        setItems((prev) => {
          const merged = mergeAppendMap(prev, found, query, savedSet);
          return sortItems(merged, sortKey);
        });
      } else {
        // new search: replace search area but keep previously loaded saved items present in `items`? We'll combine:
        // We want savedProducts to remain visible, so seed with saved items flagged true.
        const seededSaved = (saved ?? []).map((p) => ({ ...(p as any), __saved: true, __score: 0 }));
        const merged = mergeAppendMap(seededSaved, found, query, savedSet);
        setItems(sortItems(merged, sortKey));
        setLastQuery(query);
      }

      // set next cursor if available
      setNextCursor(next ?? null);
    } catch (e) {
      if (e instanceof z.ZodError) {
        console.group("❌ Zod validation failed");
        console.table(
          e.issues.map((i) => ({
            path: i.path.join("."),
            message: i.message,
            expected: (i as any).expected ?? "",
            received: (i as any).received ?? "",
          }))
        );
        console.groupEnd();
      } else {
        console.error("Search failed:", e);
      }
      setError("Search failed.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // public handler for new search (always replace)
  const handleSearch = (q: string) => performSearch(q, { append: false, cursor: null });

  // load more: requires we have lastQuery and nextCursor
  const handleLoadMore = async () => {
    if (!lastQuery) return;
    // if our API doesn't return a cursor but returns pages using offset, try to request with page info.
    if (!nextCursor) {
      // no nextCursor -> nothing to load
      return;
    }
    await performSearch(lastQuery, { append: true, cursor: nextCursor });
  };

  // Save / Unsave (same semantics as before, keep items flag in sync)
  const handleToggleSave = async (row: Partial<Product>) => {
    const k = keyOf(row);
    const alreadySaved = saved.some((s) => keyOf(s) === k);

    // optimistic toggle in items
    setItems((prev) => prev.map((it) => (keyOf(it) === k ? { ...it, __saved: !alreadySaved } : it)));

    try {
      if (alreadySaved) {
        const idOrBarcode = row.id ? String(row.id) : row.barcode ?? "";
        await productService.deleteProduct(`/products/${idOrBarcode}/`);
        setSaved((prev) => prev.filter((s) => keyOf(s) !== k));
      } else {
        const payload: any = {
          barcode: row.barcode ?? null,
          name: row.name ?? "Unnamed",
          brand: row.brand ?? null,
          description: row.description ?? null,
          size: row.size ?? null,
        
          // --- Pricing ---
          price_current: row.price_current ?? null,
          price_was: row.price_was ?? null,
          cup_price_value: row.cup_price_value ?? null,
          cup_price_unit: row.cup_price_unit ?? null,
          is_on_special: row.is_on_special ?? false,
        
          // --- Media / Metadata ---
          image_url: row.image_url ?? null,
          product_url: row.product_url ?? null,
          health_star: row.health_star ?? null,
          allergens: row.allergens ?? null,
        
          // --- Nutrition + Source ---
          nutrition: row.nutrition ?? undefined,
          primary_source: row.primary_source ?? "woolworths",
        };

        if (!payload.cup_price_value && payload.size && payload.price_current) {
          const match = payload.size.match(/([\d.]+)\s*(kg|g|l|ml)/i);
          if (match) {
            const qty = parseFloat(match[1]);
            const unit = match[2].toLowerCase();
            const grams = unit === "kg" || unit === "l" ? qty * 1000 : qty;
            payload.cup_price_value = payload.price_current / (grams / 1000);
            payload.cup_price_unit = "1kg";
          }
        }
        
        

        const savedItem = await productService.save(payload);
        setSaved((prev) => [...prev, savedItem]);
        // reflect canonical saved item into items
        setItems((prev) =>
          prev.map((it) =>
            keyOf(it) === k ? { ...(savedItem as any), __saved: true, __score: it.__score ?? 0 } : it
          )
        );
      }
    } catch (e) {
      console.error("Save/Unsave failed:", e);
      setError("Save action failed.");
      // rollback optimistic change
      setItems((prev) => prev.map((it) => (keyOf(it) === k ? { ...it, __saved: alreadySaved } : it)));
    }
  };

  // Load product details (for modal)
  const handleDetails = async (row: ScoredProduct) => {
    setSelected(row);
    const canEnrich = row.__saved || !!row.id;
    if (!canEnrich) return;
    try {
      const idOrBarcode = row.barcode || String(row.id);
      const detailed = await productService.getDetail(idOrBarcode);
      setSelected((prev) => (prev ? { ...prev, ...detailed } : detailed));
      setItems((prev) =>
        prev.map((it) =>
          keyOf(it) === keyOf(row) ? { ...it, ...detailed, __saved: it.__saved, __score: it.__score } : it
        )
      );
    } catch (err) {
      console.warn("No DB enrichment found; showing search data only", err);
    }
  };

  // Expose useful values & handlers
  return {
    // state
    saved,
    items,
    visible,
    sortKey,
    setSortKey,
    lastQuery,
    selected,
    loading,
    loadingMore,
    error,
    initLoaded: initLoaded.current,
    store,
    nextCursor,

    // actions
    setStore,
    handleSearch,
    handleLoadMore,
    handleToggleSave,
    handleDetails,
    setSelected,
  } as const;
}
