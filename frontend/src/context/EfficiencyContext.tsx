// src/context/EfficiencyContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type EfficiencyMetricKey =
  | "proteinDensity"
  | "proteinPerDollar"
  | "kcalPerDollar"
  | "proteinToFat"
  | "yieldIndex"
  | "healthValue"
  | "healthStar";

type EfficiencyContextType = {
  visibleMetrics: EfficiencyMetricKey[];
  toggleMetric: (metric: EfficiencyMetricKey) => void;
  isVisible: (metric: EfficiencyMetricKey) => boolean;
};

const EfficiencyContext = createContext<EfficiencyContextType | null>(null);

export function EfficiencyProvider({ children }: { children: ReactNode }) {
  const STORAGE_KEY = "visibleEfficiencyMetrics";

  const [visibleMetrics, setVisibleMetrics] = useState<EfficiencyMetricKey[]>(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      // fallback default
      return stored.length > 0
        ? stored
        : (["proteinPerDollar", "proteinDensity", "healthStar"] as EfficiencyMetricKey[]);
    } catch {
      return ["proteinPerDollar", "proteinDensity", "healthStar"];
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(visibleMetrics));
  }, [visibleMetrics]);

  const toggleMetric = (metric: EfficiencyMetricKey) => {
    setVisibleMetrics((prev) =>
      prev.includes(metric)
        ? prev.filter((m) => m !== metric)
        : [...prev, metric]
    );
  };

  const isVisible = (metric: EfficiencyMetricKey) => visibleMetrics.includes(metric);

  return (
    <EfficiencyContext.Provider value={{ visibleMetrics, toggleMetric, isVisible }}>
      {children}
    </EfficiencyContext.Provider>
  );
}

export function useEfficiencyContext() {
  const ctx = useContext(EfficiencyContext);
  if (!ctx) throw new Error("useEfficiencyContext must be used within EfficiencyProvider");
  return ctx;
}
