// ===============================================
// src/components/Product/ProductToolBar.tsx
// ===============================================

import { SortKey } from "@/hooks/useProductSearch";

const GENERAL: { value: SortKey; label: string }[] = [
  { value: "relevance", label: "Relevance" },
  // { value: "saved-first", label: "Saved first" },
  { value: "name", label: "A–Z (Name)" },
];

const PRICE: { value: SortKey; label: string }[] = [
  { value: "price-low-high", label: "Price: Low → High" },
  { value: "price-high-low", label: "Price: High → Low" },
  { value: "unitprice-low-high", label: "Unit Price (Low → High)" },
  { value: "unitprice-high-low", label: "Unit Price (High → Low)" },
];

const NUTRITION: { value: SortKey; label: string }[] = [
  // Yield = geometric mean of normalized efficiency and density
  { value: "yield-high-low", label: "Yield (High → Low)" },
  { value: "yield-low-high", label: "Yield (Low → High)" },

  // Explicit levers used by Yield
  { value: "efficiency-high-low", label: "Protein per $ (High → Low)" },
  { value: "density-high-low", label: "Protein / 100 kcal (High → Low)" },

  // Legacy / additional
  { value: "protein-efficiency", label: "Protein efficiency (g / $)" },
  { value: "kcal-efficiency", label: "Calorie efficiency (kcal / $)" },
  { value: "protein-to-fat", label: "Protein-to-fat ratio" },
  // { value: "health-value", label: "Health value (★ / $)" },
];

export default function ProductToolbar({
  sort,
  onChangeSort,
  count,
}: {
  sort: SortKey;
  onChangeSort: (s: SortKey) => void;
  count: number;
}) {
  return (
    <div className="flex items-center justify-between">
      {/* Item count */}
      <div className="text-sm text-gray-600">{count} items</div>

      {/* Sort dropdown */}
      <div className="flex items-center gap-2">
        <label htmlFor="sort" className="text-sm text-gray-600">
          Sort
        </label>
        <select
          id="sort"
          value={sort}
          onChange={(e) => onChangeSort(e.target.value as SortKey)}
          className="rounded-xl border border-gray-300 bg-white px-2 py-1 text-sm shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        >
          {/* ─── General ─────────────────────────────────────────── */}
          <optgroup label="General">
            {GENERAL.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </optgroup>

          {/* ─── Price-based ─────────────────────────────────────── */}
          <optgroup label="Price">
            {PRICE.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </optgroup>

          {/* ─── Nutrition-based ─────────────────────────────────── */}
          <optgroup label="Nutrition">
            {NUTRITION.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </optgroup>
        </select>
      </div>
    </div>
  );
}
