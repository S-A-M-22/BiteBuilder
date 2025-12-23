import React from "react";

const plans = [
  {
    title: "Free",
    price: "$0",
    desc: "Basics for getting started",
    features: ["Meal builder", "Local price search", "Weekly dashboard"],
    cta: "Get started",
    highlight: false,
  },
  {
    title: "Pro",
    price: "$6/mo",
    desc: "For serious planners",
    features: [
      "Advanced suggestions",
      "Deal heatmaps",
      "Export to notes & calendar",
    ],
    cta: "Start Pro",
    highlight: true,
  },
  {
    title: "Team",
    price: "$12/mo",
    desc: "Plan with a partner or flat",
    features: ["Shared pantry", "Split shopping list", "Multi-profile goals"],
    cta: "Contact us",
    highlight: false,
  },
];

const Pricing = () => {
  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          Simple pricing
        </h2>
        <p className="mt-2 text-gray-600">
          Start free. Upgrade when you need power features.
        </p>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.title}
              className={`p-6 rounded-2xl border ${
                plan.highlight
                  ? "border-2 border-green-700 shadow-lg"
                  : "border-gray-200"
              } bg-white`}
            >
              {plan.highlight && (
                <div className="inline-block text-xs font-semibold px-2 py-1 rounded-full bg-green-50 text-green-700 border border-green-200">
                  Most Popular
                </div>
              )}
              <h3 className="mt-2 text-lg font-semibold">{plan.title}</h3>
              <p className="text-sm text-gray-600">{plan.desc}</p>
              <div className="mt-2 text-4xl font-extrabold">{plan.price}</div>
              <ul className="mt-4 text-sm text-gray-600 space-y-2">
                {plan.features.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
              <a
                href="/register"
                className={`mt-6 inline-block px-5 py-2 rounded-lg font-medium ${
                  plan.highlight
                    ? "bg-green-700 text-white hover:bg-green-700"
                    : "border border-green-700 text-green-700 hover:bg-green-50"
                }`}
              >
                {plan.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;
