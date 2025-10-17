import { z } from "zod";

// Zod schemas for API responses
export const PropertyOverviewSchema = z.object({
  data: z.array(
    z.object({
      building_name: z.string(),
      total_suites: z.number(),
      occupied_suites: z.number(),
      occupancy_rate: z.number(),
      monthly_revenue: z.number(),
      total_sqft: z.number(),
    })
  ),
  row_count: z.number(),
  columns: z.array(z.string()),
  query_name: z.string(),
});

export const RevenueTrendsSchema = z.object({
  data: z.array(
    z.object({
      month: z.string(),
      total_revenue: z.number(),
      occupancy_rate: z.number(),
      avg_rent_psf: z.number().optional(),
    })
  ),
  row_count: z.number(),
  columns: z.array(z.string()),
  query_name: z.string(),
});

export const BuildingComparisonSchema = z.object({
  data: z.array(
    z.object({
      building_name: z.string(),
      total_suites: z.number(),
      occupied_suites: z.number(),
      occupancy_rate: z.number(),
      total_revenue: z.number(),
      avg_rent_psf: z.number().optional(),
    })
  ),
  row_count: z.number(),
  columns: z.array(z.string()),
  query_name: z.string(),
});

export const SuiteDetailsSchema = z.object({
  data: z.array(
    z.object({
      suite_id: z.string(),
      building_name: z.string(),
      suite_number: z.string(),
      sqft: z.number(),
      status: z.string(),
      tenant_name: z.string().optional().nullable(),
      monthly_rent: z.number().optional().nullable(),
      lease_start: z.string().optional().nullable(),
      lease_end: z.string().optional().nullable(),
    })
  ),
  row_count: z.number(),
  columns: z.array(z.string()),
  query_name: z.string(),
});

export const UploadUrlResponseSchema = z.object({
  uploadUrl: z.string(),
  objectKey: z.string(),
  expiresIn: z.number(),
});

// Type exports
export type PropertyOverview = z.infer<typeof PropertyOverviewSchema>;
export type RevenueTrends = z.infer<typeof RevenueTrendsSchema>;
export type BuildingComparison = z.infer<typeof BuildingComparisonSchema>;
export type SuiteDetails = z.infer<typeof SuiteDetailsSchema>;
export type UploadUrlResponse = z.infer<typeof UploadUrlResponseSchema>;

/**
 * Generic BI API client function
 * Sends POST request to /api/bi/{name} proxy route
 */
export async function postBI<T>(
  name: string,
  body?: unknown
): Promise<T> {
  const response = await fetch(`/api/bi/${name}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body || {}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || `API request failed: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

/**
 * Get presigned upload URL for S3
 */
export async function getUploadUrl(params: {
  org_id: string;
  building_id: string;
  filename: string;
  content_type: string;
}): Promise<UploadUrlResponse> {
  const response = await fetch("/api/bi/upload-url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Unknown error" }));
    throw new Error(error.error || "Failed to get upload URL");
  }

  const data = await response.json();
  return UploadUrlResponseSchema.parse(data);
}

/**
 * Upload file to S3 using presigned URL
 */
export async function uploadFileToS3(
  uploadUrl: string,
  file: File
): Promise<void> {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    body: file,
    headers: {
      "Content-Type": file.type,
    },
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
}

// Convenience functions with type safety
export const getBIData = {
  propertyOverview: (params?: unknown) =>
    postBI<PropertyOverview>("01_property_overview", params),

  revenueTrends: (params?: unknown) =>
    postBI<RevenueTrends>("02_revenue_trends", params),

  buildingComparison: (params?: unknown) =>
    postBI<BuildingComparison>("03_building_comparison", params),

  suiteDetails: (params?: unknown) =>
    postBI<SuiteDetails>("04_vacant_suites", params),
};
