import { Outlet } from "react-router-dom";
import Menubar from "../Menubar";
import Footer from "../LandingPageComponents/Footer";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Top bar and controls */}
      <Menubar />

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Core dashboard sections */}

        {/* Optional nested routes */}
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
