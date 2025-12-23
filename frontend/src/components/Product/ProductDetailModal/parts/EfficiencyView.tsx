import React from "react";
import type { Product } from "@/schema/zodSchema";

type Metrics = {
  pricePerKg: number | null;
  pricePer100g: number | null;
  proteinPerDollar: number | null;          // g/$
  kcalPerDollar: number | null;             // kcal/$
  proteinPerKcal: number | null;            // g/kcal
  proteinToFatRatio: number | null;         // g:g
  healthValue: number | null;               // Health★ per $/kg
  yieldIndex: number | null;                // 0..1
  efficiency_g_per_dollar: number | null;   // g/$
  density_g_per_100kcal: number | null;     // g / 100 kcal
} | null;

export default function EfficiencyView({
  product,
  metrics,
}: {
  product: Partial<Product>;
  metrics: Metrics;
}) {
  if (!metrics) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
        Missing price or nutrient data. Provide cup price and protein/energy to compute efficiency.
      </div>
    );
  }

  const Row = ({
    label,
    value,
    hint,
    strong = false,
  }: {
    label: string;
    value: React.ReactNode;
    hint?: string;
    strong?: boolean;
  }) => (
    <div className="flex items-start justify-between gap-4 border-b last:border-b-0 border-gray-100 py-2">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-right">
        <div className={strong ? "font-semibold text-gray-900" : "text-gray-800"}>{value}</div>
        {hint && <div className="text-[11px] text-gray-500">{hint}</div>}
      </div>
    </div>
  );

  const fmt = (n: number | null | undefined, dp = 2, fallback = "—") =>
    n == null || Number.isNaN(n) ? fallback : n.toFixed(dp);

  // Simple banding for yield 0..1
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
          <div className="text-sm font-medium text-gray-900">Efficiency summary</div>
          <span className={`rounded-full border px-2 py-0.5 text-xs ${yb.tone}`}>
            Yield: {fmt(metrics.yieldIndex, 3)}
            {yb.badge !== "—" ? ` · ${yb.badge}` : ""}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Protein per $</div>
            <div className="text-lg font-semibold">
              {fmt(metrics.efficiency_g_per_dollar ?? metrics.proteinPerDollar, 2)} g/$
            </div>
          </div>
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Protein / 100 kcal</div>
            <div className="text-lg font-semibold">
              {fmt(metrics.density_g_per_100kcal, 2)} g
            </div>
          </div>
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Unit price</div>
            <div className="text-lg font-semibold">${fmt(metrics.pricePerKg, 2)} / kg</div>
          </div>
          <div className="rounded-lg border bg-gray-50 p-3">
            <div className="text-xs text-gray-600">Protein : Fat</div>
            <div className="text-lg font-semibold">{fmt(metrics.proteinToFatRatio, 2)}</div>
          </div>
        </div>
      </div>

      {/* Explainer + raw numbers */}
      <div className="rounded-xl border p-4">
        <div className="mb-2 text-sm font-medium text-gray-900">How Yield works</div>
        <p className="mb-3 text-sm leading-5 text-gray-700">
          <span className="font-medium">Yield</span> is the geometric mean of two normalised levers:
          protein-per-dollar (efficiency) and protein-per-100kcal (density). It ranges 0–1.
          High yield means you’re buying protein that’s both cost-efficient and calorie-lean.
        </p>
        <div className="rounded-lg bg-gray-50 p-3 text-[12px] leading-5 text-gray-700">
          <div><span className="font-semibold">Efficiency</span> = (protein g per 100g) ÷ ($ per 100g) → g/$</div>
          <div><span className="font-semibold">Density</span> = (protein g ÷ kcal) × 100 → g per 100 kcal</div>
          <div>
            <span className="font-semibold">Yield</span> = √( min(1, Efficiency / E<sub>target</sub>) × min(1, Density / 25) )
          </div>
          <div className="mt-1 text-gray-500">
            E<sub>target</sub> is a catalog-tuned reference (e.g., 20 g/$). Ceiling 25 g/100 kcal approximates pure protein.
          </div>
        </div>

        <div className="mt-4 divide-y">
          <Row
            label="Yield Index"
            strong
            value={fmt(metrics.yieldIndex, 3)}
            hint="0–1 scale; higher is better"
          />
          <Row
            label="Protein per $"
            value={`${fmt(metrics.efficiency_g_per_dollar ?? metrics.proteinPerDollar, 2)} g/$`}
            hint="Cost efficiency"
          />
          <Row
            label="Protein / 100 kcal"
            value={`${fmt(metrics.density_g_per_100kcal, 2)} g`}
            hint="Calorie leanness"
          />
          <Row
            label="Protein : Fat"
            value={fmt(metrics.proteinToFatRatio, 2)}
            hint="Higher favors leaner protein"
          />
          <Row
            label="kcal per $"
            value={`${fmt(metrics.kcalPerDollar, 0)} kcal/$`}
          />
          <Row
            label="Health★ value"
            value={fmt(metrics.healthValue, 3)}
            hint="Health star per $/kg"
          />
          <Row
            label="Unit price"
            value={`$${fmt(metrics.pricePerKg, 2)} / kg`}
            hint="$ normalized via cup price"
          />
        </div>
      </div>
    </div>
  );
}
