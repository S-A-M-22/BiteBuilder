import React from "react";
import { useMealProductSearch } from "@/hooks/useMealProductSearch";
import type { Product } from "@/schema/zodSchema";


type Props = {
  currentMealId: string | null;
  onAddProduct: (product: Partial<Product>, qty: number, e?: React.MouseEvent) => void;
  openNutrition: (product: Partial<Product>, qty: number) => void;
  adding: boolean;
};

export default function MealProductSearchSection({
  currentMealId,
  onAddProduct,
  openNutrition,
  adding,
}: Props) {
  const { query, setQuery, results, loading, error, handleSearch, setQty } =
    useMealProductSearch();

  if (!currentMealId)
    return <p className="text-sm text-gray-500 italic">Select a meal above to add products.</p>;

  return (
    <section className="mt-4">
      <h2 className="text-lg font-medium">Search & Add Products</h2>
      <div className="mt-3 flex gap-3">
        <input
          type="search"
          aria-label="Search products"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch(query)}
          placeholder="Search products (press Enter)"
          className="flex-1 rounded border px-3 py-2"
        />
        <button
          onClick={() => handleSearch(query)}
          className="rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700"
        >
          Search
        </button>
      </div>

      {loading && <p className="text-sm text-gray-500 mt-2">Searching…</p>}
      {error && <p className="text-sm text-red-600 mt-2">{error}</p>}

      <div className="mt-4 space-y-2">
        {results.length === 0 ? (
          <div className="text-sm text-gray-500 italic">No search results yet.</div>
        ) : (
          <ul className="divide-y">
            {results.map((p) => {
              const key = String((p as any).id ?? (p as any).barcode ?? JSON.stringify(p));
              const qty = p.__qty ?? 100;
              return (
                <li key={key} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {p.image_url ? (
                      <img
                        src={p.image_url}
                        alt={p.name ?? ""}
                        className="h-12 w-12 rounded object-cover"
                      />
                    ) : (
                      <div className="h-12 w-12 rounded bg-gray-100 flex items-center justify-center text-xs text-gray-400">
                        No image
                      </div>
                    )}
                    <div className="text-left">
                      <div className="font-medium text-sm">{p.name}</div>
                      <div className="text-xs text-gray-500">{p.brand}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => openNutrition(p, qty)}
                      className="rounded border px-2 py-1 text-xs"
                    >
                      Nutrition
                    </button>
                    <button
                      disabled={adding}
                      onClick={(e) => onAddProduct(p, qty, e)}
                      className="ml-2 rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:opacity-60"
                    >
                      Add to favourites
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
