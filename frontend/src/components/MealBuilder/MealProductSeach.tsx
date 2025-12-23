import React from "react";
import useProductSearch from "@/hooks/useProductSearch";
import SearchControls from "@/components/Search/SearchControls";
import ProductGrid from "@/components/Search/ProductGrid";
import ProductDetailsModal from "../Product/ProductDetailModal";

type Props = {
  onAddProduct: (product: any) => void; // receives selected product
};

export default function MealProductSearch({ onAddProduct }: Props) {
  const {
    visible,
    initLoaded,
    lastQuery,
    selected,
    loading,
    error,
    sortKey,
    setSortKey,
    handleSearch,
    handleToggleSave,
    handleDetails,
    setSelected,
  } = useProductSearch();

  return (
    <section className="space-y-4">
      <header>
        <h2 className="text-lg font-medium">Search Products</h2>
        <p className="text-sm text-gray-600">Find items to add to your current meal.</p>
      </header>

      <SearchControls
        lastQuery={lastQuery}
        onSearch={handleSearch}
        sortKey={sortKey}
        onChangeSort={(k) => setSortKey(k)}
        count={visible.length}
        loading={loading}
        error={error}
      />

      <ProductGrid
        products={visible}
        initLoaded={initLoaded}
        onToggleSave={(p) => onAddProduct(p)}
        onDetails={handleDetails}
      />

      <ProductDetailsModal
        open={!!selected}
        product={selected ?? undefined}
        onClose={() => setSelected(null)}
      />
    </section>
  );
}
