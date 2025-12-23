// ===============================================
// src/components/Product/EnrichmentReviewModal.tsx
// ===============================================
import { Dialog } from "@headlessui/react";
import type { ProductWithProvenance } from "@/schema/zodSchema";

type Props = {
  open: boolean;
  current?: Partial<ProductWithProvenance> | null;
  enriched?: ProductWithProvenance | null;
  onAccept: () => void;
  onDiscard: () => void;
  onClose: () => void;
};

/** Compare a subset of key nutrients for review */
const compareNutrients = (current?: any, enriched?: any) => {
  if (!current || !enriched) return [];
  const keys = [
    "energy-kcal",
    "protein",
    "carbohydrates",
    "fat",
    "fiber",
    "sodium",
  ];
  return keys.map((key) => ({
    key,
    before: current[key]?.per_100?.value ?? null,
    after: enriched[key]?.per_100?.value ?? null,
    unit: current[key]?.per_100?.unit ?? enriched[key]?.per_100?.unit ?? "g",
  }));
};

export default function EnrichmentReviewModal({
  open,
  current,
  enriched,
  onAccept,
  onDiscard,
  onClose,
}: Props) {
  const match = enriched?.enrichment?.fatsecret?.source_foods?.[0];
  const diffs = compareNutrients(current?.nutrition, enriched?.nutrition);

  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="max-w-lg w-full rounded-xl bg-white p-6 shadow-xl">
          <Dialog.Title className="text-lg font-semibold text-gray-900">
            Review Enrichment
          </Dialog.Title>

          {match ? (
            <div className="mt-3 rounded-md border border-gray-200 bg-gray-50 p-3">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Matched Food:</span>{" "}
                {match.food_name ?? "Unknown"}
              </p>
              {match.food_url && (
                <a
                  href={match.food_url}
                  target="_blank"
                  className="text-xs text-blue-600 underline"
                >
                  View on FatSecret
                </a>
              )}
            </div>
          ) : (
            <p className="mt-3 text-sm text-gray-600 italic">
              No source match information available.
            </p>
          )}

          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={onDiscard}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
            >
              Discard
            </button>
            <button
              onClick={onAccept}
              className="rounded-md bg-green-600 px-3 py-1.5 text-sm text-white hover:bg-green-700"
            >
              Accept Enrichment
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
