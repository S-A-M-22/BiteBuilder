import { Goal, GoalNutrient, Nutrient } from "@/schema/zodSchema";
import GoalEditor from "./GoalEditor";
import GoalNutrientTable from "./GoalNutrientTable";
import GoalNutrientAddForm from "./GoalNutrientAddForm";
import { useResetGoal } from "@/hooks/useResetGoal";
import { useGoalProgressSync } from "@/hooks/useGoalSyncProgress";

type Props = {
  goal: Goal;
  setGoal: (g: Goal) => void;
  nutrients: GoalNutrient[];
  setNutrients: React.Dispatch<React.SetStateAction<GoalNutrient[]>>;
  catalog: Nutrient[];
  onReload?: () => Promise<void>; // 👈 optional callback from parent
};

export default function GoalEditorPanel({
  goal,
  setGoal,
  nutrients,
  setNutrients,
  catalog,
  onReload,
}: Props) {
  const { resetGoal, resetting, success, error } = useResetGoal();


  // Local state updates for child components
  const handleUpdate = async () => {
    await onReload?.();
  };

  const handleDelete = (id: string) => {
    setNutrients((prev) => prev.filter((n) => n.id !== id));
  };

  const handleAdd = (newItem: GoalNutrient) => {
    setNutrients((prev) => [...prev, newItem]);
  };

  // ---------------------------------------
  // 🔁 Handle reset goal → trigger reload
  // ---------------------------------------
  const handleResetGoal = async () => {
    await resetGoal();
    // Re-fetch latest data after reset
    await onReload?.();
  };

  return (
    <div className="border rounded-xl p-4 bg-white shadow-sm space-y-6">
      <GoalEditor goal={goal} setGoal={setGoal} />

      {/* ---------------------------------------------------------
          🔹 Reset Goal Button
      --------------------------------------------------------- */}
      <div className="flex items-center justify-between border-t pt-3">
        <button
          onClick={handleResetGoal}
          disabled={resetting}
          className="px-4 py-2 text-sm font-medium rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 transition-all"
        >
          {resetting ? "Resetting..." : "Reset Goal Progress"}
        </button>

        {success && (
          <span className="text-green-600 text-sm animate-fade-in">
            Goal reset successfully!
          </span>
        )}
        {error && <span className="text-red-600 text-sm">{error}</span>}
      </div>

      {/* Nutrient Table + Add Form */}
      <GoalNutrientTable
        nutrients={nutrients}
        catalog={catalog}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        
      />

      <GoalNutrientAddForm
        goalId={goal.id}
        catalog={catalog}
        existingNutrients={nutrients}
        onAdded={handleAdd}
      />
    </div>
  );
}
