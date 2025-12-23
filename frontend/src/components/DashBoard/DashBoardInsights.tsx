// src/components/DashBoard/InsightsSection.tsx

import { useDashboardInsights } from "@/hooks/useDashboardInsights";
import type { Goal, GoalNutrient, EatenMeal, Meal } from "@/schema/zodSchema";
import InsightsCarousel from "./InsightsCarousal";

export default function InsightsSection({
  goal,
  nutrients,
  eatenMeals,
  meals,
}: {
  goal: Goal | null;
  nutrients: GoalNutrient[];
  eatenMeals: EatenMeal[];
  meals: Meal[];
}) {
  
  const insights = useDashboardInsights(goal, nutrients, eatenMeals, meals, { limit: 3 });
  console.log("[InsightsSection] insights:", insights); //
  return <InsightsCarousel insights={insights} interval={7000} />;
}
