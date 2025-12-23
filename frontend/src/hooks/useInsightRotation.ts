// src/hooks/useInsightRotation.ts
import { useEffect, useRef, useState } from "react";
import type { Insight } from "@/types/insights";

export function useInsightRotation(insights: Insight[], intervalMs = 7000) {
  const [index, setIndex] = useState(0);
  const timerRef = useRef<number | null>(null);

  const next = () => setIndex((i) => (i + 1) % Math.max(insights.length || 1, 1));
  const prev = () => setIndex((i) => (i - 1 + Math.max(insights.length || 1, 1)) % Math.max(insights.length || 1, 1));
  const goTo = (i: number) => setIndex(i % Math.max(insights.length || 1, 1));

  useEffect(() => {
    if (!insights.length) return;
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = window.setInterval(next, intervalMs);
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [insights.map((x) => x.id).join("|"), intervalMs]);

  useEffect(() => {
    // If insights list changes size, reset to 0 to avoid out-of-bounds
    setIndex(0);
  }, [insights.length]);

  return { index, current: insights[index], next, prev, goTo };
}
