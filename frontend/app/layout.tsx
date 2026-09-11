import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KBO Live Tracker",
  description: "KBO 전체 경기와 경기 흐름을 실시간으로 확인하는 대시보드",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
