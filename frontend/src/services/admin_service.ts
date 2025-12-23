// ===============================================
// src/services/user_service.ts
// ===============================================
import apiClient from "@/lib/apiClient";
import { User } from "@/types";
import { error } from "console";


export interface PaginatedUsersResponse {
  results: User[];
  count: number;
  next: string | null;
  previous: string | null;
}

export async function fetchUsers(
  search: string = "",
  page: number = 1
): Promise<PaginatedUsersResponse> {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  params.append("page", page.toString());

  const res = await apiClient.get(`/adminUser/listUsers/?${params.toString()}`, {
    withCredentials: true,
  });
  return res.data;
}

export async function deleteUser(userId: string ): Promise<void> {
  const res = await apiClient.post(`/adminUser/deleteUser/${userId}/`, {userId}, { withCredentials: true })
  if (res){
    return;
  }
  else{
    throw new Error("Can not delete this user!");
  }
}

export async function isAdmin(): Promise<boolean> {
  const res = await apiClient.post("/adminUser/isAdmin/", { withCredentials: true });
  return res.data.is_admin === true;
}


export const adminService = {
  fetchUsers,
  deleteUser,
  isAdmin,
};

