// Uses your existing types — no schema duplication
import type { Meal, Product, ProductNutrient } from "@/schema/zodSchema";

/** Safe numeric parse */
export const num = (v: unknown, fb = 0) => {
  const n =
    typeof v === "string" ? parseFloat(v) : typeof v === "number" ? v : NaN;
  return Number.isFinite(n) ? n : fb;
};
export function per100g(product: any, code: string): number {
  if (!product) return 0;

  // --- Canonical alias mapping ---
  const aliases: Record<string, string[]> = {
    fat_total: ["fat", "total_fat", "total_fats", "fat_total", "fats_total"],
    energy_kcal: ["energy", "energy_kcal", "calories"],
    energy_kj: ["energy_kj", "kj"],
    sugars: ["sugar", "total_sugar", "sugars_total"],
    fiber: ["fibre", "fiber_total"],
    sodium: ["salt", "sodium", "na"],
    potassium: ["k", "potassium", "potassium_k"],
    calcium: ["ca", "calcium"],
    magnesium: ["mg", "magnesium"],
    iron: ["fe", "iron"],
    zinc: ["zn", "zinc"],
    vitamin_c: ["vit_c", "ascorbic_acid", "vitamin_c"],
    vitamin_d: ["vit_d", "cholecalciferol", "vitamin_d"],
    vitamin_b12: ["vit_b12", "cobalamin", "vitamin_b12"],
    folate: ["folate", "vit_b9", "folic_acid"],
    vitamin_a: ["vit_a", "retinol", "retinol_equiv"],
    protein: ["protein", "prot"],
  };

  const targets = [code, ...(aliases[code] ?? [])].map(t => t.toLowerCase());

  // 1️⃣ Relational model
  const arr = product.product_nutrients ?? [];
  for (const pn of arr as any[]) {
    const c = pn?.nutrient?.code?.toLowerCase();
    if (targets.includes(c)) return Number(pn?.amount_per_100g) || 0;
  }

  // 2️⃣ Scraper / flattened schema
  const src = product.nutrition || product.nutrients;
  if (src) {
    for (const key of targets) {
      const entry = src[key];
      if (!entry) continue;
      const val =
        entry?.per_100?.value ??
        entry?.per_100?.amount ??
        entry?.per_100 ??
        entry?.value ??
        0;
      const parsed = Number(val);
      if (Number.isFinite(parsed) && parsed > 0) return parsed;
    }
  }

  // 3️⃣ Derived fallback for energy conversions
  if (code === "energy_kcal") {
    const kj =
      per100g(product, "energy_kj") ||
      per100g(product, "energy") ||
      per100g(product, "energy-kj");
    if (kj) return kj / 4.184;
  }

  return 0;
}


export type MealTotals = {
  // Core energy + macros
  energy_kcal: number;
  energy_kj: number;
  protein: number;
  fat_total: number;
  fat_saturated: number;
  carbohydrate: number;
  sugars: number;
  fiber: number;

  // Electrolytes & minerals
  sodium: number;
  potassium: number;
  calcium: number;
  magnesium: number;
  iron: number;
  zinc: number;

  // Vitamins
  vitamin_c: number;
  vitamin_d: number;
  vitamin_b12: number;
  folate: number;        // often in µg
  vitamin_a: number;     // µg retinol equivalents

  // Economics
  price_total: number;
};


/** Aggregate totals for a meal using quantity in grams (per-100g × grams/100). */
/** Aggregate totals for a meal using quantity in grams (per-100g × grams/100). */
export function aggregateMealTotals(meal: Pick<Meal, "items">): MealTotals {
  const totals: MealTotals = {
    energy_kcal: 0,
    energy_kj: 0,
    protein: 0,
    fat_total: 0,
    fat_saturated: 0,
    carbohydrate: 0,
    sugars: 0,
    fiber: 0,
  
    sodium: 0,
    potassium: 0,
    calcium: 0,
    magnesium: 0,
    iron: 0,
    zinc: 0,
  
    vitamin_c: 0,
    vitamin_d: 0,
    vitamin_b12: 0,
    folate: 0,
    vitamin_a: 0,
  
    price_total: 0,
  };
  
  for (const item of meal.items ?? []) {
    const grams = Math.max(0, num(item?.quantity));
    if (!grams || !item?.product) continue;
    const factor = grams / 100;

    // ─── Nutrients ────────────────────────────────
totals.energy_kcal  += per100g(item.product, "energy_kcal") * factor;
totals.energy_kj    += per100g(item.product, "energy_kj") * factor;
totals.protein      += per100g(item.product, "protein") * factor;
totals.fat_total    += per100g(item.product, "fat_total") * factor;
totals.fat_saturated+= per100g(item.product, "fat_saturated") * factor;
totals.carbohydrate += per100g(item.product, "carbohydrate") * factor;
totals.sugars       += per100g(item.product, "sugars") * factor;
totals.fiber        += per100g(item.product, "fiber") * factor;
totals.sodium       += per100g(item.product, "sodium") * factor;

// ─── Micronutrients ────────────────────────────
totals.potassium    += per100g(item.product, "potassium") * factor;
totals.calcium      += per100g(item.product, "calcium") * factor;
totals.magnesium    += per100g(item.product, "magnesium") * factor;
totals.iron         += per100g(item.product, "iron") * factor;
totals.zinc         += per100g(item.product, "zinc") * factor;
totals.vitamin_c    += per100g(item.product, "vitamin_c") * factor;
totals.vitamin_d    += per100g(item.product, "vitamin_d") * factor;
totals.vitamin_b12  += per100g(item.product, "vitamin_b12") * factor;
totals.folate       += per100g(item.product, "folate") * factor;
totals.vitamin_a    += per100g(item.product, "vitamin_a") * factor;

    // ─── 💰 Price Calculation ─────────────────────────
    let unitPricePerGram: number | null = null;

    // 1️⃣ Prefer Woolworths-style cup price
    if (item.product.cup_price_value && item.product.cup_price_unit) {
      const unit = item.product.cup_price_unit.toLowerCase().trim();

      if (unit.includes("1kg")) unitPricePerGram = item.product.cup_price_value / 1000;
      else if (unit.includes("100g")) unitPricePerGram = item.product.cup_price_value / 100;
      else if (unit.includes("1g")) unitPricePerGram = item.product.cup_price_value;
      else if (unit.includes("1l")) unitPricePerGram = item.product.cup_price_value / 1000;
      else if (unit.includes("100ml")) unitPricePerGram = item.product.cup_price_value / 100;
      else if (unit.includes("1ml")) unitPricePerGram = item.product.cup_price_value;
    }

    // 2️⃣ Fallback: manual price ÷ parsed size
    if (!unitPricePerGram) {
      const totalPrice = num(item.product.price_current);
      const sizeGrams = parseSizeToGrams(item.product.size) ?? 0;
      if (totalPrice > 0 && sizeGrams > 0) {
        unitPricePerGram = totalPrice / sizeGrams;
      }
    }

    // 3️⃣ Apply to total
    if (unitPricePerGram) {
      totals.price_total += unitPricePerGram * grams;
    }
  }

  // ─── Rounding ─────────────────────────
  totals.energy_kcal = Math.round(totals.energy_kcal);
  totals.energy_kj = Math.round(totals.energy_kj);
  totals.protein = +totals.protein.toFixed(1);
  totals.price_total = +totals.price_total.toFixed(2);
  console.log("[aggregateMealTotals] totals:", totals);
  return totals;
}


export function parseSizeToGrams(size: string | null | undefined): number | null {
  if (!size) return null;
  const s = size.toLowerCase().replace(/\s+/g, "");

  // Ranges like "450g-650g" or "450g–650g" → take average
  const rangeMatch = s.match(/(\d+(?:\.\d+)?)[-–](\d+(?:\.\d+)?)/);
  if (rangeMatch) {
    const [a, b] = [parseFloat(rangeMatch[1]), parseFloat(rangeMatch[2])];
    if (s.includes("kg")) return ((a + b) / 2) * 1000;
    if (s.includes("g")) return (a + b) / 2;
  }

  // Single units
  const single = s.match(/(\d+(?:\.\d+)?)(kg|g|ml)/);
  if (!single) return null;
  const [, val, unit] = single;
  const num = parseFloat(val);
  if (unit === "kg") return num * 1000;
  if (unit === "ml") return num; // assume density ≈ 1 g/mL for liquids
  if (unit === "g") return num;
  return null;
}

export const pickKcalProtein = (t: MealTotals) => ({
  kcal: t.energy_kcal,
  protein: t.protein,
});

import type { MealItem } from "@/schema/zodSchema";

/** Compute nutrient totals for a single MealItem (quantity in grams). */
export function mealItemNutrition(item: MealItem) {
  const grams = num(item?.quantity);
  if (!item?.product || !grams) return null;

  const factor = grams / 100;

  const nutrition = {
    // --- Core macros ---
    energy_kcal: per100g(item.product, "energy_kcal") * factor,
    energy_kj: per100g(item.product, "energy_kj") * factor,
    protein: per100g(item.product, "protein") * factor,
    fat_total: per100g(item.product, "fat_total") * factor,
    fat_saturated: per100g(item.product, "fat_saturated") * factor,
    carbohydrate: per100g(item.product, "carbohydrate") * factor,
    sugars: per100g(item.product, "sugars") * factor,
    fiber: per100g(item.product, "fiber") * factor,
    sodium: per100g(item.product, "sodium") * factor,

    // --- Micronutrients ---
    potassium: per100g(item.product, "potassium") * factor,
    calcium: per100g(item.product, "calcium") * factor,
    iron: per100g(item.product, "iron") * factor,
    magnesium: per100g(item.product, "magnesium") * factor,
    cholesterol: per100g(item.product, "cholesterol") * factor,
    zinc: per100g(item.product, "zinc") * factor,
    vitamin_c: per100g(item.product, "vitamin_c") * factor,
    vitamin_d: per100g(item.product, "vitamin_d") * factor,
    vitamin_b12: per100g(item.product, "vitamin_b12") * factor,
  };

  // Optional rounding for display
  return Object.fromEntries(
    Object.entries(nutrition).map(([k, v]) => [k, +v.toFixed(1)])
  );
}

/** Get only kcal & protein for concise use in UI (e.g. pills). */
export function pickKcalProteinFromItem(item: MealItem) {
  const n = mealItemNutrition(item);
  return n
    ? { kcal: n.energy_kcal, protein: n.protein }
    : { kcal: 0, protein: 0 };
}
/** Daily Recommended Intake (general adult, 2000 kcal diet) */
export const DRI = {
  energy_kcal: 2000,
  protein: 50,
  carbohydrate: 275,
  fat_total: 70,
  fat_saturated: 20,
  fiber: 28,
  sugars: 50,
  sodium: 2300,
  potassium: 3700,
  calcium: 1000,
  magnesium: 400,
  iron: 18,
  zinc: 11,
  vitamin_c: 90,
  vitamin_d: 20,     // µg = 800 IU
  vitamin_b12: 2.4,  // µg
  folate: 400,       // µg DFE
  vitamin_a: 900,    // µg RAE
};


/**
 * Thresholds for quick nutrition heuristics.
 * Tweak to match your playbook/guidelines.
 */
// src/lib/nutritionThresholds.ts
// ------------------------------------------------------------
// Evidence-backed thresholds (AU/UK/WHO) + a few heuristics.
// "Lower is better" → use classifyThreshold(value, thresholds)
// "Higher is better" → use classifyMinimum(value, minimums)
// ------------------------------------------------------------

export type ThresholdsLowerIsBetter = Readonly<{ good: number; ok: number }>;
export type MinimumsHigherIsBetter = Readonly<{ good: number; ok: number }>;

export function classifyMinimum(
  value: number | null,
  mins: MinimumsHigherIsBetter | undefined
): "good" | "ok" | "high" | "unknown" {
  if (value == null || mins == null) return "unknown";
  if (value >= mins.good) return "good";
  if (value >= mins.ok) return "ok";
  return "high"; // "high" here = below the minimum / needs improvement
}

/**
 * LOWER-IS-BETTER thresholds that align with official guidance
 * or well-accepted label systems. These plug straight into your
 * existing classifyThreshold(value, thresholds).
 */
export const NUTRIENT_THRESHOLDS = {
  // -------------------- Ratios (heuristics) --------------------
  /** Fat / Protein (g:g). Lower = leaner. Heuristic tuned for “lean” picks. */
  fat_to_protein: { good: 0.5, ok: 1.0 } as ThresholdsLowerIsBetter,

  /** Sugars / Fibre (g:g). Lower suggests better carb quality. Heuristic. */
  sugar_to_fiber: { good: 2.0, ok: 5.0 } as ThresholdsLowerIsBetter,

  /** Saturated / Total fat (fraction). Lower is better. Heuristic aligned with ≤10% energy from SFA. */
  satfat_to_fat: { good: 0.33, ok: 0.5 } as ThresholdsLowerIsBetter,

  // -------------------- Sodium (evidence-based) --------------------
  /**
   * Solids: per 100 g sodium (mg). AU/FSANZ “low” ≤120 mg/100g.
   * Use 120 (good), 400 (ok) → >400 high.
   */
  sodium_mg_per_100g: { good: 120, ok: 400 } as ThresholdsLowerIsBetter,

  /**
   * Liquids: per 100 mL sodium (mg). FSANZ “low” also ≤120 mg/100 mL.
   * Keep same good cut-off; set 300 as OK to flag soups/broths (conservative).
   */
  sodium_mg_per_100ml: { good: 120, ok: 300 } as ThresholdsLowerIsBetter,

  // -------------------- Sugars (evidence-based traffic-light) --------------------
  /**
   * UK traffic-light for TOTAL sugars per 100 g:
   * Low ≤5 g, High >22.5 g → map to good/ok/high.
   */
  sugars_g_per_100g: { good: 5, ok: 22.5 } as ThresholdsLowerIsBetter,

  /**
   * Drinks (per 100 mL): Low ≤2.5 g, High >11.25 g (UK system).
   */
  sugars_g_per_100ml: { good: 2.5, ok: 11.25 } as ThresholdsLowerIsBetter,

  // -------------------- Saturated fat (evidence-based traffic-light) --------------------
  /**
   * Sat fat per 100 g: Low ≤1.5 g, High >5 g (UK system).
   */
  satfat_g_per_100g: { good: 1.5, ok: 5 } as ThresholdsLowerIsBetter,

  // -------------------- Total fat (traffic-light; optional) --------------------
  /**
   * Total fat per 100 g: Low ≤3 g, High >17.5 g (UK system).
   */
  fat_g_per_100g: { good: 3, ok: 17.5 } as ThresholdsLowerIsBetter,

  // -------------------- Energy density (public-health framing) --------------------
  /**
   * Energy density per 100 g (kJ).
   * Practical “snack” framing in AU uses ≤600 kJ/serve; research flags >950 kJ/100 g as high ED.
   * Use ≤600 good, ≤950 ok, >950 high to nudge toward lower ED choices.
   */
  energy_kj_per_100g: { good: 600, ok: 950 } as ThresholdsLowerIsBetter,
} as const;

/**
 * HIGHER-IS-BETTER minimums you can use with classifyMinimum(...)
 * to flag “good sources” of beneficial nutrients.
 */
export const NUTRIENT_MINIMUMS = {
  /**
   * Fibre per serving (g). Practical picking rule-of-thumb:
   * ≥5 g good, ≥3 g ok (aligns with many AU label-reading guides).
   */
  fiber_g_per_serving: { good: 5, ok: 3 } as MinimumsHigherIsBetter,

  /**
   * Protein density per 100 g (g). Heuristic useful for staples:
   * ≥10 g/100 g good, ≥5 g/100 g ok.
   */
  protein_g_per_100g: { good: 10, ok: 5 } as MinimumsHigherIsBetter,
} as const;

export type ThresholdKey = keyof typeof NUTRIENT_THRESHOLDS;

export function classifyThreshold(
  value: number | null | undefined,
  t: { good: number; ok: number },
): "good" | "ok" | "high" | "unknown" {
  if (value == null || Number.isNaN(value)) return "unknown";
  if (value <= t.good) return "good";
  if (value <= t.ok) return "ok";
  return "high";
}

export function toneForCategory(cat: "good" | "ok" | "high" | "unknown") {
  switch (cat) {
    case "good":
      return "text-green-700 bg-green-50 border-green-200";
    case "ok":
      return "text-yellow-700 bg-yellow-50 border-yellow-200";
    case "high":
      return "text-red-700 bg-red-50 border-red-200";
    default:
      return "text-gray-600 bg-gray-50 border-gray-200";
  }
}

