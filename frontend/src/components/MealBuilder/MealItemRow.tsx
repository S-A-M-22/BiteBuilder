import { useState, useMemo } from "react";
import type { MealItem } from "@/schema/zodSchema";
import { mealItemNutrition } from "@/lib/nutrition";
import { useMealItemPrice } from "@/hooks/useMealItemPrice";
import { ChevronDown, ChevronUp } from "lucide-react";

type Props = {
  item: MealItem;
  onRemove?: (itemId: string) => void;
};

const safe = (val: any, unit = "", dp = 0) => {
  const n = Number(val);
  if (!Number.isFinite(n) || n === 0) return "—";
  return `${n.toFixed(dp)}${unit ? " " + unit : ""}`;
};


export default function MealItemRow({ item, onRemove }: Props) {
  const [expanded, setExpanded] = useState(false);
  const grams = item.quantity ?? 0;

  // 🧮 Macros & price
  const n = useMemo(() => mealItemNutrition(item), [item]);
  const { price, unitPricePerGram } = useMealItemPrice(item.product, grams);

  const imageUrl =
    item.product?.image_url && item.product.image_url.startsWith("http")
      ? item.product.image_url
      : "https://placehold.co/40x40?text=🍽️";

      return (
        <div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-panel)] transition hover:border-[var(--color-accent)] hover:bg-[var(--color-hover)]">
          {/* Content section */}
          <div className="flex items-start justify-between px-4 py-3">
            {/* ─── Left side: image + product info ───────────────────────── */}
            <div className="flex items-start gap-3">
              <img
                src={imageUrl}
                alt={item.product?.name ?? "Product image"}
                className="h-11 w-11 rounded-md object-cover border border-[var(--color-line)]"
              />
              <div className="flex flex-col text-sm leading-tight">
                <div className="font-medium text-[var(--text-strong)]">
                  {item.product?.name ?? "Unnamed product"}
                </div>
      
                {/* Macro summary pills */}
                {n && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    <MacroPill label="Energy" value={`${n.energy_kcal} kcal`} />
                    <MacroPill label="Protein" value={`${n.protein} g`} />
                    <MacroPill label="Fat" value={`${n.fat_total.toFixed(1)} g`} />
                    <MacroPill label="Carbs" value={`${n.carbohydrate.toFixed(1)} g`} />
                  </div>
                )}
              </div>
            </div>
      
            {/* ─── Right side: qty + price + actions ───────────────────────── */}
            <div className="flex items-start gap-4">
              {/* Qty + price vertically stacked */}
              <div className="flex flex-col items-end text-xs leading-tight space-y-1">
                <div className="flex items-center gap-1">
                  <span className="text-[var(--text-soft)]">Qty:</span>
                  <span className="min-w-[48px] text-center rounded border border-[var(--color-line)] bg-[var(--color-surface-2)] px-2 py-[2px] font-medium text-[var(--text-strong)]">
                    {grams} g
                  </span>
                </div>
                {price > 0 && (
                  <div className="flex items-center gap-1">
                    <span className="text-[var(--text-soft)]">Price:</span>
                    <span className="min-w-[48px] text-center rounded border border-[var(--color-line)] bg-[var(--color-bg-soft)] px-2 py-[2px] font-medium text-[var(--text-strong)]">
                      ${price.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>
      
              {/* Actions */}
              <div className="flex flex-col items-end gap-1">
                <button
                  onClick={() => setExpanded((v) => !v)}
                  className="rounded-md p-1 text-[var(--text-soft)] hover:text-[var(--text-strong)]"
                  title={expanded ? 'Hide details' : 'Show nutrition'}
                >
                  {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
      
                <button
                  onClick={() => onRemove?.(item.id ?? '')}
                  className="rounded-md border border-[var(--color-line)] px-2 py-[2px] text-xs text-[var(--text-soft)] hover:bg-[var(--color-hover)]"
                >
                  Remove
                </button>
              </div>


 
</div>

        
        
      </div>

      {expanded && n && (
  <div className="border-t border-[var(--color-line)] bg-[var(--color-bg-soft)] px-4 py-3 text-xs text-[var(--text-soft)]">
    <div className="grid grid-cols-2 gap-x-8 gap-y-1 sm:grid-cols-3">
    <Nutrient label="Energy" value={`${safe(n.energy_kj, "kJ")} / ${safe(n.energy_kcal, "kcal")}`} />
<Nutrient label="Protein" value={safe(n.protein, "g", 1)} />
<Nutrient label="Fat (total)" value={safe(n.fat_total, "g", 1)} />
<Nutrient label="Sat. fat" value={safe(n.fat_saturated, "g", 1)} />
<Nutrient label="Carbs" value={safe(n.carbohydrate, "g", 1)} />
<Nutrient label="Sugars" value={safe(n.sugars, "g", 1)} />
<Nutrient label="Fiber" value={safe(n.fiber, "g", 1)} />
<Nutrient label="Sodium" value={safe(n.sodium, "mg", 0)} />

{safe(n.potassium) !== "—" && <Nutrient label="Potassium" value={safe(n.potassium, "mg", 0)} />}
{safe(n.calcium) !== "—" && <Nutrient label="Calcium" value={safe(n.calcium, "mg", 0)} />}
{safe(n.iron) !== "—" && <Nutrient label="Iron" value={safe(n.iron, "mg", 1)} />}
{safe(n.magnesium) !== "—" && <Nutrient label="Magnesium" value={safe(n.magnesium, "mg", 0)} />}
{safe(n.cholesterol) !== "—" && <Nutrient label="Cholesterol" value={safe(n.cholesterol, "mg", 0)} />}
{safe(n.zinc) !== "—" && <Nutrient label="Zinc" value={safe(n.zinc, "mg", 1)} />}
{safe(n.vitamin_c) !== "—" && <Nutrient label="Vitamin C" value={safe(n.vitamin_c, "mg", 0)} />}
{safe(n.vitamin_d) !== "—" && <Nutrient label="Vitamin D" value={safe(n.vitamin_d, "µg", 2)} />}
{safe(n.vitamin_b12) !== "—" && <Nutrient label="Vitamin B12" value={safe(n.vitamin_b12, "µg", 2)} />}

{unitPricePerGram && (
  <Nutrient label="Price (per 100g)" value={`$${(unitPricePerGram * 100).toFixed(2)}`} />
)}

    </div>
  </div>
)}
    </div>
  );
}

function Nutrient({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-dashed border-[var(--color-line-faint)] py-0.5">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="text-[var(--text-strong)]">{value}</span>
    </div>
  );
}

function MacroPill({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-full bg-[var(--color-pill-bg)] px-2 py-[2px] text-xs font-medium text-[var(--text-strong)] shadow-sm border border-[var(--color-line-faint)]">
      {label}: {value}
    </span>
  );
}
