import React from "react";

const Stats = () => {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
        <div className="md:col-span-2 grid grid-cols-3 gap-4 text-center">
          <div className="p-6 rounded-xl border border-gray-200 bg-gray-50">
            <div className="text-3xl font-bold text-gray-900">$22.4</div>
            <div className="text-xs text-gray-500">avg. daily basket</div>
          </div>
          <div className="p-6 rounded-xl border border-gray-200 bg-gray-50">
            <div className="text-3xl font-bold text-gray-900">+145g</div>
            <div className="text-xs text-gray-500">protein / day</div>
          </div>
          <div className="p-6 rounded-xl border border-gray-200 bg-gray-50">
            <div className="text-3xl font-bold text-gray-900">–12%</div>
            <div className="text-xs text-gray-500">spend vs baseline</div>
          </div>
        </div>
        <blockquote className="glass p-6 rounded-2xl border border-white/60 shadow">
          <p className="text-gray-800">
            “I hit my macros for under $160 a week — no guesswork. BiteBuilder
            is like PCPartPicker for your diet.”
          </p>
          <div className="mt-3 text-sm text-gray-600">— Early user, Sydney</div>
        </blockquote>
      </div>
    </section>
  );
};

export default Stats;
