import { useState } from "react";
import type { Meal } from "@/schema/zodSchema";
import { mealService } from "@/services/meal_service";
import { useUserSession } from "@/hooks/userSession";

interface Props {
  onMealCreated: (meal: Meal) => void;
}

export default function MealCreatorSimple({ onMealCreated }: Props) {
  const session = useUserSession();
  const [mealType, setMealType] = useState("lunch");
  const [name, setName] = useState("");
  const [dateTime, setDateTime] = useState(() =>
    new Date().toISOString().slice(0, 16)
  );
  const [notes, setNotes] = useState("");
  const [creating, setCreating] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleCreateMeal = async () => {
    if (!session.user?.id) return setMsg("❌ No user found.");
    if (!name.trim()) return setMsg("❌ Meal name is required.");

    setCreating(true);
    setMsg(null);

    try {
      const payload = {
        user: session.user.id,
        meal_type: mealType,
        name: name.trim(),
        date_time: new Date(dateTime).toISOString(),
        notes: notes.trim() || "",
        items: [],
      };

      const created = await mealService.create(payload);
      if (!created?.id) throw new Error("Server did not return meal ID.");

      setName("");
      setNotes("");
      setMsg("✅ Meal created.");
      onMealCreated(created);
    } catch (err) {
      console.error(err);
      setMsg("❌ Failed to create meal.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <section className="rounded-2xl border border-gray-200 bg-white shadow-sm p-4 space-y-4">
      {/* FORM GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* ─── Meal Name ───────────────────── */}
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">
            Meal Name <span className="text-red-500">*</span>
          </label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter meal name"
            className="rounded-md border border-gray-300 bg-gray-50 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={1000}
          />
        </div>

        {/* ─── Meal Type ───────────────────── */}
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Meal Type</label>
          <select
            value={mealType}
            onChange={(e) => setMealType(e.target.value)}
            className="rounded-md border border-gray-300 bg-gray-50 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>
        </div>

        {/* ─── Notes ───────────────────────── */}
        <div className="sm:col-span-2 flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Notes</label>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional"
            className="rounded-md border border-gray-300 bg-gray-50 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            maxLength={10000}
          />
        </div>
      </div>

      {/* ─── ACTION BAR ───────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        {msg && (
          <p
            className={`text-sm ${
              msg.startsWith("✅")
                ? "text-green-600"
                : msg.startsWith("❌")
                ? "text-red-500"
                : "text-gray-600"
            }`}
          >
            {msg}
          </p>
        )}
        <button
          onClick={handleCreateMeal}
          disabled={creating}
          className="self-end sm:self-auto rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:bg-blue-300 transition"
        >
          {creating ? "Creating…" : "Add Meal"}
        </button>
      </div>
    </section>
  );
}
