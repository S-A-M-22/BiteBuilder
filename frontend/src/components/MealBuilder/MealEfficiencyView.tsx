// src/components/MealEfficiencyView.tsx
import React, { useMemo } from "react";
import type { Meal } from "@/schema/zodSchema";
import { computeMealMetrics } from "@/lib/metrics";

export default function MealEfficiencyView({ meal }: { meal: Meal }) {
    const metrics = useMemo(() => computeMealMetrics(meal), [meal]);

  if (!metrics) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
        No efficiency data — add items with price and nutrition info.
      </div>
    );
  }

  const fmt = (n: number | null | undefined, dp = 2, fallback = "—") =>
    n == null || Number.isNaN(n) ? fallback : n.toFixed(dp);

  const yieldBand = (y: number | null) => {
    if (y == null) return { badge: "—", tone: "bg-gray-100 text-gray-700 border-gray-200" };
    if (y >= 0.80) return { badge: "Elite", tone: "bg-emerald-50 text-emerald-700 border-emerald-200" };
    if (y >= 0.60) return { badge: "Strong", tone: "bg-green-50 text-green-700 border-green-200" };
    if (y >= 0.40) return { badge: "Average", tone: "bg-yellow-50 text-yellow-700 border-yellow-200" };
    return { badge: "Weak", tone: "bg-red-50 text-red-700 border-red-200" };
  };

  const yb = yieldBand(metrics.yieldIndex);

  return (
    <div className="space-y-4">
      {/* Summary card */}
      <div className="rounded-xl border p-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="text-sm font-medium text-gray-900">Meal Efficiency Summary</div>
          <span className={`rounded-full border px-2 py-0.5 text-xs ${yb.tone}`}>
            Yield: {fmt(metrics.yieldIndex, 3)} {yb.badge !== "—" ? `· ${yb.badge}` : ""}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Protein per $</div>
            <div className="text-lg font-semibold">{fmt(metrics.proteinPerDollar, 2)} g/$</div>
          </div>
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">kcal per $</div>
            <div className="text-lg font-semibold">{fmt(metrics.kcalPerDollar, 0)} kcal/$</div>
          </div>
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Yield Index</div>
            <div className="text-lg font-semibold">{fmt(metrics.yieldIndex, 3)}</div>
          </div>
        </div>
      </div>

      {/* Explainer */}
      <div className="rounded-xl border p-4 text-sm leading-5 text-gray-700">
        <p className="mb-2 font-medium text-gray-900">What does this mean?</p>
        <p>
          <span className="font-semibold">Yield</span> measures how efficiently your meal converts
          dollars and calories into protein. A high yield means the meal gives strong protein
          returns for both cost and calorie budget.
        </p>
      </div>
    </div>
  );
}
