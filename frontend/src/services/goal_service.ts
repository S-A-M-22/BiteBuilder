import apiClient from "@/lib/apiClient";
import { GoalSchema, Goal } from "@/schema/zodSchema";
import { z } from "zod";

export const goalService = {
  async list(): Promise<Goal[]> {
    const res = await apiClient.get("/goals/");
    return z.array(GoalSchema).parse(res.data);
  },

  async retrieve(id: string): Promise<Goal> {
    const res = await apiClient.get(`/goals/${id}/`);
    return GoalSchema.parse(res.data);
  },

  async create(data: Partial<Goal>): Promise<Goal> {
    const res = await apiClient.post("/goals/", data);
    return GoalSchema.parse(res.data);
  },

  async update(id: string, data: Partial<Goal>): Promise<Goal> {
    const res = await apiClient.patch(`/goals/${id}/`, data);
    return GoalSchema.parse(res.data);
  },

  async remove(id: string) {
    return apiClient.delete(`/goals/${id}/`);
  }, 

  async getByUser(userId: string): Promise<Goal | null> {
    try {
      const res = await apiClient.get<Goal[] | Goal | null>(`/goals/?user=${userId}`);
      const data = res.data;
  
      // ✅ Handle array or single-object responses gracefully
      if (!data) return null;
  
      if (Array.isArray(data)) {
        // If backend returns an empty list, return null
        return data.length > 0 ? data[0] : null;
      }
  
      // If backend returns a single object
      if (typeof data === "object") {
        return data as Goal;
      }
  
      return null;
    } catch (err) {
      console.error("Failed to fetch goal by user:", err);
      return null;
    }
  }
  

};

