// src/hooks/useDashboardInsights.ts
import { useMemo } from "react";
import type { Goal, GoalNutrient, EatenMeal, Meal } from "@/schema/zodSchema";
import { aggregateMealTotals } from "@/lib/nutrition";
import type { Insight } from "@/types/insights";

// ---------- Config / defaults ----------
const DEFAULT_CALORIE_GOAL = 2000; // used if goal.target_calories is null
const FIBER_MIN_G = 28;            // general guideline
const SODIUM_MAX_MG = 2300;        // general guideline
const ADDED_SUGAR_MAX_PCT_KCAL = 10; // we only have total sugars; treat as soft check
const SAT_FAT_MAX_PCT_KCAL = 10;

type Totals = Record<string, number>;

function sumDayTotals(eatenMeals: EatenMeal[]): Totals {
  return eatenMeals.reduce((acc, em) => {
    const t = aggregateMealTotals(em.meal);
    for (const [k, v] of Object.entries(t)) {
      if (v == null) continue;
      acc[k] = (acc[k] ?? 0) + v;
    }
    return acc;
  }, {} as Record<string, number>);
}

function findGoalAmount(nutrients: GoalNutrient[], code: string, fallbackName?: string): number | null {
  const n =
    nutrients.find((gn) => gn.nutrient?.code === code) ||
    (fallbackName
      ? nutrients.find((gn) => gn.nutrient?.name.toLowerCase().includes(fallbackName))
      : undefined);
  return n ? n.target_amount : null;
}

function pct(n: number, d: number | null | undefined): number {
  if (!d || d <= 0) return 0;
  return (n / d) * 100;
}

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

function round1(n: number) {
  return Math.round(n * 10) / 10;
}

function energySplit(t: Totals) {
  const pE = (t.protein ?? 0) * 4;
  const fE = (t.fat_total ?? 0) * 9;
  const cE = (t.carbohydrate ?? 0) * 4;
  const total = pE + fE + cE || 0.0001;
  return {
    proteinPct: (pE / total) * 100,
    fatPct: (fE / total) * 100,
    carbPct: (cE / total) * 100,
  };
}

// ---------- Rule helpers ----------
function makeInsight(params: Omit<Insight, "id">): Insight {
  // Create a reasonably stable id from message+tags
  const base = `${params.message}|${(params.tags || []).join(",")}`;
  const id = `ins_${btoa(unescape(encodeURIComponent(base))).slice(0, 16)}`;
  return { id, ...params };
}

// ---------- Hook ----------
export function useDashboardInsights(
  goal: Goal | null,
  nutrients: GoalNutrient[],
  eatenMeals: EatenMeal[],
  meals: Meal[],
  opts?: { limit?: number }
) {
  return useMemo<Insight[]>(() => {
    if (!goal || !nutrients?.length) return [];

    const totals = sumDayTotals(eatenMeals);
    const kcal = totals.energy_kcal ?? 0;
    const protein = totals.protein ?? 0;
    const fiber = totals.fiber ?? 0;
    const sodium = totals.sodium ?? 0;
    const sugars = totals.sugars ?? 0;

    const calorieGoal = goal.target_calories ?? DEFAULT_CALORIE_GOAL;
    const proteinGoal = findGoalAmount(nutrients, "protein", "protein");
    const fiberGoal = findGoalAmount(nutrients, "fiber", "fiber") ?? FIBER_MIN_G;
    const sodiumMax = findGoalAmount(nutrients, "sodium", "sodium") ?? SODIUM_MAX_MG;

    const { proteinPct, fatPct, carbPct } = energySplit(totals);

    const out: Insight[] = [];

    // 1) Calorie pacing
    {
      const p = pct(kcal, calorieGoal);
      if (p < 50) {
        out.push(
          makeInsight({
            severity: "high",
            score: clamp(80 - p, 0, 80),
            tags: ["calories"],
            message:
              "You’re well under your daily calories — add a balanced meal to avoid underfueling.",
            metric: { key: "energy_kcal", value: round1(kcal), unit: "kcal", target: calorieGoal },
            action: { label: "Add a meal", hint: "Aim for a mix of protein + complex carbs." },
          })
        );
      } else if (p > 130) {
        out.push(
          makeInsight({
            severity: "critical",
            score: clamp(p - 130, 0, 100),
            tags: ["calories"],
            message:
              "You’re over your calorie target — lighten upcoming meals or add activity to offset.",
            metric: { key: "energy_kcal", value: round1(kcal), unit: "kcal", target: calorieGoal },
            action: { label: "Plan next meal", hint: "Lean protein + veg, modest carbs." },
          })
        );
      } else if (p >= 90 && p <= 110) {
        out.push(
          makeInsight({
            severity: "info",
            score: 15,
            tags: ["calories"],
            message: "Calorie pacing looks on track. Nice work.",
            metric: { key: "energy_kcal", value: round1(kcal), unit: "kcal", target: calorieGoal },
          })
        );
      }
    }

    // 2) Protein vs target
    if (proteinGoal && proteinGoal > 0) {
      const p = pct(protein, proteinGoal);
      if (p < 70) {
        out.push(
          makeInsight({
            severity: "high",
            score: clamp(70 - p, 0, 70),
            tags: ["protein"],
            message:
              "Protein is tracking low — add lean meats, eggs, Greek yogurt, or tofu/legumes.",
            metric: { key: "protein", value: round1(protein), unit: "g", target: proteinGoal },
            action: { label: "Boost protein", hint: "20–40 g in next meal/snack." },
          })
        );
      } else if (p > 120) {
        out.push(
          makeInsight({
            severity: "info",
            score: 20,
            tags: ["protein"],
            message: "Protein target exceeded — great for recovery and satiety.",
            metric: { key: "protein", value: round1(protein), unit: "g", target: proteinGoal },
          })
        );
      }
    }

    // 3) Fiber floor
    {
      if (fiber < fiberGoal) {
        const gap = fiberGoal - fiber;
        out.push(
          makeInsight({
            severity: gap > 10 ? "high" : "medium",
            score: clamp(gap * 2, 0, 60),
            tags: ["fiber"],
            message:
              "Fiber is below the daily floor — add whole grains, legumes, veg, or berries.",
            metric: { key: "fiber", value: round1(fiber), unit: "g", target: fiberGoal },
            action: { label: "Add fiber", hint: "Aim +8–12 g across next meals." },
          })
        );
      }
    }

    // 4) Sodium cap
    {
      if (sodium > sodiumMax) {
        out.push(
          makeInsight({
            severity: "high",
            score: clamp((sodium / sodiumMax) * 40, 0, 80),
            tags: ["sodium"],
            message: "Sodium is above your daily cap — reduce processed foods or sauces.",
            metric: { key: "sodium", value: Math.round(sodium), unit: "mg", target: sodiumMax },
            action: { label: "Lower sodium", hint: "Swap to herbs/spices; check labels." },
          })
        );
      }
    }

    // 5) Saturated fat % of kcal
    {
      const satG = totals.fat_saturated ?? 0;
      const satKcal = satG * 9;
      const satPct = pct(satKcal, kcal);
      if (kcal >= 800 && satPct > SAT_FAT_MAX_PCT_KCAL) {
        out.push(
          makeInsight({
            severity: satPct > 15 ? "high" : "medium",
            score: clamp((satPct - 10) * 3, 0, 60),
            tags: ["sat_fat"],
            message:
              "Saturated fat is high as a share of calories — prefer unsaturated fats (olive oil, nuts, fish).",
            metric: { key: "fat_saturated", value: round1(satG), unit: "g", target: undefined },
            action: { label: "Improve fat quality", hint: "Swap butter/fried foods for olive oil/fish." },
          })
        );
      }
    }

    // 6) Sugars soft guardrail (total sugars vs 10% kcal; informational)
    {
      const sugarKcal = sugars * 4;
      const sugarPct = pct(sugarKcal, kcal);
      if (kcal >= 800 && sugarPct > ADDED_SUGAR_MAX_PCT_KCAL) {
        out.push(
          makeInsight({
            severity: sugarPct > 15 ? "medium" : "info",
            score: clamp((sugarPct - 10) * 2, 0, 40),
            tags: ["sugars"],
            message:
              "Sugars are a large share of today’s calories — balance with protein/fiber to steady energy.",
            metric: { key: "sugars", value: round1(sugars), unit: "g" },
            action: { label: "Balance next meal", hint: "Add protein + fiber; pick whole fruit over juice." },
          })
        );
      }
    }

    // 7) Macro energy distribution (coarse balance)
    {
      if (proteinPct < 20) {
        out.push(
          makeInsight({
            severity: "medium",
            score: clamp((20 - proteinPct) * 1.2, 0, 40),
            tags: ["macro_balance"],
            message: "Protein <20% of energy — add a protein anchor to meals.",
            details: `P/F/C ≈ ${round1(proteinPct)}% / ${round1(fatPct)}% / ${round1(carbPct)}%`,
          })
        );
      }
      if (fatPct > 40) {
        out.push(
          makeInsight({
            severity: "medium",
            score: clamp((fatPct - 40) * 1.2, 0, 40),
            tags: ["macro_balance"],
            message: "Fats >40% of energy — rebalance with complex carbs/lean protein.",
            details: `P/F/C ≈ ${round1(proteinPct)}% / ${round1(fatPct)}% / ${round1(carbPct)}%`,
          })
        );
      }
      if (carbPct < 35) {
        out.push(
          makeInsight({
            severity: "info",
            score: clamp((35 - carbPct), 0, 25),
            tags: ["macro_balance"],
            message: "Carbs <35% of energy — add whole-grain or fruit-based carbs for fuel.",
            details: `P/F/C ≈ ${round1(proteinPct)}% / ${round1(fatPct)}% / ${round1(carbPct)}%`,
          })
        );
      }
    }

    // Sort: severity > score
    const weight: Record<Insight["severity"], number> = {
      critical: 3,
      high: 2,
      medium: 1,
      info: 0,
    };
    out.sort((a, b) => {
      const d = weight[b.severity] - weight[a.severity];
      return d !== 0 ? d : b.score - a.score;
    });

    // Optional limit
    const limit = opts?.limit ?? 3;
    return out.slice(0, limit);
  }, [goal, nutrients, eatenMeals, opts?.limit]);
}
