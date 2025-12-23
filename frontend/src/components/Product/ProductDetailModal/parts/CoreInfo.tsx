import type { Product } from "@/schema/zodSchema";

type Props = { product: Partial<Product> };

export default function CoreInfo({ product }: Props) {
  return (
    <div className="flex flex-col sm:flex-row gap-4">
      <div className="flex-shrink-0">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} className="h-40 w-40 rounded-xl object-cover" />
        ) : (
          <div className="flex h-40 w-40 items-center justify-center rounded-xl bg-gray-100 text-gray-400">
            No image
          </div>
        )}
      </div>

      <div className="flex flex-col justify-between">
        <div>
          <p className="text-sm text-gray-600">{product.brand}</p>
          {product.description && <p className="text-sm text-gray-700 mt-2">{product.description}</p>}
        </div>

        <div className="mt-3 space-y-1">
          {product.price_current != null && (
            <div className="text-lg font-semibold text-gray-900">
              ${product.price_current.toFixed(2)}
              {product.is_on_special && (
                <span className="ml-2 rounded-md bg-red-100 px-2 py-0.5 text-xs text-red-700">On Special</span>
              )}
            </div>
          )}
          {product.price_was && product.price_was > (product.price_current ?? 0) && (
            <div className="text-sm text-gray-500 line-through">Was ${product.price_was.toFixed(2)}</div>
          )}
          {product.cup_price_value && product.cup_price_unit && (
            <div className="text-sm text-gray-700">
              ${product.cup_price_value}/{product.cup_price_unit}
            </div>
          )}
          {product.health_star && <div className="text-sm text-green-700">Health Star: {product.health_star}</div>}
          {product.allergens && (
            <div className="text-sm text-gray-700">
              <strong>Allergens:</strong> {product.allergens}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
