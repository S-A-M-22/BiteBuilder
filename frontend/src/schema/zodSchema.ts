// ===============================================
// src/schema/zodSchema.ts
// ===============================================
import { z } from "zod";

/* -------------------------------------------------
   ENUMS
------------------------------------------------- */
export const GoalTypeEnum = z.enum(["lose_weight", "gain_muscle", "maintain"]);
export const MealTypeEnum = z.enum(["breakfast", "lunch", "dinner", "snack"]);
export const NutrientCategoryEnum = z
  .enum(["macronutrient", "vitamin", "mineral"])
  .optional();

/* -------------------------------------------------
   PROFILE
------------------------------------------------- */
export const ProfileSchema = z.object({
  id: z.string().uuid(),
  username: z.string().max(32),
  email: z.string().email(),
  is_admin: z.boolean().default(false),
});


/* -------------------------------------------------
   JSON (generic)
------------------------------------------------- */
export type Json =
  | string
  | number
  | boolean
  | null
  | Json[]
  | { [key: string]: Json };

export const JsonSchema: z.ZodType<Json> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(JsonSchema),
    z.record(z.string(), JsonSchema),
  ]),
);

/* -------------------------------------------------
   ENRICHMENT STATUS + ENUMS
------------------------------------------------- */
export const ProductEnrichmentStatusSchema = z.enum([
  "ready", // already enriched
  "queued", // waiting enrichment
  "none", // no enrichment available
  "not_found", // source lookup failed
]);

export const NutritionBasisEnum = z
  .enum(["per_100g", "per_serving"])
  .nullable();
export const ProductSourceEnum = z.enum([
  "woolworths",
  "openfoodfacts",
  "user_added",
]);

/* -------------------------------------------------
   NUTRITION (nested search payload)
   Matches Woolies/OFF shape: record of keys (e.g., "protein", "fat"),
   each having optional per_100 / per_serving values with units.
------------------------------------------------- */
export const NutrientValueSchema = z.object({
  value: z.number().nullable(),
  unit: z.string().nullable(),
});

export const NutritionEntrySchema = z.object({
  label: z.string().nullable().optional(),
  per_100: NutrientValueSchema.nullable().optional(),
  per_serving: NutrientValueSchema.nullable().optional(),
});

export const NutritionSchema = z
  .record(z.string(), NutritionEntrySchema)
  .optional();

/* -------------------------------------------------
   NUTRIENT (master list)
------------------------------------------------- */
export const NutrientSchema = z.object({
  id: z.string().uuid(),
  code: z.string().max(50),
  name: z.string().max(100),
  unit: z.enum(["g", "mg", "µg", "kJ", "kcal", "%", "per_serving"]),
  category: NutrientCategoryEnum.nullish(),
  display_order: z.number().int().optional(),
  is_visible: z.boolean().optional(),
});

/* -------------------------------------------------
   PRODUCT NUTRIENT (relational)
------------------------------------------------- */
export const ProductNutrientSchema = z.object({
  id: z.string().uuid().optional().nullable(),
  amount_per_100g: z.coerce.number().nullable(),
  amount_per_serving: z.coerce.number().nullable(),
  nutrient: z
    .object({
      id: z.string().uuid().optional().nullable(),
      code: z.string().optional().nullable(),
      name: z.string(),
      unit: z.string().nullable(),
      category: z.string().nullable(),
    })
    .optional()
    .nullable(),
});

/* -------------------------------------------------
   AUX / SEARCH-ONLY FIELDS
------------------------------------------------- */
export const ExternalIdsSchema = z.record(z.string(), z.string()).optional();

/* -------------------------------------------------
   PRODUCT
   Supports BOTH:
   - normalized: product_nutrients[]
   - denormalized (search): nutrition { protein: { per_100, ... }, ... }
------------------------------------------------- */
export const ProductSchema = z.object({
  id: z.string().uuid().optional(),

  // Core identifiers
  barcode: z.coerce.string().nullable(),
  name: z.string().optional(),
  brand: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  size: z.string().nullable().optional(),

  // Pricing + availability
  price_current: z.coerce.number().nullable().optional(),
  price_was: z.coerce.number().nullable().optional(), // <-- add this
  is_on_special: z.boolean().default(false),

  cup_price_value: z.coerce.number().nullable().optional(), // e.g. 12
  cup_price_unit: z.string().nullable().optional(),         // e.g. "1kg"

  // Media + metadata
  image_url: z.string().url().nullable().optional(),
  product_url: z.string().url().nullable(),
  health_star: z.string().optional().nullable().catch(null),
  allergens: z.string().optional().nullable().catch(null),

  // Serving + nutrition basis
  serving_size_value: z.coerce.number().optional().nullable().catch(null),
  serving_size_unit: z.string().max(8).optional().nullable().catch(null),
  servings_per_pack: z.coerce.number().optional().nullable().catch(null),
  nutrition_basis: NutritionBasisEnum.optional().nullable().catch(null),

  // Source + enrichment info
  primary_source: ProductSourceEnum.default("woolworths"),
  last_enriched_at: z.string().nullable().optional(),
  enrichment_attempts: z.number().optional(),

  // Related data (normalized)
  product_nutrients: z.array(ProductNutrientSchema).optional(),

  // Search/ingest-only (denormalized)
  nutrition: NutritionSchema, // keep raw nested nutrition if present

  // Optional extras from search you’re already returning
  category: z.string().nullable().optional(),
  subcategory: z.string().nullable().optional(),
  allergens_raw: z.string().nullable().optional(),
  dietary_tags: z.array(z.string()).optional(),
  dietary_tags_slugs: z.array(z.string()).optional(),
  external_ids: ExternalIdsSchema,
  is_in_stock: z.boolean().optional(),
  availability_next_date: z.string().nullable().optional(),

  // Timestamps
  created_at: z.string().datetime({ offset: true }).optional(),
  updated_at: z.string().datetime({ offset: true }).optional(),
});

/* -------------------------------------------------
   GOAL
------------------------------------------------- */
export const GoalSchema = z.object({
  id: z.string().uuid(),
  user: z.string().uuid(), // One-to-one relationship with Profile
  target_weight_kg: z.number().nullable().optional(),
  target_calories: z.number().int().nullable().optional(),
  consumed_calories: z.number().int().nullable().optional(),
  reset_frequency: z.enum(["daily", "weekly", "monthly", "none"]).default("none"),
});

/* For POST/PATCH payloads */
export const GoalInputSchema = z.object({
  user: z.string().uuid(),
  target_weight_kg: z.number().nullable().optional(),
  target_calories: z.number().int().nullable().optional(),
  reset_frequency: z.enum(["daily", "weekly", "monthly", "none"]).optional(),
});

/* -------------------------------------------------
   GOAL NUTRIENT
------------------------------------------------- */
// For GET/after-create/update
export const GoalNutrientSchema = z.object({
  id: z.string().uuid().optional(),
  goal: z.string().uuid(),
  nutrient: NutrientSchema, // nested object
  target_amount: z.number(),
  consumed_amount: z.number().default(0),
});

// For POST/PATCH payloads
export const GoalNutrientInputSchema = z.object({
  goal: z.string().uuid(),
  nutrient: z.string().uuid(),
  target_amount: z.coerce.number(),  //
  consumed_amount: z.coerce.number().optional(),
});

/* -------------------------------------------------
   MEAL ITEM
------------------------------------------------- */
export const MealItemSchema = z.object({
  id: z.string().uuid(),
  quantity: z.number(), // grams
  meal: z.string().uuid(),
  product: ProductSchema,
});

/* -------------------------------------------------
   MEAL
------------------------------------------------- */
export const MealSchema = z.object({
  id: z.string().uuid(),
  user: z.string().uuid(),
  meal_type: MealTypeEnum,
  name: z.string().nullable().optional(),
  date_time: z.string().datetime({ offset: true }),
  notes: z.string().nullable().optional(),
  items: z.array(MealItemSchema),
});

/* -------------------------------------------------
   EXPORT COLLECTION
------------------------------------------------- */
export const Schemas = {
  ProfileSchema,
  NutrientSchema,
  ProductSchema,
  ProductNutrientSchema,
  GoalSchema,
  GoalNutrientSchema,
  MealSchema,
  MealItemSchema,
};

export type Profile = z.infer<typeof ProfileSchema>;
export type Nutrient = z.infer<typeof NutrientSchema>;
export type Product = z.infer<typeof ProductSchema>;
export type ProductNutrient = z.infer<typeof ProductNutrientSchema>;
export type Goal = z.infer<typeof GoalSchema>;
export type GoalNutrient = z.infer<typeof GoalNutrientSchema>;
export type Meal = z.infer<typeof MealSchema>;
export type MealItem = z.infer<typeof MealItemSchema>;

/* -------------------------------------------------
   PRODUCT SAVE INPUT
   Lets you POST either relational nutrients or raw nested nutrition.
   Backend can map raw 'nutrition' into ProductNutrient rows.
------------------------------------------------- */
export const ProductSaveItemBase = z.object({
  // --- Core product identity ---
  barcode: z.string().nullable().optional(),
  name: z.string(),
  brand: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  size: z.string().nullable().optional(),

  // --- Price + availability ---
  price_current: z.coerce.number().nullable().optional(),
  is_on_special: z.boolean().optional(),

  // --- Media / metadata ---
  image_url: z.string().url().nullable().optional(),
  product_url: z.string().url().nullable().optional(),
  health_star: z.string().nullable().optional(),
  allergens: z.string().nullable().optional(),

  // --- Serving info ---
  serving_size_value: z.coerce.number().nullable().optional(),
  serving_size_unit: z.string().max(8).nullable().optional(),
  servings_per_pack: z.coerce.number().nullable().optional(),
  nutrition_basis: NutritionBasisEnum.optional(),

  // --- Source + enrichment info ---
  primary_source: ProductSourceEnum.optional(),

  // --- Search extras (optional passthrough) ---
  category: z.string().nullable().optional(),
  subcategory: z.string().nullable().optional(),
  allergens_raw: z.string().nullable().optional(),
  dietary_tags: z.array(z.string()).optional(),
  dietary_tags_slugs: z.array(z.string()).optional(),
  external_ids: ExternalIdsSchema,
  is_in_stock: z.boolean().optional(),
  availability_next_date: z.string().nullable().optional(),


  price_was: z.coerce.number().nullable().optional(),
  cup_price_value: z.coerce.number().nullable().optional(),
  cup_price_unit: z.string().nullable().optional(),
});

// You can include EITHER or BOTH of these in the save payload
export const ProductSaveInput = z.object({
  item: ProductSaveItemBase.extend({
    product_nutrients: z.array(ProductNutrientSchema).optional(),
    nutrition: NutritionSchema, // raw nested; backend can normalize
  }),
});
export type ProductSaveInput = z.infer<typeof ProductSaveInput>;

/* -------------------------------------------------
   PRODUCT BULK SAVE INPUT
------------------------------------------------- */
export const ProductBulkSaveInput = z.object({
  items: z.array(ProductSaveInput.shape.item),
});
export type ProductBulkSaveInput = z.infer<typeof ProductBulkSaveInput>;

/* Convenient partial type */
export type ProductPartial = z.infer<
  ReturnType<(typeof ProductSchema)["partial"]>
>;

/* --------------------------------------------
   FATSECRET PROVENANCE + ENRICHMENT
-------------------------------------------- */
export const FatSecretProvenanceSchema = z.object({
  food_id: z.number(),
  food_entry_name: z.string().nullable().optional(),
  food_name: z.string().nullable().optional(),
  food_type: z.string().nullable().optional(),
  food_url: z.string().url().nullable().optional(),
});

export const FatSecretEnrichmentSchema = z.object({
  method: z.literal("fatsecret_nlp"),
  timestamp: z.string(),
  source_foods: z.array(FatSecretProvenanceSchema),
});

/**
 * Extends the existing ProductSchema with provenance
 * and enrichment metadata — useful for enrichment responses.
 */
export const ProductWithProvenanceSchema = ProductSchema.extend({
  enrichment: z
    .object({
      fatsecret: FatSecretEnrichmentSchema.optional(),
    })
    .optional(),
  provenance: FatSecretEnrichmentSchema.optional(),
});

export type ProductWithProvenance = z.infer<typeof ProductWithProvenanceSchema>;


export const EatenMealSchema = z.object({
  id: z.string().uuid(),
  user: z.string().uuid(),
  eaten_at: z.string().datetime({ offset: true }),
  meal: MealSchema,
});


export type EatenMeal = z.infer<typeof EatenMealSchema>;

export const EatenMealWriteSchema = z.object({
  user: z.string().uuid(),
  meal: z.string().uuid(),
});