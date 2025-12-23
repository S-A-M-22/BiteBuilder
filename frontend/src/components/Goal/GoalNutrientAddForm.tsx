import { useState, useMemo } from "react";
import { Nutrient, GoalNutrient } from "@/schema/zodSchema";
import { goalNutrientService } from "@/services/goalNutrient_service";

type Props = {
  goalId: string;
  catalog: Nutrient[];
  existingNutrients: GoalNutrient[];
  onAdded: (newItem: GoalNutrient) => void;
};

export default function GoalNutrientAddForm({
  goalId,
  catalog,
  existingNutrients,
  onAdded,
}: Props) {
  const [nutrientId, setNutrientId] = useState("");
  const [target, setTarget] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ✅ Filter out nutrients already linked to this goal
  const availableNutrients = useMemo(() => {
    const usedIds = new Set(existingNutrients.map((gn) => gn.nutrient.id));
    return catalog.filter((n) => !usedIds.has(n.id));
  }, [catalog, existingNutrients]);

  const selected = availableNutrients.find((n) => n.id === nutrientId);

  const handleAdd = async () => {
    if (!nutrientId || !target) return;
    setLoading(true);
    setError(null);

    try {
      const payload = {
        goal: goalId,
        nutrient: nutrientId,
        target_amount: parseFloat(target),
        consumed_amount: 0, // ✅ new field — start at zero
      };

      const created = await goalNutrientService.create(payload);

      // Merge local nutrient for instant UI update
      const fullCreated: GoalNutrient = {
        ...created,
        nutrient: created.nutrient ?? catalog.find((n) => n.id === nutrientId)!,
      };

      onAdded(fullCreated);
      setNutrientId("");
      setTarget("");
    } catch (err) {
      console.error("Failed to add nutrient:", err);
      setError(err?.message ?? "Failed to add nutrient");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border-t pt-4">
      <h3 className="text-base font-semibold mb-3">Add New Nutrient Target</h3>

      <div className="flex flex-col md:flex-row md:items-end gap-3">
        {/* Nutrient Select */}
        <div className="flex flex-col w-full md:w-1/3">
          <label className="text-sm text-gray-700 font-medium mb-1">
            Nutrient
          </label>
          <select
            value={nutrientId}
            onChange={(e) => setNutrientId(e.target.value)}
            className="border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">
              {availableNutrients.length === 0
                ? "All nutrients added"
                : "Select nutrient"}
            </option>
            {availableNutrients.map((n) => (
              <option key={n.id} value={n.id}>
                {n.name} ({n.unit})
              </option>
            ))}
          </select>
        </div>

        {/* Target */}
        <div className="flex flex-col w-full md:w-1/4">
          <label className="text-sm text-gray-700 font-medium mb-1">
            Target Amount
          </label>
          <input
            type="number"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="e.g. 100"
            className="border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
            max={1000000000}
          />
        </div>

        {/* Unit */}
        <div className="flex flex-col justify-end text-sm text-gray-600 md:w-1/6">
          {selected ? <span>Unit: {selected.unit}</span> : <span>&nbsp;</span>}
        </div>

        {/* Add button */}
        <button
          onClick={handleAdd}
          disabled={loading || !nutrientId || !target}
          className={`px-4 py-2 rounded-md text-sm font-medium text-white ${
            loading || !nutrientId || !target
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loading ? "Adding..." : "Add"}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
    </div>
  );
}
