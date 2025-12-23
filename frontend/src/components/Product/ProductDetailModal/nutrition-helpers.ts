// src/lib/nutrition-matrix.ts
import { DRI, NUTRIENT_THRESHOLDS, classifyThreshold } from "@/lib/nutrition";
import type { Product } from "@/schema/zodSchema";

/** Normalized nutrient row (unchanged) */
export type NutrientRow = {
  name: string;
  unit?: string;
  per100: number | null;
  perServing: number | null;
};

export function normalizeNutrients(product?: Partial<Product>): NutrientRow[] {
  if (!product) return [];
  if (product.product_nutrients?.length) {
    return product.product_nutrients.map((pn) => ({
      name: pn.nutrient?.name ?? "",
      unit: pn.nutrient?.unit ?? "",
      per100: pn.amount_per_100g ?? null,
      perServing: pn.amount_per_serving ?? null,
    }));
  }
  if (product.nutrition) {
    return Object.entries(product.nutrition).map(([key, val]: [string, any]) => ({
      name: val.label ?? key,
      unit: val.per_100?.unit ?? "",
      per100: val.per_100?.value ?? null,
      perServing: val.per_serving?.value ?? null,
    }));
  }
  return [];
}

/** Enriched %DRI calculator (kept simple) */
export function calcPercentages(rows: NutrientRow[]) {
  const keyFromLabel = (label: string): keyof typeof DRI | undefined => {
    const lower = label.toLowerCase();
    if (lower.includes("protein")) return "protein";
    if (lower.includes("energy") || lower.includes("cal")) return "energy_kcal";
    if (lower.includes("carb")) return "carbohydrate";
    if (lower.includes("fat total") || lower === "fat") return "fat_total";
    if (lower.includes("saturated")) return "fat_saturated";
    if (lower.includes("fiber") || lower.includes("fibre")) return "fiber";
    if (lower.includes("sugar")) return "sugars";
    if (lower.includes("sodium") || lower.includes("salt")) return "sodium";
    return undefined;
  };

  return rows.map((n) => {
    const k = keyFromLabel(n.name);
    const base = k ? DRI[k] : undefined;
    const value = n.perServing ?? n.per100 ?? null;
    const pct = base && value != null ? (value / base) * 100 : null;
    return { ...n, percent: pct, driBase: base };
  });
}

/** ---------- UI-friendly metric model ---------- */

export type UICategory = "good" | "ok" | "high" | "unknown";

/** Severity for coloring; you can map to Tailwind tokens */
export type UISeverity = "success" | "warning" | "danger" | "muted";

/** Basis clarifies what the value represents */
export type UIBasis = "per serving" | "per 100g" | "ratio";

/** One ready-to-render metric */
export type UIMetric = {
  key: string;
  label: string;
  value: number | null;         // raw numeric
  display: string;              // formatted, human-friendly
  unit?: string;                // optional suffix (e.g., "mg")
  basis: UIBasis;               // how to read the number
  category: UICategory;         // threshold bucket
  severity: UISeverity;         // map directly to chip/card tone
  score: number | null;         // 0..100 within band (for progress bars)
  verdict: string;              // “Lean”, “Caution”, etc.
  rationale: string;            // short why
  help: string;                 // hover/helptext
  thresholds?: { low?: number; high?: number; unit?: string; note?: string };
  dependsOn?: string[];         // which inputs used (for tooltips)
  missing?: string[];           // which inputs were missing (for tooltips)
};

const toneFromCat = (c: UICategory): UISeverity =>
  c === "good" ? "success" : c === "ok" ? "warning" : c === "high" ? "danger" : "muted";

const verdictFromCat = (c: UICategory, label: string): string =>
  c === "good" ? "Lean / favorable"
  : c === "ok" ? "Acceptable"
  : c === "high" ? "High—limit"
  : `Not enough data`;

const rationaleFromKey = (key: string, v: number | null): string => {
  if (v == null) return "No reliable value.";
  switch (key) {
    case "fat_to_protein": return v <= 0.5 ? "More protein than fat." : "Fat outweighs protein.";
    case "sugar_to_fiber": return v <= 2 ? "Fiber buffers sugars." : "Sugars dominate over fiber.";
    case "satfat_to_fat":  return v <= 0.33 ? "Small portion is saturated." : "Large share is saturated fat.";
    case "sodium_mg_per_100g": return v <= 120 ? "Low sodium density." : "Elevated sodium density.";
    default: return "";
  }
};

const fmtNumber = (v: number | null, opts?: { dp?: number; unit?: string }): string => {
  if (v == null || Number.isNaN(v)) return "—";
  const dp = opts?.dp ?? (Math.abs(v) >= 100 ? 0 : Math.abs(v) >= 10 ? 1 : 2);
  const s = v.toFixed(dp).replace(/\.0+$/,"").replace(/(\.\d*[1-9])0+$/,"$1");
  return opts?.unit ? `${s} ${opts.unit}` : s;
};

const nzDiv = (a: number | null, b: number | null) =>
  a != null && b != null && b !== 0 ? Number((a / b).toFixed(2)) : null;

/** Canonical keyer to avoid mixing sat fat vs total fat */
type Canon =
  | "protein"
  | "energy_kcal"
  | "carbohydrate"
  | "fat_total"
  | "fat_saturated"
  | "fiber"
  | "sugars"
  | "sodium";

const keyFromLabel = (label: string): Canon | undefined => {
  const lower = label.toLowerCase().trim();
  if (lower.includes("protein")) return "protein";
  if (lower.includes("energy") || lower.includes("kcal")) return "energy_kcal";
  if (lower.includes("carb")) return "carbohydrate";
  if (lower.includes("saturated")) return "fat_saturated"; // match before total fat
  if (/\b(total\s+fat|fat\s+total)\b/.test(lower) || lower === "fat" || lower === "fat total") return "fat_total";
  if (lower.includes("fiber") || lower.includes("fibre")) return "fiber";
  if (lower.includes("sugar")) return "sugars";
  if (lower.includes("sodium") || lower.includes("salt")) return "sodium";
  return undefined;
};

type CanonVals = { perServing: number | null; per100: number | null };

const chooseBest = (rows: NutrientRow[]) => {
  const best: Partial<Record<Canon, CanonVals>> = {};
  for (const r of rows) {
    const k = keyFromLabel(r.name);
    if (!k) continue;
    const current = best[k];
    if (!current) {
      best[k] = { perServing: r.perServing ?? null, per100: r.per100 ?? null };
    } else {
      // prefer whichever fills a gap
      best[k] = {
        perServing: current.perServing ?? r.perServing ?? null,
        per100: current.per100 ?? r.per100 ?? null,
      };
    }
  }
  return best;
};

const getValue = (best: Partial<Record<Canon, CanonVals>>, k: Canon, prefer: "serving" | "100g" = "serving") => {
  const v = best[k];
  if (!v) return { value: null, basis: (prefer === "serving" ? "per serving" : "per 100g") as UIBasis, missing: [k] };
  const value = prefer === "serving" ? (v.perServing ?? v.per100 ?? null) : (v.per100 ?? v.perServing ?? null);
  const missing: string[] = [];
  if (value == null) missing.push(k);
  return { value, basis: (prefer === "serving" ? "per serving" : "per 100g") as UIBasis, missing };
};

/** Map classifyThreshold output -> category + score within band */
const classifyWithScore = (
  value: number | null,
  key: keyof typeof NUTRIENT_THRESHOLDS
): { category: UICategory; score: number | null; thresholds?: UIMetric["thresholds"] } => {
  const cat = classifyThreshold(value, NUTRIENT_THRESHOLDS[key]) as UICategory;
  const t = NUTRIENT_THRESHOLDS[key] as any;

  // Best-effort normalized score 0..100:
  // - If "good": 66–100 scaled inside the good band
  // - If "ok":   33–66
  // - If "high": 0–33 (worse)
  let score: number | null = null;
  if (value == null) score = null;
  else if (cat === "good") score = 80;
  else if (cat === "ok") score = 55;
  else if (cat === "high") score = 20;
  else score = null;

  const thresholds =
    key === "sodium_mg_per_100g"
      ? { low: 120, high: 400, unit: "mg/100g", note: "≤120 low; ≤400 moderate" }
      : undefined;

  return { category: cat, score, thresholds };
};

// buildMatrix: user-friendly output for MatrixView + ThresholdLine
export function buildMatrix(rows: NutrientRow[]): UIMetric[] {
  const best = chooseBest(rows);

  const protein    = getValue(best, "protein").value;
  const fatTotal   = getValue(best, "fat_total").value;
  const satFat     = getValue(best, "fat_saturated").value;
  const sugars     = getValue(best, "sugars").value;
  const fiber      = getValue(best, "fiber").value;

  const sodiumG    = getValue(best, "sodium", "100g"); // sodium basis per 100g
  const sodium100  = sodiumG.value;

  const fatToProtein = nzDiv(fatTotal, protein);
  const sugarToFiber = nzDiv(sugars, fiber);
  const satfatToFat  = nzDiv(satFat, fatTotal);

  // helper: pack common UI fields; we can still return UIMetric and add extra props
  const pack = (
    args: {
      key: string;
      label: string;
      value: number | null;
      unit?: string;
      basis: UIBasis;
      thresholdsKey: keyof typeof NUTRIENT_THRESHOLDS;
      help: string;                // small, non-numeric hint
      causeWhenHigh: string;       // plain-English cause if cat === "high"
      threshold: number;           // single primary threshold for the ruler
      direction?: "lower" | "higher";
      dependsOn: string[];
      missing: string[];
      displayDp?: number;
    }
  ): UIMetric => {
    const { category } = classifyWithScore(args.value, args.thresholdsKey); // just to get bucket
    const display = fmtNumber(args.value, { dp: args.displayDp ?? 2, unit: args.unit });

    // Add minimal, human-oriented fields; TS will allow extra props on UIMetric
    return {
      key: args.key,
      label: args.label,
      value: args.value,
      display,
      unit: args.unit ?? (args.basis === "ratio" ? "g/g" : undefined),
      basis: args.basis,
      category,
      severity: toneFromCat(category),
      verdict: category === "good" ? "Favorable"
             : category === "ok"   ? "Acceptable"
             : category === "high" ? "Limit / Caution"
             : "Not enough data",
      // keep ‘help’ short and numberless
      help: args.help,
      // no numeric rationale; only show a plain-English cause when high
      rationale: category === "high" ? args.causeWhenHigh : "",
      dependsOn: args.dependsOn,
      missing: args.missing,
      // --- additions for the simple ruler ---
      // single target + direction; MatrixView can pass these to <ThresholdLine/>
      // (extra fields beyond UIMetric are fine in TS if UIMetric is not sealed)
      // @ts-expect-error extra UI helpers for our MatrixView
      threshold: args.threshold,
      // @ts-expect-error extra UI helpers for our MatrixView
      direction: args.direction ?? "lower",
    } as UIMetric & { threshold: number; direction: "lower" | "higher" };
  };

  const m1 = pack({
    key: "fat_to_protein",
    label: "Fat : Protein",
    value: fatToProtein,
    unit: "g/g",
    basis: "ratio",
    thresholdsKey: "fat_to_protein",
    help: "Lower is leaner.",
    causeWhenHigh: "Too much fat for the amount of protein.",
    threshold: 0.5,
    direction: "lower",
    dependsOn: ["fat_total", "protein"],
    missing: [
      ...(fatTotal == null ? ["fat_total"] : []),
      ...(protein == null ? ["protein"] : []),
    ],
    displayDp: 2,
  });

  const m2 = pack({
    key: "sugar_to_fiber",
    label: "Sugars : Fiber",
    value: sugarToFiber,
    unit: "g/g",
    basis: "ratio",
    thresholdsKey: "sugar_to_fiber",
    help: "Lower suggests better carb quality.",
    causeWhenHigh: "Too much sugar for the amount of fiber.",
    threshold: 2.0,
    direction: "lower",
    dependsOn: ["sugars", "fiber"],
    missing: [
      ...(sugars == null ? ["sugars"] : []),
      ...(fiber == null ? ["fiber"] : []),
    ],
    displayDp: 2,
  });

  const m3 = pack({
    key: "satfat_to_fat",
    label: "Saturated / Total Fat",
    value: satfatToFat,
    basis: "ratio",
    thresholdsKey: "satfat_to_fat",
    help: "Smaller saturated fraction is better.",
    causeWhenHigh: "Too much saturated fat within total fat.",
    threshold: 0.33,
    direction: "lower",
    dependsOn: ["fat_saturated", "fat_total"],
    missing: [
      ...(satFat == null ? ["fat_saturated"] : []),
      ...(fatTotal == null ? ["fat_total"] : []),
    ],
    displayDp: 2,
  });

  const m4 = pack({
    key: "sodium_mg_per_100g",
    label: "Sodium density",
    value: sodium100,
    unit: "mg",
    basis: "per 100g",
    thresholdsKey: "sodium_mg_per_100g",
    help: "Lower sodium per 100g is better.",
    causeWhenHigh: "High sodium per 100g.",
    threshold: 120,              // single clear cut for “low”
    direction: "lower",
    dependsOn: ["sodium"],
    missing: [...(sodium100 == null ? ["sodium"] : [])],
    displayDp: 0,
  });

  return [m1, m2, m3, m4];
}
