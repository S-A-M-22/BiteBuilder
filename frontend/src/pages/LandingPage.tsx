import Navbar from "@/components/LandingPageComponents/Navbar";
import useRevealOnScroll from "../hooks/useRevealOnScroll";
import Hero from "@/components/LandingPageComponents/Hero";
import Features from "@/components/LandingPageComponents/Features";
import HowItWorks from "@/components/LandingPageComponents/HowItWorks";
import Stats from "@/components/LandingPageComponents/Stats";
import Pricing from "@/components/LandingPageComponents/Pricing";
import FAQ from "@/components/LandingPageComponents/FAQ";
import Footer from "@/components/LandingPageComponents/Footer";

const LandingPage = () => {
  useRevealOnScroll();
  return (
    <div className="bg-gray-50 text-gray-800 antialiased">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Stats />
      <Pricing />
      <FAQ />
      <Footer />
    </div>
  );
};

export default LandingPage;
