import type { Metadata } from "next";
import "./globals.css";

const eventName = process.env.NEXT_PUBLIC_EVENT_NAME || "Photobooth Sinh Nhật";

export const metadata: Metadata = {
  title: `${eventName} 📸`,
  description: "Quà nhỏ từ tiệc sinh nhật — quét QR là có ảnh siêu cute mang về!",
  openGraph: {
    title: eventName,
    description: "Ảnh chibi siêu cute từ photobooth sinh nhật ✨",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Quicksand:wght@500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased">
        <div aria-hidden className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <span className="float animate-drift" style={{ top: "10%", left: "5%", fontSize: 56 }}>🦖</span>
          <span className="float animate-drift" style={{ top: "20%", right: "8%", animationDelay: "-4s" }}>❄️</span>
          <span className="float animate-drift" style={{ top: "60%", left: "3%", animationDelay: "-10s", fontSize: 64 }}>🎀</span>
          <span className="float animate-drift" style={{ top: "75%", right: "6%", animationDelay: "-7s" }}>🌟</span>
          <span className="float animate-drift" style={{ top: "40%", left: "12%", animationDelay: "-12s", fontSize: 40 }}>💖</span>
          <span className="float animate-drift" style={{ top: "85%", left: "50%", animationDelay: "-3s", fontSize: 36 }}>✨</span>
        </div>
        {children}
      </body>
    </html>
  );
}
