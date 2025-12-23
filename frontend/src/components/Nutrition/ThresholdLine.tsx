// src/components/Nutrition/ThresholdLine.tsx
import React from "react";

type OverflowMode = "fill" | "replace" | "arrow";
type Direction = "lower" | "higher";

type Props = {
  value: number | null;
  threshold: number;
  direction?: Direction;          // "lower" means lower is better
  format?: (n: number) => string; // e.g. (n)=>n.toFixed(1)+" g/g"
  showTicks?: boolean;            // minor ticks every 0.2×
  maxFactor?: number;             // ruler right edge (kept at 2 to pin 1× at center)
  dangerFactor?: number;          // darker zone start on limit side (e.g., 1.5×)
  overflowMode?: OverflowMode;    // "fill" | "replace" | "arrow"
  thresholdLabel?: string;        // custom text, else uses formatted threshold
  className?: string;             // optional wrapper class
};

export default function ThresholdLine({
  value,
  threshold,
  direction = "lower",
  format,
  showTicks = true,
  maxFactor = 2,
  dangerFactor = 1.5,
  overflowMode = "fill",
  thresholdLabel,
  className = "",
}: Props) {
  const mid = 50; // center tick (1×)
  const fmt = (n: number) => (format ? format(n) : String(n));
  const r = value == null ? null : value / threshold;
  const overshoot = r != null && r > maxFactor;
  const pos = r == null ? null : Math.max(0, Math.min(100, r * 50)); // 1× -> 50%
  const goodLeft = direction === "lower";
  const dangerPct = Math.max(0, Math.min(100, dangerFactor * 50));

  // ticks every 0.2× (10% width since 1× == 50%)
  const ticks: number[] = [];
  if (showTicks) {
    for (let rr = 0.2; rr < maxFactor; rr += 0.2) {
      const p = Math.max(0, Math.min(100, rr * 50));
      if (Math.abs(p - mid) > 0.1) ticks.push(p);
    }
  }

  // status text (below bar)
  const status = (() => {
    if (value == null) return "Not enough data";
    if (direction === "lower") {
      if (value <= threshold) return "Under target";
      return overshoot ? `Over target · >${maxFactor}×` : "Over target";
    } else {
      if (value >= threshold) return "Under target";
      return overshoot ? `Over target · >${maxFactor}×` : "Over target";
    }
  })();

  // --- REPLACE mode: show only a warning ---
  if (overshoot && overflowMode === "replace") {
    return (
      <div className={`relative ${className}`}>
        {/* Fixed threshold badge */}
        <div className="absolute -top-3 right-0">
          <span className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-[11px] text-gray-700 shadow-sm">
            {thresholdLabel ?? `Threshold: ${fmt(threshold)}`}
          </span>
        </div>

        <div className="rounded-md border border-red-300 bg-red-50 px-2 py-1 text-[11px] text-red-700 mt-2">
          Off-scale: &gt; {maxFactor}× target
        </div>
        <div className="mt-1 text-[11px] text-gray-600">
          {direction === "lower" ? "Over target · Lower is better" : "Over target · Higher is better"}
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>

      {/* Bar */}
      <div className="mt-4 relative h-2 w-full rounded bg-gray-100 overflow-hidden">
        {/* Good half */}
        <div
          className="absolute inset-y-0"
          style={{
            left: goodLeft ? 0 : `${mid}%`,
            width: "50%",
            background: "rgba(34,197,94,0.18)", // green/18
          }}
        />
        {/* Limit half */}
        <div
          className="absolute inset-y-0"
          style={{
            left: goodLeft ? `${mid}%` : 0,
            width: "50%",
            background: "rgba(239,68,68,0.16)", // red/16
          }}
        />
        {/* Darker danger segment */}
        <div
          className="absolute inset-y-0 pointer-events-none"
          style={{
            left: goodLeft ? `${dangerPct}%` : 0,
            width: goodLeft ? `${100 - dangerPct}%` : `${dangerPct}%`,
            background: "rgba(239,68,68,0.28)", // red/28
          }}
        />

        {/* Minor ticks */}
        {ticks.map((t, i) => (
          <div key={i} className="absolute top-0 h-full w-px bg-gray-300/50" style={{ left: `${t}%` }} />
        ))}

        {/* Threshold tick (center, 1×) */}
        <div className="absolute top-0 h-full w-0.5 bg-gray-600/70" style={{ left: `${mid}%` }} />

        {/* Pointer */}
        {pos != null && (
          <>
            <div className="absolute -top-1 h-4 w-0.5 bg-current" style={{ left: `${pos}%` }} />
            {overshoot && overflowMode === "arrow" && (
              <div className="absolute -top-3 right-0 flex items-center gap-1 pr-1">
                <div className="h-5 w-0.5 bg-current opacity-80" />
                <div
                  className="w-0 h-0"
                  style={{
                    borderLeft: "10px solid currentColor",
                    borderTop: "8px solid transparent",
                    borderBottom: "8px solid transparent",
                  }}
                />
              </div>
            )}
          </>
        )}

        {/* FILL overflow overlay */}
        {overshoot && overflowMode === "fill" && (
          <div className="absolute inset-0 bg-red-200/70">
            <div className="absolute right-1 top-1 rounded px-1.5 py-0.5 text-[10px] font-medium text-red-900 bg-red-100/80">
              OFF-SCALE
            </div>
          </div>
        )}
      </div>

      {/* Below-bar captions */}
      <div className="relative mt-1 text-[11px] text-gray-600">
        <span className="block">
          {status}
          <span className="opacity-70">
            {" "}
            · {direction === "lower" ? "Lower is better" : "Higher is better"}
          </span>
        </span>
      </div>
    </div>
  );
}
