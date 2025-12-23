import apiClient from "@/lib/apiClient";
import {
  GoalNutrientSchema,
  GoalNutrient,
  GoalNutrientInputSchema,
} from "@/schema/zodSchema";
import { GoalNutrientInput } from "@/types";
import { z } from "zod";


export const goalNutrientService = {
  // -------------------------------
  // List all nutrients for a goal
  // -------------------------------
  async list(goalId: string): Promise<GoalNutrient[]> {
    const res = await apiClient.get(`/goal-nutrients/?goal_id=${goalId}`);
    return z.array(GoalNutrientSchema).parse(res.data);
  },

  // -------------------------------
  // Create new goal-nutrient link
  // -------------------------------
  async create(data: Partial<GoalNutrientInput>): Promise<GoalNutrient> {
    // validate outgoing payload (IDs only)
    GoalNutrientInputSchema.parse(data);
    const res = await apiClient.post("/goal-nutrients/", data);
    // validate backend response (nested object)
    return GoalNutrientSchema.parse(res.data);
  },

  // -------------------------------
  // Update existing goal-nutrient
  // -------------------------------
  async update(id: string, data: Partial<GoalNutrientInput>) {
    const res = await apiClient.patch(`/goal-nutrients/${id}/`, data);
    return GoalNutrientInputSchema.parse(res.data);
  },

  // -------------------------------
  // Delete goal-nutrient link
  // -------------------------------
  async remove(id: string) {
    return apiClient.delete(`/goal-nutrients/${id}/`);
  },
};
