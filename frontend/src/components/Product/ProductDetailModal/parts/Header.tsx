import { X } from "lucide-react";
import type { ViewMode } from "..";

type Props = {
  title: string;
  view: ViewMode; // "standard" | "matrix" | "efficiency"
  onChangeView: (v: ViewMode) => void;
  onClose: () => void;
};

const TABS: { id: ViewMode; label: string }[] = [
  { id: "standard", label: "Standard" },
  { id: "matrix", label: "Matrix" },
  { id: "efficiency", label: "Efficiency" }, // ✅ new
];

export default function Header({ title, view, onChangeView, onClose }: Props) {
  return (
    <div className="flex items-center justify-between border-b p-4">
      <h2 className="text-lg font-semibold">{title}</h2>

      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">View:</span>

        {/* Tabs */}
        <div
          role="tablist"
          aria-label="Product detail views"
          className="inline-flex overflow-hidden rounded-lg border"
        >
          {TABS.map((t) => {
            const active = view === t.id;
            return (
              <button
                key={t.id}
                role="tab"
                aria-selected={active}
                aria-controls={`panel-${t.id}`}
                tabIndex={active ? 0 : -1}
                className={[
                  "px-3 py-1 text-sm outline-none",
                  active
                    ? "bg-blue-600 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50",
                  "focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-0",
                ].join(" ")}
                onClick={() => onChangeView(t.id)}
              >
                {t.label}
              </button>
            );
          })}
        </div>
      </div>

      <button
        onClick={onClose}
        className="rounded-md p-1 text-gray-500 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-blue-500"
        aria-label="Close"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  );
}
