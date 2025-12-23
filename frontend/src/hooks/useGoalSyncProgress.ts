import { useCallback } from "react";
import { goalService } from "@/services/goal_service";
import { goalNutrientService } from "@/services/goalNutrient_service";
import { aggregateMealTotals } from "@/lib/nutrition";
import type { Goal, GoalNutrient } from "@/schema/zodSchema";
import { eatenMealService } from "@/services/meal_service";

/**
 * Syncs goal progress based on all eaten meals.
 * Should be triggered manually or on interval after meals are eaten.
 */
export function useGoalProgressSync() {
  const syncGoalProgress = useCallback(async (goal: Goal) => {
    try {
      // 1️⃣ Get all eaten meals for the user
      const eatenMeals = await eatenMealService.list();

      // 2️⃣ Aggregate all nutrients across eaten meals
      const totals: Record<string, number> = {};
      for (const eaten of eatenMeals) {
        const mealTotals = aggregateMealTotals(eaten.meal);
        for (const [code, value] of Object.entries(mealTotals)) {
          totals[code] = (totals[code] ?? 0) + (value ?? 0);
        }
      }
      // Update goal’s consumed calories
      const energy = totals.energy_kcal ?? 0;
      console.log("new energy is")
      await goalService.update(goal.id, { consumed_calories: energy });

      console.log("✅ Goal progress synced from eaten meals.");
    } catch (e) {
      // console.error("Failed to sync goal progress:", err);
    }
  }, []);

  return { syncGoalProgress };
}
