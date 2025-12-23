import { useState, useEffect } from "react";

const STORAGE_KEY = "efficiencyMetricsVisible";

export function useEfficiencyToggle() {
  const [visibleMetrics, setVisibleMetrics] = useState<string[]>(() => {
    if (typeof window === "undefined") return ["proteinPerDollar"];
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '["proteinPerDollar"]');
    } catch {
      return ["proteinPerDollar"];
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(visibleMetrics));
  }, [visibleMetrics]);

  function toggle(metric: string) {
    setVisibleMetrics(prev =>
      prev.includes(metric)
        ? prev.filter(m => m !== metric)
        : [...prev, metric]
    );
  }

  const isVisible = (m: string) => visibleMetrics.includes(m);
  return { visibleMetrics, toggle, isVisible };
}
