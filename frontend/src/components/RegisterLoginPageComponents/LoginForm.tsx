import React, { ChangeEvent, FormEvent } from "react";
import { Link } from "react-router-dom";

interface LoginForm {
  username: string;
  password: string;
  remember: boolean;
}

interface LoginFormCompProps {
  form: LoginForm;
  error: string | null;
  handleChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

const LoginFormComp: React.FC<LoginFormCompProps> = ({
  form,
  error,
  handleChange,
  handleSubmit,
}) => {
  return (
    <div className="order-1 lg:order-2">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white/90 shadow-xl ring-1 ring-black/5 backdrop-blur">
        <div className="p-6 sm:p-8">
          <h2 className="text-center text-xl font-semibold tracking-tight">
            Log in
          </h2>

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            {/* Username */}
            <div>
              <label
                htmlFor="username"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Email or Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={form.username}
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                placeholder="you@bitebuilder.app"
                maxLength={1000}
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-slate-700"
                >
                  Password
                </label>
                <Link
                  to="/reset"
                  className="text-sm text-emerald-700 hover:text-emerald-800"
                >
                  Forgot?
                </Link>
              </div>
              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                placeholder="••••••••"
                maxLength={1000}
              />
            </div>

            {/* Remember me + register */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 select-none text-sm text-slate-700">
                <input
                  type="checkbox"
                  name="remember"
                  checked={form.remember}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-slate-300 text-emerald-700 focus:ring-emerald-500"
                />
                <span>Remember me</span>
              </label>
              <Link
                to="/register"
                className="text-sm text-slate-600 hover:text-slate-900"
              >
                New here?{" "}
                <span className="underline underline-offset-4">
                  Create an account
                </span>
              </Link>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-emerald-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5">
                <path
                  fill="currentColor"
                  d="M12 4l8 8-8 8-1.41-1.41L16.17 13H4v-2h12.17l-5.58-5.59L12 4z"
                />
              </svg>
              Log in
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginFormComp;
