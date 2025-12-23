import { useState, useRef } from "react";

export function useTooltip(timeout = 1600) {
  const [tooltipOpen, setTooltipOpen] = useState(false);
  const [tooltipText, setTooltipText] = useState("");
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const timer = useRef<number | null>(null);

  const showAtCursor = (e: React.MouseEvent, text: string) => {
    const x = e.clientX + 8;
    const y = e.clientY + 8;
    triggerTooltip(text, x, y);
  };

  const showCenter = (text: string) => {
    triggerTooltip(text, window.innerWidth / 2 - 80, 80);
  };

  const triggerTooltip = (text: string, x: number, y: number) => {
    setTooltipPos({ x, y });
    setTooltipText(text);
    setTooltipOpen(true);
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      setTooltipOpen(false);
      timer.current = null;
    }, timeout) as unknown as number;
  };

  const Tooltip = () =>
    tooltipOpen ? (
      <div
        style={{
          position: "fixed",
          left: tooltipPos.x,
          top: tooltipPos.y,
          transform: "translate(-4px, -4px)",
          zIndex: 9999,
          pointerEvents: "none",
        }}
      >
        <div className="rounded-md px-3 py-1 text-sm bg-black text-white shadow">
          {tooltipText}
        </div>
      </div>
    ) : null;

  return { Tooltip, showAtCursor, showCenter };
}
