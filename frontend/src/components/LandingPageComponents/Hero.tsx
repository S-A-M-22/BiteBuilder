import React from "react";

const Hero = () => {
  return (
    <section className="relative">
      <div className="max-w-7xl mx-auto px-6 pt-20 pb-16 lg:pt-28 lg:pb-24 text-center">
        <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full border border-green-200 text-green-700 bg-green-50 mb-5">
          <span className="h-2 w-2 rounded-full bg-green-600 animate-pulse"></span>
          New: postcode price search & protein-per-dollar
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold leading-tight text-gray-900">
          Smarter groceries.{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-green-700 to-emerald-400">
            Healthier meals
          </span>
          .
        </h1>
        <p className="mt-5 text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
          Set goals, compare prices near you, and assemble balanced meals — all
          in one streamlined flow.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row justify-center gap-3">
          <a
            href="/register"
            className="px-6 py-3 rounded-xl bg-green-700 text-white font-semibold hover:bg-green-600 shadow"
          >
            Get Started Free
          </a>
          <a
            href="#features"
            className="px-6 py-3 rounded-xl border border-green-600 text-green-700 font-semibold bg-white hover:bg-green-50"
          >
            See Features
          </a>
        </div>
      </div>
    </section>
  );
};

export default Hero;
