import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import AppRoutes from "./App";

// ==========================
// Disable all console logs in production
// ==========================
if (process.env.NODE_ENV === "production") {
  console.log = () => {};
  console.info = () => {};
  console.warn = () => {};
  console.debug = () => {};
  console.trace = () => {};
}

// ==========================
// Mount React App
// ==========================
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppRoutes />
  </StrictMode>
);
