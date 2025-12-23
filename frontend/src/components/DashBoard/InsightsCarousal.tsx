import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Insight } from "@/types/insights";

type Props = {
  insights: Insight[];
  autoRotate?: boolean;
  interval?: number;
};

export default function DashboardInsightsCard({
  insights,
  autoRotate = true,
  interval = 7000,
}: Props) {
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(false);

  // --- Auto rotation ---
  useEffect(() => {
    if (!autoRotate || paused || insights.length <= 1) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % insights.length);
    }, interval);
    return () => clearInterval(id);
  }, [insights.length, autoRotate, paused, interval]);

  // --- Nav handlers ---
  const prev = () => setIndex((i) => (i - 1 + insights.length) % insights.length);
  const next = () => setIndex((i) => (i + 1) % insights.length);

  if (!insights.length) return null;

  const current = insights[index];
  const severityColor: Record<Insight["severity"], string> = {
    critical: "text-red-600",
    high: "text-orange-600",
    medium: "text-amber-600",
    info: "text-emerald-600",
  };
  console.log("[InsightsSection] Mounted");

  return (
    <div
      className="relative rounded-2xl bg-white border border-gray-200 p-6 shadow-sm select-none"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      {/* --- Header --- */}
      <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center justify-between">
        <span>Insights & Tips</span>
        <span className="text-xs text-gray-400">
          {index + 1}/{insights.length}
        </span>
      </h2>

      {/* --- Rotating insight --- */}
      <div className="min-h-[6.5rem] relative overflow-hidden flex flex-col items-center justify-center text-center px-4 py-2 transition-all duration-300 ease-in-out">


        <AnimatePresence mode="wait">
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.35 }}
            className="flex flex-col items-center gap-2"
          >
            {/* severity tag */}
            <span
              className={`text-xs font-medium uppercase tracking-wide ${severityColor[current.severity]}`}
            >
              {current.severity}
            </span>

            {/* message */}
            <p className="text-gray-600 text-sm leading-snug max-w-md">
              {current.message}
            </p>

            {/* metric line */}
            {current.metric && (
              <p className="text-xs text-gray-500">
                {current.metric.key}:{" "}
                <span className="font-medium text-gray-700">
                  {current.metric.value}
                  {current.metric.unit ? ` ${current.metric.unit}` : ""}
                </span>
                {current.metric.target && (
                  <>
                    {" / "}
                    {Array.isArray(current.metric.target)
                      ? current.metric.target.join("–")
                      : current.metric.target}
                  </>
                )}
              </p>
            )}

            {/* hint line */}
            {current.action?.hint && (
              <p className="text-[11px] text-gray-400">{current.action.hint}</p>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* --- Navigation --- */}
      {insights.length > 1 && (
        <>
          <button
            onClick={prev}
            aria-label="Previous insight"
            className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 shadow-sm"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            onClick={next}
            aria-label="Next insight"
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 shadow-sm"
          >
            <ChevronRight size={18} />
          </button>
        </>
      )}

      {/* --- Pagination dots & optional action --- */}
      <div className="flex justify-center items-center gap-3 mt-3">
        <div className="flex gap-1">
          {insights.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 w-4 rounded-full transition-all ${
                i === index ? "bg-emerald-500" : "bg-gray-300"
              }`}
            />
          ))}
        </div>
        {current.action && (
          <button className="text-xs font-medium text-emerald-600 hover:text-emerald-700 transition">
            {current.action.label}
          </button>
        )}
      </div>
    </div>
  );
}
