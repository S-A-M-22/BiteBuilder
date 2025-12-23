import { useState, useEffect, useCallback } from "react";
import { useUser } from "@/context/UserSessionProvider";
import { goalService } from "@/services/goal_service";
import { goalNutrientService } from "@/services/goalNutrient_service";
import { nutrientService } from "@/services/nutrient_service";
import { eatenMealService, mealService } from "@/services/meal_service";
import { useGoalProgressSync } from "./useGoalSyncProgress";

import type { Goal, GoalNutrient, Nutrient, EatenMeal, Meal } from "@/schema/zodSchema";

/**
 * useDashboardData
 * Gracefully handles dashboard initialization with silent fallbacks.
 */
export function useDashboardData() {
  const { user } = useUser();
  const { syncGoalProgress } = useGoalProgressSync();

  const [goal, setGoal] = useState<Goal | null>(null);
  const [goalNutrients, setGoalNutrients] = useState<GoalNutrient[]>([]);
  const [catalog, setCatalog] = useState<Nutrient[]>([]);
  const [eatenMeals, setEatenMeals] = useState<EatenMeal[]>([]);
  const [meals, setMeals] = useState<Meal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const safeExec = async <T,>(fn: () => Promise<T>, fallback: T): Promise<T> => {
    try {
      return await fn();
    } catch {
      return fallback;
    }
  };

  const init = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError(null);

    try {
      // 1️⃣ Nutrient catalog
      const catalogData = await safeExec(() => nutrientService.list(), []);
      setCatalog(catalogData);

      // 2️⃣ Get or create goal
      let currentGoal = await safeExec(() => goalService.getByUser(user.id), null);
      if (!currentGoal) {
        currentGoal = await safeExec(
          () =>
            goalService.create({
              user: user.id,
              target_weight_kg: 70,
              target_calories: 2000,
              reset_frequency: "none",
            }),
          null
        );
      }

      if (!currentGoal) throw new Error("Goal unavailable");
      setGoal(currentGoal);

      // 3️⃣ Meals & Eaten meals
      const [eatenData, currentMeals] = await Promise.all([
        safeExec(() => eatenMealService.list(), []),
        safeExec(() => mealService.list(), []),
      ]);
      setEatenMeals(eatenData);
      setMeals(currentMeals);

      // 4️⃣ Sync goal progress silently
      await safeExec(() => syncGoalProgress(currentGoal!), null);

      // 5️⃣ Goal nutrients
      const goalNutrs = await safeExec(() => goalNutrientService.list(currentGoal!.id), []);
      setGoalNutrients(goalNutrs);
    } catch (err) {
      // Only set minimal error state — don’t throw or log
    } finally {
      setLoading(false);
    }
  }, [user?.id, syncGoalProgress]);

  useEffect(() => {
    init();
  }, [init]);

  return {
    user,
    goal,
    goalNutrients,
    catalog,
    eatenMeals,
    meals,
    loading,
    error,
    reload: init,
    setEatenMeals,
    setGoalNutrients,
  };
}
