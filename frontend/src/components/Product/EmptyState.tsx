export default function EmptyState({
  title = "No results",
  subtitle = "Try a different search term.",
}: {
  title?: string;
  subtitle?: string;
}) {
  return (
    <div className="rounded-2xl border p-8 text-center text-gray-500">
      <div className="text-base font-medium">{title}</div>
      <div className="mt-1 text-sm">{subtitle}</div>
    </div>
  );
}
