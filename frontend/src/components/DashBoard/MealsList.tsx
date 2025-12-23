import { useState } from "react";
import type { Meal } from "@/schema/zodSchema";
import DashboardMealCard from "./DashboardMealCard";
import { useUserSession } from "@/hooks/userSession";


type Props = {
  Meals: Meal[];
  onRefresh?: () => Promise<void>; //
};

export default function EatenMealsList({ Meals, onRefresh  }: Props) {
  const [meals] = useState<Meal[]>(Meals);

  if (!meals.length)
    return (
      <div className="rounded-xl border bg-white p-6 text-sm text-gray-500">
        You dont have any meals currently, try to add some!
      </div>
    );

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Current Meals</h2>
        <div className="text-xs text-gray-500">{meals.length} total</div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {meals.map((m) => (
          <DashboardMealCard
            meal={m}
          />
        ))}
      </div>
    </section>
  );
}