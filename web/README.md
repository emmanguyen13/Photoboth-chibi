# 🌐 Photobooth Web Gallery

Next.js app cho gallery khách quét QR. Deploy lên Vercel.

## Local dev

```bash
cd web
npm install
cp .env.example .env.local
# Điền NEXT_PUBLIC_SUPABASE_URL từ Supabase project
npm run dev
```

→ http://localhost:3000

## Deploy lên Vercel

1. **vercel.com → Add New → Project**
2. Import repo `Photoboth-chibi` từ GitHub
3. **Root Directory:** chọn `web` (quan trọng — repo có cả Python backend, Vercel chỉ build folder này)
4. Framework preset: Next.js (tự nhận)
5. Environment Variables: điền 4 biến từ `.env.example`
6. Deploy → đợi ~2 phút

Sau khi deploy, copy Vercel URL (ví dụ `photoboth-chibi.vercel.app`) → paste vào `.env` của app local:
```env
GALLERY_URL=https://photoboth-chibi.vercel.app
```

## Routes

| Path | Mục đích |
|---|---|
| `/` | Landing page (không bắt buộc) |
| `/photo/{id}` | Khách quét QR → xem + tải ảnh |
| `/not-found` | Khi ảnh không tồn tại |
