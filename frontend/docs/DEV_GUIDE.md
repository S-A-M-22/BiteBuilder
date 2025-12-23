# BiteBuilder Frontend Development Guide

## 1. Project Structure

```
src/
  pages/          - Each file = a full page (route)
  components/     - Reusable UI parts (Navbar, Footer, Menubar, etc.)
  services/       - API functions using apiClient
  schema/         - Zod schemas for validation
  hooks/          - Reusable logic (session, scroll)
  router/         - Public and Private routes
  lib/            - Shared libraries (apiClient)
  types/          - Types inferred from Zod
```

---

## 2. Creating a New Page

**File:** `src/pages/<PageName>.tsx`

### Example

```tsx
import { useEffect, useState } from "react";
import Menubar from "@/components/Menubar";
import Footer from "@/components/LandingPageComponents/Footer";
import { profileService } from "@/services/profileService";
import { Profile } from "@/types";

export default function ProfilePage() {
  // 1. State
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 2. Fetch data
  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await profileService.getProfile();
        setProfile(data);
      } catch {
        setError("Failed to load profile");
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  // 3. Render
  if (loading) return <div className="p-10 text-gray-500">Loading...</div>;
  if (error) return <div className="p-10 text-red-600">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Menubar />
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <section className="bg-white rounded-2xl p-6 shadow border border-gray-200">
          <h1 className="text-3xl font-bold mb-2">Your Profile</h1>
          <p className="text-gray-600">Welcome back, {profile?.username}</p>
        </section>
      </main>
      <Footer />
    </div>
  );
}
```

### Rules

- Use Tailwind only. No `.css` imports.
- Consistent layout: `min-h-screen`, `max-w-7xl`, `px-6 py-10`.
- One top-level `div` → `Menubar`, `main`, `Footer`.

---

## 3. Adding a Route

**Files:**

- `src/router/PublicRoutes.tsx` → non-auth pages
- `src/router/PrivateRoutes.tsx` → login-protected pages

**Example**

```tsx
import ProfilePage from "@/pages/ProfilePage";

<Route path="/profile" element={<ProfilePage />} />;
```

---

## 4. Creating a Service Function

**File:** `src/services/<name>Service.ts`

```ts
import apiClient from "@/lib/apiClient";
import { Profile } from "@/types";

export const profileService = {
  async getProfile(): Promise<Profile> {
    const { data } = await apiClient.get("/profile/");
    return data;
  },

  async updateProfile(payload: Partial<Profile>) {
    const { data } = await apiClient.put("/profile/", payload);
    return data;
  },
};
```

### Rules

- Use `apiClient` (already configured with interceptors).
- Return typed data.
- Handle errors in the page, not in the service.
- Keep one service file per resource (`goalService`, `userService`, etc.).

---

## 5. Validation with Zod

**File:** `src/schema/zodSchema.ts`

```ts
import { z } from "zod";

export const ExampleSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
});

export type Example = z.infer<typeof ExampleSchema>;
```

Use `.safeParse()` before submitting user input:

```ts
const result = ExampleSchema.safeParse(formData);
if (!result.success) return alert("Invalid data");
```

---

## 6. Styling Rules

All styles must use Tailwind.

**Example**

```tsx
<button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl">
  Save
</button>
```

**Avoid**

```tsx
import "./Profile.css";
```

---

## 7. Standard Workflow

1. Create new page in `src/pages/`
2. Add route in `PublicRoutes` or `PrivateRoutes`
3. Create service in `src/services/`
4. Add or reuse a Zod schema
5. Style everything using Tailwind
6. Keep layout consistent with other pages

---

## 8. Quick Template

```tsx
import { useState, useEffect } from "react";
import Menubar from "@/components/Menubar";
import Footer from "@/components/LandingPageComponents/Footer";
import { exampleService } from "@/services/exampleService";

export default function ExamplePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    exampleService
      .getAll()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <Menubar />
      <main className="max-w-7xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold mb-4">Example Page</h1>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </main>
      <Footer />
    </div>
  );
}
```
