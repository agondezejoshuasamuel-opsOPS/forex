const $ = (id) => document.getElementById(id);

const chart = $("chart");
const ctx = chart.getContext("2d");

function fmt(v, digits = 5) {
  return v === null || v === undefined || !Number.isFinite(Number(v))
    ? "—"
    : Number(v).toFixed(digits);
}

function resizeCanvas() {
  const rect = chart.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  chart.width = Math.max(1, Math.floor(rect.width * ratio));
  chart.height = Math.max(1, Math.floor(rect.height * ratio));
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function draw(data) {
  const rect = chart.getBoundingClientRect();
  const W = rect.width;
  const H = rect.height;
  ctx.clearRect(0, 0, W, H);

  const rows = data.candles || [];
  const valid = rows.filter(r => Number.isFinite(r.close));
  if (valid.length < 2) {
    ctx.fillStyle = "#8c9ab0";
    ctx.font = "14px system-ui";
    ctx.fillText("Waiting for enough price data...", 20, 30);
    return;
  }

  const values = [];
  for (const r of valid) {
    values.push(r.close);
    if (Number.isFinite(r.ema20)) values.push(r.ema20);
    if (Number.isFinite(r.ema50)) values.push(r.ema50);
  }

  let min = Math.min(...values);
  let max = Math.max(...values);
  const padding = Math.max((max - min) * 0.12, 0.00015);
  min -= padding; max += padding;

  const left = 12, right = 12, top = 16, bottom = 24;
  const plotW = W - left - right;
  const plotH = H - top - bottom;

  const x = i => left + (i / (valid.length - 1)) * plotW;
  const y = v => top + (max - v) / (max - min) * plotH;

  ctx.strokeStyle = "#1e2a3c";
  ctx.lineWidth = 1;
  for (let g = 0; g <= 5; g++) {
    const gy = top + (g / 5) * plotH;
    ctx.beginPath();
    ctx.moveTo(left, gy);
    ctx.lineTo(W - right, gy);
    ctx.stroke();

    const label = (max - (g / 5) * (max - min)).toFixed(5);
    ctx.fillStyle = "#66758c";
    ctx.font = "11px system-ui";
    ctx.fillText(label, left + 4, gy - 4);
  }

  function line(key, stroke, width) {
    ctx.beginPath();
    let started = false;
    valid.forEach((r, i) => {
      const value = Number(r[key]);
      if (!Number.isFinite(value)) return;
      const px = x(i), py = y(value);
      if (!started) { ctx.moveTo(px, py); started = true; }
      else ctx.lineTo(px, py);
    });
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
    ctx.stroke();
  }

  line("ema50", "#e9c46a", 1.5);
  line("ema20", "#64a8ff", 1.5);
  line("close", "#43d19e", 2.2);

  const latest = valid[valid.length - 1];
  ctx.fillStyle = "#43d19e";
  ctx.beginPath();
  ctx.arc(x(valid.length - 1), y(latest.close), 4, 0, Math.PI * 2);
  ctx.fill();
}

function updateUI(data) {
  $("mode").textContent = data.mode;
  $("price").textContent = fmt(data.price);
  $("state").textContent = data.analysis?.state || "—";
  $("score").textContent = data.analysis?.ready ? data.analysis.score : "warming";
  $("rsi").textContent = fmt(data.rsi14, 2);

  $("ema20").textContent = fmt(data.ema20);
  $("ema50").textContent = fmt(data.ema50);
  $("macd").textContent = fmt(data.macd, 6);
  $("macdSignal").textContent = fmt(data.macd_signal, 6);
  $("atr").textContent = fmt(data.atr14, 6);

  $("headline").textContent = data.analysis?.message || "Waiting for market data...";

  const reasons = $("reasons");
  reasons.innerHTML = "";
  const reasonList = data.analysis?.reasons || [];
  if (!reasonList.length) reasonList.push("The algorithm is waiting for enough candles.");
  reasonList.forEach(r => {
    const li = document.createElement("li");
    li.textContent = r;
    reasons.appendChild(li);
  });

  const details = $("details");
  details.innerHTML = "";
  const detailList = data.analysis?.details || [];
  detailList.forEach(r => {
    const li = document.createElement("li");
    li.textContent = r;
    details.appendChild(li);
  });

  draw(data);
}

function connect() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${protocol}://${location.host}/ws`);

  ws.onopen = () => $("mode").textContent = "CONNECTED";
  ws.onmessage = event => {
    try { updateUI(JSON.parse(event.data)); }
    catch (e) { console.error(e); }
  };
  ws.onclose = () => {
    $("mode").textContent = "RECONNECTING...";
    setTimeout(connect, 1500);
  };
  ws.onerror = () => ws.close();
}

window.addEventListener("resize", () => {
  resizeCanvas();
});

resizeCanvas();
connect();
