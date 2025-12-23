import type { EatenMeal } from "@/schema/zodSchema";
import { useMealTotals } from "@/hooks/useMealNutrition";
import { format } from "date-fns";
import MacroBar from "../MealBuilder/MealCardComponent/Macrobar";
import { X } from "lucide-react";

import { useState } from "react";
import { eatenMealService } from "@/services/meal_service";

// ----------------------------------------------------------
// Utility helpers reused from MealCard
// ----------------------------------------------------------
function previewImage(eatenMeal: EatenMeal) {
  for (const it of eatenMeal.meal.items ?? []) {
    const url = it?.product?.image_url;
    if (url) return url;
  }
  return null;
}

function previewNames(eatenMeal: EatenMeal, max = 2) {
  const out: string[] = [];
  for (const it of eatenMeal.meal.items ?? []) {
    const name = it?.product?.name ?? undefined;
    if (name) out.push(name);
    if (out.length >= max) break;
  }
  return out;
}

// ----------------------------------------------------------
// Component
// ----------------------------------------------------------
export default function EatenMealCard({
  eatenMeal,
  onDeleted,
}: {
  eatenMeal: EatenMeal;
  onDeleted?: (id: string) => void;
}) {
  const { meal } = eatenMeal;
  const { totals, mini } = useMealTotals(meal);
  const img = previewImage(eatenMeal);
  const names = previewNames(eatenMeal);
  const itemCount = meal.items?.length ?? 0;
  const name = (meal.name ?? "").trim();

  const [deleting, setDeleting] = useState(false);

  async function handleDelete() {
    const confirmDelete = confirm("Delete this eaten meal?");
    if (!confirmDelete) return;

    try {
      setDeleting(true);
      await eatenMealService.remove(eatenMeal.id);
      onDeleted?.(eatenMeal.id);
    } catch (err) {
      console.error("Failed to delete meal:", err);
      alert("Failed to delete this meal.");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div
      className={[
        "relative w-full rounded-2xl border bg-[var(--color-panel)]",
        "border-[var(--color-line)] shadow-[0_1px_2px_rgba(0,0,0,0.05)]",
        "p-4 transition-colors hover:bg-[var(--color-hover)] group",
      ].join(" ")}
    >
      {/* --- Delete Button --- */}
      <button
        onClick={handleDelete}
        disabled={deleting}
        className={[
          "absolute -top-0 -right-0 rounded-full p-1 transition-all duration-200",
          "opacity-0 translate-y-[-2px] group-hover:opacity-100 group-hover:translate-y-0",
          "hover:bg-[var(--color-surface-2)] text-[var(--text-soft)] hover:text-red-500",
        ].join(" ")}
        title="Delete meal"
      >
        <X size={13} strokeWidth={2} />
      </button>
  
      <div className="flex items-start gap-3">
        {/* Thumbnail */}
        <div className="h-12 w-12 shrink-0 rounded-xl overflow-hidden border border-[var(--color-line)] bg-[var(--color-surface-2)]">
          {img ? (
            <img src={img} alt="" className="h-full w-full object-cover" />
          ) : null}
        </div>
  
        {/* Content */}
        <div className="min-w-0 flex-1 space-y-2">
          {/* Header */}
          <div className="flex items-center justify-between min-w-0 pr-4">
            <h3 className="font-semibold text-[var(--text-strong)] truncate">
              {name || "Unnamed Meal"}
            </h3>
            <span className="text-[10px] rounded-full border px-2 py-0.5 bg-[var(--color-surface-2)] border-[var(--color-line)] text-[var(--text-soft)]">
              {meal.meal_type}
            </span>
          </div>
  
          {/* Sub line */}
          <p className="text-sm text-[var(--text-dim)] truncate">
            {names.length ? names.join(" • ") : "No products"}
            {itemCount > names.length ? " • …" : ""}
          </p>
  
          {/* Macros */}
          <MacroBar
            kcal={mini.kcal}
            protein={mini.protein}
            carbs={totals.carbohydrate}
            fat={totals.fat_total}
          />
  
          {/* Timestamp */}
          <div className="flex justify-end">
            <span className="text-[11px] font-medium text-[var(--text-soft)] bg-[var(--color-surface-2)] border border-[var(--color-line)] px-2 py-0.5 rounded-lg">
              🍽️ Eaten at{" "}
              <span className="font-semibold text-[var(--text-strong)]">
                {format(new Date(eatenMeal.eaten_at), "EEE, dd MMM yyyy • HH:mm")}
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
