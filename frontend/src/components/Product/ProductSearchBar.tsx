import { useEffect, useRef, useState } from "react";

export default function ProductSearchBar({
  onSearch,
  placeholder = "Search products (e.g., chicken breast)…",
}: {
  onSearch: (q: string) => void;
  placeholder?: string;
}) {
  const [q, setQ] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="flex w-full items-center gap-2">
      <label htmlFor="product-search" className="sr-only">
        Product search
      </label>
      <input
        ref={inputRef}
        id="product-search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSearch(q)}
        placeholder={placeholder}
        className="w-full rounded-2xl border px-4 py-3 outline-none ring-0 focus:border-gray-400"
        aria-label="Search products"
        maxLength={1000}
      />
      <button
        type="button"
        onClick={() => onSearch(q)}
        className="rounded-2xl border px-4 py-3 text-sm hover:bg-gray-50"
        aria-label="Run search"
      >
        Search
      </button>
    </div>
  );
}
