import { useMemo } from "react";
import type { Meal } from "@/schema/zodSchema";
import { aggregateMealTotals, pickKcalProtein } from "@/lib/nutrition";

export function useMealTotals(meal: Meal | null | undefined) {
  const totals = useMemo(
    () =>
      meal
        ? aggregateMealTotals(meal)
        : aggregateMealTotals({ items: [] as any }),
    [meal],
  );
  const mini = useMemo(() => pickKcalProtein(totals), [totals]);
  console.log("logging totals")
  console.log(totals)
  return { totals, mini };
}
