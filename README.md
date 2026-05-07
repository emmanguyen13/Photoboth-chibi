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

### C. QR code mode LOCAL (mặc định, không cần internet)

App tự động dò IP nội bộ của máy Mac. Khi khách quét QR:
1. Khách kết nối WiFi sự kiện
2. Quét QR → trang web hiện ra với ảnh + nút "Tải về máy"
3. Tải xong là ảnh nằm trong Photos của khách

**Cần làm:** Chia sẻ password WiFi cho khách (in lên 1 bảng nhỏ đặt cạnh photobooth: "📶 WiFi: [tên] / [pass] — Quét QR sau khi kết nối nha!")

**Kiểm tra IP đúng chưa:**
```bash
ipconfig getifaddr en0   # IP WiFi (Mac thường là en0)
```

Sau khi server chạy, mở `/api/status` xem IP đang trỏ. Nếu sai router, thêm `PUBLIC_URL=http://192.168.x.x:8000` vào `.env` để override.

**Optional — QR cloud (khách giữ được ảnh sau sự kiện):** uncomment block SUPABASE trong `.env.example`, tạo project free tại supabase.com.

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
├── backend/
│   ├── main.py          # FastAPI app
│   ├── camera.py        # gphoto2 / webcam
│   ├── compositor.py    # Pillow overlay
│   ├── storage.py       # Supabase + QR
│   ├── printer.py       # CUPS lp
│   └── build_frames.py  # SVG → PNG
├── frontend/
│   ├── index.html       # Touchscreen UI
│   ├── style.css
│   └── app.js
├── assets/
│   └── frames/
│       ├── dinosaur/frame.svg
│       ├── frozen/frame.svg
│       └── sanrio/frame.svg
├── output/              # Ảnh đã chụp lưu vào đây
├── requirements.txt
├── .env.example
└── README.md
```
