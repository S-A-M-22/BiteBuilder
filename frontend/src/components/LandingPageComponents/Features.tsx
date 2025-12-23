const features = [
  {
    id: "NG",
    title: "Nutrition Goals",
    desc: "Daily & weekly macros with auto-adjusting targets based on your activity and cut/bulk goals.",
    list: [
      "Macro caps & alerts",
      "Weekly trend view",
      "Goal presets (cut/maintain/bulk)",
    ],
  },
  {
    id: "PS",
    title: "Smart Price Search",
    desc: "Compare products by postcode with distance-weighting and protein-per-dollar ranking.",
    list: [
      "Coles / Woolies / Aldi coverage",
      '"Nearest good enough" pick',
      "Deal heatmap",
    ],
  },
  {
    id: "MB",
    title: "Meal Builder",
    desc: "Assemble meals with live macros and costs. Save templates for fast reuse.",
    list: [
      "Drag ingredients in",
      "Swap with cheaper equivalents",
      "One-click add to shopping list",
    ],
  },
];

const Features = () => {
  return (
    <section id="features" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          Everything you need to eat smart on a budget
        </h2>
        <p className="mt-3 text-gray-600">
          Set targets, build meals, track spend — BiteBuilder keeps every choice
          aligned to your plan.
        </p>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((f) => (
            <div
              key={f.title}
              className="p-6 rounded-2xl border border-gray-200 bg-gradient-to-b from-white to-gray-50 hover:shadow-lg transition"
            >
              <div className="h-10 w-10 rounded-lg bg-green-100 text-green-700 flex items-center justify-center font-bold">
                {f.id}
              </div>
              <h3 className="mt-4 text-xl font-semibold text-gray-900">
                {f.title}
              </h3>
              <p className="mt-2 text-gray-600">{f.desc}</p>
              <ul className="mt-3 text-sm text-gray-600 list-disc pl-5 space-y-1">
                {f.list.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
