import apiClient from "@/lib/apiClient";
import { NutrientSchema, Nutrient } from "@/schema/zodSchema";
import { z } from "zod";

export const nutrientService = {
  async list(): Promise<Nutrient[]> {
    const res = await apiClient.get("/nutrients/");
    return z.array(NutrientSchema).parse(res.data);
  },

  async retrieve(id: string): Promise<Nutrient> {
    const res = await apiClient.get(`/nutrients/${id}/`);
    return NutrientSchema.parse(res.data);
  },

  async create(data: Partial<Nutrient>): Promise<Nutrient> {
    const res = await apiClient.post("/nutrients/", data);
    return NutrientSchema.parse(res.data);
  },

  async update(id: string, data: Partial<Nutrient>): Promise<Nutrient> {
    const res = await apiClient.put(`/nutrients/${id}/`, data);
    return NutrientSchema.parse(res.data);
  },

  async remove(id: string) {
    return apiClient.delete(`/nutrients/${id}/`);
  },
};
