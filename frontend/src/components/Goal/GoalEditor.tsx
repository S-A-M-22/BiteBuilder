// ===============================================
// src/components/Goal/GoalEditor.tsx
// ===============================================
import { useState } from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { goalService } from "@/services/goal_service";
import { Goal } from "@/schema/zodSchema";

// Updated schema to match new backend model
const GoalFormSchema = z.object({
  target_weight_kg: z.number().min(0, "Weight must be positive"),
  target_calories: z.number().min(0, "Calories must be positive"),
  reset_frequency: z.enum(["daily", "weekly", "monthly", "none"]),
});

type GoalFormValues = z.infer<typeof GoalFormSchema>;

type Props = {
  goal: Goal;
  setGoal: (g: Goal) => void;
};

export default function GoalEditor({ goal, setGoal }: Props) {
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const form = useForm<GoalFormValues>({
    resolver: zodResolver(GoalFormSchema),
    defaultValues: {
      target_weight_kg: goal.target_weight_kg ?? 70,
      target_calories: goal.target_calories ?? 2000,
      reset_frequency: goal.reset_frequency ?? "none",
    },
  });

  const onSubmit = async (data: GoalFormValues) => {
    try {
      setSaving(true);
      setStatus(null);
      const updated = await goalService.update(goal.id, data);
      setGoal(updated);
      setStatus("✅ Goal updated successfully.");
    } catch (err) {
      console.error(err);
      setStatus("❌ Failed to update goal.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={form.handleSubmit(onSubmit)}
      className="space-y-4 border rounded-xl p-6 bg-[var(--color-panel)] shadow-sm"
    >
      <h3 className="text-base font-semibold text-[var(--color-ink)]">
        Goal Settings
      </h3>

      {/* Weight */}
      <div>
        <label className="text-sm font-medium text-gray-700">
          Target Weight (kg)
        </label>
        <input
          type="number"
          step="0.1"
          {...form.register("target_weight_kg", { valueAsNumber: true })}
          className="mt-1 w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          max={1000000000}
        />
      </div>

      {/* Calories */}
      <div>
        <label className="text-sm font-medium text-gray-700">
          Target Calories (kcal)
        </label>
        <input
          type="number"
          {...form.register("target_calories", { valueAsNumber: true })}
          className="mt-1 w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
          max={1000000000}
        />
      </div>

      {/* Reset Frequency */}
      <div>
        <label className="text-sm font-medium text-gray-700">
          Reset Frequency
        </label>
        <select
          {...form.register("reset_frequency")}
          className="mt-1 w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="none">Never (manual reset)</option>
        </select>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={saving}
        className={`px-4 py-2 text-sm font-medium text-white rounded-md ${
          saving
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        {saving ? "Saving..." : "Save Goal"}
      </button>

      {status && (
        <p
          className={`text-sm ${
            status.startsWith("✅") ? "text-green-600" : "text-red-600"
          }`}
        >
          {status}
        </p>
      )}
    </form>
  );
}
