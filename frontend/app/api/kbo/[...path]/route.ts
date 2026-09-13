import { NextRequest } from "next/server";

const LOCAL_API_BASE = "http://127.0.0.1:8000/api/v1";

function upstreamBase() {
  const configured = (process.env.KBO_API_BASE_URL || LOCAL_API_BASE).replace(/\/$/, "");
  return /^https?:\/\//.test(configured) ? configured : `http://${configured}`;
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const pathname = path.map(encodeURIComponent).join("/");
  const target = new URL(`${upstreamBase()}/${pathname}`);
  target.search = request.nextUrl.search;

  try {
    const response = await fetch(target, {
      cache: "no-store",
      headers: { accept: "application/json" },
    });
    const headers = new Headers({ "cache-control": "no-store" });
    const contentType = response.headers.get("content-type");
    if (contentType) headers.set("content-type", contentType);
    return new Response(await response.arrayBuffer(), {
      status: response.status,
      headers,
    });
  } catch {
    return Response.json(
      { detail: "백엔드 API에 연결할 수 없습니다." },
      { status: 502, headers: { "cache-control": "no-store" } },
    );
  }
}
