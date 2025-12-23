export default function TopBar() {
  return (
    <section className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Scope</span>
          <div className="inline-flex rounded-xl border overflow-hidden">
            <button className="px-3 py-1.5 text-sm tab-active">Today</button>
            <button className="px-3 py-1.5 text-sm">Yesterday</button>
            <button className="px-3 py-1.5 text-sm">This week</button>
            <button className="px-3 py-1.5 text-sm">Custom</button>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button className="btn">Search</button>
        <button className="btn">Add Meal</button>
        <button className="btn">Set Goals</button>
        <button className="btn">Refresh</button>
        <span className="text-xs text-gray-500">Data as of —</span>
      </div>
    </section>
  );
}
