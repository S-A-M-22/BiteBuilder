// src/types/insights.ts
export type InsightSeverity = "critical" | "high" | "medium" | "info";

export type InsightTag =
  | "calories"
  | "protein"
  | "fiber"
  | "sodium"
  | "sat_fat"
  | "sugars"
  | "macro_balance";

export type Insight = {
  id: string; // stable key for dedupe/dismiss
  severity: InsightSeverity;
  score: number; // 0–100 priority (higher first within same severity)
  message: string;
  details?: string;
  tags: InsightTag[];
  metric?: {
    key: string;
    value: number | null;
    unit?: string;
    target?: number | [number, number];
  };
  action?: {
    label: string;
    onClick?: () => void; // optional callback (wire up in UI)
    hint?: string; // extra guidance shown next to button
  };
};
