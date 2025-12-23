import type { Meal } from "@/schema/zodSchema";
import { useMealTotals } from "@/hooks/useMealNutrition";
import { computeMealMetrics } from "@/lib/metrics";
import { useMemo } from "react";

type Props = { meal: Meal; selected?: boolean; onClick?: () => void };

function previewImage(meal: Meal) {
  for (const it of meal.items ?? []) {
    const url = it?.product?.image_url;
    if (url) return url;
  }
  return null;
}

function previewNames(meal: Meal, max = 2) {
  const names: string[] = [];
  for (const it of meal.items ?? []) {
    if (it?.product?.name) names.push(it.product.name);
    if (names.length >= max) break;
  }
  return names;
}

function Nutrient({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-xs">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="font-medium text-[var(--text-strong)]">{value}</span>
    </div>
  );
}

export default function MealCard({ meal, selected = false, onClick }: Props) {
  const { totals } = useMealTotals(meal);
  const metrics = useMemo(() => computeMealMetrics(meal), [meal]);

  const img = previewImage(meal);
  const names = previewNames(meal);
  const name = (meal.name ?? "").trim();
  const price_total = totals.price_total;

  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={selected}
      className={[
        "block w-full text-left rounded-xl border transition-all outline-none",
        "bg-[var(--color-panel)] border-[var(--color-line)] hover:bg-[var(--color-hover)]",
        "focus-visible:ring-2 focus-visible:ring-emerald-400",
        selected
          ? "ring-2 ring-emerald-400 shadow-[0_0_0_4px_rgba(16,185,129,0.12)]"
          : "hover:shadow-[0_6px_16px_-8px_rgba(0,0,0,0.25)]",
        "px-4 py-3",
      ].join(" ")}
    >
      <div className="flex items-start gap-3">
        {/* Thumbnail */}
        <div className="h-12 w-12 shrink-0 rounded-lg overflow-hidden border border-[var(--color-line)] bg-[var(--color-surface-2)]">
          {img && <img src={img} alt="" className="h-full w-full object-cover" />}
        </div>

        {/* Text */}
        <div className="flex-1 min-w-[160px] space-y-2">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-[var(--text-strong)] truncate text-sm">
              {name || "Untitled Meal"}
            </h3>
            <span className="text-[10px] text-[var(--text-soft)] px-1.5 border border-[var(--color-line)] rounded">
              {meal.meal_type}
            </span>
          </div>

          {/* Items */}
          <p className="text-xs text-[var(--text-dim)] truncate">
            {names.length ? names.join(" • ") : "No products"}
          </p>

          {/* Key nutrients — ultra-light */}
          <div className="rounded-md bg-[var(--color-bg-soft)] border border-[var(--color-line)]/40 p-2 space-y-0.5">
            <Nutrient label="Energy" value={`${totals.energy_kcal?.toFixed(0) ?? "—"} kcal`} />
            <Nutrient label="Protein" value={`${totals.protein?.toFixed(1) ?? "—"} g`} />
            <Nutrient label="Fat" value={`${totals.fat_total?.toFixed(1) ?? "—"} g`} />
            <Nutrient label="Carbs" value={`${totals.carbohydrate?.toFixed(1) ?? "—"} g`} />
            {totals.sodium && totals.sodium > 0 && (
              <Nutrient label="Sodium" value={`${totals.sodium.toFixed(0)} mg`} />
            )}
          </div>

          {/* Efficiency */}
          {metrics && (
            <div className="text-[10px] text-[var(--text-soft)] flex flex-wrap gap-x-3 pt-1">
              {metrics.proteinPerDollar && (
                <span>{metrics.proteinPerDollar.toFixed(2)} g protein / $</span>
              )}
              {metrics.kcalPerDollar && (
                <span>{metrics.kcalPerDollar.toFixed(0)} kcal / $</span>
              )}
              {metrics.yieldIndex && (
                <span>Yield {metrics.yieldIndex.toFixed(1)}</span>
              )}
            </div>
          )}

          {price_total > 0 && (
            <div className="text-right text-xs font-medium text-[var(--text-strong)]">
              ${price_total.toFixed(2)}
            </div>
          )}
        </div>
      </div>
    </button>
  );
}
