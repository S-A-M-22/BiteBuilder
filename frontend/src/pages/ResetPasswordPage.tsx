// src/pages/ResetPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { useUser } from "@/context/UserSessionProvider";
import useRevealOnScroll from "@/hooks/useRevealOnScroll";
import NavbarAltPage from "@/components/LandingPageComponents/NavbarAltPage";
import Footer from "@/components/LandingPageComponents/Footer";
import ResetMsg from "@/components/RegisterLoginPageComponents/ResetMsg";
import ResetForm from "@/components/RegisterLoginPageComponents/ResetForm";

/* ==========================
   ZOD FORM SCHEMA
========================== */
const ResetFormSchema = z
  .object({
    email: z.string().email("Invalid email"),
    password: z
      .string()
      .min(9, "Password must be at least 9 characters long")
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{9,}$/,
        "Password must include at least one uppercase letter, one lowercase letter, and one number",
      ),
    checkPassword: z.string(),
  })
  .refine((data) => data.password === data.checkPassword, {
    message: "Passwords do not match",
    path: ["checkPassword"],
  });

type ResetFormData = z.infer<typeof ResetFormSchema>;

/* ==========================
   COMPONENT
========================== */
export default function ResetPage() {
  const navigate = useNavigate();
  const { handleReset, handleResetOTP } = useUser(); // ⬅️ from the same context as Login

  const [formData, setFormData] = useState<ResetFormData>({
    email: "",
    password: "",
    checkPassword: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // loading states
  const [submitting, setSubmitting] = useState(false);
  const [verifying, setVerifying] = useState(false);

  // OTP modal state
  const [showOtp, setShowOtp] = useState(false);
  const [otpEmail, setOtpEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpError, setOtpError] = useState<string | null>(null);

  useRevealOnScroll();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, type, value, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // STEP 1: start reset (send code) – mirrors LoginPage.handleSubmit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSubmitting(true);

    const parsed = ResetFormSchema.safeParse(formData);
    if (!parsed.success) {
      const first = parsed.error.issues[0];
      setError(first?.message || "Please check the input fields.");
      setSubmitting(false);
      return;
    }

    try {
      const { email, password, checkPassword } = parsed.data;

      // Expected: { success: true, email?: string } on success
      const res = await handleReset(email, password);

      if (res?.success === false) {
        throw new Error("Invalid email.");
      }

      setOtpEmail(res?.email || email);
      setShowOtp(true);
      setOtpCode("");
      setOtpError(null);
    } catch (err: any) {
      console.error("Reset start failed:", err);
      setError(
        err?.message ||
          err?.data?.error ||
          "Failed to start reset. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  // STEP 2: verify OTP -> finalize reset – mirrors LoginPage.onVerifyOtp
  const onVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setOtpError(null);

    if (otpCode.length !== 6) {
      setOtpError("Please enter the 6-digit code.");
      return;
    }

    setVerifying(true);
    try {
      // Expected: { success: true }
      const res = await handleResetOTP(otpCode);
      if (res === false) {
        throw new Error("Invalid or expired code.");
      }

      setShowOtp(false);
      setSuccess(true);
      navigate("/login");
    } catch (err: any) {
      setOtpError(err?.message || "Invalid or expired code");
    } finally {
      setVerifying(false);
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
          <ResetMsg />
          <ResetForm
            form={formData}
            error={error}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
            success={success}
          />
        </section>
      </main>

      <Footer />

      {/* OTP Modal (same style as LoginPage) */}
      {showOtp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <form
            onSubmit={onVerifyOtp}
            className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl"
          >
            <h3 className="mb-2 text-xl font-semibold">
              Enter verification code
            </h3>
            <p className="mb-4 text-sm text-slate-600">
              We sent a 6-digit code to <b>{otpEmail}</b>. Please enter it
              below.
            </p>

            <input
              className="mb-2 w-full rounded-lg border p-3"
              value={otpCode}
              onChange={(e) =>
                setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              placeholder="6-digit code"
              inputMode="numeric"
              maxLength={6}
              autoFocus
              required
            />

            {otpError && (
              <div className="mb-2 text-sm text-red-600">{otpError}</div>
            )}

            <div className="mt-2 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowOtp(false)}
                className="rounded-lg border px-4 py-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
              >
                Confirm
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 🔥 GLOBAL LOADING OVERLAY 🔥 */}
      {(submitting || verifying) && (
        <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-xl">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent"></div>
            <p className="text-slate-700 font-medium text-sm">
              {submitting ? "Sending code..." : "Verifying OTP..."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
