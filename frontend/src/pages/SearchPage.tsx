import React, { useState } from "react";
import useProductSearch from "@/hooks/useProductSearch";
import SearchControls from "@/components/Search/SearchControls";
import ProductGrid from "@/components/Search/ProductGrid";

import StoreSelector from "@/components/Search/StoreSelector";
import { CheckCircle } from "lucide-react";
import ProductDetailsModal from "@/components/Product/ProductDetailModal";

export default function SearchPage() {
  const {
    saved,
    visible,
    initLoaded,
    lastQuery,
    selected,
    loading,
    loadingMore,
    error,
    sortKey,
    setSortKey,
    store,
    nextCursor,

    setStore,
    handleSearch,
    handleLoadMore,
    handleToggleSave,
    handleDetails,
    setSelected,
  } = useProductSearch();

  const [savedNotice, setSavedNotice] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(true);

  // --- Wrap save handler to show toast ---
  const handleSaveWithNotice = async (product: any) => {
    await handleToggleSave(product);
    setSavedNotice(`Saved “${product.name ?? product.title ?? "item"}”!`);
    setTimeout(() => setSavedNotice(null), 2000);
  };

  // --- Wrap search handler to reset view ---
  const handleSearchWithReset = async (query: string) => {
    setShowAll(false);
    await handleSearch(query);
  };

  const savedSet = new Set(saved.map((s) => s.barcode ?? s.id));

  // If showAll = true, show everything; else filter saved out
  const newResults = showAll
    ? visible
    : visible.filter((p) => !savedSet.has(p.barcode ?? p.id));

  const savedItems = visible.filter((p) => savedSet.has(p.barcode ?? p.id));

  return (
    <div className="mx-auto max-w-6xl p-6 space-y-6">
      {/* Header */}
      <header>
        <h1 className="text-2xl font-semibold">Product Search</h1>
        <p className="text-sm text-gray-600">
          Browse products, view nutrition, and save favourites for later.
        </p>
      </header>

      {/* Saved Notification */}
      {savedNotice && (
        <div className="flex items-center gap-2 text-sm bg-green-50 text-green-700 border border-green-200 rounded-lg px-3 py-2 animate-fade-in">
          <CheckCircle className="w-4 h-4" />
          {savedNotice}
        </div>
      )}

      {/* Search Controls */}
      <SearchControls
        lastQuery={lastQuery}
        onSearch={handleSearchWithReset}
        sortKey={sortKey}
        onChangeSort={(k) => setSortKey(k)}
        count={visible.length}
        loading={loading}
        error={error}
        store={store}
      />

      {/* Optional Toggle */}
      {saved.length > 0 && (
        <div className="text-sm text-gray-600 flex justify-end">
          <button
            onClick={() => setShowAll((s) => !s)}
            className="text-blue-600 hover:underline"
          >
            {showAll ? "Hide saved in results" : "Show saved in results"}
          </button>
        </div>
      )}

      {/* Search Results */}
      <section className="space-y-3">
        {visible.length > 0 && (
          <h2 className="text-lg font-medium text-gray-800 flex items-center gap-2">
            Search Results
          </h2>
        )}
        <ProductGrid
          products={newResults}
          initLoaded={initLoaded}
          onToggleSave={handleSaveWithNotice}
          onDetails={handleDetails}
        />
      </section>

      {/* Saved Products */}
      {savedItems.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-medium text-gray-800 flex items-center gap-2">
            Saved Products
          </h2>
          <ProductGrid
            products={savedItems}
            initLoaded={initLoaded}
            onToggleSave={handleSaveWithNotice}
            onDetails={handleDetails}
          />
        </section>
      )}

      {/* Load more */}
      <div className="flex justify-center mt-4">
        {loadingMore ? (
          <div className="rounded-xl border p-3 text-sm">Loading more…</div>
        ) : nextCursor ? (
          <button
            onClick={handleLoadMore}
            className="rounded bg-slate-700 px-4 py-2 text-white hover:bg-slate-800"
          >
            Load more results
          </button>
        ) : null}
      </div>

      {/* Modals */}
      <ProductDetailsModal
        open={!!selected}
        product={selected ?? undefined}
        onClose={() => setSelected(null)}
      />

      <StoreSelector store={store} onSelect={setStore} />
    </div>
  );
}
