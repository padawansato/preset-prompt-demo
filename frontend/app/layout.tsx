import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Preset Prompt Studio (demo)",
  description: "プリセットプロンプト実行アプリのデモ",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
