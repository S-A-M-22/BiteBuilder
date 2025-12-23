// src/components/Mealbuilder/MealCard.tsx
import type { Meal } from "@/schema/zodSchema";
import { useMealTotals } from "@/hooks/useMealNutrition";
import MacroBar from "@/components/MealBuilder/MealCardComponent/Macrobar";

type Props = {
  meal: Meal;
};

function previewImage(meal: Meal) {
  for (const it of meal.items ?? []) {
    const url = it?.product?.image_url;
    if (url) return url;
  }
  return null;
}

function previewNames(meal: Meal, max = 2) {
  const out: string[] = [];
  for (const it of meal.items ?? []) {
    const name = it?.product?.name ?? undefined;
    if (name) out.push(name);
    if (out.length >= max) break;
  }
  return out;
}

export default function DashboardMealCard({ meal}: Props) {
  const { totals, mini } = useMealTotals(meal);
  const img = previewImage(meal);
  const names = previewNames(meal);
  const itemCount = meal.items?.length ?? 0;
  const name = (meal.name ?? "").trim();

  return (
      <div className="flex items-start gap-3">
        <div className="h-12 w-12 shrink-0 rounded-xl overflow-hidden border border-[var(--color-line)] bg-[var(--color-surface-2)]">
          {img ? (
            <img src={img} alt="" className="h-full w-full object-cover" />
          ) : null}
        </div>

        <div className="min-w-0 flex-1 space-y-2">
          {/* --- Primary label --- */}
          <div className="flex items-center justify-between min-w-0">
            <h3 className="font-semibold text-[var(--text-strong)] truncate">
              {name}
            </h3>
            <span className="text-[10px] rounded-full border px-2 py-0.5 bg-[var(--color-surface-2)] border-[var(--color-line)] text-[var(--text-soft)]">
              {meal.meal_type}
            </span>
          </div>

          {/* --- Sub line: product names --- */}
          <p className="text-sm text-[var(--text-dim)] truncate">
            {names.length ? names.join(" • ") : "No products"}
            {itemCount > names.length ? " • …" : ""}
          </p>

          {/* --- Macros --- */}
          <MacroBar
            kcal={mini.kcal}
            protein={mini.protein}
            carbs={totals.carbohydrate}
            fat={totals.fat_total}
          />
        </div>
      </div>

  );
}