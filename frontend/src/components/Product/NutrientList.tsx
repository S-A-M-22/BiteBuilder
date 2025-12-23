import { ProductNutrient } from "@/schema/zodSchema";

type Props = {
  nutrients: ProductNutrient[];
};

export default function NutrientList({ nutrients }: Props) {
  if (nutrients.length === 0)
    return <p className="text-xs text-gray-400">No nutrient data available.</p>;

  return (
    <div className="text-xs text-gray-700">
      <p className="font-semibold mb-1">Key nutrients (per 100g):</p>
      <ul className="grid grid-cols-2 gap-x-3 gap-y-1">
        {nutrients.map((pn) => (
          <li key={pn.id} className="flex justify-between">
            <span>{pn.nutrient.name}</span>
            <span className="text-gray-600">
              {pn.amount_per_100g} {pn.nutrient.unit}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
