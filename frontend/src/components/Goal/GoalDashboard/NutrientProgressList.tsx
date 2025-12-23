import { useMemo, useState } from "react";
import { GoalNutrient } from "@/schema/zodSchema";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Info } from "lucide-react";

interface NutrientProgressListProps {
  nutrients: GoalNutrient[];
}

export default function NutrientProgressList({ nutrients }: NutrientProgressListProps) {
  const [expanded, setExpanded] = useState(true);
  const [sortMode, setSortMode] = useState<"name" | "progress">("progress");

  // -------------------------------------------------------------
  // 🔹 Prepare and optionally sort progress data
  // -------------------------------------------------------------
  const progressData = useMemo(() => {
    const data = nutrients.map((gn) => ({
      ...gn,
      progress:
        gn.target_amount > 0
          ? Math.min(gn.consumed_amount / gn.target_amount, 1)
          : 0,
    }));

    if (sortMode === "progress") {
      return data.sort((a, b) => b.progress - a.progress);
    }
    return data.sort((a, b) => a.nutrient.name.localeCompare(b.nutrient.name));
  }, [nutrients, sortMode]);

  // -------------------------------------------------------------
  // 🔹 Progress → gradient color mapping
  // -------------------------------------------------------------
  const getProgressColor = (progress: number): string => {
    if (progress > 1.0) return "hsl(0, 80%, 55%)";           // 🔴 Overshoot
    if (progress < 0.2) return "hsl(0, 85%, 55%)";           // 🔴 Under-fueled
    if (progress < 0.4) return "hsl(45, 90%, 55%)";          // 🟡 Warming up
    if (progress < 0.6) return "hsl(130, 65%, 50%)";         // 🟢 Fresh green
    if (progress < 0.8) return "hsl(140, 70%, 45%)";         // 🟢 Deeper green
    return "hsl(150, 80%, 40%)";                             // ✅ Confident strong green
  };

  return (
    <div className="space-y-4">
      {/* -------------------------------------------------------------
          🔹 Header + controls
      ------------------------------------------------------------- */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">Nutrient Progress</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setSortMode(sortMode === "progress" ? "name" : "progress")}
            className="text-xs px-2 py-1 rounded-md border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 transition-colors"
          >
            Sort: {sortMode === "progress" ? "By Progress" : "By Name"}
          </button>

          <button
            onClick={() => setExpanded((e) => !e)}
            className="p-1 text-gray-600 hover:text-gray-900"
          >
            {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>
      </div>

      {/* -------------------------------------------------------------
          🔹 Animated Nutrient Bars
      ------------------------------------------------------------- */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            key="progress-list"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="space-y-3"
          >
            {progressData.map((gn, i) => (
              <div
                key={gn.id}
                className="group relative rounded-lg border border-gray-100 bg-white/60 p-3 shadow-sm hover:shadow-md transition-all duration-300"
              >
                <div className="flex justify-between text-sm font-medium text-gray-700 mb-1">
                  <span className="truncate">{gn.nutrient.name}</span>
                  <span className="text-gray-600">
                    {gn.consumed_amount.toFixed(1)} / {gn.target_amount} {gn.nutrient.unit}
                  </span>
                </div>

                <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className="absolute top-0 left-0 h-full rounded-full"
                  style={{
                    backgroundColor: getProgressColor(gn.consumed_amount / gn.target_amount),
                    width: `${Math.min(gn.consumed_amount / gn.target_amount, 1) * 100}%`,
                    filter: `drop-shadow(0 0 3px ${getProgressColor(gn.consumed_amount / gn.target_amount)}80)`,
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(gn.consumed_amount / gn.target_amount, 1) * 100}%` }}
                  transition={{ duration: 0.8, ease: "easeOut" }}
                />

                </div>


              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
