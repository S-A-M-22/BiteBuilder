import { Goal, GoalNutrient } from "@/schema/zodSchema";
import GoalCalorieRing from "./GoalCalorieRing";
import NutrientProgressList from "./NutrientProgressList";

export default function GoalDashboardSummary({
  goal,
  nutrients,
}: {
  goal: Goal;
  nutrients: GoalNutrient[];
}) {
  // 1️⃣ Try to find the energy-related nutrient (kcal or kJ)
  const energy = nutrients.find((n) => {
    const name = n.nutrient.name.toLowerCase();
    return name.includes("energy") || name.includes("calorie");
  });

  // 2️⃣ Derive calories from synced nutrient data rather than stale goal field
  const consumedCalories =
    energy?.consumed_amount ?? goal.consumed_calories ?? 0;

  const targetCalories =
    energy?.target_amount ?? goal.target_calories ?? 0;

  // 3️⃣ Defensive: avoid division by zero or NaN
  const safeConsumed = Number.isFinite(consumedCalories) ? consumedCalories : 0;
  const safeTarget = Number.isFinite(targetCalories) ? targetCalories : 0;

  return (
    <div className="border rounded-xl p-6 bg-[var(--color-panel)] shadow-sm space-y-6">
      <h2 className="text-lg font-semibold text-[var(--color-ink)]">
        Goal Overview
      </h2>

      {/* 🔹 Use nutrient-based calories as primary progress */}
      <GoalCalorieRing
        consumedCalories={safeConsumed}
        targetCalories={safeTarget}
      />

      <NutrientProgressList nutrients={nutrients} />
    </div>
  );
}
