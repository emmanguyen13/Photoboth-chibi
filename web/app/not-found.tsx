export default function NotFound() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 py-12 text-center gap-6">
      <div className="text-9xl animate-bobble">🦖</div>
      <h1 className="font-display text-4xl sm:text-5xl text-ink leading-tight">
        Ủa, ảnh đâu rồi nhỉ?
      </h1>
      <p className="text-ink-soft max-w-md text-lg">
        Có thể QR đã hết hạn, hoặc link bị gõ sai 1 chữ. Bạn quét lại QR ở photobooth nha!
      </p>
      <a
        href="/"
        className="inline-flex items-center gap-2 bg-pink text-white font-bold text-lg px-7 py-4 rounded-full shadow-pink hover:scale-105 transition-transform"
      >
        ← Về trang chính
      </a>
    </main>
  );
}
