const steps = [
  {
    step: "STEP 1",
    title: "Set your targets",
    desc: "Calories, protein & limits. Choose cut/maintain/bulk and your postcode.",
  },
  {
    step: "STEP 2",
    title: "Find the value",
    desc: "Search nearby stores; we highlight the best protein-per-dollar and real deals.",
  },
  {
    step: "STEP 3",
    title: "Build & save",
    desc: "Assemble meals, save a weekly plan, export the shopping list. Done.",
  },
];

const HowItWorks = () => {
  return (
    <section id="how" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          From goal → cart in minutes
        </h2>
        <p className="mt-3 text-gray-600">
          A fast 3-step flow designed for real life.
        </p>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          {steps.map((s) => (
            <div
              key={s.step}
              className="p-6 bg-white rounded-2xl border border-gray-200"
            >
              <div className="text-xs font-semibold text-green-700">
                {s.step}
              </div>
              <h3 className="mt-1 text-lg font-semibold">{s.title}</h3>
              <p className="text-gray-600">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
