import { useState, useCallback } from "react";
import { goalService } from "@/services/goal_service";
import { goalNutrientService } from "@/services/goalNutrient_service";

import { useUser } from "@/context/UserSessionProvider";
import type { GoalNutrient } from "@/schema/zodSchema";
import { eatenMealService } from "@/services/meal_service";

export function useResetGoal() {
  const { user } = useUser();
  const [resetting, setResetting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetGoal = useCallback(async () => {
    if (!user?.id) {
      console.warn("No authenticated user found.");
      setError("No authenticated user found.");
      return;
    }

    try {
      setResetting(true);
      setSuccess(false);
      setError(null);

      // 1️⃣ Fetch goal for this user
      const goal = await goalService.getByUser(user.id);
      if (!goal?.id) {
        setError("No active goal found.");
        return;
      }

      // 2️⃣ Delete all eaten meals (reset consumption history)
      const allEatenMeals = await eatenMealService.list();
      const userMeals = allEatenMeals.filter(
        (m) => m.user === user.id
      );

      await Promise.all(
        userMeals.map((em) => eatenMealService.remove(em.id))
      );
      console.log(`🗑 Deleted ${userMeals.length} eaten meals for user.`);

      // 3️⃣ Reset goal nutrients
      const goalNutrients: GoalNutrient[] = await goalNutrientService.list(goal.id);
      await Promise.all(
        goalNutrients.map((gn) =>
          goalNutrientService.update(gn.id, { consumed_amount: 0 })
        )
      );

      // 4️⃣ Reset total calories
      await goalService.update(goal.id, { consumed_calories: 0 });

      setSuccess(true);
      console.log("✅ Goal reset successfully (EatenMeals wiped).");
    } catch (err) {
      console.error("Error resetting goal:", err);
      setError(err?.message ?? "Failed to reset goal.");
    } finally {
      setResetting(false);
    }
  }, [user]);

  return {
    resetGoal,
    resetting,
    success,
    error,
  };
}
