type Row = {
    name: string;
    unit?: string;
    per100: number | null;
    perServing: number | null;
    percent: number | null; // % of DRI
  };
  
  type Props = { rows: Row[] };
  
  export default function StandardTable({ rows }: Props) {
    if (rows.length === 0) {
      return <p className="mt-4 text-sm text-gray-500">No nutrition information available.</p>;
    }
  
    return (
      <div>
        <h3 className="mt-4 mb-2 text-base font-semibold">Nutrition Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-t border-gray-200">
            <thead className="bg-gray-50 text-left text-gray-700">
              <tr>
                <th className="p-2">Nutrient</th>
                <th className="p-2 text-right">Per 100g</th>
                <th className="p-2 text-right">Per Serving</th>
                <th className="p-2 text-right">% of DRI</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((n) => (
                <tr key={n.name} className="border-t hover:bg-gray-50">
                  <td className="p-2 text-gray-800">
                    {n.name}
                    {n.unit && <span className="text-gray-500"> ({n.unit})</span>}
                  </td>
                  <td className="p-2 text-right text-gray-700">{n.per100 ?? "-"}</td>
                  <td className="p-2 text-right text-gray-700">{n.perServing ?? "-"}</td>
                  <td className={`p-2 text-right font-semibold ${toneByPercent(n.percent)}`}>
                    {n.percent != null ? `${n.percent.toFixed(0)}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
  
  function toneByPercent(pct: number | null) {
    if (pct == null) return "text-gray-400";
    if (pct >= 120) return "text-red-600";
    if (pct >= 100) return "text-orange-600";
    if (pct >= 80) return "text-green-700";
    if (pct >= 40) return "text-green-500";
    return "text-gray-500";
  }
  