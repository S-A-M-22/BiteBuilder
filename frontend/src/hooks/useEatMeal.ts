import { useState, useCallback, useEffect } from "react";
import type { Meal } from "@/schema/zodSchema";
import { useUser } from "@/context/UserSessionProvider";
import { eatenMealService } from "@/services/meal_service";
import { goalService } from "@/services/goal_service";
import { useGoalProgressSync } from "./useGoalSyncProgress";

export function useEatMeal(autoResetMs = 2500) {
  const { user } = useUser();
  const [eating, setEating] = useState(false);
  const [eaten, setEaten] = useState(false);
  const { syncGoalProgress } = useGoalProgressSync();

  const eatMeal = useCallback(
    async (meal: Meal) => {
      if (!user) {
        console.warn("No authenticated user found.");
        return;
      }

      try {
        setEating(true);

        // ✅ 1. Record as eaten
        await eatenMealService.create({
          user: user.id,
          meal: meal.id,
        });

        // ✅ 2. Mark as eaten
        setEaten(true);

        // ✅ 3. Sync goal progress
        const goal = await goalService.getByUser(user.id);
        if (goal) {
          await syncGoalProgress(goal);
        }
      } catch (err) {
        console.error("Error recording eaten meal:", err);
      } finally {
        setEating(false);
      }
    },
    [user, syncGoalProgress]
  );

  // 🕒 optional auto-reset after X ms
  useEffect(() => {
    if (eaten && autoResetMs) {
      const timer = setTimeout(() => setEaten(false), autoResetMs);
      return () => clearTimeout(timer);
    }
  }, [eaten, autoResetMs]);

  const resetEaten = useCallback(() => setEaten(false), []);

  return { eatMeal, eating, eaten, resetEaten };
}
