// src/pages/LoginPage.tsx
import NavbarAltPage from "@/components/LandingPageComponents/NavbarAltPage";
import Footer from "@/components/DashBoard/Footer";
import LoginMsg from "@/components/RegisterLoginPageComponents/LoginMsg";
import LoginForm from "@/components/RegisterLoginPageComponents/LoginForm";
import { useUser } from "@/context/UserSessionProvider";
import { useState, ChangeEvent, FormEvent, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useUserSession } from "@/hooks/userSession";

type LoginFormState = {
  username: string;
  password: string;
  remember: boolean;
};

const LoginPage = () => {
  const navigate = useNavigate();
  // const { user, loading, handleLogin, handleOTP } = useUser();
  const { handleLogin, handleOTP, reload } = useUser();
  const { user, loading } = useUserSession();
  const [submitting, setSubmitting] = useState(false);
  const [verifying, setVerifying] = useState(false);

  // redirect if already logged in
  useEffect(() => {
    if (!loading && user) navigate("/app/dashboard");
  }, [loading, user, navigate]);

  // form + errors
  const [form, setForm] = useState<LoginFormState>({
    username: "",
    password: "",
    remember: false,
  });
  const [error, setError] = useState<string | null>(null);

  // OTP modal state
  const [showOtp, setShowOtp] = useState(false);
  const [otpEmail, setOtpEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpError, setOtpError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // STEP 1: start login -> server sends OTP and sets a pending session
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const res = await handleLogin(
        form.username,
        form.password,
        form.remember,
      );
      if (res.success) {
        setOtpEmail(res.email);
        setShowOtp(true);
        setOtpCode("");
        setOtpError(null);
        return; // wait for OTP verification
      } else {
        throw new Error("Login failed!");
      }
    } catch (err) {
      console.error("Login failed:", err);
      setError("Invalid email, username or password.");
    } finally {
      setSubmitting(false);
    }
  };

  // STEP 2: verify OTP -> backend flips otp_verified=true
  const onVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setOtpError(null);
    setVerifying(true);
    try {
      const res = await handleOTP(otpCode);
      if (res) {
        setShowOtp(false);
        reload();
        navigate("/app/dashboard/");
      } else {
        throw new Error("OTP failed!");
      }
    } catch (err: any) {
      setOtpError("Invalid or expired code");
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 via-white to-white text-slate-800">
      <NavbarAltPage />

      <main className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <section className="relative mt-14 grid grid-cols-1 items-center gap-10 lg:grid-cols-2">
          <LoginMsg />

          <LoginForm
            form={form}
            error={error}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
          />
        </section>
      </main>

      <Footer />

      {/* OTP Modal */}
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
                className="rounded-lg bg-emerald-700 px-4 py-2 text-white hover:bg-emerald-600"
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
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-700 border-t-transparent"></div>
            <p className="text-slate-700 font-medium text-sm">
              {submitting ? "Sending login request..." : "Verifying OTP..."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginPage;
