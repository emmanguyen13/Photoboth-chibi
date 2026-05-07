# 📸 Photobooth Sinh Nhật — Cute Chibi Edition

App photobooth tự dựng cho tiệc sinh nhật. Hỗ trợ:
- 🦖 ❄️ 🎀 3 theme: Khủng Long / Frozen-inspired / Kawaii cat
- 📷 Máy ảnh DSLR (Canon/Nikon/Fuji qua gphoto2) hoặc webcam test
- 🖨️ In ảnh 4x6" qua máy in nhiệt (CUPS)
- 📱 QR code cho khách quét tải ảnh về máy
- 🌐 UI cảm ứng full-screen cho iPad/touchscreen

---

## ⚡ Setup nhanh (15 phút)

### 1. Cài dependencies hệ thống (Mac)

```bash
# gphoto2 cho DSLR + librsvg để build khung
brew install gphoto2 libgphoto2 librsvg

# imagesnap để test webcam (optional, fallback của fallback)
brew install imagesnap
```

### 2. Cài Python deps

```bash
cd "/Users/emma/Desktop/CLAUDE CODE/photobooth"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional cho webcam test:
pip install opencv-python
```

### 3. Build khung từ SVG → PNG

```bash
python -m backend.build_frames
```

Kiểm tra `assets/frames/*/frame.png` đã có file.

### 4. Tạo file `.env`

```bash
cp .env.example .env
# Mở .env và điền config (xem hướng dẫn từng phần bên dưới)
```

### 5. Chạy thử với webcam

```bash
# Trong .env: CAMERA_MODE=webcam
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Mở http://localhost:8000 → chọn theme → chụp test! ✨

---

## 🎯 Setup cho ngày sự kiện thật

### A. Kết nối DSLR (Canon/Nikon/Fuji)

1. Cắm USB từ máy ảnh vào MacBook
2. **Tắt Photos.app auto-import** (System Settings → Cameras → Photos): nếu không thì gphoto2 sẽ bị tranh quyền với máy ảnh
3. Test gphoto2 nhận máy:
   ```bash
   gphoto2 --auto-detect
   gphoto2 --capture-image-and-download
   ```
4. Trong `.env` set: `CAMERA_MODE=dslr`
5. Restart server

**Camera tested OK với gphoto2:**
- Canon: Hầu hết EOS DSLR + R-series Mirrorless
- Nikon: D-series + Z-series (một số model)
- Fuji: X-T series, X-S series (cần bật "USB Auto / Tether Auto" trong menu máy)
- Sony: **Một phần** — Sony A7 IV trở lên cần Sony Camera Remote SDK riêng (chưa hỗ trợ trong app này)

Nếu máy chị không nhận, chị paste output của `gphoto2 --auto-detect` em fix.

### B. Cấu hình máy in Canon

1. **Cài driver Canon trên Mac** (nếu chưa có):
   - Selphy CP series: Mac thường nhận tự động qua AirPrint hoặc USB
   - PIXMA series: tải driver tại canon.com/support
2. System Settings → Printers & Scanners → "+" → chọn máy Canon
3. Lấy tên printer:
   ```bash
   lpstat -p
   ```
4. Copy tên (ví dụ `Canon_SELPHY_CP1500` hoặc `Canon_PIXMA_TS5350`) vào `.env`:
   ```env
   PRINT_ENABLED=true
   PRINTER_NAME=Canon_SELPHY_CP1500
   ```
5. Test in trước sự kiện:
   ```bash
   lp -d Canon_SELPHY_CP1500 -o media=4x6 -o fit-to-page assets/frames/sanrio/frame.png
   ```

**Lưu ý cho Selphy CP:** dùng giấy + mực Canon KP-108IN (108 ảnh 10x15cm, giá ~600k). 1 tiệc 30 khách x 2 ảnh ~ 60 lượt in vẫn dư.

**Lưu ý cho PIXMA:** in ảnh chậm hơn Selphy (~30 giây/ảnh) nên khách phải xếp hàng. Selphy chỉ ~50 giây/ảnh nhưng máy chuyên dụng nên ổn định hơn.

### C. QR code — chọn 1 trong 2 mode

#### 🌟 Mode B (recommend): Vercel + Supabase — QR sống mãi sau sự kiện

Setup 1 lần (~15 phút), khách quét QR ở đâu cũng được, ảnh giữ vĩnh viễn.

**Bước 1 — Tạo Supabase:**
1. https://supabase.com → New project (free)
2. Settings → API → copy `URL` và `anon public key`
3. Storage → New bucket → tên `photobooth` → Public ✓

**Bước 2 — Deploy `web/` lên Vercel:**
1. https://vercel.com → Add New Project → Import repo `Photoboth-chibi` từ GitHub
2. **Root Directory: `web`** (quan trọng!)
3. Environment Variables, thêm 4 biến:
   ```
   NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_BUCKET = photobooth
   NEXT_PUBLIC_EVENT_NAME = Sinh Nhật Vui Vẻ
   NEXT_PUBLIC_EVENT_HASHTAG = #happybirthday
   ```
4. Deploy → đợi ~2 phút → copy URL (ví dụ `photoboth-chibi.vercel.app`)

**Bước 3 — Link 2 thứ trong `.env` local:**
```env
GALLERY_URL=https://photoboth-chibi.vercel.app
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_BUCKET=photobooth
```

→ Khi chụp, ảnh tự upload Supabase, QR trỏ Vercel page. Khách quét ở 4G hay WiFi đều xem + tải được.

#### 🏠 Mode A: Local IP — đơn giản, không internet

Để trống `GALLERY_URL` và Supabase. App tự dò IP nội bộ. Khách phải:
1. Kết nối WiFi sự kiện
2. Quét QR → trang web mobile-friendly hiện ảnh + nút tải

**In bảng WiFi đặt cạnh booth:** "📶 WiFi: [tên] / [pass] — Quét QR sau khi kết nối"

**Kiểm tra IP:**
```bash
ipconfig getifaddr en0   # Mac WiFi thường là en0
```

Sau sự kiện QR die (vì IP local). Phù hợp tiệc nhỏ, ít tốn config.

### D. Hiển thị full-screen trên iPad/touchscreen

Trên thiết bị hiển thị, mở Safari/Chrome → http://[ip-máy-server]:8000 → bấm "Add to Home Screen" để chạy fullscreen như native app.

---

## 🎨 Tùy chỉnh khung

Mỗi theme có 1 file SVG: `assets/frames/{dinosaur,frozen,sanrio}/frame.svg`

Mở file SVG bằng VS Code/Inkscape để chỉnh màu, thêm sticker. Sau khi sửa:

```bash
python -m backend.build_frames
```

Muốn dùng PNG sẵn (mua từ Creative Market, Etsy)? Đặt file PNG 1200x1800 vào `assets/frames/{theme}/frame.png` (vùng giữa 1000x1300 từ y=220 nên trong suốt — đó là chỗ ảnh khách).

Muốn thêm theme mới? Tạo folder mới trong `assets/frames/` + thêm card vào `frontend/index.html`.

---

## 🛠 Troubleshooting

| Triệu chứng | Fix |
|---|---|
| `Camera not ready` | Check `.env` `CAMERA_MODE`. Webcam: cần permissions cho Terminal trong System Settings → Privacy → Camera |
| `gphoto2: could not claim USB device` | Đóng Photos.app, Image Capture, các app dùng camera. `pkill PTPCamera` |
| Khung lệch / ảnh bị crop sai | Mở `backend/compositor.py` chỉnh `win_w`, `win_h`, `win_x`, `win_y` |
| QR code mở 404 | Supabase chưa config OR bucket chưa Public. Check `SUPABASE_URL` không phải `xxxxx` |
| Print failed | `lpstat -p` xem printer đúng tên chưa. Test thử `lp -d <name> file.jpg` |

---

## 📁 Cấu trúc

```
photobooth/
├── backend/             # 🐍 Python — chạy local trên Mac (chụp + in)
│   ├── main.py          # FastAPI app
│   ├── camera.py        # gphoto2 / webcam
│   ├── compositor.py    # Pillow overlay
│   ├── storage.py       # Supabase upload + QR
│   ├── printer.py       # CUPS lp (Canon)
│   └── build_frames.py  # SVG → PNG
├── frontend/            # 🖼️ UI cảm ứng — chạy trên iPad/touchscreen
│   ├── index.html
│   ├── style.css
│   └── app.js
├── web/                 # 🌐 Next.js — deploy lên Vercel cho khách quét QR
│   ├── app/
│   │   ├── page.tsx           # Landing
│   │   └── photo/[id]/page.tsx # Photo viewer
│   ├── package.json
│   └── README.md
├── assets/
│   └── frames/
│       ├── dinosaur/frame.svg
│       ├── frozen/frame.svg
│       └── sanrio/frame.svg
├── output/              # Ảnh chụp lưu vào đây (gitignored)
├── requirements.txt     # Python deps
├── .env.example
└── README.md
```

## 🌊 Data flow (Mode B)

```
   📷 DSLR (USB)
       ↓
  🐍 Mac local app  ─upload→  ☁️ Supabase Storage
       ↓                            ↑
  🖨️ Canon printer            (lưu vĩnh viễn)
       ↓                            ↑
  📺 Touchscreen UI         🌐 Vercel page ←─ 📱 Khách quét QR
       ↓
   🔗 QR code → vercel.app/photo/{id}
```
