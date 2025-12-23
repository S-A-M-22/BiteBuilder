import React from "react";
import ProductCard from "@/components/Product/ProductCard";
import EmptyState from "@/components/Product/EmptyState";
import type { Product } from "@/schema/zodSchema";
import { EfficiencyProvider } from "@/context/EfficiencyContext";
import EfficiencyToolbar from "../Product/EfficiencyToolbar";

type ScoredProduct = Partial<Product> & { __score?: number; __saved?: boolean };
type Props = {
  products: ScoredProduct[];
  initLoaded: boolean;
  onToggleSave: (p: Partial<Product>) => Promise<void> | void;
  onDetails: (p: ScoredProduct) => Promise<void> | void;
};

export default function ProductGrid({ products, initLoaded, onToggleSave, onDetails }: Props) {
  if (products.length === 0 && initLoaded) {
    return <EmptyState title="No products yet" subtitle="Search for items or save from results." />;
  }

  return (
    <EfficiencyProvider>
  <EfficiencyToolbar />
  <main className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
    {products.map(p => (
      <ProductCard
        key={p.barcode ?? String(p.id)}
        product={p}
        saved={!!p.__saved}
        onToggleSave={onToggleSave}
        onDetails={onDetails}
      />
    ))}
  </main>
</EfficiencyProvider>

  );
}
