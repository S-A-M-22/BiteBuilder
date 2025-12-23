import type { Meal } from "@/schema/zodSchema";
import MealCard from "./MealCard";

type Props = {
  meals: Meal[];
  currentMeal: Meal | null;
  onSelectMeal: (meal: Meal) => void;
  title?: string;
  emptyHint?: string;
};

export default function ExistingMealsSection({
  meals,
  currentMeal,
  onSelectMeal,
  title = "Existing meals",
  emptyHint = "No meals yet.",
}: Props) {
  const total = meals?.length ?? 0;

  return (
    <section className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[var(--text-soft)]">{title}</h2>
        <div className="text-xs text-[var(--text-soft)]">{total} total</div>
      </div>

      {/* Empty state */}
      {(!meals || meals.length === 0) && (
        <div className="rounded-xl border border-[var(--color-line)] bg-[var(--color-panel)] p-6 text-sm text-[var(--text-soft)] text-center">
          {emptyHint}
        </div>
      )}

      {/* Meal list */}
      {meals && meals.length > 0 && (
        <div
          className="
            flex flex-col gap-3
            overflow-y-auto
            max-h-[60vh] min-h-[200px]
            scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent
            pr-1
          "
        >
          {meals.map((meal) => {
            const selected = currentMeal?.id === meal.id;
            return (
              <div
                key={meal.id}
                className={`
                  transition-transform hover:scale-[1.01]
                  ${selected ? "ring-2 ring-blue-400 rounded-lg" : ""}
                `}
              >
                <MealCard
                  meal={meal}
                  selected={selected}
                  onClick={() => onSelectMeal(meal)}
                />
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
