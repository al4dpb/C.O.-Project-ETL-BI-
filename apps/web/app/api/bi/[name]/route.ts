import { NextResponse } from "next/server";

const BI_API_URL = process.env.BI_API_URL;

if (!BI_API_URL) {
  throw new Error("BI_API_URL environment variable is not set");
}

export async function POST(
  req: Request,
  { params }: { params: { name: string } }
) {
  try {
    const body = await req.json().catch(() => ({}));

    const response = await fetch(`${BI_API_URL}/v1/query/${params.name}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(body),
      cache: "no-store", // Ensure fresh data
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error querying ${params.name}:`, error);
    return NextResponse.json(
      { error: "Failed to fetch data from BI API" },
      { status: 500 }
    );
  }
}

export async function GET(
  _req: Request,
  { params }: { params: { name: string } }
) {
  try {
    const response = await fetch(`${BI_API_URL}/v1/query/${params.name}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({}),
      cache: "no-store",
    });

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error querying ${params.name}:`, error);
    return NextResponse.json(
      { error: "Failed to fetch data from BI API" },
      { status: 500 }
    );
  }
}
