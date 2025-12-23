// src/components/RegisterLoginPageComponents/ResetForm.tsx
import { ChangeEvent, FormEvent } from "react";
import { Link } from "react-router-dom";

export interface ResetForm {
  email: string;
  password: string;
  checkPassword: string;
}

interface ResetFormCompProps {
  form: ResetForm;
  error: string | null;
  handleChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
  success?: boolean;
}

const ResetFormComp: React.FC<ResetFormCompProps> = ({
  form,
  error,
  handleChange,
  handleSubmit,
  success,
}) => {
  return (
    <div className="order-1 lg:order-2">
      <div className="mx-auto w-full max-w-md rounded-2xl bg-white/90 shadow-xl ring-1 ring-black/5 backdrop-blur">
        <div className="p-6 sm:p-8">
          <h2 className="text-center text-xl font-semibold tracking-tight">
            Reset Password
          </h2>

          {error && (
            <p className="text-sm text-red-600 text-center mt-2">{error}</p>
          )}
          {success && (
            <p className="text-sm text-green-600 text-center mt-2">
              Reset successful! Redirecting...
            </p>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {["email", "password", "checkPassword"].map((key) => (
              <div key={key}>
                <label
                  htmlFor={key}
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  {key === "checkPassword"
                    ? "Confirm Password"
                    : key.charAt(0).toUpperCase() + key.slice(1)}
                </label>
                <input
                  id={key}
                  name={key}
                  type={
                    key.includes("password")
                      ? "password"
                      : key === "email"
                        ? "email"
                        : "text"
                  }
                  value={(form as any)[key]}
                  maxLength={1000}
                  onChange={handleChange}
                  required
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 shadow-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 placeholder:text-slate-400"
                  placeholder={key === "email" ? "you@example.com" : "••••••••"}
                />
              </div>
            ))}

            <button
              type="submit"
              className="mt-2 w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-md hover:bg-emerald-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            >
              Confirm
            </button>

            <div className="pt-2 text-center text-sm">
              <Link
                to="/login"
                className="text-slate-600 hover:text-slate-900 underline underline-offset-4"
              >
                login now?
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ResetFormComp;
