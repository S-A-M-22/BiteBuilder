import { useState, useMemo } from "react";
import { X } from "lucide-react";
import type { Product } from "@/schema/zodSchema";

import Header from "./parts/Header";
import CoreInfo from "./parts/CoreInfo";
import StandardTable from "./parts/StandardTable";
import MatrixView from "./parts/MatrixView";
import { buildMatrix, calcPercentages, normalizeNutrients } from "./nutrition-helpers";

type Props = {
  open: boolean;
  product?: Partial<Product>;
  onClose: () => void;
};

// in ProductDetailsModal.tsx
export type ViewMode = "standard" | "matrix" | "efficiency"; // ✅ add

import { useProductMetrics } from "@/hooks/useProductMetrics";
import EfficiencyView from "./parts/EfficiencyView";


export default function ProductDetailsModal({ open, product, onClose }: Props) {
  const [view, setView] = useState<ViewMode>("standard");

  const nutrients = useMemo(() => normalizeNutrients(product), [product]);
  const withPercentages = useMemo(() => calcPercentages(nutrients), [nutrients]);
  const matrix = useMemo(() => buildMatrix(nutrients), [nutrients]);

  const metrics = useProductMetrics(product); // ✅ compute yield, g/$, etc.

  if (!open || !product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white shadow-xl">
        {/* Header: add the "efficiency" tab (see section 3) */}
        <Header title={product.name ?? "Product"} view={view} onChangeView={setView} onClose={onClose} />

        <div className="p-4 space-y-4">
          <CoreInfo product={product} />

          {view === "standard" && <StandardTable rows={withPercentages} />}
          {view === "matrix" && <MatrixView cards={matrix} />}
          {view === "efficiency" && <EfficiencyView product={product} metrics={metrics} />} {/* ✅ */}

          <div className="mt-4 flex justify-between text-xs text-gray-400">
            <span>
              Source: {product.primary_source ?? "unknown"} | Updated:{" "}
              {product.updated_at ? new Date(product.updated_at).toLocaleString() : "—"}
            </span>
            {product.product_url && (
              <a
                href={product.product_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                View on store
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
