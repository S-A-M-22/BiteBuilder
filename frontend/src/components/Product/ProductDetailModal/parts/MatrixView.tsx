// src/components/Nutrition/MatrixView.tsx
import { toneForCategory } from "@/lib/nutrition";
import { UIMetric } from "../nutrition-helpers";
import ThresholdLine from "@/components/Nutrition/ThresholdLine";


type OldCard = {
  key: string;
  label: string;
  value: number | null;
  cat: "good" | "ok" | "high" | "unknown";
  help: string;
};
type Props = { cards: readonly OldCard[] | readonly UIMetric[] };
const fmt = (v: number | null, dp = 2) => (v == null ? "—" : Number.isInteger(v) ? v : Number(v.toFixed(dp)));
const isUIMetric = (x: any): x is UIMetric => x && "verdict" in x && "basis" in x;

const verdictLabel = (cat: OldCard["cat"]) =>
  cat === "good" ? "Favorable" :
  cat === "ok"   ? "Acceptable" :
  cat === "high" ? "Limit / Caution" :
                   "Not enough data";

// Plain-English reason only; no numeric targets here
function simpleReason(key: string, cat: OldCard["cat"]) {
  if (cat !== "high") return "";
  switch (key) {
    case "fat_to_protein":     return "Too much fat for the amount of protein.";
    case "sugar_to_fiber":     return "Too much sugar for the amount of fiber.";
    case "satfat_to_fat":      return "Too much saturated fat within total fat.";
    case "sodium_mg_per_100g": return "High sodium per 100g.";
    default: return "Above the preferred threshold.";
  }
}

// Single primary threshold per metric for the ruler
function thresholdFor(key: string) {
  switch (key) {
    case "fat_to_protein":     return { threshold: 0.5, direction: "lower" as const };
    case "sugar_to_fiber":     return { threshold: 2.0, direction: "lower" as const };
    case "satfat_to_fat":      return { threshold: 0.33, direction: "lower" as const };
    case "sodium_mg_per_100g": return { threshold: 120, direction: "lower" as const };
    default:                   return { threshold: 1, direction: "lower" as const };
  }
}

export default function MatrixView({ cards }: Props) {
  const items = cards as any[];

  return (
    <div>
      <h3 className="mt-4 mb-2 text-base font-semibold">Nutrient Matrix</h3>

      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((m) => {
          const cat = isUIMetric(m) ? m.category : m.cat;
          const tone = toneForCategory(cat);
          const value = isUIMetric(m) ? m.value : m.value;
          const valueText = isUIMetric(m) ? m.display : fmt(m.value);
          const basisText =
            isUIMetric(m) && m.basis !== "ratio"
              ? `${m.unit ? `${m.unit} ` : ""}/ ${m.basis}`
              : "";

          const { threshold, direction } = thresholdFor(m.key);

          return (
            <div key={m.key} className={`rounded-xl border px-4 py-3 ${tone}`}>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="text-sm font-medium">{m.label}</div>
                  <div className="mt-0.5 text-xs text-gray-600">{isUIMetric(m) ? m.help : m.help}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold tabular-nums">
                    {valueText}
                    {basisText ? <span className="ml-1 text-xs text-gray-500">{basisText}</span> : null}
                  </div>
                  <div className="mt-0.5 text-[11px] uppercase tracking-wide">
                    <strong>{verdictLabel(cat)}</strong>
                  </div>
                </div>
              </div>

              {/* Minimal ruler: under/over the single target */}
              <div className="mt-2">
  <div className="mb-1 text-[10px] text-gray-500 text-right">
    Threshold: {threshold}
  </div>
  <ThresholdLine
    value={value}
    threshold={threshold}
    direction={direction}
    format={(n) => n.toFixed(2)}
  />
</div>

              {/* When high, show a short plain-English reason only */}
              {cat === "high" && (
                <div className="mt-2 text-xs text-red-700">{simpleReason(m.key, cat)}</div>
              )}

              {/* Optional: missing inputs hint (only if you pass UIMetric) */}
              {isUIMetric(m) && m.missing?.length ? (
                <div className="mt-2 text-[11px] text-amber-700">Missing: {m.missing.join(", ")}</div>
              ) : null}
            </div>
          );
        })}
      </div>

      <div className="mt-3 text-xs text-gray-500">
        Ratios use <em>per serving</em> if available, otherwise <em>per 100g</em>. Sodium uses <em>per 100g</em>.
      </div>
    </div>
  );
}
