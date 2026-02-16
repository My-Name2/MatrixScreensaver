import streamlit as st
import json

st.set_page_config(page_title="Matrix Word Rain", layout="wide", initial_sidebar_state="expanded")

# --- Sidebar ---
st.sidebar.markdown("# 🖥️ Matrix Word Rain")
st.sidebar.markdown("---")

words_input = st.sidebar.text_area(
    "Words (one per line or space-separated):",
    value="Inessentialist\nessentialism\nof\nessentials\nwith\nthe\nessential\nessentialing\ninessentially\nessential",
    height=180,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Layout")
num_columns = st.sidebar.slider("Number of streams", 8, 60, 28)
font_size = st.sidebar.slider("Font size (px)", 8, 22, 13)
trails_per_col = st.sidebar.slider("Trails per column", 1, 4, 2)
gap_words = st.sidebar.slider("Gap between trails (words)", 0, 10, 2)

st.sidebar.markdown("---")
st.sidebar.markdown("### Speed")
base_speed = st.sidebar.slider("Fall speed (lower = faster)", 0.5, 6.0, 2.0, 0.25)
speed_variance = st.sidebar.slider("Speed variance", 0.0, 3.0, 1.0, 0.25)
spawn_rate = st.sidebar.slider("Spawn rate (lower = faster)", 0.1, 1.5, 0.35, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### Style")
brightness = st.sidebar.slider("Glow brightness", 0.3, 1.0, 0.8, 0.05)
trail_length = st.sidebar.slider("Trail length (words)", 3, 25, 12)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎬 GIF Export")
gif_duration = st.sidebar.slider("GIF duration (sec)", 2, 15, 5)
gif_fps = st.sidebar.slider("GIF FPS", 10, 30, 15)
gif_width = st.sidebar.slider("GIF width (px)", 320, 1280, 640, 10)
gif_height = st.sidebar.slider("GIF height (px)", 200, 800, 400, 10)

if st.sidebar.button("🔄 Regenerate", use_container_width=True):
    st.rerun()

# Parse words
raw = words_input.replace("\n", " ").split()
words = [w.strip() for w in raw if w.strip()]
if not words:
    words = ["essential"]

words_json = json.dumps(words)

html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gif.js/0.2.0/gif.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body, html {{
    width: 100%; height: 100%; overflow: hidden;
    background: #000;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
  }}
  #matrix {{
    position: relative;
    width: 100%; height: 100vh;
    overflow: hidden;
    background: #000;
  }}
  .w {{
    position: absolute;
    white-space: nowrap;
    font-size: {font_size}px;
    line-height: 1;
    pointer-events: none;
  }}
  #matrix::after {{
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(0deg,
      rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px,
      transparent 1px, transparent 3px);
    pointer-events: none; z-index: 10;
  }}
  #matrix::before {{
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.5) 100%);
    pointer-events: none; z-index: 11;
  }}
  #rec-btn {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 100;
    background: #001a00;
    color: #00ff41;
    border: 2px solid #00ff41;
    padding: 12px 24px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  #rec-btn:hover {{
    background: #003300;
    box-shadow: 0 0 15px #00ff4155;
  }}
  #rec-btn.recording {{
    border-color: #ff4444;
    color: #ff4444;
    animation: pulse 1s infinite;
  }}
  #rec-btn.encoding {{
    border-color: #ffaa00;
    color: #ffaa00;
    cursor: wait;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  #progress-bar {{
    position: fixed;
    bottom: 70px;
    right: 20px;
    z-index: 100;
    width: 180px;
    height: 6px;
    background: #001a00;
    border: 1px solid #003300;
    display: none;
  }}
  #progress-fill {{
    height: 100%;
    width: 0%;
    background: #00ff41;
    transition: width 0.1s;
  }}
</style>
</head>
<body>
<div id="matrix"></div>
<button id="rec-btn" onclick="toggleRecord()">⏺ Record GIF</button>
<div id="progress-bar"><div id="progress-fill"></div></div>
<script>
(function() {{
  const words = {words_json};
  const numCols = {num_columns};
  const maxTrails = {trails_per_col};
  const gapWords = {gap_words};
  const baseSpeed = {base_speed};
  const speedVar = {speed_variance};
  const bri = {brightness};
  const trailLen = {trail_length};
  const spawnMs = {spawn_rate} * 1000;
  const C = document.getElementById('matrix');
  const H = C.offsetHeight || 750;
  const W = C.offsetWidth || 1200;
  const colW = W / numCols;
  const lnH = {font_size} * 1.6;
  const gapPx = gapWords * lnH;

  function pick(last) {{
    let w = words[Math.floor(Math.random() * words.length)];
    let t = 0;
    while (w === last && words.length > 1 && t++ < 10)
      w = words[Math.floor(Math.random() * words.length)];
    return w;
  }}

  function Trail(x) {{
    const v = (Math.random() - 0.5) * 2 * speedVar;
    this.x = x;
    this.headY = -lnH;
    this.speed = H / Math.max(0.5, baseSpeed + v);
    this.drops = [];
    this.lastWord = '';
    this.lastSpawn = 0;
    this.maxTravel = H * (0.4 + Math.random() * 1.0);
    this.traveled = 0;
    this.done = false;
    this.dead = false;
  }}

  Trail.prototype.tailY = function() {{
    if (this.drops.length === 0) return this.headY;
    return this.drops[0].y;
  }};

  Trail.prototype.update = function(now, dt) {{
    const mv = this.speed * dt;
    this.headY += mv;
    this.traveled += mv;

    if (!this.done && now - this.lastSpawn >= spawnMs * (0.7 + Math.random() * 0.6)) {{
      const word = pick(this.lastWord);
      this.lastWord = word;
      const el = document.createElement('div');
      el.className = 'w';
      el.textContent = word;
      el.style.left = this.x + 'px';
      el.style.top = this.headY + 'px';
      C.appendChild(el);
      this.drops.push({{ el: el, y: this.headY }});
      this.lastSpawn = now;
    }}

    if (!this.done && this.traveled >= this.maxTravel) {{
      this.done = true;
    }}

    for (let i = this.drops.length - 1; i >= 0; i--) {{
      const d = this.drops[i];
      const dist = (this.headY - d.y) / lnH;

      if (dist <= 0.5) {{
        d.el.style.color = '#fff';
        d.el.style.textShadow = '0 0 14px #00ff41,0 0 30px #00ff41,0 0 5px #fff';
        d.el.style.opacity = '1';
      }} else if (dist <= trailLen * 0.25) {{
        d.el.style.color = '#00ff41';
        d.el.style.textShadow = '0 0 10px #00ff41,0 0 3px #00cc33';
        d.el.style.opacity = (bri * 0.95).toFixed(2);
      }} else if (dist <= trailLen * 0.6) {{
        const f = (dist - trailLen * 0.25) / (trailLen * 0.35);
        d.el.style.color = '#00aa30';
        d.el.style.textShadow = '0 0 4px #00882a';
        d.el.style.opacity = Math.max(0.08, bri * (0.7 - f * 0.4)).toFixed(2);
      }} else if (dist <= trailLen) {{
        const f = (dist - trailLen * 0.6) / (trailLen * 0.4);
        d.el.style.color = '#005a15';
        d.el.style.textShadow = 'none';
        d.el.style.opacity = Math.max(0.02, 0.15 - f * 0.13).toFixed(2);
      }} else {{
        d.el.remove();
        this.drops.splice(i, 1);
        continue;
      }}
    }}

    if (this.done && this.drops.length === 0) {{
      this.dead = true;
    }}
  }};

  function Column(index) {{
    this.index = index;
    this.x = index * colW;
    this.trails = [];
    const t = new Trail(this.x);
    t.headY = Math.random() * H;
    t.lastSpawn = -Math.random() * spawnMs * 3;
    this.trails.push(t);
  }}

  Column.prototype.update = function(now, dt) {{
    for (let i = this.trails.length - 1; i >= 0; i--) {{
      this.trails[i].update(now, dt);
      if (this.trails[i].dead) this.trails.splice(i, 1);
    }}

    if (this.trails.length < maxTrails) {{
      let canSpawn = true;
      if (this.trails.length > 0) {{
        let lowestHead = -Infinity;
        for (let i = 0; i < this.trails.length; i++) {{
          if (this.trails[i].headY > lowestHead) lowestHead = this.trails[i].headY;
        }}
        const trailTopOfNewest = lowestHead - trailLen * lnH;
        if (trailTopOfNewest < gapPx) canSpawn = false;
      }}
      if (canSpawn) {{
        const t = new Trail(this.x);
        t.headY = -lnH;
        t.lastSpawn = now;
        this.trails.push(t);
      }}
    }}

    if (this.trails.length === 0) {{
      const t = new Trail(this.x);
      t.headY = -lnH;
      t.lastSpawn = now;
      this.trails.push(t);
    }}
  }};

  const columns = [];
  for (let i = 0; i < numCols; i++) columns.push(new Column(i));

  let lt = performance.now();
  function frame(now) {{
    const dt = (now - lt) / 1000;
    lt = now;
    for (let i = 0; i < columns.length; i++) columns[i].update(now, dt);
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);

  // ==================== GIF RECORDING ====================
  const gifDuration = {gif_duration};
  const gifFps = {gif_fps};
  const gifW = {gif_width};
  const gifH = {gif_height};
  let isRecording = false;
  let isEncoding = false;

  window.toggleRecord = function() {{
    if (isEncoding) return;
    if (isRecording) return; // let it finish
    startRecording();
  }};

  function startRecording() {{
    const btn = document.getElementById('rec-btn');
    const bar = document.getElementById('progress-bar');
    const fill = document.getElementById('progress-fill');

    isRecording = true;
    btn.className = 'recording';
    btn.textContent = '⏺ Recording...';
    bar.style.display = 'block';
    fill.style.width = '0%';

    // Create offscreen canvas
    const canvas = document.createElement('canvas');
    canvas.width = gifW;
    canvas.height = gifH;
    const ctx = canvas.getContext('2d');

    const totalFrames = gifDuration * gifFps;
    const frameDelay = 1000 / gifFps;
    let framesCaptured = 0;
    const frameDataList = [];

    function captureFrame() {{
      if (framesCaptured >= totalFrames) {{
        encodeGif(frameDataList, frameDelay);
        return;
      }}

      // Draw black background
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, gifW, gifH);

      // Scale factor from live view to gif
      const sx = gifW / W;
      const sy = gifH / H;

      // Draw all .w elements
      const els = C.querySelectorAll('.w');
      els.forEach(el => {{
        const left = parseFloat(el.style.left) || 0;
        const top = parseFloat(el.style.top) || 0;
        const color = el.style.color || '#00ff41';
        const opacity = parseFloat(el.style.opacity) || 0;
        const text = el.textContent;

        if (opacity < 0.03) return;

        ctx.save();
        ctx.globalAlpha = opacity;
        ctx.fillStyle = color;
        ctx.font = Math.max(6, Math.round({font_size} * sx)) + 'px Share Tech Mono, Courier New, monospace';

        // Add glow for bright words
        if (color === '#fff' || color === '#ffffff' || color === 'rgb(255, 255, 255)') {{
          ctx.shadowColor = '#00ff41';
          ctx.shadowBlur = 8 * sx;
        }} else if (color === '#00ff41') {{
          ctx.shadowColor = '#00ff41';
          ctx.shadowBlur = 4 * sx;
        }} else {{
          ctx.shadowBlur = 0;
        }}

        ctx.fillText(text, left * sx, (top + {font_size}) * sy);
        ctx.restore();
      }});

      // Capture frame data
      frameDataList.push(ctx.getImageData(0, 0, gifW, gifH));
      framesCaptured++;
      fill.style.width = (framesCaptured / totalFrames * 50) + '%';

      setTimeout(captureFrame, frameDelay);
    }}

    captureFrame();
  }}

  function encodeGif(frames, delay) {{
    const btn = document.getElementById('rec-btn');
    const bar = document.getElementById('progress-bar');
    const fill = document.getElementById('progress-fill');

    isRecording = false;
    isEncoding = true;
    btn.className = 'encoding';
    btn.textContent = '⚙ Encoding...';

    const gif = new GIF({{
      workers: 2,
      quality: 10,
      width: gifW,
      height: gifH,
      workerScript: 'https://cdnjs.cloudflare.com/ajax/libs/gif.js/0.2.0/gif.worker.js'
    }});

    // Add frames
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = gifW;
    tempCanvas.height = gifH;
    const tempCtx = tempCanvas.getContext('2d');

    for (let i = 0; i < frames.length; i++) {{
      tempCtx.putImageData(frames[i], 0, 0);
      gif.addFrame(tempCtx, {{ copy: true, delay: delay }});
    }}

    gif.on('progress', function(p) {{
      fill.style.width = (50 + p * 50) + '%';
    }});

    gif.on('finished', function(blob) {{
      isEncoding = false;
      btn.className = '';
      btn.textContent = '⏺ Record GIF';
      bar.style.display = 'none';

      // Download
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'matrix_rain.gif';
      a.click();
      URL.revokeObjectURL(url);
    }});

    gif.render();
  }}
}})();
</script>
</body>
</html>
"""

st.components.v1.html(html, height=750, scrolling=False)

st.markdown(
    """
    <style>
    .stApp { background-color: #000000 !important; }
    header[data-testid="stHeader"] { background-color: #000000 !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }
    section[data-testid="stSidebar"] {
        background-color: #050f05 !important;
        border-right: 1px solid #003300 !important;
    }
    section[data-testid="stSidebar"] * { color: #00dd38 !important; }
    section[data-testid="stSidebar"] textarea {
        background-color: #001a00 !important;
        color: #00ff41 !important;
        border-color: #003300 !important;
        font-family: 'Courier New', monospace !important;
    }
    section[data-testid="stSidebar"] button {
        background-color: #002200 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #003300 !important;
    }
    iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
