// src/hooks/useMealItemPrice.ts
import { useMemo } from "react";
import type { Product } from "@/schema/zodSchema";
import { parseSizeToGrams, num } from "@/lib/nutrition";

/**
 * Computes unit price and total price for a given product & quantity (grams),
 * matching the same logic used in aggregateMealTotals().
 */
export function useMealItemPrice(product: Product | undefined, grams: number) {
  return useMemo(() => {
    if (!product || !grams) return { unitPricePerGram: null, price: 0 };

    let unitPricePerGram: number | null = null;

    // 1️⃣ Prefer Woolworths-style cup price
    if (product.cup_price_value && product.cup_price_unit) {
      const unit = product.cup_price_unit.toLowerCase().trim();
      if (unit.includes("1kg")) unitPricePerGram = product.cup_price_value / 1000;
      else if (unit.includes("100g")) unitPricePerGram = product.cup_price_value / 100;
      else if (unit.includes("1g")) unitPricePerGram = product.cup_price_value;
      else if (unit.includes("1l")) unitPricePerGram = product.cup_price_value / 1000;
      else if (unit.includes("100ml")) unitPricePerGram = product.cup_price_value / 100;
      else if (unit.includes("1ml")) unitPricePerGram = product.cup_price_value;
    }

    // 2️⃣ Fallback: total price ÷ parsed size
    if (!unitPricePerGram) {
      const totalPrice = num(product.price_current);
      const sizeGrams = parseSizeToGrams(product.size) ?? 0;
      if (totalPrice > 0 && sizeGrams > 0)
        unitPricePerGram = totalPrice / sizeGrams;
    }

    // 3️⃣ Compute total price for given grams
    const price = unitPricePerGram ? unitPricePerGram * grams : 0;

    return { unitPricePerGram, price };
  }, [product, grams]);
}
