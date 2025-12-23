// src/pages/ProfilePage.tsx
import { useUserSession } from "@/hooks/userSession";
import { useNavigate } from "react-router-dom";
import { useEffect, useMemo, useRef, useState } from "react";
import { Profile, GenderType, profileService } from "@/services/profile_service"

function bmiFor(h?: number | null, w?: number | null) {
  if (!h || !w || h <= 0 || w <= 0) return null;
  const m = h / 100;
  return w / (m * m);
}

function bmiLabel(bmi: number | null) {
  if (bmi == null) return "—";
  if (bmi < 18.5) return "Underweight";
  if (bmi < 25) return "Normal";
  if (bmi < 30) return "Overweight";
  return "Obese";
}

const pretty = (n: number | null | undefined, d = 1) =>
  n == null ? "—" : n.toFixed(d);

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, loading } = useUserSession();

  const [initializing, setInitializing] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [p, setP] = useState<Profile | null>(null);

  const fileRef = useRef<HTMLInputElement | null>(null);

  // kick unauthenticated users back to login
  useEffect(() => {
    if (!loading && !user) navigate("/login");
  }, [loading, user, navigate]);

  // load profile on mount
  useEffect(() => {
    (async () => {
      try {
        const prof = await profileService.fetchProfile();
        setP(prof);
      } catch (e: any) {
        setError(e?.message || "Failed to load profile");
      } finally {
        setInitializing(false);
      }
    })();
  }, []);

  const bmi = useMemo(
    () => bmiFor(p?.height_cm, p?.weight_kg),
    [p?.height_cm, p?.weight_kg],
  );

  const handleChange = (name: keyof Profile, value: any) => {
    if (!p) return;
    setP({ ...p, [name]: value });
  };

  const validate = (): string | null => {
    if (!p) return null;
    if (p.age != null && (p.age < 13 || p.age > 120)) return "Age must be 13-120";
    if (p.height_cm != null && (p.height_cm < 80 || p.height_cm > 250)) return "Height looks off (80-250 cm)";
    if (p.weight_kg != null && (p.weight_kg < 20 || p.weight_kg > 350)) return "Weight looks off (20-350 kg)";
    return null;
  };

  const onSave = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!p) return;
    const v = validate();
    if (v) {
      setError(v);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await profileService.updateProfile({
        username: p.username ?? null,
        age: p.age ?? null,
        gender: p.gender ?? null,
        height_cm: p.height_cm ?? null,
        weight_kg: p.weight_kg ?? null,
        postcode: p.postcode ?? null,
      });
      setEditing(false);
    } catch (e: any) {
      setError(e?.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const initials = () => {
    const base = p?.username || p?.email || "?";
    return base.slice(0, 2).toUpperCase();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 via-white to-white text-slate-800">
      <main className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <section className="relative mt-14 grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
          <div className="space-y-6">
            <h1 className="text-3xl font-bold leading-tight sm:text-4xl">
              Your Profile
            </h1>
            <p className="max-w-prose text-slate-600">
              Manage your account details stored in Supabase. Update your age,
              gender, height, weight, and postcode — we calculate your BMI
              automatically.
            </p>
            <ul className="grid grid-cols-1 gap-2 text-sm text-slate-600">
              <li>• Email is managed by authentication</li>
              <li>• Changes are saved securely</li>
              <li>
                • You can reset your password in the login page by verifing your
                email address
              </li>
              <li>
                • If you need any help, please contact us: wenmirenxin@gmail.com
              </li>
            </ul>
          </div>

          {/* Right: Profile Card */}
          <form
            onSubmit={onSave}
            className="rounded-2xl bg-white p-6 shadow-xl"
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Account details</h2>
              {!editing ? (
                <button
                  type="button"
                  onClick={() => setEditing(true)}
                  className="rounded-lg border px-4 py-2 text-sm hover:bg-slate-50"
                >
                  Edit
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="rounded-lg border px-4 py-2 text-sm"
                    onClick={() => setEditing(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                  >
                    Save
                  </button>
                </div>
              )}
            </div>

            {/* Error banner */}
            {error && (
              <div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Header row: avatar + summary */}
            <div className="mb-6 flex items-center gap-4">
              <div className="h-16 w-16 overflow-hidden rounded-full bg-slate-100 grid place-items-center text-slate-500">
                {p?.avatar ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={p.avatar} alt="avatar" className="h-full w-full object-cover" />
                ) : (
                  <span className="text-sm font-semibold">{initials()}</span>
                )}
              </div>
              <div className="space-y-1">
                <div className="font-medium">{p?.username || "—"}</div>
                <div className="text-sm text-slate-600">{p?.email || "—"}</div>
              </div>
            </div>

            {/* Form grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">

              <div>
                <label className="mb-1 block text-sm font-medium" htmlFor="age">
                  Age
                </label>
                <input
                  id="age"
                  type="number"
                  min={6}
                  max={150}
                  value={p?.age ?? ""}
                  onChange={(e) =>
                    handleChange(
                      "age",
                      e.target.value ? Number(e.target.value) : null,
                    )
                  }
                  disabled={!editing}
                  className="w-full rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-50"
                />
              </div>

              <div>
                <label
                  className="mb-1 block text-sm font-medium"
                  htmlFor="gender"
                >
                  Gender
                </label>
                <select
                  id="gender"
                  value={p?.gender ?? ""}
                  onChange={(e) =>
                    handleChange("gender", e.target.value as GenderType)
                  }
                  disabled={!editing}
                  className="w-full rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-50"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label
                  className="mb-1 block text-sm font-medium"
                  htmlFor="height"
                >
                  Height (cm)
                </label>
                <input
                  id="height"
                  type="number"
                  min={40}
                  max={400}
                  value={p?.height_cm ?? ""}
                  onChange={(e) =>
                    handleChange(
                      "height_cm",
                      e.target.value ? Number(e.target.value) : null,
                    )
                  }
                  disabled={!editing}
                  className="w-full rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-50"
                />
              </div>

              <div>
                <label
                  className="mb-1 block text-sm font-medium"
                  htmlFor="weight"
                >
                  Weight (kg)
                </label>
                <input
                  id="weight"
                  type="number"
                  step="0.1"
                  min={1}
                  max={1000000}
                  value={p?.weight_kg ?? ""}
                  onChange={(e) =>
                    handleChange(
                      "weight_kg",
                      e.target.value ? Number(e.target.value) : null,
                    )
                  }
                  disabled={!editing}
                  className="w-full rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-50"
                />
              </div>

              <div className="sm:col-span-2">
                <label
                  className="mb-1 block text-sm font-medium"
                  htmlFor="postcode"
                >
                  Postcode
                </label>
                <input
                  id="postcode"
                  value={p?.postcode ?? ""}
                  onChange={(e) => handleChange("postcode", e.target.value)}
                  disabled={!editing}
                  maxLength={16}
                  placeholder="e.g. 2006"
                  className="w-full rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-50"
                />
              </div>
            </div>

            {/* Metrics */}
            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border p-4 text-center">
                <div className="text-xs text-slate-500">BMI</div>
                <div className="mt-1 text-2xl font-semibold">
                  {pretty(bmi, 1)}
                </div>
                <div className="text-xs text-slate-500">{bmiLabel(bmi)}</div>
              </div>
              <div className="rounded-2xl border p-4 text-center">
                <div className="text-xs text-slate-500">Height</div>
                <div className="mt-1 text-2xl font-semibold">
                  {p?.height_cm ? `${p.height_cm} cm` : "—"}
                </div>
              </div>
              <div className="rounded-2xl border p-4 text-center">
                <div className="text-xs text-slate-500">Weight</div>
                <div className="mt-1 text-2xl font-semibold">
                  {p?.weight_kg ? `${pretty(p.weight_kg)} kg` : "—"}
                </div>
              </div>
            </div>
          </form>
        </section>
      </main>

      {/* Global loading/overlay, matching your LoginPage style */}
      {(initializing || saving) && (
        <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-xl">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
            <p className="text-sm font-medium text-slate-700">
              {initializing ? "Loading profile…" : "Saving changes…"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
