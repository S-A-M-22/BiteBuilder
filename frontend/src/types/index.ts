// src/types/index.ts
import type { z } from "zod";
import {
  GoalSchema,
  GoalNutrientSchema,
  MealSchema,
  MealItemSchema,
  ProductSchema,
  ProductNutrientSchema,
  NutrientSchema,
  GoalTypeEnum,
  MealTypeEnum,
  ProfileSchema,
  GoalNutrientInputSchema,
} from "@/schema/zodSchema";

/* ==========================
   ENUM TYPES
========================== */
export type GoalType = z.infer<typeof GoalTypeEnum>;
export type MealType = z.infer<typeof MealTypeEnum>;

/* ==========================
   ENTITY TYPES
========================== */
export type User = z.infer<typeof ProfileSchema>;
export type Goal = z.infer<typeof GoalSchema>;
export type GoalNutrientInput = z.infer<typeof GoalNutrientInputSchema>;
export type GoalNutrient = z.infer<typeof GoalNutrientSchema>;
export type Meal = z.infer<typeof MealSchema>;
export type MealItem = z.infer<typeof MealItemSchema>;
export type Product = z.infer<typeof ProductSchema>;
export type ProductNutrient = z.infer<typeof ProductNutrientSchema>;
export type Nutrient = z.infer<typeof NutrientSchema>;

/* ==========================
   NESTED OR POPULATED TYPES (optional)
========================== */
// Example: a populated meal with its meal items and product info
export type PopulatedMeal = Meal & {
  items: (MealItem & { product: Product })[];
};

// Example: goal with nutrient targets expanded
export type GoalWithNutrients = Goal & {
  nutrients: (GoalNutrient & { nutrient: Nutrient })[];
};

export enum ProductSource {
  openfoodfacts = "openfoodfacts",
  user_added = "user added",
}

// src/types/store.ts
export interface Store {
  id: string; // Woolworths StoreNo
  name: string; // Store name, e.g. "Miller"
  address: string | null; // Primary address line
  suburb: string | null; // Suburb name
  state: string | null; // NSW, VIC, etc.
  postcode: string | null; // 2168
  latitude: string | null; // Decimal degrees (string from API)
  longitude: string | null; // Decimal degrees (string from API)
  is_open: boolean; // Whether store is open now
  today_hours?: string | null; // Human readable hours e.g. "7:00 AM - 9:00 PM"
}
