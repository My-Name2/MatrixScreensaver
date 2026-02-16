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
trail_length = st.sidebar.slider("Trail length (words)", 3, 20, 10)

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
    will-change: transform, opacity;
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
  const baseSpeed = {base_speed};       // seconds to cross screen
  const speedVar = {speed_variance};
  const brightness = {brightness};
  const trailLen = {trail_length};
  const spawnRate = {spawn_rate};        // seconds between spawns per stream
  const container = document.getElementById('matrix');
  const H = container.offsetHeight || 750;
  const W = container.offsetWidth || 1200;
  const colWidth = W / numCols;
  const lineH = {font_size} * 1.4;

  // Per-stream state: each stream tracks its active words for trail fading
  const streams = [];

  function pickWord(lastWord) {{
    let w = words[Math.floor(Math.random() * words.length)];
    let tries = 0;
    while (w === lastWord && words.length > 1 && tries < 10) {{
      w = words[Math.floor(Math.random() * words.length)];
      tries++;
    }}
    return w;
  }}

  function Stream(index) {{
    this.index = index;
    this.x = index * colWidth;
    this.active = [];
    this.lastWord = '';
    // Randomize speed per stream
    const v = (Math.random() - 0.5) * 2 * speedVar;
    this.pxPerSec = H / Math.max(1, baseSpeed + v);
    // Stagger start
    this.nextSpawn = Math.random() * spawnRate * 15;
  }}

  Stream.prototype.spawn = function(now) {{
    const word = pickWord(this.lastWord);
    this.lastWord = word;

    const el = document.createElement('div');
    el.className = 'word';
    el.textContent = word;
    el.style.left = this.x + 'px';
    el.style.top = '-30px';
    container.appendChild(el);

    const item = {{ el: el, y: -30, born: now }};
    this.active.push(item);

    // Schedule next spawn
    this.nextSpawn = now + spawnRate * 1000 * (0.7 + Math.random() * 0.6);
  }};

  Stream.prototype.update = function(now, dt) {{
    // Spawn new word?
    if (now >= this.nextSpawn) {{
      this.spawn(now);
    }}

    // Move & style each word
    for (let i = this.active.length - 1; i >= 0; i--) {{
      const item = this.active[i];
      item.y += this.pxPerSec * dt;
      item.el.style.transform = 'translateY(' + item.y + 'px)';

      // Position in trail: 0 = newest (leading), higher = older
      const pos = this.active.length - 1 - i;

      if (pos === 0) {{
        // Leading edge - bright white
        item.el.style.color = '#ffffff';
        item.el.style.textShadow = '0 0 12px #00ff41, 0 0 25px #00ff41, 0 0 4px #fff';
        item.el.style.opacity = '1.0';
      }} else if (pos <= trailLen * 0.3) {{
        // Bright green
        item.el.style.color = '#00ff41';
        item.el.style.textShadow = '0 0 8px #00ff41, 0 0 2px #00cc33';
        item.el.style.opacity = (brightness * 0.9).toFixed(2);
      }} else if (pos <= trailLen * 0.7) {{
        // Mid green
        const fade = 1 - ((pos - trailLen * 0.3) / (trailLen * 0.4));
        item.el.style.color = '#00aa30';
        item.el.style.textShadow = '0 0 4px #00aa30';
        item.el.style.opacity = (Math.max(0.15, fade * brightness * 0.6)).toFixed(2);
      }} else if (pos <= trailLen) {{
        // Dim
        const fade = 1 - ((pos - trailLen * 0.7) / (trailLen * 0.3));
        item.el.style.color = '#005a15';
        item.el.style.textShadow = 'none';
        item.el.style.opacity = (Math.max(0.05, fade * 0.2)).toFixed(2);
      }} else {{
        // Beyond trail - fade out and remove
        item.el.style.opacity = '0';
      }}

      // Remove if off screen or fully faded
      if (item.y > H + 50 || pos > trailLen + 2) {{
        container.removeChild(item.el);
        this.active.splice(i, 1);
      }}
    }}
  }};

  // Init streams
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
    section[data-testid="stSidebar"] button:hover {
        background-color: #003300 !important;
    }
    iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
