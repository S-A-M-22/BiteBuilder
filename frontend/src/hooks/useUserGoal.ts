// src/hooks/useUserGoal.ts
import { useEffect, useState, useCallback } from "react";
import { useUser } from "@/context/UserSessionProvider";
import { goalService } from "@/services/goal_service";
import { goalNutrientService } from "@/services/goalNutrient_service";
import type { Goal, GoalNutrient } from "@/schema/zodSchema";

/**
 * Fetches the current user's Goal and GoalNutrients.
 * Automatically creates a goal if none exists.
 */
export function useUserGoal() {
  const { user } = useUser();
  const [goal, setGoal] = useState<Goal | null>(null);
  const [nutrients, setNutrients] = useState<GoalNutrient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGoal = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError(null);
    try {
      // ensure a goal exists
      let g = await goalService.getByUser(user.id);
      if (!g) {
        g = await goalService.create({
          user: user.id,
          target_weight_kg: 70,
          target_calories: 2000,
          reset_frequency: "none",
        });
      }
      const goalNutrients = await goalNutrientService.list(g.id);
      setGoal(g);
      setNutrients(goalNutrients);
    } catch (err: any) {
      console.error("useUserGoal error:", err);
      setError(err.message ?? "Failed to load goal");
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchGoal();
  }, [fetchGoal]);

  return { goal, goalNutrients: nutrients, loading, error, reload: fetchGoal };
}
