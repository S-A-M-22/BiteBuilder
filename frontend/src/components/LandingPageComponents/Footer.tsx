import React from "react";

const Footer = () => {
  return (
    <footer className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-emerald-100 via-green-100 to-emerald-50"></div>
      <div className="max-w-7xl mx-auto px-6 py-16 text-center">
        <h3 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          Plan smarter meals today
        </h3>
        <p className="mt-2 text-gray-700">
          Join free and get your first weekly plan in minutes.
        </p>
        <div className="mt-6">
          <a className="px-6 py-3 rounded-xl bg-green-600 text-white font-semibold hover:bg-green-700 shadow">
            Build better bites. Build a better you.
          </a>
        </div>
        <p className="mt-8 text-xs text-gray-600">
          © 2025 BiteBuilder. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
