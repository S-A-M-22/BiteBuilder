import { FC } from "react";

interface FAQItem {
  q: string;
  a: string;
}

const faqs: FAQItem[] = [
  {
    q: "Which stores are supported?",
    a: "We start with Coles, Woolworths and Aldi in Australia, then expand with community-submitted stores.",
  },
  {
    q: "Can I customise macro goals?",
    a: "Yes — set daily & weekly targets, caps, and presets (cut / maintain / bulk). We’ll guide you each step.",
  },
  {
    q: "Is BiteBuilder free?",
    a: "Yes — the core experience is free. Pro unlocks advanced suggestions, heatmaps and exports.",
  },
];

const FAQ: FC = () => {
  return (
    <section id="faq" className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          Questions, answered
        </h2>
        <p className="mt-3 text-gray-600">
          Everything you need to know about BiteBuilder.
        </p>

        <div className="mt-10 text-left space-y-4">
          {faqs.map((item) => (
            <details
              key={item.q}
              className="border border-gray-200 rounded-xl bg-white p-5 group"
            >
              <summary className="cursor-pointer flex items-center justify-between">
                <span className="font-semibold">{item.q}</span>
                <span className="transition group-open:rotate-45 text-2xl leading-none">
                  +
                </span>
              </summary>
              <p className="mt-3 text-gray-600">{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FAQ;
