import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "@/components/DashBoard/DashboardLayout";
import DashboardPage from "@/pages/DashboardPage";
import GoalsPage from "@/pages/GoalsPage";
import { useUser } from "@/context/UserSessionProvider";
import SearchPage from "@/pages/SearchPage";
import MealBuilderPage from "@/pages/MealBuilderPage";
import ProfilePage from "@/pages/ProfilePage";

export default function PrivateRoutes() {
  const { user, loading } = useUser();

  if (loading) return <div style={{ padding: 16 }}>loading… (auth)</div>;
  if (!user) return <Navigate to="/login" replace />;


  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="goals" element={<GoalsPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="meal" element={<MealBuilderPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route
          path="*"
          element={
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
              <h1 className="text-xl font-semibold text-gray-800 mb-3">
                Page Not Found
              </h1>
              <p className="text-gray-600 mb-6">
                This section doesn’t exist or has been moved.
              </p>
              <Navigate to="/dashboard" replace />
            </div>
          }
        />

      </Route>
    </Routes>
  );
}
