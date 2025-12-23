import apiClient from "@/lib/apiClient";
import { z } from "zod";
import {
  MealSchema,
  type Meal,
  MealItemSchema,
  type MealItem,
} from "@/schema/zodSchema";

/* -------------------------------------------------------------------------- */
/*                               🔹 ENDPOINTS                                 */
/* -------------------------------------------------------------------------- */

const MEALS_BASE = "/meals";
const ITEMS_BASE = "/meal-items";

/* -------------------------------------------------------------------------- */
/*                             🔹 REQUEST SHAPES                              */
/* -------------------------------------------------------------------------- */

// Payload used when creating a meal
export const MealCreateSchema = z.object({
  user: z.string(),
  meal_type: z.string(),
  date_time: z.string().datetime({ offset: true }),
  name: z.string().optional(),
  notes: z.string().optional(),
  items: z.array(
    z.object({
      product: z.string(), // barcode
      quantity: z.number(),
    }),
  ),
});



export type MealCreate = z.infer<typeof MealCreateSchema>;

// Payload used when updating a meal (partial)
export const MealUpdateSchema = MealCreateSchema.partial();
export type MealUpdate = z.infer<typeof MealUpdateSchema>;

/* -------------------------------------------------------------------------- */
/*                               🔹 MEAL SERVICE                              */
/* -------------------------------------------------------------------------- */

export const mealService = {
  /** Fetch all meals */
  async list(): Promise<Meal[]> {
    const res = await apiClient.get(`${MEALS_BASE}/`);
    return z.array(MealSchema).parse(res.data);
  },

  /** Fetch a single meal */
  async retrieve(id: string): Promise<Meal> {
    const res = await apiClient.get(`${MEALS_BASE}/${id}/`);
    return MealSchema.parse(res.data);
  },

  /** Create a new meal (with nested items) */
  async create(data: MealCreate): Promise<Meal> {
    const validated = MealCreateSchema.parse(data);
    const res = await apiClient.post(`${MEALS_BASE}/`, validated);
    return MealSchema.parse(res.data);
  },

  /** Update an existing meal */
  async update(id: string, data: MealUpdate): Promise<Meal> {
    const validated = MealUpdateSchema.parse(data);
    const res = await apiClient.put(`${MEALS_BASE}/${id}/`, validated);
    return MealSchema.parse(res.data);
  },

  /** Delete a meal */
  async remove(id: string): Promise<void> {
    await apiClient.delete(`${MEALS_BASE}/${id}/`);
  },
};

/* -------------------------------------------------------------------------- */
/*                           🔹 MEAL ITEM SERVICE                             */
/* -------------------------------------------------------------------------- */

export const mealItemService = {
  /** Fetch all meal items */
  async list(): Promise<MealItem[]> {
    const res = await apiClient.get(`${ITEMS_BASE}/`);
    return z.array(MealItemSchema).parse(res.data);
  },

  /** Create a meal item */
  async create(data: {
    meal: string; // meal UUID
    product: string; // product barcode
    quantity: number;
  }): Promise<MealItem> {
    const res = await apiClient.post(`${ITEMS_BASE}/`, data);
    return MealItemSchema.parse(res.data);
  },

  /** Delete a meal item */
  async remove(id: string): Promise<void> {
    await apiClient.delete(`${ITEMS_BASE}/${id}/`);
  },
};


/* -------------------------------------------------------------------------- */
/*                           🔹 EATEN MEAL SERVICE                            */
/* -------------------------------------------------------------------------- */

import { EatenMealSchema } from "@/schema/zodSchema"; 
import type { EatenMeal } from "@/schema/zodSchema";

const EATEN_MEALS_BASE = "/eaten-meals";

// Payload for creating an eaten meal
export const EatenMealCreateSchema = z.object({
  user: z.string(), // user UUID
  meal: z.string(), // meal UUID
});
export type EatenMealCreate = z.infer<typeof EatenMealCreateSchema>;

export const eatenMealService = {
  /** Fetch all eaten meals */
  async list(): Promise<EatenMeal[]> {
    const res = await apiClient.get(`${EATEN_MEALS_BASE}/`);
    return z.array(EatenMealSchema).parse(res.data);
  },

  /** Retrieve a single eaten meal (with nested meal info) */
  async retrieve(id: string): Promise<EatenMeal> {
    const res = await apiClient.get(`${EATEN_MEALS_BASE}/${id}/`);
    return EatenMealSchema.parse(res.data);
  },

  /** Log a new eaten meal (user eats a saved meal) */
  async create(data: EatenMealCreate): Promise<EatenMeal> {
    const validated = EatenMealCreateSchema.parse(data);
    const res = await apiClient.post(`${EATEN_MEALS_BASE}/`, validated);
    return EatenMealSchema.parse(res.data);
  },

  /** Delete an eaten meal record (if you want undo functionality) */
  async remove(id: string): Promise<void> {
    await apiClient.delete(`${EATEN_MEALS_BASE}/${id}/`);
  },
};
