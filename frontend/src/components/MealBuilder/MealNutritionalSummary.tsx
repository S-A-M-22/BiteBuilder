// src/components/MealNutritionSummary.tsx
import { useState } from "react";
import { useMealTotals } from "@/hooks/useMealNutrition";
import type { Meal, GoalNutrient, Goal } from "@/schema/zodSchema";
import { COLORS } from "@/types/colours";
import { DRI } from "@/lib/nutrition";
import MealNutritionSummaryWithGoals from "./MealNutritionSummaryWithGoals";
import MealEfficiencyView from "./MealEfficiencyView";

/**
 * Displays nutrient totals for a meal.
 * Modes:
 * - Absolute (e.g. 45 g)
 * - % DRI
 * - Goals (progress bars)
 * - Efficiency (aggregate yield/cost metrics)
 */
type Props = {
  meal: Meal;
  goalNutrients?: GoalNutrient[];
  goal?: Goal;
};

export default function MealNutritionSummary({ meal, goalNutrients = [], goal }: Props) {
  const { totals } = useMealTotals(meal);
  console.log("showing totals")
  console.log(totals)
  const hasItems = meal.items && meal.items.length > 0;

  const [viewMode, setViewMode] = useState<
    "absolute" | "percent" | "goals" | "efficiency"
  >("absolute");

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setViewMode(e.target.value as any);
  };

  // ────────────────────────────────────────────────────────────────
  // View: Goals
  // ────────────────────────────────────────────────────────────────
  if (viewMode === "goals") {
    return (
      <div>
        <header className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-medium text-[var(--text-soft)] tracking-wide uppercase">
            Nutritional Summary
          </h3>
          <select
            value={viewMode}
            onChange={handleChange}
            className="text-xs border rounded-md px-2 py-1 bg-[var(--color-surface-1)] text-[var(--text-dim)]"
          >
            <option value="absolute">Absolute</option>
            <option value="percent">% DRI</option>
            <option value="goals">Goals</option>
            <option value="efficiency">Efficiency</option>
          </select>
        </header>

        <MealNutritionSummaryWithGoals
          meal={meal}
          goalNutrients={goalNutrients}
          goal={goal}
        />
      </div>
    );
  }

  // ────────────────────────────────────────────────────────────────
  // View: Efficiency
  // ────────────────────────────────────────────────────────────────
  if (viewMode === "efficiency") {
    return (
      <div>
        <header className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-medium text-[var(--text-soft)] tracking-wide uppercase">
            Nutritional Summary
          </h3>
          <select
            value={viewMode}
            onChange={handleChange}
            className="text-xs border rounded-md px-2 py-1 bg-[var(--color-surface-1)] text-[var(--text-dim)]"
          >
            <option value="absolute">Absolute</option>
            <option value="percent">% DRI</option>
            {goalNutrients.length > 0 && <option value="goals">Goals</option>}
            <option value="efficiency">Efficiency</option>
          </select>
        </header>

        <MealEfficiencyView meal={meal} />
      </div>
    );
  }

  // ────────────────────────────────────────────────────────────────
  // View: Absolute or % DRI
  // ────────────────────────────────────────────────────────────────
  const percent = (value: number, key: keyof typeof DRI) => {
    const base = DRI[key];
    if (!base || !value) return "—";
    const pct = (value / base) * 100;
    return `${pct.toFixed(0)}%`;
  };

  const nutrients = [
    { label: "Energy", key: "energy_kcal", unit: "kcal" },
    { label: "Protein", key: "protein", unit: "g" },
    { label: "Carbs", key: "carbohydrate", unit: "g" },
    { label: "Fat", key: "fat_total", unit: "g" },
    { label: "Sat. Fat", key: "fat_saturated", unit: "g" },
    { label: "Sugars", key: "sugars", unit: "g" },
    { label: "Fiber", key: "fiber", unit: "g" },
    { label: "Sodium", key: "sodium", unit: "mg" },
    { label: "Potassium", key: "potassium", unit: "mg" },
    { label: "Calcium", key: "calcium", unit: "mg" },
    { label: "Iron", key: "iron", unit: "mg" },
    { label: "Magnesium", key: "magnesium", unit: "mg" },
    { label: "Cholesterol", key: "cholesterol", unit: "mg" },
    { label: "Zinc", key: "zinc", unit: "mg" },
    { label: "Vitamin C", key: "vitamin_c", unit: "mg" },
    { label: "Vitamin D", key: "vitamin_d", unit: "µg" },
    { label: "Vitamin B12", key: "vitamin_b12", unit: "µg" },
  ] as const;

  const visible = nutrients.filter((n) => {
    const value = (totals as any)[n.key];
    return value != null && value !== 0;
  });

  return (
    <section className="rounded-xl border border-[var(--color-line)] bg-[var(--color-panel)] p-4">
      <header className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--text-soft)] tracking-wide uppercase">
          Nutritional Summary
        </h3>
        {hasItems && (
          <select
            value={viewMode}
            onChange={handleChange}
            className="text-xs border rounded-md px-2 py-1 bg-[var(--color-surface-1)] text-[var(--text-dim)]"
          >
            <option value="absolute">Absolute</option>
            <option value="percent">% DRI</option>
            {goalNutrients.length > 0 && <option value="goals">Goals</option>}
            <option value="efficiency">Efficiency</option>
          </select>
        )}
      </header>

      {hasItems ? (
        visible.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {visible.map((n) => {
              const value = (totals as any)[n.key];
              const display =
                viewMode === "percent"
                  ? percent(value, n.key)
                  : `${value?.toFixed?.(1) ?? 0} ${n.unit}`;

              return (
                <div
                  key={n.key}
                  className="flex flex-col rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] px-3 py-2 text-center shadow-sm transition-all hover:shadow-md"
                >
                  <span className="text-xs text-[var(--text-dim)]">{n.label}</span>
                  <span
                    style={{ color: COLORS[n.label] }}
                    className="text-sm font-semibold"
                  >
                    {display}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-[var(--text-dim)] italic mt-1">
            No nutrients detected for this meal.
          </p>
        )
      ) : (
        <p className="text-sm text-[var(--text-dim)] italic mt-1">
          Add some products to see nutritional totals.
        </p>
      )}
    </section>
  );
}
