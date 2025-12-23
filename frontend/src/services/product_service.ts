/**
 * productService.ts
 * -------------------------------------------------------------
 * Centralized API service for interacting with Django Product endpoints.
 * Routes now include:
 *   - GET  /api/products/
 *   - GET  /api/products/:barcode/detail/
 *   - GET  /api/products/search/?q=
 *   - POST /api/products/save/
 * -------------------------------------------------------------
 */

import apiClient from "@/lib/apiClient";
import {
  Product,
  ProductSchema,
  ProductSaveInput,
  ProductPartial,
  ProductWithProvenanceSchema,
  ProductWithProvenance,
} from "@/schema/zodSchema";
import { z } from "zod";

export const productService = {
  async list(): Promise<ProductPartial[]> {
    const res = await apiClient.get("/products/");
    return z.array(ProductSchema.partial()).parse(res.data);
  },

  async getDetail(barcode: string): Promise<Product> {
    const res = await apiClient.get(`/products/${barcode}/detail/`);
    return ProductSchema.parse(res.data);
  },

  async get(id: string): Promise<Product> {
    const res = await apiClient.get(`/products/${id}/`);
    return ProductSchema.parse(res.data);
  },

  async search(q: string): Promise<{ status: string; items: Product[] }> {
    const res = await apiClient.get(`/products/search/`, { params: { q } });
    const validatedItems = z.array(ProductSchema).parse(res.data.items);
    return { status: res.data.status, items: validatedItems };
  },

  async save(item: z.infer<typeof ProductSaveInput>["item"]): Promise<Product> {
    const res = await apiClient.post("/products/save/", { item });
    return ProductSchema.parse(res.data);
  },

  async deleteProduct(id: string): Promise<void> {
    await apiClient.delete(`${id}`);
  },

  async enrich(
    item: Partial<Product>,
    opts?: { preview?: boolean },
  ): Promise<ProductWithProvenance> {
    if (item.id && !opts?.preview) {
      const res = await apiClient.post(`/products/${item.barcode}/enrich/`);
      return ProductWithProvenanceSchema.parse(res.data.product);
    }

    // always use preview endpoint when preview === true
    const res = await apiClient.post(`/products/preview-enrich/`, { item });
    return ProductWithProvenanceSchema.parse(res.data.enriched);
  },
};
