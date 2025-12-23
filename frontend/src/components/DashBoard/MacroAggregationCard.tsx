// src/components/Dashboard/MacroAggregationCard.tsx
import { EatenMeal } from "@/schema/zodSchema";
import { aggregateMealTotals } from "@/lib/nutrition";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function MacroAggregationCard({ eatenMeals }: { eatenMeals: EatenMeal[] }) {
  if (!eatenMeals?.length)
    return (
      <div className="rounded-2xl border bg-white p-6 text-sm text-gray-500">
        No meals eaten yet today.
      </div>
    );

  // Aggregate totals
  const totals = eatenMeals.reduce((acc, em) => {
    const mealTotals = aggregateMealTotals(em.meal);
    for (const [k, v] of Object.entries(mealTotals)) {
      acc[k] = (acc[k] ?? 0) + (v ?? 0);
    }
    return acc;
  }, {} as Record<string, number>);

  const protein = totals.protein ?? 0;
  const fat = totals.fat_total ?? 0;
  const carbs = totals.carbohydrate ?? 0;
  const kcal = totals.energy_kcal ?? 0;

  // Macro energy contribution (kcal = P×4 + F×9 + C×4)
  const macroData = [
    { name: "Protein", value: protein * 4 },
    { name: "Fat", value: fat * 9 },
    { name: "Carbs", value: carbs * 4 },
  ];

  const COLORS = ["#10B981", "#F59E0B", "#3B82F6"]; // emerald, amber, blue

  return (
    <div className="rounded-2xl border bg-white shadow-sm p-6 space-y-5 hover:shadow-md transition-all">
      <h2 className="text-lg font-semibold text-gray-800">Total Nutrients Eaten</h2>

      {/* Macro Ring */}
      <div className="flex items-center justify-center relative">
        <div className="w-44 h-44">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={macroData}
                dataKey="value"
                nameKey="name"
                innerRadius="70%"
                outerRadius="90%"
                stroke="none"
                paddingAngle={1}
              >
                {macroData.map((entry, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(val, name) =>
                  `${name}: ${((val as number / kcal) * 100).toFixed(1)}%`
                }
                contentStyle={{
                  fontSize: "0.75rem",
                  borderRadius: "8px",
                  background: "rgba(255,255,255,0.9)",
                  border: "1px solid #e5e7eb",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Center text */}
        <div className="absolute text-center">
          <p className="text-xs text-gray-500">Total</p>
          <p className="text-2xl font-bold text-gray-900">{Math.round(kcal)}</p>
          <p className="text-sm text-gray-500">kcal</p>
        </div>
      </div>

      {/* Breakdown Labels */}
      <div className="grid grid-cols-3 text-center mt-2">
        <div>
          <p className="text-xs text-gray-500">Protein</p>
          <p className="font-medium text-emerald-600">{Math.round(protein)} g</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Fat</p>
          <p className="font-medium text-amber-500">{Math.round(fat)} g</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Carbs</p>
          <p className="font-medium text-blue-500">{Math.round(carbs)} g</p>
        </div>
      </div>

      {/* Legend + Ratio summary */}
      <div className="flex justify-center gap-4 mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-emerald-500 rounded-full" /> Protein
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-amber-500 rounded-full" /> Fat
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-blue-500 rounded-full" /> Carbs
        </span>
      </div>

      <p className="text-xs text-gray-400 text-center mt-3 italic">
        Protein 4 kcal/g • Fat 9 kcal/g • Carbs 4 kcal/g
      </p>
    </div>
  );
}
