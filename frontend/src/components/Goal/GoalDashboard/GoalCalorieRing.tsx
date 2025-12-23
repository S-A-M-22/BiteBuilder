import { useState, useMemo } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { motion, AnimatePresence } from "framer-motion";

interface GoalCalorieRingProps {
  consumedCalories: number;
  targetCalories: number;
}

export default function GoalCalorieRing({
  consumedCalories,
  targetCalories,
}: GoalCalorieRingProps) {
  const [view, setView] = useState<"calories" | "percent" | "remaining">(
    "calories"
  );

  // -------------------------------------------------------------
  // 🔹 Derived metrics
  // -------------------------------------------------------------
  const rawProgress = targetCalories > 0 ? consumedCalories / targetCalories : 0;
const progress = Math.min(rawProgress, 1); // for rendering ring fill
const remaining = Math.max(targetCalories - consumedCalories, 0);

// -------------------------------------------------------------
// 🔹 Dynamic ring color based on *raw* progress
// -------------------------------------------------------------
const progressColor = useMemo(() => {
  if (rawProgress > 1.0) return "hsl(0, 80%, 55%)";           // 🔴 Overshoot
  if (rawProgress < 0.2) return "hsl(0, 85%, 55%)";           // 🔴 Under-fueled
  if (rawProgress < 0.4) return "hsl(45, 90%, 55%)";          // 🟡 Warming up
  if (rawProgress < 0.6) return "hsl(130, 65%, 50%)";         // 🟢 Fresh green
  if (rawProgress < 0.8) return "hsl(140, 70%, 45%)";         // 🟢 Deeper green
  return "hsl(150, 80%, 40%)";                                // ✅ Confident strong green
}, [rawProgress]);

const isOvershoot = rawProgress > 1.0;


const displayText = useMemo(() => {
  if (isOvershoot) {
    const over = Math.round(consumedCalories - targetCalories);
    switch (view) {
      case "calories":
        return `${Math.round(consumedCalories)} kcal`;
      case "percent":
        return `${Math.round(rawProgress * 100)}%`;
      case "remaining":
        return `+${over} kcal over`;
    }
  } else {
    switch (view) {
      case "calories":
        return `${Math.round(consumedCalories)} / ${Math.round(targetCalories)} kcal`;
      case "percent":
        return `${Math.round(rawProgress * 100)}%`;
      case "remaining":
        return `${Math.round(remaining)} kcal left`;
    }
  }
}, [view, consumedCalories, targetCalories, rawProgress, remaining, isOvershoot]);


  // -------------------------------------------------------------
  // 🔹 Chart data + styles
  // -------------------------------------------------------------
  const data = [
    { name: "Consumed", value: progress * 100 },
    { name: "Remaining", value: 100 - progress * 100 },
  ];

  return (
    <div className="relative h-64 flex flex-col items-center justify-center select-none">
   <ResponsiveContainer width="80%" height="80%">
      <PieChart>
        <Pie
          data={data}
          innerRadius={70}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
          stroke="none"
          animationBegin={0}
          animationDuration={800}
        >
          {/* 🔹 Solid color for progress */}
          <Cell fill={progressColor} />
          {/* 🔹 Neutral gray background for remaining */}
          <Cell fill="#e5e7eb" />
        </Pie>

        <Tooltip
          formatter={(value, name) =>
            name === "Consumed"
              ? `${Math.round(progress * 100)}%`
              : `${Math.round(100 - progress * 100)}%`
          }
        />
      </PieChart>
    </ResponsiveContainer>


      {/* -------------------------------------------------------------
          🔹 Center Text (Animated)
      ------------------------------------------------------------- */}
      <div className="absolute text-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={view}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
            className="text-xl font-semibold text-gray-900"
          >
            {displayText}
          </motion.p>
        </AnimatePresence>
        <p className="text-sm text-gray-500">{view === "percent" ? "of target" : ""}</p>
      </div>

      {/* -------------------------------------------------------------
          🔹 Toggle Buttons
      ------------------------------------------------------------- */}
      <div className="absolute bottom-0 flex space-x-2">
        {["calories", "percent", "remaining"].map((mode) => (
            <button
            key={mode}
            onClick={() => setView(mode as any)}
            className={`px-3 py-1 text-xs rounded-full border transition-all duration-200 shadow-sm
                ${
                view === mode
                    ? "bg-gray-900 text-white border-gray-900 hover:bg-gray-800"
                    : "bg-gray-100/80 text-gray-700 border-gray-300 hover:bg-gray-200 hover:text-gray-900"
                }`}
            >
            {mode === "calories"
                ? "Calories"
                : mode === "percent"
                ? "Percent"
                : "Remaining"}
            </button>
        ))}
        </div>

    </div>
  );
}
