// src/lib/metrics.ts
import type { Meal, Product } from "@/schema/zodSchema";
import { per100g } from "@/lib/nutrition";

export function normalizePricePerKg(product?: Partial<Product>): number | null {
  if (!product?.cup_price_value || !product.cup_price_unit) return null;
  const val = product.cup_price_value;
  const unit = product.cup_price_unit.toLowerCase().trim();

  if (unit.includes("1kg"))   return val;
  if (unit.includes("100g"))  return val * 10;
  if (unit.includes("1g"))    return val * 1000;
  if (unit.includes("1l"))    return val;        // assume ~1 kg/L
  if (unit.includes("100ml")) return val * 10;
  if (unit.includes("1ml"))   return val * 1000;
  return null;
}

/** Pure helper: build yield index from already-normalized inputs */
function calcYieldIndex(
  protPer100g: number,     // g / 100g
  kcalPer100g: number,     // kcal / 100g
  pricePerKg: number,      // $ / kg
  E_TARGET = 20,           // tune from your catalog (e.g., 75th pct)
) {
  if (!protPer100g || !kcalPer100g || !pricePerKg) return null;

  // $ per 100g
  const pricePer100g = pricePerKg / 10;                     // $/100g
  const efficiency   = protPer100g / pricePer100g;          // g / $
  const density      = (protPer100g / kcalPer100g) * 100;   // g / 100 kcal

  const normEff = Math.min(1, efficiency / E_TARGET);
  const normDen = Math.min(1, density / 25);                // 25 g/100 kcal ceiling (~pure protein)

  const yieldIndex = Math.sqrt(normEff * normDen);

  return {
    efficiency_g_per_dollar: +efficiency.toFixed(3),
    density_g_per_100kcal: +density.toFixed(2),
    yieldIndex: +yieldIndex.toFixed(3),
  };
}

/**
 * Core efficiency metrics — pure function (no hooks).
 * Uses cup price normalized to $/kg for *all* $-based metrics.
 */
export function computeMetrics(product?: Partial<Product>) {
  if (!product) return null;

  const pricePerKg = normalizePricePerKg(product);
  if (!pricePerKg || pricePerKg <= 0) return null;

  // Nutrients (robust fallbacks)
  const protein = per100g(product, "protein") ?? 0;
  const kcal    = per100g(product, "energy_kcal") ?? 0;
  const fat     = per100g(product, "fat_total") ?? per100g(product, "fat") ?? 0;
  const healthStar = Number(product.health_star);

  // $-metrics
  const pricePer100g = pricePerKg / 10;
  const proteinPerDollar = protein ? +(protein / pricePer100g).toFixed(2) : null;
  const kcalPerDollar    = kcal ? +(kcal / pricePer100g).toFixed(0) : null;

  // Ratios
  const proteinToFatRatio = fat > 0 ? +(protein / fat).toFixed(2) : null;
  const proteinPerKcal    = kcal > 0 ? +(protein / kcal).toFixed(3) : null;
  const healthValue       = product.health_star != null
    ? +((healthStar || 0) / pricePerKg).toFixed(3)
    : null;

  // Yield
  const yi = calcYieldIndex(protein, kcal, pricePerKg);

  const metrics = {
    pricePerKg,
    pricePer100g: +pricePer100g.toFixed(3),
    proteinPerDollar,
    kcalPerDollar,
    proteinPerKcal,
    proteinToFatRatio,
    healthValue,
    yieldIndex: yi?.yieldIndex ?? null,
    efficiency_g_per_dollar: yi?.efficiency_g_per_dollar ?? null,
    density_g_per_100kcal: yi?.density_g_per_100kcal ?? null,
  };

  // Debug group
  const missing = Object.entries(metrics)
    .filter(([_, v]) => v === null || Number.isNaN(v))
    .map(([k]) => k);

  console.groupCollapsed(`🧮 computeMetrics for: ${product.name ?? "Unnamed Product"}`);
  console.table(metrics);
  if (missing.length)
    console.warn("⚠️ Missing or invalid fields:", missing);
  else
    console.info("✅ All fields populated.");
  console.groupEnd();

  return metrics;
}



export function computeMealMetrics(meal?: Meal) {
  const items = meal?.items ?? [];
  if (items.length === 0) return null;

  let totalWeight = 0;
  const agg = { proteinPerDollar: 0, kcalPerDollar: 0, yieldIndex: 0 };

  for (const it of items) {
    const metrics = computeMetrics(it.product);
    if (!metrics) continue;

    const weight = it.quantity ?? 100;
    totalWeight += weight;
    agg.proteinPerDollar += (metrics.proteinPerDollar ?? 0) * weight;
    agg.kcalPerDollar += (metrics.kcalPerDollar ?? 0) * weight;
    agg.yieldIndex += (metrics.yieldIndex ?? 0) * weight;
  }

  for (const key of Object.keys(agg) as (keyof typeof agg)[]) {
    agg[key] = +(agg[key] / totalWeight).toFixed(2);
  }

  return agg;
}
