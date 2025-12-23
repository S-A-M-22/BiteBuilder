import { useMemo } from "react";
import type { Product } from "@/schema/zodSchema";
import { computeMetrics } from "@/lib/metrics";

/**
 * React-friendly memoized wrapper for product metrics.
 */
export function useProductMetrics(product?: Partial<Product>) {
  return useMemo(() => {
    if (!product) return null;
    

    // 🔧 Normalize search payloads → canonical shape
    const normalized = {
      ...product,
      nutrients: product.nutrients ?? product.nutrition ?? null,
    };
    return computeMetrics(normalized);
  }, [product]);
}
