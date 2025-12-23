// src/components/RegisterLoginPageComponents/RegisterForm.tsx
import React, { ChangeEvent, FormEvent, useState } from "react";
import { Link } from "react-router-dom";

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  checkPassword: string;
  agree: boolean;
}

interface RegisterFormCompProps {
  form: RegisterForm;
  error: string | null;
  handleChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
  success?: boolean;
}

const RegisterFormComp: React.FC<RegisterFormCompProps> = ({
  form,
  error,
  handleChange,
  handleSubmit,
  success,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showCheckPassword, setShowCheckPassword] = useState(false);

  return (
    <div className="order-1 lg:order-2">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white/90 shadow-xl ring-1 ring-black/5 backdrop-blur">
        <div className="p-6 sm:p-8">
          <h2 className="text-center text-xl font-semibold tracking-tight">
            Sign up
          </h2>

          {error && (
            <p className="text-sm text-red-600 text-center mt-2">{error}</p>
          )}
          {success && (
            <p className="text-sm text-green-700 text-center mt-2">
              Registration successful! Redirecting...
            </p>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {/* Username */}
            <div>
              <label
                htmlFor="username"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={form.username}
                onChange={handleChange}
                required
                placeholder="Your username"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                maxLength={1000}
              />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                maxLength={1000}
              />
            </div>

            {/* Password */}
            <div className="relative">
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={handleChange}
                required
                placeholder="••••••••"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 pr-12 text-slate-900 shadow-sm outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                maxLength={1000}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-[38px] text-xs text-slate-500 hover:text-slate-800"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>

            {/* Confirm Password */}
            <div className="relative">
              <label
                htmlFor="checkPassword"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Confirm Password
              </label>
              <input
                id="checkPassword"
                name="checkPassword"
                type={showCheckPassword ? "text" : "password"}
                value={form.checkPassword}
                onChange={handleChange}
                required
                placeholder="••••••••"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 pr-12 text-slate-900 shadow-sm outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                maxLength={1000}
              />
              <button
                type="button"
                onClick={() => setShowCheckPassword((v) => !v)}
                className="absolute right-3 top-[38px] text-xs text-slate-500 hover:text-slate-800"
              >
                {showCheckPassword ? "Hide" : "Show"}
              </button>
            </div>

            {/* Terms and Agreement */}
            <div className="flex items-center gap-2 select-none text-sm text-slate-700">
              <input
                type="checkbox"
                name="agree"
                checked={form.agree}
                onChange={handleChange}
                className="h-4 w-4 rounded border-slate-300 text-emerald-700 focus:ring-emerald-500"
                required
              />
              <span>
                I agree to the{" "}
                <a href="#" className="underline underline-offset-4">
                  Terms
                </a>{" "}
                &{" "}
                <a href="#" className="underline underline-offset-4">
                  Privacy Policy
                </a>
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="mt-2 w-full rounded-xl bg-emerald-700 px-4 py-3 text-sm font-semibold text-white shadow-md hover:bg-emerald-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              Sign up
            </button>

            {/* Redirect to Login */}
            <div className="pt-2 text-center text-sm">
              <Link
                to="/"
                className="text-slate-600 hover:text-slate-900 underline underline-offset-4"
              >
                Already have an account? Click here
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterFormComp;
