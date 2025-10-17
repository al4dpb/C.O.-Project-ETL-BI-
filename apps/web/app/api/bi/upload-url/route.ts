import { NextResponse } from "next/server";

const BI_API_URL = process.env.BI_API_URL;

if (!BI_API_URL) {
  throw new Error("BI_API_URL environment variable is not set");
}

export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Validate required fields
    if (!body.org_id || !body.building_id || !body.filename || !body.content_type) {
      return NextResponse.json(
        { error: "Missing required fields: org_id, building_id, filename, content_type" },
        { status: 400 }
      );
    }

    const response = await fetch(`${BI_API_URL}/v1/upload-url`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error generating upload URL:", error);
    return NextResponse.json(
      { error: "Failed to generate upload URL" },
      { status: 500 }
    );
  }
}
