import { NextRequest, NextResponse } from "next/server";

const ALLOWED_IMAGE_HOSTS = new Set(["sports-phinf.pstatic.net"]);

export async function GET(request: NextRequest) {
  const source = request.nextUrl.searchParams.get("url");
  if (!source) {
    return NextResponse.json({ detail: "이미지 URL이 필요합니다." }, { status: 400 });
  }

  let imageUrl: URL;
  try {
    imageUrl = new URL(source);
  } catch {
    return NextResponse.json({ detail: "올바르지 않은 이미지 URL입니다." }, { status: 400 });
  }

  if (imageUrl.protocol !== "https:" || !ALLOWED_IMAGE_HOSTS.has(imageUrl.hostname)) {
    return NextResponse.json({ detail: "허용되지 않은 이미지 호스트입니다." }, { status: 403 });
  }

  try {
    const upstream = await fetch(imageUrl, {
      headers: {
        Accept: "image/avif,image/webp,image/png,image/*,*/*;q=0.8",
        Referer: "https://m.sports.naver.com/",
        "User-Agent": "KBO-Live-Tracker/1.0",
      },
      next: { revalidate: 60 * 60 * 24 },
    });
    const contentType = upstream.headers.get("content-type") ?? "";
    if (!upstream.ok || !contentType.startsWith("image/")) {
      return NextResponse.json({ detail: "이미지를 불러오지 못했습니다." }, { status: 502 });
    }

    return new NextResponse(await upstream.arrayBuffer(), {
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=86400, stale-while-revalidate=604800",
      },
    });
  } catch {
    return NextResponse.json({ detail: "이미지 서버에 연결하지 못했습니다." }, { status: 502 });
  }
}
