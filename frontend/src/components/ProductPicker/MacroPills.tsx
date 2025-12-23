type Props = {
  energyKj?: number | null;
  proteinG?: number | null;
  carbsG?: number | null;
  fatG?: number | null;
  className?: string;
  dense?: boolean;
};

export default function MacroPills({
  energyKj,
  proteinG,
  carbsG,
  fatG,
  className = "",
  dense = true,
}: Props) {
  const pill = (label: string, value?: number | null, unit = "") =>
    value == null || Number.isNaN(value) ? null : (
      <span
        className={`inline-flex items-center rounded-md border border-[var(--color-line)] bg-[var(--color-surface-1)] ${dense ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm"}`}
      >
        <span className="font-medium text-[var(--text-strong)] mr-1">
          {label}
        </span>
        <span className="tabular-nums">
          {Math.round(value)}
          {unit}
        </span>
      </span>
    );

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {pill("kJ", energyKj)}
      {pill("P", proteinG, "g")}
      {pill("C", carbsG, "g")}
      {pill("F", fatG, "g")}
    </div>
  );
}
