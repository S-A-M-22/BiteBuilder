// src/lib/apiClient.ts
import axios, {
  AxiosError,
  AxiosInstance,
  AxiosHeaders,
  InternalAxiosRequestConfig,
} from "axios";
import Cookies from "js-cookie";
import { emitLogout } from "@/context/authBus";

const apiClient: AxiosInstance = axios.create({
  baseURL: "/api",
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
  },
  // let axios auto-copy csrftoken -> header
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

/* ---------------- Request: attach CSRF token ---------------- */
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = Cookies.get("csrftoken");
  if (token) {
    const hdrs =
      config.headers instanceof AxiosHeaders
        ? config.headers
        : AxiosHeaders.from(config.headers || {});
    hdrs.set("X-CSRFToken", token);
    hdrs.set("X-Requested-With", "XMLHttpRequest");
    config.headers = hdrs;
  }
  return config;
});

/* Helper: ensure csrftoken cookie exists (hit a CSRF-seeded GET) */
async function ensureCsrfCookie(): Promise<void> {
  try {
    await axios.get("/api/auth/csrf/seed", { withCredentials: true });
  } catch {
    // silent
  }
}

/* ---------------- Response: auto-logout + CSRF retry ---------------- */
let retriedForCsrf = false;

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    const err = error as AxiosError<any>;
    const status = err.response?.status;
    const url = err.config?.url ?? "";

    // 423 = locked/expired session
    const isAuth = /^\/?auth\/(login|register|verify|verify_otp|logout)\/?$/i.test(
      url,
    );
    if (!isAuth && status === 423) emitLogout();

    // Detect CSRF failure
    const looksLikeCsrf =
      (status === 403 || status === 419) &&
      typeof err.response?.data === "object" &&
      JSON.stringify(err.response.data).toLowerCase().includes("csrf");

    if (looksLikeCsrf && !retriedForCsrf && err.config) {
      retriedForCsrf = true;
      await ensureCsrfCookie();
      const cfg = err.config as InternalAxiosRequestConfig;
      const token = Cookies.get("csrftoken");
      if (token) {
        const hdrs =
          cfg.headers instanceof AxiosHeaders
            ? cfg.headers
            : AxiosHeaders.from(cfg.headers || {});
        hdrs.set("X-CSRFToken", token);
        hdrs.set("X-Requested-With", "XMLHttpRequest");
        cfg.headers = hdrs;
      }
      return apiClient.request(cfg);
    }
    retriedForCsrf = false;

    // Debug logging in dev mode
    if (import.meta.env.MODE === "development") {
      console.error(
        [
          "----- API ERROR -----",
          `Method: ${err.config?.method?.toUpperCase() ?? "(no method)"}`,
          `URL: ${url}`,
          `Status: ${status ?? "unknown"}`,
          `Message: ${err.message ?? "Unknown error"}`,
          err.response?.data
            ? `Data: ${JSON.stringify(err.response.data, null, 2)}`
            : "",
          "----------------------",
        ]
          .filter(Boolean)
          .join("\n"),
      );
    }

    // Return unified error object
    return Promise.reject({
      message: err.message,
      status,
      url,
      data: err.response?.data,
      isAxiosError: axios.isAxiosError(err),
    });
  },
);

export default apiClient;
