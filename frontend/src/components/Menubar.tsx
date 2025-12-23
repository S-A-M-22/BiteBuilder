import { useUserSession } from "@/hooks/userSession";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const MenuBar = () => {
  const [open, setOpen] = useState(false);
  const { user, handleLogout } = useUserSession();
  const navigate = useNavigate();

  const onLogout = () => {

    handleLogout(navigate);       // ensures backend + localStorage cleared first
  }

  const isAdmin = user?.is_admin;

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-green-600 text-white font-bold">
            BB
          </span>
          <span className="text-2xl font-bold text-gray-900">BiteBuilder</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm">

          <Link to="/app/search" className="text-gray-700 hover:text-green-700">
            Search
          </Link>
          <Link to="/app/meal" className="text-gray-700 hover:text-green-700">
            Build your Meals
          </Link>
          <Link to="/app/dashboard" className="text-gray-700 hover:text-green-700">
            Dashboard
          </Link>
          <Link to="/app/goals" className="text-gray-700 hover:text-green-700">
            Your Goals
          </Link>
          {isAdmin && (
            <Link to="/admin/dashboard" className="text-gray-700 hover:text-green-700">
                Admin Dashboard
            </Link>
          )}

        </nav>

        <div className="hidden md:flex items-center gap-3">

          {isAdmin && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700 border border-green-200">
              🏬 • Admin
            </span>
            )
          }
          
          <Link
            to="/app/profile"
            className="px-4 py-2 text-gray-700 hover:text-green-700"
          >
            {user?.username ?? "Unknown"}
          </Link>

          <button
            onClick={onLogout}
            className="px-4 py-2 rounded-lg bg-green-600 text-white font-medium hover:bg-green-700"
          >
            Logout
          </button>
        </div>

        <button
          className="md:hidden p-2 rounded-lg border border-gray-900"
          onClick={() => setOpen(!open)}
        >
          ☰
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="px-6 py-3 flex flex-col gap-3">
            <Link
              to="/app/search"
              className="text-gray-700 hover:text-green-700"
            >
              Search
            </Link>
            <Link to="/app/meal" className="text-gray-700 hover:text-green-700">
              Build your Meals
            </Link>
            <Link
              to="/app/dashboard"
              className="text-gray-700 hover:text-green-700"
            >
              Dashboard
            </Link>
            <Link
              to="/app/goals"
              className="text-gray-700 hover:text-green-700"
            >
              Your Goals
            </Link>
            <div className="pt-2 border-t border-gray-100 flex gap-3">
              <Link
                to="/app/profile"
                className="px-4 py-2 text-gray-700 hover:text-green-700"
              >
                {user?.username ?? "Unknown"}
              </Link>
              <button
                onClick={onLogout}
                className="px-4 py-2 rounded-lg bg-green-600 text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default MenuBar;
