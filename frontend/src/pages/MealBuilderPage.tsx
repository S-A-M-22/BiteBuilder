import React, { useEffect, useMemo, useState } from "react";
import type { Meal, Product } from "@/schema/zodSchema";
import { mealItemService, mealService } from "@/services/meal_service";
import ExistingMealsSection from "@/components/MealBuilder/ExistingMealsSection";
import ProductPicker from "@/components/ProductPicker/ProductPicker";
import SelectedMealSection from "@/components/MealBuilder/SelectedMealSection";
import MealCreatorSimple from "@/components/MealBuilder/MealCreatorSimple";

import MealProductSearchSection from "@/components/MealBuilder/MealProductSearchSection";
import { productService } from "@/services/product_service";
import { useFavourites } from "@/hooks/useFavourites";
import { useTooltip } from "@/hooks/useTooltips";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import ProductDetailsModal from "@/components/Product/ProductDetailModal";

export default function MealBuilderPage() {
  const [meals, setMeals] = useState<Meal[]>([]);
  const [currentMeal, setCurrentMeal] = useState<Meal | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [adding, setAdding] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailProduct, setDetailProduct] = useState<Partial<Product> | null>(null);

  const { Tooltip, showAtCursor, showCenter } = useTooltip();
  const { addFavourite, isLocallySaved } = useFavourites();

  useEffect(() => {
    (async () => {
      try {
        setMeals(await mealService.list());
      } catch (err) {
        console.error("Failed to load meals:", err);
      }
    })();
  }, []);

  const handleDeleteMeal = async (id: string) => {
    const prev = meals;
    setDeletingId(id);
    setMeals((m) => m.filter((x) => x.id !== id));
    if (currentMeal?.id === id) setCurrentMeal(null);
    try {
      await mealService.remove(id);
    } catch (err) {
      console.error("Failed to delete meal", err);
      setMeals(prev);
    } finally {
      setDeletingId(null);
    }
  };

  const handleRemoveItem = async (id: string) => {
    if (!currentMeal) return;
    const prevItems = currentMeal.items ?? [];
    const updated = prevItems.filter((it) => it.id !== id);
    setCurrentMeal({ ...currentMeal, items: updated });
    setMeals((ms) => ms.map((m) => (m.id === currentMeal.id ? { ...m, items: updated } : m)));
    try {
      await mealItemService.remove(id);
    } catch (err) {
      console.error("Failed to delete meal item:", err);
      setCurrentMeal({ ...currentMeal, items: prevItems });
      setMeals((ms) =>
        ms.map((m) => (m.id === currentMeal.id ? { ...m, items: prevItems } : m))
      );
    }
  };

  const handleAddSearchProduct = async (product: Partial<Product>, qty = 100, e?: React.MouseEvent) => {
    if (!currentMeal?.id) return showCenter("Select a meal first.");
    if (!product) return;

    if (isLocallySaved(product)) {
      e ? showAtCursor(e, "Item already favourited") : showCenter("Item already favourited");
      return;
    }

    setAdding(true);
    try {
      const saved = await (productService as any).save(product);
      const item = (saved as any)?.item ?? saved;
      if (item) addFavourite(item);
      setRefreshKey((k) => k + 1);
      e ? showAtCursor(e, "Saved to favourites") : showCenter("Saved to favourites");
    } catch (err) {
      console.error("Failed to save product", err);
      showCenter("Save failed");
    } finally {
      setAdding(false);
    }
  };

  const openNutritionModal = async (p: Partial<Product>, qty = 100) => {
    try {
      const detail = await productService.getDetail(String((p as any)?.id ?? ""));
      setDetailProduct({ ...p, ...detail, __qty: qty });
      setDetailOpen(true);
    } catch {
      setDetailProduct({ ...p, __qty: qty });
      setDetailOpen(true);
    }
  };

  const closeNutritionModal = () => {
    setDetailOpen(false);
    setDetailProduct(null);
  };

  const mealStatus = useMemo(() => {
    if (!currentMeal) return "No meal selected — select or create one.";
    const dt = new Date(currentMeal.date_time ?? Date.now()).toLocaleString("en-AU");
    return `Selected meal: ${String(currentMeal.meal_type).toUpperCase()} • ${dt}`;
  }, [currentMeal]);

  return (
    <main className="mx-auto max-w-[1280px] 2xl:max-w-[1440px] p-6">
      {/* Top bar */}
      <header className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Meal Builder</h1>
        <p className="text-sm text-muted-foreground">{mealStatus}</p>
      </header>

      {/* FLEX LAYOUT: fixed sidebar + fluid canvas */}
      <div className="flex flex-col gap-6 lg:flex-row">
        {/* LEFT: fixed-width, sticky sidebar */}
        <aside
  className="
    w-full lg:w-[360px] xl:w-[400px] lg:flex-none
    lg:sticky lg:top-20
  "
>
  <div
    className="
      rounded-2xl border border-gray-200 bg-white
      shadow-sm p-4 space-y-4
      h-fit
    "
  >
    <MealCreatorSimple
      onMealCreated={(newMeal) => {
        setMeals((prev) => [newMeal, ...prev]);
        setCurrentMeal(newMeal);
      }}
    />

    <ExistingMealsSection
      meals={meals}
      currentMeal={currentMeal}
      onSelectMeal={setCurrentMeal}
    />

    {currentMeal && (
      <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
        <h3 className="text-sm font-semibold mb-2 text-gray-700">Quick Summary</h3>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>Items: {currentMeal.items?.length ?? 0}</li>
          <li>Date: {new Date(currentMeal.date_time ?? "").toLocaleDateString()}</li>
          <li>Type: {currentMeal.meal_type}</li>
        </ul>
      </div>
    )}
  </div>
</aside>

        {/* RIGHT: builder canvas */}
        <section className="flex-1 min-w-0 space-y-4">
          {currentMeal ? (
            <>
              <SelectedMealSection
                meal={currentMeal}
                deletingId={deletingId}
                onDeleteMeal={handleDeleteMeal}
                onRemoveItem={handleRemoveItem}
              />

              <Tabs defaultValue="search" className="w-full">
                <TabsList className="flex border-b border-gray-200 mb-3">
                  <TabsTrigger
                    value="search"
                    className="px-4 py-2 text-sm data-[state=active]:border-b-2 data-[state=active]:border-blue-600"
                  >
                    Search Products
                  </TabsTrigger>
                  <TabsTrigger
                    value="picker"
                    className="px-4 py-2 text-sm data-[state=active]:border-b-2 data-[state=active]:border-blue-600"
                  >
                    My Saved Items
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="search" className="min-w-0">
                  <MealProductSearchSection
                    currentMealId={currentMeal?.id ?? null}
                    onAddProduct={handleAddSearchProduct}
                    openNutrition={openNutritionModal}
                    adding={adding}
                  />
                </TabsContent>

                <TabsContent value="picker" className="min-w-0">
                  <ProductPicker
                    key={refreshKey}
                    mealId={currentMeal.id}
                    existingItems={currentMeal.items}
                    onItemAdded={(item) => {
                      setCurrentMeal((m) =>
                        m ? { ...m, items: [...(m.items ?? []), item] } : m
                      );
                      setMeals((ms) =>
                        ms.map((m) =>
                          m.id === currentMeal.id
                            ? { ...m, items: [...(m.items ?? []), item] }
                            : m
                        )
                      );
                    }}
                  />
                </TabsContent>
              </Tabs>
            </>
          ) : (
            <div className="rounded-2xl border border-dashed border-gray-300 bg-gray-50/60 p-10 text-center text-gray-600">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">
            Welcome to your Meal Builder
          </h2>
          <p className="max-w-md mx-auto text-sm leading-relaxed text-gray-600">
            To get started, create a new meal using the panel on the left.
            Once a meal is selected, you’ll be able to:
          </p>
          <ul className="mt-4 inline-block text-left text-sm text-gray-600 space-y-1">
            <li>• Add products and adjust serving sizes</li>
            <li>• View live nutritional summaries</li>
            <li>• Save frequent items for quick reuse</li>
          </ul>
          <p className="mt-6 text-xs text-gray-500 italic">
            Tip: You can always return here to edit or delete past meals.
          </p>
        </div>

          )}
        </section>
      </div>

      <ProductDetailsModal
        open={detailOpen}
        product={detailProduct ? { ...(detailProduct as Partial<Product>) } : undefined}
        onClose={closeNutritionModal}
      />
      <Tooltip />
    </main>
  );
}
