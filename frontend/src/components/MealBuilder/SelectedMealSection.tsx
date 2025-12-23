import type { Meal } from "@/schema/zodSchema";
import MealItemRow from "./MealItemRow";
import MealNutritionSummary from "./MealNutritionalSummary";
import { useEatMeal } from "@/hooks/useEatMeal";
import { motion } from "framer-motion";
import { useUserGoal } from "@/hooks/useUserGoal";

type Props = {
  meal: Meal;
  deletingId: string | null;
  onDeleteMeal: (id: string) => void;
  onRemoveItem?: (itemId: string) => void;
};

export default function SelectedMealSection({
  meal,
  deletingId,
  onDeleteMeal,
  onRemoveItem,
}: Props) {
  const { eatMeal, eating, eaten } = useEatMeal(800);
  const { goal, goalNutrients, loading } = useUserGoal();

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-gray-200 bg-white shadow-sm p-6 space-y-6"
    >
      {/* ─── Header ───────────────────────────────────────────── */}
      <header className="flex flex-wrap justify-between items-start gap-3">
        <div>
          <h2 className="text-xl font-semibold capitalize">{meal.meal_type}</h2>
          <p className="text-sm text-gray-500">
            {new Date(meal.date_time).toLocaleString()}
          </p>
        </div>

        <div className="flex gap-2">
          {/* Eat Button */}
          <button
            onClick={() => eatMeal(meal)}
            disabled={eating || eaten}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              eating
                ? "bg-gray-100 text-gray-400"
                : eaten
                ? "bg-green-100 text-green-700 border border-green-200"
                : "bg-green-600 text-white hover:bg-green-700"
            }`}
          >
            {eating ? "Logging…" : eaten ? "Eaten ✅" : "Eat"}
          </button>

          {/* Delete Button */}
          <button
            type="button"
            onClick={() => onDeleteMeal(meal.id)}
            disabled={deletingId === meal.id}
            className="px-4 py-1.5 rounded-lg text-sm font-medium border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-60"
          >
            {deletingId === meal.id ? "Deleting…" : "Delete"}
          </button>
        </div>
      </header>

      {/* ─── Nutrition Summary ─────────────────────────────────── */}
      <div className="rounded-xl bg-gray-50 border border-gray-200 p-4">
        <MealNutritionSummary meal={meal} goalNutrients={goalNutrients} goal={goal} />
      </div>

      {/* ─── Meal Items List ───────────────────────────────────── */}
      <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-600">Added Products</h3>
          <button
            type="button"
            className="text-sm text-blue-600 hover:text-blue-700 transition"
          >
            + Add item
          </button>
        </div>

        {meal.items && meal.items.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {meal.items.map((it) => (
              <li
                key={it.id ?? it.product?.barcode ?? Math.random()}
                className="py-2"
              >
                {/* ✅ Safe: MealItemRow has no <li> wrapper now */}
                <MealItemRow item={it} onRemove={onRemoveItem} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 italic">
            No products added yet.
          </p>
        )}
      </div>
    </motion.section>
  );
}
