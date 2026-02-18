import streamlit as st
import json

st.set_page_config(page_title="Matrix Word Rain", layout="wide", initial_sidebar_state="collapsed")

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
gap_words = st.sidebar.slider("Gap between trails (words)", 0, 10, 4)

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
st.sidebar.markdown("### 🎨 Color")

color_mode = st.sidebar.radio("Color mode", ["Classic Green", "Solid Color", "Rainbow"], index=0)

solid_color = "#00ff41"
rainbow_speed = 3.0

if color_mode == "Solid Color":
    solid_color = st.sidebar.color_picker("Pick a color", "#00ff41")
elif color_mode == "Rainbow":
    rainbow_speed = st.sidebar.slider("Rainbow cycle speed (lower = faster)", 0.5, 10.0, 3.0, 0.25)

if st.sidebar.button("🔄 Regenerate", use_container_width=True):
    st.rerun()

# Parse words
raw = words_input.replace("\n", " ").split()
words = [w.strip() for w in raw if w.strip()]
if not words:
    words = ["essential"]

words_json = json.dumps(words)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

sr, sg, sb = hex_to_rgb(solid_color)
color_mode_js = {"Classic Green": "green", "Solid Color": "solid", "Rainbow": "rainbow"}[color_mode]

html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body, html {{
    width: 100%; height: 100%; overflow: hidden;
    background: #000;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
  }}
  #matrix {{
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    overflow: hidden;
    background: radial-gradient(ellipse at center, #000d00 0%, #000 70%);
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
  #fsBtn {{
    position: fixed;
    top: 12px; right: 14px;
    z-index: 200;
    background: rgba(0,20,0,0.75);
    border: 1px solid #00ff41;
    color: #00ff41;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 12px;
    padding: 5px 10px;
    cursor: pointer;
    border-radius: 3px;
    letter-spacing: 0.05em;
    transition: background 0.2s, box-shadow 0.2s;
  }}
  #fsBtn:hover {{
    background: rgba(0,60,0,0.9);
    box-shadow: 0 0 8px #00ff41;
  }}
</style>
</head>
<body>
<div id="matrix"></div>
<button id="fsBtn">⛶ FULLSCREEN</button>
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
  const colorMode = "{color_mode_js}";
  const solidR = {sr}, solidG = {sg}, solidB = {sb};
  const rainbowSpeed = {rainbow_speed};

  const C = document.getElementById('matrix');
  let H = window.innerHeight;
  let W = window.innerWidth;
  const lnH = {font_size} * 1.6;
  let colW = W / numCols;

  // Gap in pixels that must exist between the TAIL of one trail and the HEAD of a new one
  // We measure this as: new trail starts at y=-lnH, so the previous trail's head
  // must be at least (trailLen + gapWords) * lnH below the top before we spawn.
  const minHeadBeforeSpawn = (trailLen + gapWords) * lnH;

  const colHueOffsets = [];
  for (let i = 0; i < numCols; i++) {{
    colHueOffsets.push((i / numCols) * 360);
  }}

  function hslToRgb(h, s, l) {{
    s /= 100; l /= 100;
    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return [Math.round(f(0)*255), Math.round(f(8)*255), Math.round(f(4)*255)];
  }}

  function getBaseColor(colIndex, now) {{
    if (colorMode === 'green') return [0, 255, 65];
    if (colorMode === 'solid') return [solidR, solidG, solidB];
    const hue = (((now / (rainbowSpeed * 1000)) * 360) + colHueOffsets[colIndex]) % 360;
    return hslToRgb(hue, 100, 55);
  }}

  function pick(last) {{
    let w = words[Math.floor(Math.random() * words.length)];
    let t = 0;
    while (w === last && words.length > 1 && t++ < 10)
      w = words[Math.floor(Math.random() * words.length)];
    return w;
  }}

  function Trail(x, colIndex) {{
    const v = (Math.random() - 0.5) * 2 * speedVar;
    this.x = x;
    this.colIndex = colIndex;
    this.headY = -lnH;
    this.speed = H / Math.max(0.5, baseSpeed + v);
    this.drops = [];
    this.lastWord = '';
    this.lastSpawn = 0;
    // Travel the full screen height plus trail tail length so tail clears bottom
    this.maxTravel = H + trailLen * lnH;
    this.traveled = 0;
    this.done = false;
    this.dead = false;
  }}

  Trail.prototype.update = function(now, dt) {{
    const mv = this.speed * dt;
    this.headY += mv;
    this.traveled += mv;

    const [br, bg, bb] = getBaseColor(this.colIndex, now);

    // Spawn words at head while trail is active and head is within screen
    if (!this.done && this.headY < H + lnH) {{
      if (now - this.lastSpawn >= spawnMs * (0.7 + Math.random() * 0.6)) {{
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
    }}

    if (!this.done && this.traveled >= this.maxTravel) {{
      this.done = true;
    }}

    for (let i = this.drops.length - 1; i >= 0; i--) {{
      const d = this.drops[i];
      const dist = (this.headY - d.y) / lnH;

      if (dist <= 0.5) {{
        d.el.style.color = '#fff';
        d.el.style.textShadow = `0 0 14px rgb(${{br}},${{bg}},${{bb}}),0 0 30px rgb(${{br}},${{bg}},${{bb}}),0 0 5px #fff`;
        d.el.style.opacity = '1';
      }} else if (dist <= trailLen * 0.25) {{
        d.el.style.color = `rgb(${{br}},${{bg}},${{bb}})`;
        d.el.style.textShadow = `0 0 10px rgb(${{br}},${{bg}},${{bb}}),0 0 3px rgba(${{br}},${{bg}},${{bb}},0.6)`;
        d.el.style.opacity = (bri * 0.95).toFixed(2);
      }} else if (dist <= trailLen * 0.6) {{
        const f = (dist - trailLen * 0.25) / (trailLen * 0.35);
        const dr = Math.round(br * 0.55), dg = Math.round(bg * 0.55), db = Math.round(bb * 0.55);
        d.el.style.color = `rgb(${{dr}},${{dg}},${{db}})`;
        d.el.style.textShadow = `0 0 4px rgba(${{dr}},${{dg}},${{db}},0.5)`;
        d.el.style.opacity = Math.max(0.08, bri * (0.7 - f * 0.4)).toFixed(2);
      }} else if (dist <= trailLen) {{
        const f = (dist - trailLen * 0.6) / (trailLen * 0.4);
        const dr = Math.round(br * 0.25), dg = Math.round(bg * 0.25), db = Math.round(bb * 0.25);
        d.el.style.color = `rgb(${{dr}},${{dg}},${{db}})`;
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

  // Column manages a queue of sequentially-spawned trails.
  // Key fix: a new trail only spawns when the PREVIOUS trail's head has moved
  // far enough down that (trailLen + gapWords) * lnH of clear space exists
  // at the top of the column for the new trail to start without overlap.
  function Column(index) {{
    this.index = index;
    this.x = index * colW;
    this.trails = [];
    // Seed initial trail at a random position so screen fills immediately
    const t = new Trail(this.x, index);
    t.headY = Math.random() * H;
    t.lastSpawn = performance.now() - Math.random() * spawnMs * 3;
    this.trails.push(t);
  }}

  Column.prototype.canSpawnNext = function() {{
    if (this.trails.length === 0) return true;
    if (this.trails.length >= maxTrails) return false;

    // Find the trail whose head is furthest down (most advanced).
    // A new trail starts at headY = -lnH and moves at a similar speed.
    // To avoid overlap, we need the leading trail's head to be at least
    // minHeadBeforeSpawn pixels below the top, so the new trail's full
    // body (trailLen words) plus the gap fits above it when they're closest.
    let maxHeadY = -Infinity;
    for (let i = 0; i < this.trails.length; i++) {{
      if (this.trails[i].headY > maxHeadY) maxHeadY = this.trails[i].headY;
    }}
    return maxHeadY >= minHeadBeforeSpawn;
  }};

  Column.prototype.update = function(now, dt) {{
    for (let i = this.trails.length - 1; i >= 0; i--) {{
      this.trails[i].update(now, dt);
      if (this.trails[i].dead) this.trails.splice(i, 1);
    }}

    if (this.canSpawnNext()) {{
      const t = new Trail(this.x, this.index);
      t.headY = -lnH;
      t.lastSpawn = now;
      this.trails.push(t);
    }}

    // Safety: column went completely empty
    if (this.trails.length === 0) {{
      const t = new Trail(this.x, this.index);
      t.headY = -lnH;
      t.lastSpawn = now;
      this.trails.push(t);
    }}
  }};

  const columns = [];
  for (let i = 0; i < numCols; i++) {{
    columns.push(new Column(i));
  }}

  let lt = performance.now();
  function frame(now) {{
    const dt = Math.min((now - lt) / 1000, 0.05); // cap dt to avoid jumps
    lt = now;
    for (let i = 0; i < columns.length; i++) {{
      columns[i].update(now, dt);
    }}
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);

  // --- Fullscreen ---
  const fsBtn = document.getElementById('fsBtn');
  function updateBtnLabel() {{
    const isFs = !!(document.fullscreenElement || document.webkitFullscreenElement);
    fsBtn.textContent = isFs ? '✕ EXIT FULL' : '⛶ FULLSCREEN';
  }}
  fsBtn.addEventListener('click', function() {{
    const isFs = !!(document.fullscreenElement || document.webkitFullscreenElement);
    if (!isFs) {{
      const el = document.documentElement;
      if (el.requestFullscreen) el.requestFullscreen();
      else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    }} else {{
      if (document.exitFullscreen) document.exitFullscreen();
      else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
    }}
  }});
  document.addEventListener('fullscreenchange', updateBtnLabel);
  document.addEventListener('webkitfullscreenchange', updateBtnLabel);
}})();
</script>
</body>
</html>
"""

# Inject CSS to stretch iframe to fill viewport and kill all Streamlit chrome padding
st.markdown("""
<style>
.stApp { background-color: #000 !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }
/* Kill ALL padding/margin around the main content block */
.main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
/* Stretch the iframe to viewport height */
iframe {
    border: none !important;
    display: block !important;
    width: 100% !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}
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
</style>
""", unsafe_allow_html=True)

st.components.v1.html(html, height=800, scrolling=False)
