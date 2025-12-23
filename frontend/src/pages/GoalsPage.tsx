import { useEffect, useState, useCallback } from "react";
import { useUser } from "@/context/UserSessionProvider";
import { goalService } from "@/services/goal_service";
import { nutrientService } from "@/services/nutrient_service";
import { goalNutrientService } from "@/services/goalNutrient_service";
import { Goal, GoalNutrient, Nutrient } from "@/schema/zodSchema";
import LoadingState from "@/components/LoadingState";
import GoalDashboardSummary from "@/components/Goal/GoalDashboard/GoalDashboardSummary";
import GoalEditorPanel from "@/components/Goal/GoalEditorPanel";
import { useGoalProgressSync } from "@/hooks/useGoalSyncProgress";


export default function GoalDashboardPage() {
  const { user } = useUser();
  const [goal, setGoal] = useState<Goal | null>(null);
  const [nutrients, setNutrients] = useState<GoalNutrient[]>([]);
  const [catalog, setCatalog] = useState<Nutrient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { syncGoalProgress } = useGoalProgressSync(); 

  // 🔁 Centralized reloadable initializer
  const init = useCallback(async () => {
    if (!user?.id) return;
    setLoading(true);
    setError(null);

    try {
      // Fetch catalog
      const [catalogData] = await Promise.all([nutrientService.list()]);
      setCatalog(catalogData);

      // Ensure goal exists
      let current = await goalService.getByUser(user.id);
      if (!current) {
        current = await goalService.create({
          user: user.id,
          target_weight_kg: 70,
          target_calories: 2000,
          reset_frequency: "none",
        });
      }

      await syncGoalProgress(current);

      // Fetch goal nutrients
      const goalNutrients = await goalNutrientService.list(current.id);

      setGoal(current);
      setNutrients(goalNutrients);
    } catch (err) {
      console.error("Failed to initialize goal dashboard:", err);
      setError(err?.message ?? "Initialization failed");
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  // 🧠 Run on mount / user change
  useEffect(() => {
    init();
  }, [init]);


  // ---------------------------------------------------
  // Rendering
  // ---------------------------------------------------
  if (!user) return <p className="p-6">Please log in.</p>;
  if (loading) return <LoadingState />;
  if (error) return <p className="text-red-600 p-6">{error}</p>;
  if (!goal) return <p className="p-6">No goal found.</p>;

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-semibold">Your Goal Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GoalDashboardSummary
          goal={goal}
          nutrients={nutrients}
        />
        <GoalEditorPanel
          goal={goal}
          setGoal={setGoal}
          nutrients={nutrients}
          setNutrients={setNutrients}
          catalog={catalog}
          onReload={init} // 👈 full reload if needed
        />
      </div>
    </div>
  );
}
