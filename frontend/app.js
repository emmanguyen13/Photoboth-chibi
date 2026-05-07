const screens = {
  theme: document.getElementById('screen-theme'),
  countdown: document.getElementById('screen-countdown'),
  processing: document.getElementById('screen-processing'),
  result: document.getElementById('screen-result'),
};
const statusBar = document.getElementById('status-bar');
const countdownEl = document.getElementById('countdown');
const countdownHint = document.getElementById('countdown-hint');
const resultPhoto = document.getElementById('result-photo');
const resultQr = document.getElementById('result-qr');
const btnPrint = document.getElementById('btn-print');
const btnAgain = document.getElementById('btn-again');
const printStatus = document.getElementById('print-status');
const confetti = document.getElementById('confetti');

const COUNTDOWN_HINTS = {
  3: '🎬 Sẵn sàng nha~',
  2: '😊 Cười tươi lên!',
  1: '✨ Tạo dáng cute!',
};
const CONFETTI_PIECES = ['🦖', '❄️', '🎀', '⭐', '💖', '✨', '🌸', '🍃'];

let currentTheme = null;
let currentPhotoId = null;
let serverStatus = {};

function show(name) {
  Object.values(screens).forEach(s => s.classList.remove('active'));
  screens[name].classList.add('active');
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function loadStatus() {
  try {
    const r = await fetch('/api/status');
    serverStatus = await r.json();
    if (serverStatus.camera_ready) {
      const qrMode = serverStatus.supabase_configured ? '☁️ cloud' : '🏠 local IP';
      const printMode = serverStatus.print_enabled ? '✓ in OK' : '✗ in tắt';
      statusBar.textContent = `📷 ${serverStatus.camera_mode} • 🖨️ ${printMode} • 📱 QR ${qrMode}`;
      statusBar.className = 'status-bar ready';
    } else {
      statusBar.textContent = '⚠️ Camera chưa kết nối — kiểm tra .env';
      statusBar.className = 'status-bar error';
    }
  } catch {
    statusBar.textContent = '⚠️ Server không phản hồi';
    statusBar.className = 'status-bar error';
  }
}

document.querySelectorAll('.theme-card').forEach(card => {
  card.addEventListener('click', () => {
    currentTheme = card.dataset.theme;
    startCountdown();
  });
});

async function startCountdown() {
  show('countdown');
  for (const n of [3, 2, 1]) {
    countdownEl.textContent = n;
    countdownHint.textContent = COUNTDOWN_HINTS[n];
    await sleep(900);
  }
  countdownEl.textContent = '📸';
  countdownHint.textContent = '✨ Click! ✨';
  await sleep(350);
  await capture();
}

async function capture() {
  show('processing');
  try {
    const r = await fetch(`/api/capture?theme=${currentTheme}`, { method: 'POST' });
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: r.statusText }));
      throw new Error(err.detail || 'Capture failed');
    }
    const data = await r.json();
    currentPhotoId = data.photo_id;
    resultPhoto.src = data.preview_url + '?t=' + Date.now();
    resultQr.src = data.qr_url + '&t=' + Date.now();
    printStatus.textContent = '';
    printStatus.className = 'print-status';
    show('result');
    burstConfetti();
  } catch (e) {
    alert('Lỗi: ' + e.message);
    show('theme');
  }
}

function burstConfetti() {
  confetti.innerHTML = '';
  for (let i = 0; i < 28; i++) {
    const span = document.createElement('span');
    span.textContent = CONFETTI_PIECES[Math.floor(Math.random() * CONFETTI_PIECES.length)];
    span.style.left = (10 + Math.random() * 80) + '%';
    span.style.setProperty('--cx', (Math.random() * 200 - 100) + 'px');
    span.style.fontSize = (16 + Math.random() * 24) + 'px';
    span.style.animationDelay = (Math.random() * 0.6) + 's';
    span.style.animationDuration = (2.5 + Math.random() * 1.5) + 's';
    confetti.appendChild(span);
  }
}

btnPrint.addEventListener('click', async () => {
  if (!currentPhotoId) return;
  if (!serverStatus.print_enabled) {
    printStatus.textContent = '⚠️ In chưa được bật. Set PRINT_ENABLED=true trong .env';
    printStatus.className = 'print-status error';
    return;
  }
  btnPrint.disabled = true;
  printStatus.textContent = '🖨️ Đang gửi tới máy in...';
  printStatus.className = 'print-status';
  try {
    const r = await fetch(`/api/print?photo_id=${currentPhotoId}&copies=1`, { method: 'POST' });
    const data = await r.json();
    if (data.ok) {
      printStatus.textContent = '✓ Đã gửi! Ảnh đang ra nha~';
    } else {
      printStatus.textContent = '✗ ' + data.message;
      printStatus.className = 'print-status error';
    }
  } catch (e) {
    printStatus.textContent = '✗ ' + e.message;
    printStatus.className = 'print-status error';
  } finally {
    setTimeout(() => { btnPrint.disabled = false; }, 1800);
  }
});

btnAgain.addEventListener('click', () => {
  currentTheme = null;
  currentPhotoId = null;
  confetti.innerHTML = '';
  show('theme');
});

loadStatus();
setInterval(loadStatus, 10000);
