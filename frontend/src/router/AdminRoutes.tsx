// ===============================================
// src/router/AdminRoutes.tsx
// ===============================================
import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "@/components/DashBoard/DashboardLayout";
import AdminDashboardPage from "@/pages/AdminDashboardPage";
import GoalsPage from "@/pages/GoalsPage";
import SearchPage from "@/pages/SearchPage";
import MealBuilderPage from "@/pages/MealBuilderPage";
import { useUser } from "@/context/UserSessionProvider"; 

export default function AdminRoutes() {
  const { user, loading } = useUser();

  // Wait for session to resolve
  if (loading) return null;

  // Redirect unauthenticated users to login
  if (!user) return <Navigate to="/login" replace />;

  // Redirect regular users to their normal dashboard
  if (!user.is_admin) return <Navigate to="/app/dashboard" replace />;

  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="dashboard" element={<AdminDashboardPage />} />
        <Route path="goals" element={<GoalsPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="meal" element={<MealBuilderPage />} />
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route
          path="*"
          element={
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
              <h1 className="text-xl font-semibold text-gray-800 mb-3">
                Admin Page Not Found
              </h1>
              <p className="text-gray-600 mb-6">
                This admin section doesn’t exist or you lack permissions.
              </p>
              <Navigate to="/admin/dashboard" replace />
            </div>
          }
        />

      </Route>
    </Routes>
  );
}
