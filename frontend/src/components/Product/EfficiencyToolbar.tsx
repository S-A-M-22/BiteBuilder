import { useEfficiencyContext } from "@/context/EfficiencyContext";

export default function EfficiencyToolbar() {
  const { toggleMetric, isVisible } = useEfficiencyContext();

  const options = [
    { key: "proteinDensity", label: "Protein / 100 kcal" },
    { key: "proteinPerDollar", label: "Protein / $" },
    { key: "kcalPerDollar", label: "kcal / $" },
    { key: "yieldIndex", label: "Yield Index" },
    { key: "healthStar", label: "Health★" },
  ];

  return (
    <div className="mb-4 flex flex-wrap items-center gap-3 rounded-lg border bg-white p-3 shadow-sm">
      <span className="text-sm font-medium text-gray-600">Show:</span>
      {options.map(({ key, label }) => (
        <label key={key} className="flex items-center gap-1 text-xs text-gray-700">
          <input
            type="checkbox"
            checked={isVisible(key as any)}
            onChange={() => toggleMetric(key as any)}
            className="accent-blue-600"
          />
          {label}
        </label>
      ))}
    </div>
  );
}
