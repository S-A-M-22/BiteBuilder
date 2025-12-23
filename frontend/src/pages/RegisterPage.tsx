// src/pages/RegisterPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { userAuth } from "@/services/user_auth";
import useRevealOnScroll from "@/hooks/useRevealOnScroll";
import NavbarAltPage from "@/components/LandingPageComponents/NavbarAltPage";
import Footer from "@/components/DashBoard/Footer";
import RegisterMsg from "@/components/RegisterLoginPageComponents/RegisterMsg";
import RegisterForm from "@/components/RegisterLoginPageComponents/RegisterForm";

/* ==========================
   ZOD FORM SCHEMA
========================== */
const RegisterFormSchema = z
  .object({
    username: z
      .string()
      .max(32, "Username must be at most 32 characters")
      .refine((val) => !val.includes("@"), {
        message: "Username cannot contain '@'",
      }),
    email: z.string().email("Invalid email"),
    password: z
      .string()
      .min(9, "Password must be at least 9 characters long")
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{9,}$/,
        "Password must include at least one uppercase letter, one lowercase letter, and one number",
      ),
    checkPassword: z.string(),
    agree: z.boolean().refine((v) => v === true, {
      message: "You must agree to the terms and privacy policy",
    }),
  })
  .refine((data) => data.password === data.checkPassword, {
    message: "Passwords do not match",
    path: ["checkPassword"],
  });

type RegisterFormData = z.infer<typeof RegisterFormSchema>;

/* ==========================
   COMPONENT
========================== */
export default function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<RegisterFormData>({
    username: "",
    email: "",
    password: "",
    checkPassword: "",
    agree: false,
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showVerificationPopup, setShowVerificationPopup] = useState(false);

  useRevealOnScroll();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, type, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSubmitting(true);

    const result = RegisterFormSchema.safeParse(formData);
    if (!result.success) {
      const first = result.error.issues[0];
      setError(first?.message || "Please check the input fields.");
      setSubmitting(false);
      return;
    }

    try {
      const { username, email, password } = result.data;
      const user = await userAuth.registerUser(username, email, password);

      if (!user) throw new Error("No user returned from backend");

      setSuccess(true);
      setShowVerificationPopup(true); // 🔔 show popup
    } catch (err: any) {
      console.error("Registration failed:", err);
      setError(err?.data?.error || "Failed to register. Please try again later.");
    } finally {
      setSubmitting(false);
    }
  };

  /* ==========================
     UI
  ========================== */
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 via-white to-white text-slate-800">
      <NavbarAltPage />

      <main className="relative mx-auto max-w-7xl py-8 px-4 sm:px-6 lg:px-8">
        <section className="mt-14 grid grid-cols-1 lg:grid-cols-2 items-center gap-10">
          <RegisterMsg />
          <RegisterForm
            form={formData}
            error={error}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
            success={success}
          />
        </section>
      </main>

      <Footer />

      {/* 🔥 GLOBAL LOADING OVERLAY 🔥 */}
      {submitting && (
        <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-xl">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-700 border-t-transparent"></div>
            <p className="text-slate-700 font-medium text-sm">Checking...</p>
          </div>
        </div>
      )}

      {/* ✅ EMAIL VERIFICATION POPUP ✅ */}
      {showVerificationPopup && (
        <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 text-center max-w-sm mx-auto">
            <h2 className="text-lg font-semibold text-emerald-700 mb-3">
              Please check your email
            </h2>
            <p className="text-sm text-slate-600 mb-6">
              We’ve sent a verification link to <br />
              <span className="font-medium">{formData.email}</span>. <br />
              Please verify your email before logging in.
            </p>
            <button
              onClick={() => {
                setShowVerificationPopup(false);
                navigate("/");
              }}
              className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
            >
              Go to Home
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
