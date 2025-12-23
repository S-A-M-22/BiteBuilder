import React, { useState } from "react";
import { Link } from "react-router-dom";

const NavbarAltPage = () => {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-green-700 text-white font-bold">
            BB
          </span>
          <span className="text-2xl font-bold text-gray-900">BiteBuilder</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm">
          <Link to="/#features" className="text-gray-700 hover:text-green-700">
            Features
          </Link>
          <Link to="/#how" className="text-gray-700 hover:text-green-700">
            How it works
          </Link>
          <Link to="/#pricing" className="text-gray-700 hover:text-green-700">
            Pricing
          </Link>
          <Link to="/#faq" className="text-gray-700 hover:text-green-700">
            FAQ
          </Link>
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link
            to="/login"
            className="px-4 py-2 text-gray-700 hover:text-green-700"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="px-4 py-2 rounded-lg bg-green-700 text-white font-medium hover:bg-green-600"
          >
            Sign Up
          </Link>
        </div>

        <button
          className="md:hidden p-2 rounded-lg border border-gray-200"
          onClick={() => setOpen(!open)}
        >
          ☰
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="px-6 py-3 flex flex-col gap-3">
            <Link to="/#features" className="py-2">
              Features
            </Link>
            <Link to="/#how" className="py-2">
              How it works
            </Link>
            <Link to="/#pricing" className="py-2">
              Pricing
            </Link>
            <Link to="/#faq" className="py-2">
              FAQ
            </Link>
            <div className="pt-2 border-t border-gray-100 flex gap-3">
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg border border-gray-200"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg bg-green-700 text-white"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default NavbarAltPage;
