// src/services/user_auth.ts
import apiClient from "@/lib/apiClient";
import { User } from "@/types";

// ===============================
// Auth Service Functions (Django + Supabase)
// ===============================
export type LoginStartResp = {
  otp_required: true;
  email: string;
  message?: string;
};

// ---------- REGISTER ----------
export async function registerUser(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  const res = await apiClient.post(
    "/auth/register/",
    { username, email, password },
    { withCredentials: true },
  );

  if (res.status === 200 || res.status === 201) {
    return {
      id: res.data.user_id,
      username: res.data.username,
      email: res.data.email,
      is_admin:res.data.is_admin,
    };
  }

  throw new Error(res.data?.error || "Registration failed");
}

// ---------- LOGIN ----------
export async function loginUser(
  username: string,
  password: string,
  remember: boolean,
): Promise<{ id: string; username: string; email: string }> {
  const res = await apiClient.post(
    "/auth/login/",
    { username, password, remember },
    { withCredentials: true },
  );

  if (res.status === 200 && res.data.user_id) {
    return res.data as User;
  }

  throw new Error(res.data?.error || "Login failed");
}

// ---------- OTP ----------
export async function verifyOtp(
  code: string,
): Promise<{ id: string; username: string; email: string, is_admin: boolean }> {
  const res = await apiClient.post(
    "/auth/verify_otp/",
    { code },
    { withCredentials: true },
  );
  if (res.status === 200) {
    return res.data as User;
  }
  throw new Error(res.data?.error || "OTP failed");
}

// ---------- LOGOUT ----------
export async function logoutUser(): Promise<{ message: string }> {
  const res = await apiClient.post(
    "/auth/logout/",
    {},
    { withCredentials: true },
  );
  return res.data; // { message: "Logged out" }
}

// ---------- Reset Password ----------
export async function resetPassword(email: string, password: string) {
  const res = await apiClient.post(
    "auth/resetPassword/",
    { email, password },
    { withCredentials: true },
  );

  if (res.status === 200 && res.data.user_id) {
    return res.data;
  }

  throw new Error(res.data?.error || "Reset password failed");
}

// ---------- Reset Pssword OTP ----------
export async function resetPasswordOTP(code: string) {
  const res = await apiClient.post(
    "auth/api_otp_resetPassword/",
    { code },
    { withCredentials: true },
  );
  if (res.status === 200) {
    return;
  }
  throw new Error(res.data?.error || "OTP failed");
}

// ---------- VERIFY SESSION ----------
export async function getCurrentUser(): Promise<User | null> {
  try {
    const res = await apiClient.get("/auth/verify/", { withCredentials: true });
    if (res.data.authenticated) {
      return {
        id: res.data.user_id,
        username: res.data.username,
        email: res.data.email,
        is_admin: res.data.is_admin,
      };
    }
    return null;
  } catch {
    return null;
  }
}



// ---------- Export Group ----------
export const userAuth = {
  loginUser,
  verifyOtp,
  registerUser,
  logoutUser,
  getCurrentUser,
  resetPassword,
  resetPasswordOTP,

};
