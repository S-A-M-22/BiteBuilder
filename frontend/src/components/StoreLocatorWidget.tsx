import { useState } from "react";
import apiClient from "@/lib/apiClient";
import { Store } from "@/types";

export default function StoreLocatorWidget({
  onSelect,
}: {
  onSelect?: (store: Store) => void;
}) {
  const [postcode, setPostcode] = useState("");
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    setError("");
    if (!postcode.trim()) {
      setError("Please enter a valid postcode.");
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.get("/stores/nearby/", {
        params: { postcode },
      });
      setStores(res.data);
      if (res.data.length === 0) setError("No Supermarkets found nearby.");
    } catch (err) {
      console.error(err);
      setError("Failed to fetch store data.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm space-y-3">
      <h3 className="font-semibold text-lg">Find Your Nearest SuperMarket</h3>

      {/* Input + Button */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Enter postcode (e.g. 2168)"
          value={postcode}
          onChange={(e) => setPostcode(e.target.value)}
          className="flex-1 border rounded-md px-3 py-1 text-sm"
          maxLength={12}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-green-600 text-white rounded-md px-3 py-1 text-sm hover:bg-green-700 transition"
        >
          {loading ? "Searching..." : "Find Stores"}
        </button>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* Store List */}
      <ul className="divide-y divide-gray-100">
        {stores.map((s) => (
          <li
            key={s.id}
            onClick={() => onSelect?.(s)}
            className="cursor-pointer p-2 hover:bg-gray-50 rounded-md transition"
          >
            <div className="font-medium">{s.name}</div>
            <div className="text-sm text-gray-600">
              {s.address}, {s.suburb} {s.state} {s.postcode}
            </div>
            {s.today_hours && (
              <div className="text-xs text-gray-500">🕒 {s.today_hours}</div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
