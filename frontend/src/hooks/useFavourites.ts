import { useEffect, useMemo, useState } from "react";
import type { Product } from "@/schema/zodSchema";
import { productService } from "@/services/product_service";

export function useFavourites() {
  const [savedProducts, setSavedProducts] = useState<Product[]>([]);
  const [favourites, setFavourites] = useState<Product[]>([]);

  // --- Load saved/favourite products into local cache ---
  useEffect(() => {
    (async () => {
      try {
        let favs: Product[] = [];
        if (typeof (productService as any).favourites === "function") {
          favs = await (productService as any).favourites();
        } else if (typeof (productService as any).listSaved === "function") {
          favs = await (productService as any).listSaved();
        }
        setSavedProducts(favs ?? []);
        setFavourites(favs ?? []);
      } catch (err) {
        console.warn("Failed to load favourites:", err);
        setSavedProducts([]);
      }
    })();
  }, []);

  const safeKey = (p: Partial<Product>) =>
    (p as any).id ?? (p as any).barcode ?? (p as any).gtin ?? (p as any).code ?? JSON.stringify(p);

  const savedKeys = useMemo(() => {
    const s = new Set<string>();
    for (const p of savedProducts) {
      const k = String(safeKey(p) ?? "");
      if (k) s.add(k);
    }
    return s;
  }, [savedProducts]);

  const isLocallySaved = (p: Partial<Product>) => {
    const id = (p as any)?.id;
    const barcode = (p as any)?.barcode;
    if (!id && !barcode) return false;
    return [...savedProducts, ...favourites].some(
      (f) =>
        (id && String((f as any)?.id) === String(id)) ||
        (barcode && String((f as any)?.barcode) === String(barcode))
    );
  };

  const addFavourite = (product: Product) => {
    setSavedProducts((prev) =>
      prev.find((p) => String(p.id) === String(product.id)) ? prev : [...prev, product]
    );
    setFavourites((prev) =>
      prev.find((p) => String(p.id) === String(product.id)) ? prev : [...prev, product]
    );
  };

  return {
    favourites,
    savedProducts,
    setSavedProducts,
    setFavourites,
    savedKeys,
    isLocallySaved,
    addFavourite,
  };
}
