import { useEffect, useState, useMemo } from "react";
import type { Product, MealItem } from "@/schema/zodSchema";
import { productService } from "@/services/product_service";
import { mealItemService } from "@/services/meal_service";
import { parseSizeToGrams, num, per100g } from "@/lib/nutrition";

type Props = {
  mealId: string;
  existingItems?: MealItem[];
  onItemAdded?: (item: MealItem) => void;
};

export default function ProductPicker({
  mealId,
  existingItems = [],
  onItemAdded,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState<Record<string, boolean>>({});
  const [qtyByBarcode, setQtyByBarcode] = useState<Record<string, number>>({});
  const [query, setQuery] = useState("");

  const existingBarcodes = new Set(
    existingItems.map((it) => it.product?.barcode ?? it.product)
  );

  // ✅ Filter products dynamically by name or brand
  const visibleProducts = useMemo(() => {
    const filtered = products.filter(
      (p) =>
        p.barcode &&
        !existingBarcodes.has(p.barcode) &&
        (!query ||
          p.name?.toLowerCase().includes(query.toLowerCase()) ||
          p.brand?.toLowerCase().includes(query.toLowerCase()))
    );
    return filtered;
  }, [products, existingBarcodes, query]);

  // ✅ Load saved products on mount
  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await productService.list();
        if (!alive) return;
        setProducts(list as any);
      } catch (e) {
        if (alive) setError("Failed to load products");
        console.error(e);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  const setQty = (barcode: string, v: number) =>
    setQtyByBarcode((s) => ({ ...s, [barcode]: v }));

  const handleAdd = async (p: Product) => {
    if (!p?.barcode) return;
    const barcode = p.barcode;
    const qty = Math.max(1, Math.round(qtyByBarcode[barcode] ?? 100));
    setAdding((s) => ({ ...s, [barcode]: true }));
    try {
      const item = await mealItemService.create({
        meal: mealId,
        product: barcode,
        quantity: qty,
      });
      onItemAdded?.(item);
    } catch (e) {
      console.error("Failed to add product to meal", e);
    } finally {
      setAdding((s) => ({ ...s, [barcode]: false }));
    }
  };

  const pricePerGram = (product: Product): number | null => {
    let unitPricePerGram: number | null = null;

    if (product.cup_price_value && product.cup_price_unit) {
      const unit = product.cup_price_unit.toLowerCase().trim();
      if (unit.includes("1kg")) unitPricePerGram = product.cup_price_value / 1000;
      else if (unit.includes("100g")) unitPricePerGram = product.cup_price_value / 100;
      else if (unit.includes("1g")) unitPricePerGram = product.cup_price_value;
      else if (unit.includes("1l")) unitPricePerGram = product.cup_price_value / 1000;
      else if (unit.includes("100ml")) unitPricePerGram = product.cup_price_value / 100;
      else if (unit.includes("1ml")) unitPricePerGram = product.cup_price_value;
    }

    if (!unitPricePerGram) {
      const totalPrice = num(product.price_current);
      const sizeGrams = parseSizeToGrams(product.size) ?? 0;
      if (totalPrice > 0 && sizeGrams > 0)
        unitPricePerGram = totalPrice / sizeGrams;
    }

    return unitPricePerGram;
  };

  return (
    <section className="space-y-3">
      <header className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Add products</h2>
      </header>

      {/* 🔍 Search Bar */}
      <div className="relative mb-2">
        <input
          type="text"
          placeholder="Search products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-1)] px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="rounded-xl border border-[var(--color-line)] bg-[var(--color-panel)]">
        {loading ? (
          <div className="p-4 space-y-2">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 p-2">
                <div className="h-12 w-12 rounded bg-[var(--color-surface-2)] animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-2/3 rounded bg-[var(--color-surface-2)] animate-pulse" />
                  <div className="h-3 w-1/3 rounded bg-[var(--color-surface-2)] animate-pulse" />
                </div>
                <div className="h-9 w-24 rounded bg-[var(--color-surface-2)] animate-pulse" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="p-4 text-sm text-red-400">{error}</div>
        ) : visibleProducts.length === 0 ? (
          <div className="p-4 text-sm text-[var(--text-soft)]">
            {products.length === 0
              ? "No saved products yet."
              : query
              ? `No matches for "${query}".`
              : "All your products are already added to this meal."}
          </div>
        ) : (
          <ul className="divide-y divide-[var(--color-line)]">
            {visibleProducts.map((p) => {
              const barcode = p.barcode!;
              const qty = qtyByBarcode[barcode] ?? 100;
              const unitPrice = pricePerGram(p);
              const estPrice = unitPrice ? unitPrice * qty : null;
              const protein100 = per100g(p, "protein");
              const kcal100 = per100g(p, "energy_kcal");

              return (
                <li
                  key={barcode}
                  className="grid grid-cols-[auto_1fr_auto] items-center gap-3 p-3"
                >
                  <img
                    src={p.image_url ?? ""}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.visibility = "hidden";
                    }}
                    alt={p.name ?? "product"}
                    className="h-12 w-12 rounded object-cover border border-[var(--color-line)] bg-[var(--color-surface-1)]"
                  />

                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-[var(--text-strong)]">
                      {p.name ?? "Unnamed product"}
                    </div>
                    <div className="text-xs text-[var(--text-soft)]">
                      {p.brand ?? p.barcode ?? "—"}
                    </div>

                    <div className="mt-1 flex flex-wrap gap-2 text-[10px] text-[var(--text-soft)]">
                      {kcal100 > 0 && <span>{Math.round(kcal100)} kcal / 100g</span>}
                      {protein100 > 0 && (
                        <span className="font-medium text-[var(--text-strong)]">
                          {protein100.toFixed(1)} g protein / 100g
                        </span>
                      )}
                      {unitPrice && <span>${(unitPrice * 100).toFixed(2)} / 100g</span>}
                      {estPrice && (
                        <span className="font-medium text-[var(--text-strong)]">
                          ≈ ${estPrice.toFixed(2)} for {qty} g
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={qty}
                      onChange={(e) => setQty(barcode, Number(e.target.value))}
                      className="w-20 rounded-lg border border-[var(--color-line)] bg-[var(--color-surface-1)] px-2 py-2 text-sm tabular-nums"
                      aria-label="Quantity in grams"
                      max={1000000000000}
                    />
                    <span className="text-xs text-[var(--text-soft)]">g</span>
                    <button
                      type="button"
                      disabled={adding[barcode]}
                      onClick={() => handleAdd(p)}
                      className="rounded-lg border border-[var(--color-line)] px-3 py-2 text-sm hover:bg-[var(--color-hover)] disabled:opacity-60"
                    >
                      {adding[barcode] ? "Adding…" : "Add"}
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="px-1 pb-1 text-xs text-[var(--text-soft)]">
        Showing saved products
      </div>
    </section>
  );
}
