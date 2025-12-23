// GoalNutrientTable.tsx
import { useState } from "react";
import { goalNutrientService } from "@/services/goalNutrient_service";
import { GoalNutrient, Nutrient } from "@/schema/zodSchema";

interface Props {
  nutrients: GoalNutrient[];
  catalog: Nutrient[];
  onUpdate: (updated: GoalNutrient) => void;
  onDelete: (id: string) => void;
}

export default function GoalNutrientTable({
  nutrients,
  catalog,
  onUpdate,
  onDelete,
}: Props) {
  const [savingId, setSavingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleSave = async (gn: GoalNutrient, value: number) => {
    try {
      setSavingId(gn.id);
      const updated = await goalNutrientService.update(gn.id, {
        goal: gn.goal,
        target_amount: value,
      });
      onUpdate(updated);
    } finally {
      setSavingId(null);
    }
  };

  const handleDelete = async (gn: GoalNutrient) => {
    if (!confirm(`Delete ${gn.nutrient.name}?`)) return;
    try {
      setDeletingId(gn.id);
      await goalNutrientService.remove(gn.id);
      onDelete(gn.id);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div>
      <h3 className="text-base font-semibold mb-3">Nutrient Targets</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr>
              <th className="p-2 text-left">Nutrient</th>
              <th className="p-2 text-center">Target</th>
              <th className="p-2 text-left">Unit</th>
              <th className="p-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {nutrients.map((gn) => {
              const meta = catalog.find((n) => n.id === gn.nutrient.id);
              return (
                <GoalNutrientRow
                  key={gn.id}
                  gn={gn}
                  meta={meta}
                  savingId={savingId}
                  deletingId={deletingId}
                  onSave={handleSave}
                  onDelete={handleDelete}
                />
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------
// Child component with Save + Delete support
// ---------------------------------------------
function GoalNutrientRow({
  gn,
  meta,
  savingId,
  deletingId,
  onSave,
  onDelete,
}: {
  gn: GoalNutrient;
  meta?: Nutrient;
  savingId: string | null;
  deletingId: string | null;
  onSave: (gn: GoalNutrient, value: number) => void;
  onDelete: (gn: GoalNutrient) => void;
}) {
  const [value, setValue] = useState(gn.target_amount);

  const isSaving = savingId === gn.id;
  const isDeleting = deletingId === gn.id;

  return (
    <tr key={gn.id} className="border-b hover:bg-gray-50">
      <td className="p-2 font-medium">{meta?.name ?? "Unknown"}</td>
      <td className="p-2 text-center">
        <input
          type="number"
          value={value}
          onChange={(e) => setValue(Number(e.target.value))}
          className="border rounded-md p-1 w-24 text-center"
          disabled={isSaving || isDeleting}
          max={1000000000000}
        />
      </td>
      <td className="p-2 text-gray-500">{meta?.unit ?? "g"}</td>
      <td className="p-2 text-right space-x-2">
        <button
          onClick={() => onSave(gn, value)}
          disabled={isSaving || isDeleting}
          className={`px-3 py-1 text-xs rounded-md ${
            isSaving
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-indigo-500 text-white hover:bg-indigo-600"
          }`}
        >
          {isSaving ? "Saving..." : "Save"}
        </button>

        <button
          onClick={() => onDelete(gn)}
          disabled={isDeleting || isSaving}
          className={`px-3 py-1 text-xs rounded-md ${
            isDeleting
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-red-500 text-white hover:bg-red-600"
          }`}
        >
          {isDeleting ? "Deleting..." : "Delete"}
        </button>
      </td>
    </tr>
  );
}
