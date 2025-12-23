// src/hooks/useUserSession.tsx
import { useEffect, useState } from "react";
import { userAuth } from "@/services/user_auth";
import { User } from "@/types";
import { AxiosError } from "axios";
import { Factory } from "lucide-react";

export function useUserSession() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // -----------------------------------------
  // Restore + verify session from backend
  // -----------------------------------------
  useEffect(() => {
    (async () => {
      try {
        const current = await userAuth.getCurrentUser();
        if (current) {
          setUser(current);
          console.log("is Admin: ", current.is_admin);
          localStorage.setItem("user", JSON.stringify(current));
        } else {
          localStorage.removeItem("user");
          setUser(null);
        }
      } catch (err: unknown) {
        localStorage.removeItem("user");
        console.error("Session verify failed:", err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // -----------------------------------------
  // Handle login
  // -----------------------------------------
  async function handleLogin(
    username: string,
    password: string,
    remember: boolean,
  ): Promise<{ success: boolean; email: string }> {
    setError(null);
    try {
      const loggedIn = await userAuth.loginUser(username, password, remember);
      if (loggedIn) {
        return { success: true, email: loggedIn.email };
      }
      return { success: false, email: null };
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        console.error("Login failed:", err.response?.data || err.message);
        setError(
          (err.response?.data as { error?: string })?.error ||
            "Login failed. Check your credentials.",
        );
      } else if (err instanceof Error) {
        console.error("Error:", err.message);
        setError(err.message);
      } else {
        console.error("Unknown error:", err);
        setError("An unexpected error occurred during login.");
      }
      return { success: false, email: null };
    }
  }

  async function handleOTP(code: string): Promise<boolean> {
    setError(null);
    try {
      const loggedIn = await userAuth.verifyOtp(code);
      if (loggedIn) {
        setUser(loggedIn);
        localStorage.setItem("user", JSON.stringify(loggedIn));
        return true;
      }
    } catch (err: unknown) {
      setError("Invalid code or expired, try login again.");
      return false;
    }
  }

  // -----------------------------------------
  // Handle register
  // -----------------------------------------
  async function handleRegister(
    username: string,
    email: string,
    password: string,
  ): Promise<boolean> {
    setError(null);
    try {
      const registered = await userAuth.registerUser(username, email, password);
      if (registered) {
        setUser(registered);
        localStorage.setItem("user", JSON.stringify(registered));
        return true;
      }
      return false;
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        console.error("Register failed:", err.response?.data || err.message);
        setError(
          (err.response?.data as { error?: string })?.error ||
            "Registration failed. Please try again.",
        );
      } else if (err instanceof Error) {
        console.error("Error:", err.message);
        setError(err.message);
      } else {
        console.error("Unknown error:", err);
        setError("An unexpected error occurred during registration.");
      }
      return false;
    }
  }

  // -----------------------------------------
  // Handle logout
  // -----------------------------------------
  async function handleLogout(
    navigate?: (path: string) => void,
  ): Promise<void> {
    try {
      const res = await userAuth.logoutUser();
      console.log(res?.message);
      localStorage.removeItem("user");
      sessionStorage.clear();
      setUser(null);
      setLoading(true);
      if (navigate) navigate("/");
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        console.error("Logout failed:", err.response?.data || err.message);
      } else if (err instanceof Error) {
        console.error("Logout error:", err.message);
      } else {
        console.error("Unknown logout error:", err);
      }
    }
  }

  async function reload() {
    const current = await userAuth.getCurrentUser();
    console.log(current);
    setUser(current);
    localStorage.setItem("user", JSON.stringify(current));
    setLoading(false);
  }

  // -----------------------------------------
  // Handle resetPassword
  // -----------------------------------------
  async function handleReset(
    email: string,
    password: string,
  ): Promise<{ success: boolean; email: string }> {
    setError(null);
    try {
      const loggedIn = await userAuth.resetPassword(email, password);
      if (loggedIn) {
        return { success: true, email: loggedIn.email };
      }
      return { success: false, email: null };
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        console.error(
          "Reset Password failed:",
          err.response?.data || err.message,
        );
        setError(
          (err.response?.data as { error?: string })?.error ||
            "Reset Password failed. Check your credentials.",
        );
      } else if (err instanceof Error) {
        console.error("Error:", err.message);
        setError(err.message);
      } else {
        console.error("Unknown error:", err);
        setError("An unexpected error occurred during login.");
      }
      return { success: false, email: null };
    }
  }

  async function handleResetOTP(code: string): Promise<boolean> {
    setError(null);
    try {
      await userAuth.resetPasswordOTP(code);
    } catch (err: unknown) {
      setError("Invalid code or expired, try login again.");
      return false;
    }
  }

  return {
    user,
    loading,
    error,
    handleLogin,
    handleRegister,
    handleLogout,
    handleOTP,
    reload,
    handleReset,
    handleResetOTP,
  };
}
