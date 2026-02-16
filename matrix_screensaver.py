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

st.sidebar.markdown("---")
st.sidebar.markdown("### Speed")
base_speed = st.sidebar.slider("Fall speed (lower = faster)", 0.5, 6.0, 2.0, 0.25)
speed_variance = st.sidebar.slider("Speed variance", 0.0, 3.0, 1.0, 0.25)
spawn_rate = st.sidebar.slider("Spawn rate (lower = faster)", 0.1, 1.5, 0.35, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### Style")
brightness = st.sidebar.slider("Glow brightness", 0.3, 1.0, 0.8, 0.05)
trail_length = st.sidebar.slider("Trail length (words)", 3, 25, 12)
respawn_delay = st.sidebar.slider("Respawn delay (sec)", 0.0, 3.0, 0.2, 0.1)

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
  const words = {words_json};
  const numCols = {num_columns};
  const trailsPerCol = {trails_per_col};
  const baseSpeed = {base_speed};
  const speedVar = {speed_variance};
  const bri = {brightness};
  const trailLen = {trail_length};
  const spawnMs = {spawn_rate} * 1000;
  const respawnMs = {respawn_delay} * 1000;
  const C = document.getElementById('matrix');
  const H = C.offsetHeight || 750;
  const W = C.offsetWidth || 1200;
  const colW = W / numCols;
  const lnH = {font_size} * 1.6;

  const RUNNING = 0, DRAINING = 1, WAITING = 2;

  function pick(last) {{
    let w = words[Math.floor(Math.random() * words.length)];
    let t = 0;
    while (w === last && words.length > 1 && t++ < 10)
      w = words[Math.floor(Math.random() * words.length)];
    return w;
  }}

  function newTrail(colIdx, initial) {{
    const v = (Math.random() - 0.5) * 2 * speedVar;
    const spd = H / Math.max(0.5, baseSpeed + v);
    let startY;
    if (initial) {{
      startY = Math.random() * H;
    }} else {{
      startY = Math.random() < 0.4 ? -lnH : Math.random() * H * 0.2;
    }}
    return {{
      colIdx: colIdx,
      x: colIdx * colW,
      headY: startY,
      speed: spd,
      drops: [],
      lastWord: '',
      lastSpawn: 0,
      state: RUNNING,
      maxTravel: H * (0.3 + Math.random() * 1.0),
      traveled: 0,
      waitUntil: 0
    }};
  }}

  // Create multiple trails per column, staggered
  const allTrails = [];
  for (let col = 0; col < numCols; col++) {{
    for (let t = 0; t < trailsPerCol; t++) {{
      const tr = newTrail(col, true);
      // Stagger the multiple trails within a column
      tr.headY = Math.random() * H * (0.3 + t * 0.5 / trailsPerCol) + t * (H / trailsPerCol) * Math.random();
      tr.lastSpawn = -Math.random() * spawnMs * 5;
      allTrails.push(tr);
    }}
  }}

  let lt = performance.now();

  function frame(now) {{
    const dt = (now - lt) / 1000;
    lt = now;

    for (let si = 0; si < allTrails.length; si++) {{
      const s = allTrails[si];

      // WAITING
      if (s.state === WAITING) {{
        if (now >= s.waitUntil) {{
          const ns = newTrail(s.colIdx, false);
          ns.lastSpawn = now;
          allTrails[si] = ns;
        }}
        continue;
      }}

      // RUNNING - move head, spawn words
      if (s.state === RUNNING) {{
        const mv = s.speed * dt;
        s.headY += mv;
        s.traveled += mv;

        if (now - s.lastSpawn >= spawnMs * (0.7 + Math.random() * 0.6)) {{
          const word = pick(s.lastWord);
          s.lastWord = word;
          const el = document.createElement('div');
          el.className = 'w';
          el.textContent = word;
          el.style.left = s.x + 'px';
          el.style.top = s.headY + 'px';
          C.appendChild(el);
          s.drops.push({{ el: el, y: s.headY }});
          s.lastSpawn = now;
        }}

        if (s.traveled >= s.maxTravel) {{
          s.state = DRAINING;
        }}
      }}

      // Style drops
      for (let i = s.drops.length - 1; i >= 0; i--) {{
        const d = s.drops[i];
        const dist = (s.headY - d.y) / lnH;

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
          s.drops.splice(i, 1);
          continue;
        }}
      }}

      // DRAINING - keep head moving so trail scrolls off
      if (s.state === DRAINING) {{
        s.headY += s.speed * dt;
        if (s.drops.length === 0) {{
          s.state = WAITING;
          s.waitUntil = now + respawnMs * (0.3 + Math.random() * 0.7);
        }}
      }}
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
