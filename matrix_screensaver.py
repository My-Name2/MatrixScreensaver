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
st.sidebar.markdown("### 🎨 Color Mode")
color_mode = st.sidebar.radio("Color mode", ["Matrix Green", "Solid Color", "Rainbow"])

custom_color = "#00ff41"
rainbow_speed = 3.0

if color_mode == "Solid Color":
    custom_color = st.sidebar.color_picker("Pick a color", "#00ff41")
elif color_mode == "Rainbow":
    rainbow_speed = st.sidebar.slider("Rainbow cycle speed (s)", 0.5, 15.0, 3.0, 0.5)

if st.sidebar.button("🔄 Regenerate", use_container_width=True):
    st.rerun()

# Parse words
raw = words_input.replace("\n", " ").split()
words = [w.strip() for w in raw if w.strip()]
if not words:
    words = ["essential"]

words_json = json.dumps(words)

# Convert hex color to rgb components for JS
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

r, g, b = hex_to_rgb(custom_color)

# Build color mode JS
if color_mode == "Rainbow":
    color_js = f"""
  const COLOR_MODE = 'rainbow';
  const RAINBOW_SPEED = {rainbow_speed};
  function getHue(now) {{
    return (now / (RAINBOW_SPEED * 1000) * 360) % 360;
  }}
  function headColor(now) {{
    return `hsl(${{getHue(now)}}, 100%, 95%)`;
  }}
  function headGlow(now) {{
    const h = getHue(now);
    return `0 0 14px hsl(${{h}},100%,60%), 0 0 30px hsl(${{h}},100%,50%), 0 0 5px #fff`;
  }}
  function brightColor(now) {{
    return `hsl(${{getHue(now)}}, 100%, 65%)`;
  }}
  function brightGlow(now) {{
    const h = getHue(now);
    return `0 0 10px hsl(${{h}},100%,55%), 0 0 3px hsl(${{h}},80%,40%)`;
  }}
  function midColor(now) {{
    const h = getHue(now);
    return `hsl(${{h}}, 80%, 40%)`;
  }}
  function dimColor(now) {{
    const h = getHue(now);
    return `hsl(${{h}}, 60%, 20%)`;
  }}
"""
else:
    if color_mode == "Solid Color":
        hr, hg, hb = r, g, b
    else:
        hr, hg, hb = 0, 255, 65

    # Compute derived darker shades
    mid_r, mid_g, mid_b = int(hr*0.55), int(hg*0.55), int(hb*0.55)
    dim_r, dim_g, dim_b = int(hr*0.25), int(hg*0.25), int(hb*0.25)
    glow1_r, glow1_g, glow1_b = min(255, int(hr*1.0)), min(255, int(hg*1.0)), min(255, int(hb*1.0))

    color_js = f"""
  const COLOR_MODE = 'solid';
  function headColor(now) {{ return 'rgb(255,255,255)'; }}
  function headGlow(now) {{ return '0 0 14px rgb({hr},{hg},{hb}), 0 0 30px rgb({hr},{hg},{hb}), 0 0 5px #fff'; }}
  function brightColor(now) {{ return 'rgb({hr},{hg},{hb})'; }}
  function brightGlow(now) {{ return '0 0 10px rgb({hr},{hg},{hb}), 0 0 3px rgb({mid_r},{mid_g},{mid_b})'; }}
  function midColor(now) {{ return 'rgb({mid_r},{mid_g},{mid_b})'; }}
  function dimColor(now) {{ return 'rgb({dim_r},{dim_g},{dim_b})'; }}
"""

html = f"""
<!DOCTYPE html>
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
    position: relative;
    width: 100%; height: 100vh;
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
</style>
</head>
<body>
<div id="matrix"></div>
<script>
(function() {{
  {color_js}

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
        d.el.style.color = headColor(now);
        d.el.style.textShadow = headGlow(now);
        d.el.style.opacity = '1';
      }} else if (dist <= trailLen * 0.25) {{
        d.el.style.color = brightColor(now);
        d.el.style.textShadow = brightGlow(now);
        d.el.style.opacity = (bri * 0.95).toFixed(2);
      }} else if (dist <= trailLen * 0.6) {{
        const f = (dist - trailLen * 0.25) / (trailLen * 0.35);
        d.el.style.color = midColor(now);
        d.el.style.textShadow = 'none';
        d.el.style.opacity = Math.max(0.08, bri * (0.7 - f * 0.4)).toFixed(2);
      }} else if (dist <= trailLen) {{
        const f = (dist - trailLen * 0.6) / (trailLen * 0.4);
        d.el.style.color = dimColor(now);
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
      if (this.trails[i].dead) {{
        this.trails.splice(i, 1);
      }}
    }}

    if (this.trails.length < maxTrails) {{
      let canSpawn = true;
      if (this.trails.length > 0) {{
        let lowestHead = -Infinity;
        for (let i = 0; i < this.trails.length; i++) {{
          if (this.trails[i].headY > lowestHead) lowestHead = this.trails[i].headY;
        }}
        const trailTopOfNewest = lowestHead - trailLen * lnH;
        if (trailTopOfNewest < gapPx) {{
          canSpawn = false;
        }}
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
  for (let i = 0; i < numCols; i++) {{
    columns.push(new Column(i));
  }}

  let lt = performance.now();
  function frame(now) {{
    const dt = (now - lt) / 1000;
    lt = now;
    for (let i = 0; i < columns.length; i++) {{
      columns[i].update(now, dt);
    }}
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
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
