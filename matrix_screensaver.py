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

st.sidebar.markdown("---")
st.sidebar.markdown("### Speed")
base_speed = st.sidebar.slider("Fall speed (lower = faster)", 0.5, 6.0, 2.0, 0.25)
speed_variance = st.sidebar.slider("Speed variance", 0.0, 3.0, 1.0, 0.25)
spawn_rate = st.sidebar.slider("Spawn rate (lower = faster)", 0.1, 1.5, 0.4, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### Style")
brightness = st.sidebar.slider("Glow brightness", 0.3, 1.0, 0.8, 0.05)
trail_length = st.sidebar.slider("Trail length (words)", 3, 25, 12)

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
  .word {{
    position: absolute;
    white-space: nowrap;
    font-size: {font_size}px;
    line-height: 1;
    pointer-events: none;
  }}
  /* Scanlines */
  #matrix::after {{
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(0deg,
      rgba(0,0,0,0.12) 0px, rgba(0,0,0,0.12) 1px,
      transparent 1px, transparent 3px);
    pointer-events: none; z-index: 10;
  }}
  /* Vignette */
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
  const baseSpeed = {base_speed};
  const speedVar = {speed_variance};
  const brightness = {brightness};
  const trailLen = {trail_length};
  const spawnInterval = {spawn_rate} * 1000;
  const container = document.getElementById('matrix');
  const H = container.offsetHeight || 750;
  const W = container.offsetWidth || 1200;
  const colWidth = W / numCols;
  const lineH = {font_size} * 1.6;

  function pickWord(last) {{
    let w = words[Math.floor(Math.random() * words.length)];
    let t = 0;
    while (w === last && words.length > 1 && t < 10) {{
      w = words[Math.floor(Math.random() * words.length)];
      t++;
    }}
    return w;
  }}

  // Each stream: head moves down, leaves words behind that fade out
  function Stream(index) {{
    this.index = index;
    this.x = index * colWidth;
    this.drops = []; // {{ el, row, birthTime }}
    this.lastWord = '';
    this.reset(true);
  }}

  Stream.prototype.reset = function(initial) {{
    // Random speed
    const v = (Math.random() - 0.5) * 2 * speedVar;
    this.speed = H / Math.max(1, baseSpeed + v); // px per sec

    // Head starts at random Y if initial, else from top or random
    if (initial) {{
      this.headY = Math.random() * H;
    }} else {{
      // Sometimes start from top, sometimes from random spot
      this.headY = Math.random() < 0.3 ? -lineH : Math.random() * H * 0.3;
    }}

    this.lastSpawn = performance.now() - Math.random() * spawnInterval;
    this.alive = true;

    // Random lifespan: how far the head travels before this stream resets
    this.maxTravel = H * (0.5 + Math.random() * 1.5);
    this.traveled = 0;
  }};

  Stream.prototype.update = function(now, dt) {{
    if (!this.alive) return;

    // Move head down
    const movePx = this.speed * dt;
    this.headY += movePx;
    this.traveled += movePx;

    // Spawn a new word at head position
    if (now - this.lastSpawn >= spawnInterval * (0.7 + Math.random() * 0.6)) {{
      const word = pickWord(this.lastWord);
      this.lastWord = word;

      const el = document.createElement('div');
      el.className = 'word';
      el.textContent = word;
      el.style.left = this.x + 'px';
      el.style.top = this.headY + 'px';
      container.appendChild(el);

      this.drops.push({{ el: el, y: this.headY, born: now }});
      this.lastSpawn = now;
    }}

    // Style drops based on distance from head
    for (let i = this.drops.length - 1; i >= 0; i--) {{
      const drop = this.drops[i];
      // How far behind the head (in word-slots)
      const distPx = this.headY - drop.y;
      const pos = distPx / lineH;

      if (pos <= 0.5) {{
        // Leading word - bright white
        drop.el.style.color = '#ffffff';
        drop.el.style.textShadow = '0 0 14px #00ff41, 0 0 30px #00ff41, 0 0 5px #fff';
        drop.el.style.opacity = '1.0';
      }} else if (pos <= trailLen * 0.25) {{
        // Bright green
        drop.el.style.color = '#00ff41';
        drop.el.style.textShadow = '0 0 10px #00ff41, 0 0 3px #00cc33';
        drop.el.style.opacity = (brightness * 0.95).toFixed(2);
      }} else if (pos <= trailLen * 0.6) {{
        // Mid green with fade
        const t = (pos - trailLen * 0.25) / (trailLen * 0.35);
        const op = brightness * (0.7 - t * 0.35);
        drop.el.style.color = '#00aa30';
        drop.el.style.textShadow = '0 0 4px #00882a';
        drop.el.style.opacity = Math.max(0.1, op).toFixed(2);
      }} else if (pos <= trailLen) {{
        // Dim tail
        const t = (pos - trailLen * 0.6) / (trailLen * 0.4);
        const op = 0.2 - t * 0.15;
        drop.el.style.color = '#005a15';
        drop.el.style.textShadow = 'none';
        drop.el.style.opacity = Math.max(0.03, op).toFixed(2);
      }} else {{
        // Past trail - remove
        container.removeChild(drop.el);
        this.drops.splice(i, 1);
        continue;
      }}

      // Also remove if off screen
      if (drop.y > H + 50 || drop.y < -50) {{
        container.removeChild(drop.el);
        this.drops.splice(i, 1);
      }}
    }}

    // Reset stream when head has traveled far enough
    if (this.traveled > this.maxTravel) {{
      this.alive = false;
      // Let remaining drops fade out, then reset
      const self = this;
      const fadeCheck = setInterval(function() {{
        // Remove any remaining
        for (let i = self.drops.length - 1; i >= 0; i--) {{
          const drop = self.drops[i];
          const distPx = self.headY - drop.y;
          const pos = distPx / lineH;
          if (pos > trailLen) {{
            container.removeChild(drop.el);
            self.drops.splice(i, 1);
          }}
        }}
        if (self.drops.length === 0) {{
          clearInterval(fadeCheck);
          // Pause before respawning
          setTimeout(function() {{
            self.reset(false);
          }}, Math.random() * 2000 + 500);
        }}
      }}, 200);
    }}
  }};

  // Init streams with staggered starts
  const streams = [];
  for (let i = 0; i < numCols; i++) {{
    streams.push(new Stream(i));
  }}

  // Animation loop
  let lastTime = performance.now();

  function frame(now) {{
    const dt = (now - lastTime) / 1000;
    lastTime = now;

    for (let s = 0; s < streams.length; s++) {{
      streams[s].update(now, dt);
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
    section[data-testid="stSidebar"] button:hover {{
        background-color: #003300 !important;
    }}
    iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
