import { useState, useMemo } from "react";
import { useMealTotals } from "@/hooks/useMealNutrition";
import type { Meal, GoalNutrient, Goal } from "@/schema/zodSchema";
import { COLORS } from "@/types/colours";
import { DRI } from "@/lib/nutrition";

/**
 * Displays total nutrient values for a meal,
 * filtered to only non-null nutrients,
 * showing % of DRI and contribution to goals.
 */
type Props = {
  meal: Meal;
  goal?: Goal; // 🟩 used to adapt "Energy" → "Calories" if applicable
  goalNutrients?: GoalNutrient[];
};

export default function MealNutritionSummaryWithGoals({
  meal,
  goal,
  goalNutrients = [],
}: Props) {
  const { totals } = useMealTotals(meal);
  const hasItems = meal.items && meal.items.length > 0;
  const [showPercent, setShowPercent] = useState(false);

  const percentDRI = (value: number, key: keyof typeof DRI) => {
    const base = DRI[key];
    if (!base || !value) return "—";
    return `${((value / base) * 100).toFixed(0)}%`;
  };

  // 🧩 Extended list of nutrients — macro + key micros
  const nutrientList = [
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
    { label: "Vitamin C", key: "vitamin_c", unit: "mg" },
    { label: "Vitamin D", key: "vitamin_d", unit: "µg" },
  ] as const;

  // 🧮 Map for quick nutrient lookup
  const validNutrients = useMemo(() => {
    return nutrientList.filter((n) => {
      const val = (totals as any)[n.key];
      return val != null && val !== 0 && !Number.isNaN(val);
    });
  }, [totals]);

  // 🔹 Map "energy_kcal" to calorie goal if present
const findGoal = (code: string) => {
  if (code === "energy_kcal" && goal) {
    const energyGoal = goalNutrients.find((g) => {
      const name = g.nutrient.name.toLowerCase();
      return name.includes("energy") || name.includes("calorie");
    });
    if (energyGoal) return energyGoal;

    // fallback to synthesized pseudo-goal
    return {
      nutrient: { code: "energy_kcal", name: "Calories" },
      target_amount: goal.target_calories ?? 0,
      consumed_amount: goal.consumed_calories ?? 0,
      goal: goal.id,
      id: "synthetic-energy-goal",
    } as GoalNutrient;
  }

  return goalNutrients.find((g) => g.nutrient.code === code);
};

  const getContributionPct = (value: number, goal?: GoalNutrient) => {
    if (!goal || goal.target_amount <= 0) return null;
    return (value / goal.target_amount) * 100;
  };

  // 🧠 Auto-adapt “Energy” label if goal tracks calories
  const adaptLabel = (label: string, key: string) => {
    if (key === "energy_kcal" && goal?.target_calories) return "Calories";
    return label;
  };

  return (
    <section className="rounded-xl border border-[var(--color-line)] bg-[var(--color-panel)] p-4">
      <header className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--text-soft)] tracking-wide uppercase">
          Nutritional Summary
        </h3>

        {hasItems && (
          <div className="flex items-center gap-2">
            <label className="text-xs text-[var(--text-dim)]">Show % DRI</label>
            <input
              type="checkbox"
              checked={showPercent}
              onChange={(e) => setShowPercent(e.target.checked)}
              className="h-3 w-3 accent-blue-600 cursor-pointer"
            />
          </div>
        )}
      </header>

      {hasItems ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {validNutrients.map((n) => {
            const value = (totals as any)[n.key] ?? 0;
            const goalN = findGoal(n.key);
            const contributionPct = getContributionPct(value, goalN);

            const display = showPercent
              ? percentDRI(value, n.key as keyof typeof DRI)
              : `${value.toFixed?.(1)} ${n.unit}`;

            return (
              <div
                key={n.key}
                className="flex flex-col rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-2)] px-3 py-2 text-center shadow-sm transition-all hover:shadow-md"
              >
                <span className="text-xs text-[var(--text-dim)]">
                  {adaptLabel(n.label, n.key)}
                </span>
                <span
                  style={{ color: COLORS[n.label] ?? "var(--color-ink)" }}
                  className="text-sm font-semibold"
                >
                  {display}
                </span>

                {goalN && (
                  <>
                    <span className="text-[11px] text-gray-500 mt-0.5">
                      {contributionPct
                        ? `${contributionPct.toFixed(1)}% of goal`
                        : "—"}
                    </span>
                    <div className="mt-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          contributionPct && contributionPct > 100
                            ? "bg-red-500"
                            : "bg-green-500"
                        }`}
                        style={{
                          width: `${Math.min(contributionPct ?? 0, 100)}%`,
                        }}
                      />
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-[var(--text-dim)] italic mt-1">
          Add some products to see nutritional totals.
        </p>
      )}
    </section>
  );
}
