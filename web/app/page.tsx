const eventName = process.env.NEXT_PUBLIC_EVENT_NAME || "Photobooth Sinh Nhật";
const hashtag = process.env.NEXT_PUBLIC_EVENT_HASHTAG || "#happybirthday";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 text-center">
      <div className="inline-block bg-ink text-white px-5 py-2 rounded-full text-xs font-bold tracking-[0.3em] mb-4 shadow-soft">
        📸 PHOTOBOOTH
      </div>

      <h1 className="font-display text-5xl sm:text-7xl font-bold text-ink leading-none mb-4 tracking-tight">
        {eventName}
      </h1>

      <p className="text-lg sm:text-xl text-ink-soft mb-12 max-w-md">
        Cám ơn bạn đã đến chung vui! Quét QR ở photobooth để lưu ảnh kỷ niệm về máy ✨
      </p>

      <div className="grid grid-cols-3 gap-4 sm:gap-8 max-w-md w-full">
        <ThemeBadge emoji="🦖" name="Khủng Long" color="bg-green-100" />
        <ThemeBadge emoji="❄️" name="Tuyết" color="bg-blue-100" />
        <ThemeBadge emoji="🎀" name="Kawaii" color="bg-pink-soft" />
      </div>

      <p className="mt-12 text-pink font-bold text-xl animate-wiggle">{hashtag}</p>
    </main>
  );
}

function ThemeBadge({ emoji, name, color }: { emoji: string; name: string; color: string }) {
  return (
    <div className={`${color} rounded-3xl p-6 shadow-soft flex flex-col items-center gap-2`}>
      <div className="text-6xl animate-bobble">{emoji}</div>
      <div className="text-sm font-bold text-ink">{name}</div>
    </div>
  );
}
