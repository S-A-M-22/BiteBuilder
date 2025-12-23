// src/components/Search/SearchControls.tsx
import React from "react";
import ProductSearchBar from "@/components/Product/ProductSearchBar";
import ProductToolbar, { SortKey } from "@/components/Product/ProductToolBar";

type Props = {
  lastQuery: string;
  onSearch: (q: string) => void;
  sortKey: SortKey;
  onChangeSort: (k: SortKey) => void;
  count: number;
  loading: boolean;
  error?: string | null;
  store?: any | null;
};

export default function SearchControls({
  lastQuery,
  onSearch,
  sortKey,
  onChangeSort,
  count,
  loading,
  error,
  store,
}: Props) {
  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <ProductSearchBar onSearch={onSearch} />
        {store ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700 border border-green-200">
            🏬 {store.name} • {store.suburb}, {store.state}
          </span>
        ) : (
          <span className="text-xs text-gray-500 italic">No store selected</span>
        )}
      </div>

      <ProductToolbar sort={sortKey} onChangeSort={onChangeSort} count={count} />

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {loading && <div className="rounded-xl border p-3 text-sm">Loading…</div>}
    </div>
  );
}
