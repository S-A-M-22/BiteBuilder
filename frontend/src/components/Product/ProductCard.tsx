import { Product } from "@/schema/zodSchema";
import { Heart, Info } from "lucide-react";
import { useProductMetrics } from "@/hooks/useProductMetrics";
import { useEfficiencyContext } from "@/context/EfficiencyContext";

type Props = {
  product: Partial<Product>;
  saved: boolean;
  onToggleSave: (product: Partial<Product>) => void;
  onDetails: (product: Partial<Product>) => void;
};

function Chip({
  children,
  tone = "neutral",
  title,
}: {
  children: React.ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger";
  title?: string;
}) {
  const tones = {
    neutral: "bg-gray-50 text-gray-700 border-gray-200",
    success: "bg-green-50 text-green-700 border-green-100",
    warning: "bg-yellow-50 text-yellow-700 border-yellow-100",
    danger: "bg-red-50 text-red-700 border-red-100",
  } as const;

  return (
    <span
      title={title}
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

function HealthStarPill({ value }: { value: number }) {
  let tone: "success" | "warning" | "danger" = "danger";
  if (value >= 4) tone = "success";
  else if (value >= 2.5) tone = "warning";
  return <Chip tone={tone}>⭐ {value.toFixed(1)}</Chip>;
}

export default function ProductCard({
  product,
  saved,
  onToggleSave,
  onDetails,
}: Props) {
  const {
    name,
    brand,
    price_current,
    price_was,
    is_on_special,
    image_url,
    health_star,
    primary_source,
  } = product;

  const discountPercent =
    price_was && price_current && price_was > price_current
      ? Math.round(((price_was - price_current) / price_was) * 100)
      : null;

  // ✅ unified metrics hook
  const metrics = useProductMetrics(product);
  const { isVisible } = useEfficiencyContext();

  const proteinPerDollar =
    metrics?.proteinPerDollar != null ? `${metrics.proteinPerDollar} g / $` : null;
  const kcalPerDollar =
    metrics?.kcalPerDollar != null ? `${metrics.kcalPerDollar} kcal / $` : null;
  const proteinDensity =
    metrics?.proteinPerKcal != null
      ? `${(metrics.proteinPerKcal * 100).toFixed(1)} g / 100 kcal`
      : null;

  return (
    <div className="relative flex flex-col rounded-2xl border border-gray-200 bg-white p-3 shadow-sm transition-all hover:shadow-md">
      {/* Image */}
      <button
        type="button"
        onClick={() => onDetails(product)}
        className="relative mb-2 aspect-square w-full overflow-hidden rounded-xl bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-400"
        aria-label={`View details for ${name ?? "product"}`}
      >
        {image_url ? (
          <img
            src={image_url}
            alt={name ?? "Product image"}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-gray-400">
            No image
          </div>
        )}
        {is_on_special && (
          <span className="absolute left-2 top-2 flex items-center gap-1 rounded-md bg-red-500/95 px-2 py-0.5 text-xs font-semibold text-white shadow-sm">
            <span>On&nbsp;Special</span>
            {discountPercent !== null && (
              <span className="rounded bg-white/20 px-1.5 py-0.5 text-[10px] font-bold">
                -{discountPercent}%
              </span>
            )}
          </span>
        )}
      </button>

      {/* Title / Brand */}
      <button type="button" onClick={() => onDetails(product)} className="text-left">
        <p className="font-medium text-gray-900 line-clamp-1">
          {name ?? "Unnamed product"}
        </p>
        <p className="text-sm text-gray-500 line-clamp-1">{brand ?? "—"}</p>
      </button>

      {/* Price + Save */}
      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-baseline gap-2">
          {price_current != null && (
            <span className="font-semibold text-gray-900">
              ${price_current.toFixed(2)}
            </span>
          )}
          {metrics?.pricePerKg && (
            <Chip title="Normalized to per-kg">
              ${metrics.pricePerKg.toFixed(2)}/kg
            </Chip>
          )}
        </div>

        <div className="flex items-center gap-1">
          <button
            title="View details"
            onClick={() => onDetails(product)}
            className="rounded-md p-1 text-gray-500 hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <Info className="h-4 w-4" />
          </button>

          <button
            title={saved ? "Unsave" : "Save"}
            onClick={() => onToggleSave(product)}
            className={`rounded-md p-1 focus:outline-none focus:ring-2 focus:ring-blue-400 ${
              saved
                ? "bg-blue-100 text-blue-600 hover:bg-blue-200"
                : "text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            }`}
          >
            <Heart
              className={`h-4 w-4 ${saved ? "fill-blue-500 text-blue-500" : ""}`}
            />
          </button>
        </div>
      </div>

      {/* Comparative Metrics */}
<div className="mt-2 flex flex-wrap gap-1">

  {/* 🔹 Protein metrics */}
  {isVisible("proteinDensity") && metrics?.proteinPerKcal && (
    <Chip tone="neutral" title="Protein per 100 kcal">
      {(metrics.proteinPerKcal * 100).toFixed(1)} g / 100 kcal
    </Chip>
  )}


  {/* 🔹 Efficiency metrics */}
  {isVisible("proteinPerDollar") && metrics?.proteinPerDollar && (
    <Chip tone="success" title="Protein per dollar">
      {metrics.proteinPerDollar} g / $
    </Chip>
  )}

  {isVisible("kcalPerDollar") && metrics?.kcalPerDollar && (
    <Chip tone="warning" title="Calories per dollar">
      {metrics.kcalPerDollar} kcal / $
    </Chip>
  )}

  {isVisible("yieldIndex") && metrics?.yieldIndex && (
    <Chip tone="warning" title="Protein Yield Index">
      Yield {(metrics.yieldIndex * 100).toFixed(0)}%
    </Chip>
  )}

  {/* 🔹 Health-based value */}
  {isVisible("healthValue") && metrics?.healthValue && (
    <Chip tone="success" title="Health-star cost efficiency">
      {(metrics.healthValue).toFixed(2)}⭐ / $
    </Chip>
  )}

  {isVisible("healthStar") &&
    product.health_star &&
    !Number.isNaN(Number(product.health_star)) && (
      <HealthStarPill value={Number(product.health_star)} />
    )}
</div>


      {/* Source */}
      <div className="mt-2 text-right text-[10px] text-gray-400">
        {primary_source ?? "unknown"}
      </div>
    </div>
  );
}
