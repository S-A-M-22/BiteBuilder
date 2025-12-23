import { Routes, Route, Link } from "react-router-dom";
import LandingPage from "../pages/LandingPage";
import Login from "../pages/LoginPage";
import Register from "../pages/RegisterPage";
import Reset from "../pages/ResetPasswordPage";

function FallbackHandler() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <h1 className="text-xl font-semibold text-gray-800 mb-3">
        You’ve reached an unknown page
      </h1>
      <p className="text-gray-600 mb-6">
        If you came here after verifying your email, you can safely return home.
      </p>
      <Link
        to="/"
        className="px-4 py-2 rounded-md bg-emerald-600 text-white hover:bg-emerald-700 transition"
      >
        Return to Home
      </Link>
    </div>
  );
}

export default function PublicRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/reset" element={<Reset />} />
      {/* 👇 fallback for unknown URLs (includes Supabase redirect) */}
      <Route path="*" element={<FallbackHandler />} />
    </Routes>
  );
}
