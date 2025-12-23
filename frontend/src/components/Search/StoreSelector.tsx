// src/components/Search/StoreSelector.tsx
import React from "react";
import StoreLocatorWidget from "@/components/StoreLocatorWidget";

type Props = {
  store: any | null;
  onSelect: (s: any | null) => void;
};

export default function StoreSelector({ store, onSelect }: Props) {
  return (
    <section className="mt-4">
      <StoreLocatorWidget onSelect={onSelect} />
      {store && (
        <p className="mt-2 text-xs text-gray-700">
          Selected: <span className="font-medium">{store.name}</span>
          {store.distance ? ` (${store.distance} km)` : ""}
        </p>
      )}
    </section>
  );
}
