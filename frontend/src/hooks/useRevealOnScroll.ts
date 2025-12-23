import { useEffect } from "react";

const useRevealOnScroll = (selector = ".reveal", threshold = 0.12) => {
  useEffect(() => {
    const elements = document.querySelectorAll(selector);
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("show");
            observer.unobserve(entry.target); // stop observing once visible
          }
        });
      },
      { threshold },
    );

    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [selector, threshold]);
};

export default useRevealOnScroll;
