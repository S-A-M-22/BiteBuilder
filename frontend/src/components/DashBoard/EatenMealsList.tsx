import { useState } from "react";
import type { EatenMeal } from "@/schema/zodSchema";
import EatenMealCard from "./EatenMealCard";
import { useGoalProgressSync } from "@/hooks/useGoalSyncProgress";
import { useUserSession } from "@/hooks/userSession";
import { goalService } from "@/services/goal_service";


type Props = {
  eatenMeals: EatenMeal[];
  onRefresh?: () => Promise<void>; //
};

export default function EatenMealsList({ eatenMeals, onRefresh  }: Props) {
  const [meals, setMeals] = useState<EatenMeal[]>(eatenMeals);
  const { syncGoalProgress } = useGoalProgressSync();
  const { user } = useUserSession(); // ensure user is loaded

  const handleDeleted = async (id: string) => {
    try {
      // 1️⃣ Remove meal locally
      setMeals((prev) => prev.filter((m) => m.id !== id));

      // 2️⃣ Refetch and sync goal progress
      if (!user?.id) return;
      const goal = await goalService.getByUser(user.id);
      if (goal) {
        await syncGoalProgress(goal);
      }
      if (onRefresh) await onRefresh();
    } catch (err) {
      console.error("Failed to sync goal progress after deletion:", err);
    }
  };

  if (!meals.length)
    return (
      <div className="rounded-xl border bg-white p-6 text-sm text-gray-500">
        No meals eaten yet today. Append the eaten meal on your meal builder page!
      </div>
    );

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Eaten Meals</h2>
        <div className="text-xs text-gray-500">{meals.length} total</div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {meals.map((em) => (
          <EatenMealCard
            key={em.id}
            eatenMeal={em}
            onDeleted={handleDeleted}
          />
        ))}
      </div>
    </section>
  );
}
