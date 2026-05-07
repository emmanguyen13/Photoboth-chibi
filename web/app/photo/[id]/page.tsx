import { notFound } from "next/navigation";
import type { Metadata } from "next";

const eventName = process.env.NEXT_PUBLIC_EVENT_NAME || "Photobooth Sinh Nhật";
const hashtag = process.env.NEXT_PUBLIC_EVENT_HASHTAG || "#happybirthday";

function buildPhotoUrl(id: string): string | null {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const bucket = process.env.NEXT_PUBLIC_SUPABASE_BUCKET || "photobooth";
  if (!supabaseUrl) return null;
  const safeId = id.replace(/[^a-zA-Z0-9_-]/g, "");
  return `${supabaseUrl.replace(/\/$/, "")}/storage/v1/object/public/${bucket}/${safeId}.jpg`;
}

async function photoExists(url: string): Promise<boolean> {
  try {
    const res = await fetch(url, { method: "HEAD", cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

type Params = { id: string };

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { id } = await params;
  const url = buildPhotoUrl(id);
  return {
    title: `Ảnh kỷ niệm — ${eventName}`,
    description: "Tải ảnh chibi siêu cute từ tiệc sinh nhật về máy 📸✨",
    openGraph: url ? { images: [url] } : undefined,
  };
}

export default async function PhotoPage({ params }: { params: Promise<Params> }) {
  const { id } = await params;
  const url = buildPhotoUrl(id);

  if (!url) {
    return <ConfigMissing />;
  }

  const ok = await photoExists(url);
  if (!ok) {
    notFound();
  }

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-8 sm:py-12 gap-6">
      <header className="text-center">
        <div className="inline-block bg-ink text-white px-4 py-1.5 rounded-full text-[11px] font-bold tracking-[0.25em] mb-3 shadow-soft">
          📸 ẢNH KỶ NIỆM
        </div>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-ink tracking-tight">
          {eventName}
        </h1>
      </header>

      <div className="animate-dropIn">
        <div className="polaroid max-w-md sm:max-w-lg">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={url} alt="Ảnh kỷ niệm" />
        </div>
      </div>

      <a
        href={url}
        download={`${id}.jpg`}
        className="inline-flex items-center gap-2 bg-pink text-white font-bold text-lg px-7 py-4 rounded-full shadow-pink hover:scale-105 active:scale-95 transition-transform"
      >
        ⬇️ Tải về máy
      </a>

      <div className="text-center text-ink-soft text-sm max-w-sm leading-relaxed">
        Hoặc <span className="font-bold">nhấn giữ</span> vào ảnh →{" "}
        <span className="font-bold">"Lưu vào ảnh"</span>
        <br />
        để lưu vào thư viện điện thoại 📱
      </div>

      <a
        href="/"
        className="text-pink font-bold text-base hover:underline mt-4"
      >
        ← Về trang chính
      </a>

      <footer className="mt-8 text-center text-pink font-bold text-lg animate-wiggle">
        {hashtag}
      </footer>
      <p className="text-ink-soft text-xs">Cám ơn bạn đã đến chung vui! 🎉</p>
    </main>
  );
}

function ConfigMissing() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 text-center gap-4">
      <div className="text-7xl">⚙️</div>
      <h1 className="font-display text-3xl text-ink">Chưa cấu hình Supabase</h1>
      <p className="text-ink-soft max-w-md">
        Vercel cần env vars: <code className="bg-pink-soft px-2 py-1 rounded">NEXT_PUBLIC_SUPABASE_URL</code>{" "}
        và <code className="bg-pink-soft px-2 py-1 rounded">NEXT_PUBLIC_SUPABASE_BUCKET</code>.
        Xem README.
      </p>
    </main>
  );
}
