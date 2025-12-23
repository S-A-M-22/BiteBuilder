type Props = {
  kcal: number;
  protein: number;
  carbs: number; // grams
  fat: number; // grams
  className?: string;
  variant?: "pills"; // future: "tiles" | "inline"
};

function Pill({
  label,
  value,
  className = "",
}: {
  label: string;
  value: string | number;
  className?: string;
}) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full",
        "border px-2.5 py-1 text-xs",
        "bg-[var(--color-surface-2)] border-[var(--color-line)] text-[var(--text-soft)]",
        className,
      ].join(" ")}
    >
      <span className="font-medium text-[var(--text-strong)]">{value}</span>
      <span className="opacity-75">{label}</span>
    </span>
  );
}

export default function MacroBar({
  kcal,
  protein,
  carbs,
  fat,
  className = "",
}: Props) {
  // Only "pills" for now — variants let you swap designs later.
  return (
    <div className={["flex flex-wrap gap-2", className].join(" ")}>
      <Pill label="kcal" value={`≈ ${kcal}`} />
      <Pill
        label="protein"
        value={`${protein} g`}
        className="border-emerald-500/30"
      />
      <Pill
        label="carbs"
        value={`${carbs.toFixed(1)} g`}
        className="border-sky-500/30"
      />
      <Pill
        label="fat"
        value={`${fat.toFixed(1)} g`}
        className="border-amber-500/30"
      />
    </div>
  );
}
