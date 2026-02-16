import streamlit as st
import random
import json

st.set_page_config(page_title="Matrix Word Rain", layout="wide", initial_sidebar_state="expanded")

# --- Sidebar for word input ---
st.sidebar.markdown("# 🖥️ Matrix Word Rain")
st.sidebar.markdown("---")

words_input = st.sidebar.text_area(
    "Words (one per line or space-separated):",
    value="Inessentialist\nessentialism\nof\nessentials\nwith\nthe\nessential\nessentialing\ninessentially\nessential",
    height=180,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Layout")
num_columns = st.sidebar.slider("Number of columns", 8, 60, 28)
font_size = st.sidebar.slider("Font size (px)", 8, 22, 13)
words_per_col = st.sidebar.slider("Words per column", 10, 50, 25)

st.sidebar.markdown("---")
st.sidebar.markdown("### Speed")
base_speed = st.sidebar.slider("Fall speed (lower = faster)", 2.0, 20.0, 8.0, 0.5)
speed_variance = st.sidebar.slider("Speed variance", 0.0, 10.0, 4.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("### Style")
brightness = st.sidebar.slider("Glow brightness", 0.3, 1.0, 0.8, 0.05)
trail_length = st.sidebar.slider("Bright trail length", 1, 8, 3)

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
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #000000;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
  }}

  #matrix-container {{
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    background: radial-gradient(ellipse at center, #000d00 0%, #000000 70%);
  }}

  .column {{
    position: absolute;
    top: 0;
    display: flex;
    flex-direction: column;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
  }}

  .word {{
    white-space: nowrap;
    overflow: hidden;
    padding: 1px 2px;
    font-size: {font_size}px;
    line-height: 1.4;
  }}

  @keyframes fall {{
    from {{ transform: translateY(-100%); }}
    to {{ transform: translateY(100vh); }}
  }}

  /* Scanline overlay */
  #matrix-container::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
      0deg,
      rgba(0,0,0,0.12) 0px,
      rgba(0,0,0,0.12) 1px,
      transparent 1px,
      transparent 3px
    );
    pointer-events: none;
    z-index: 10;
  }}

  /* Vignette */
  #matrix-container::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.5) 100%);
    pointer-events: none;
    z-index: 11;
  }}
</style>
</head>
<body>
<div id="matrix-container"></div>
<script>
(function() {{
  const words = {words_json};
  const numCols = {num_columns};
  const baseSpeed = {base_speed};
  const speedVariance = {speed_variance};
  const brightness = {brightness};
  const wordsPerCol = {words_per_col};
  const trailLen = {trail_length};
  const container = document.getElementById('matrix-container');

  function getShuffledWords(count) {{
    let result = [];
    let pool = [...words];
    let last = '';
    for (let i = 0; i < count; i++) {{
      if (pool.length === 0) pool = [...words];
      let available = pool.filter(w => w !== last);
      if (available.length === 0) available = pool;
      const idx = Math.floor(Math.random() * available.length);
      const chosen = available[idx];
      result.push(chosen);
      last = chosen;
      const poolIdx = pool.indexOf(chosen);
      if (poolIdx > -1) pool.splice(poolIdx, 1);
    }}
    return result;
  }}

  function createColumn(index) {{
    const col = document.createElement('div');
    col.className = 'column';

    const colWidth = container.offsetWidth / numCols;
    col.style.left = (index * colWidth) + 'px';
    col.style.width = colWidth + 'px';

    const wordCount = wordsPerCol + Math.floor(Math.random() * 10) - 5;
    const shuffled = getShuffledWords(Math.max(5, wordCount));

    shuffled.forEach((word, i) => {{
      const span = document.createElement('div');
      span.className = 'word';
      span.textContent = word;

      const distFromEnd = shuffled.length - 1 - i;

      if (distFromEnd === 0) {{
        // Leading edge - white bright
        span.style.color = '#ffffff';
        span.style.textShadow = '0 0 12px #00ff41, 0 0 25px #00ff41, 0 0 4px #fff';
        span.style.opacity = '1.0';
      }} else if (distFromEnd <= trailLen) {{
        // Bright trail
        const fade = 1.0 - (distFromEnd / (trailLen + 1)) * 0.3;
        span.style.color = '#00ff41';
        span.style.textShadow = '0 0 8px #00ff41, 0 0 2px #00cc33';
        span.style.opacity = (fade * brightness).toFixed(2);
      }} else if (distFromEnd <= trailLen + 4) {{
        // Mid section
        const fade = 0.5 - (distFromEnd - trailLen) * 0.05;
        span.style.color = '#00aa30';
        span.style.textShadow = '0 0 4px #00aa30';
        span.style.opacity = (Math.max(0.2, fade) * brightness).toFixed(2);
      }} else {{
        // Dim tail
        span.style.color = '#004a10';
        span.style.textShadow = 'none';
        span.style.opacity = (0.15 + Math.random() * 0.15).toFixed(2);
      }}

      col.appendChild(span);
    }});

    // Speed with variance
    const variance = (Math.random() - 0.5) * 2 * speedVariance;
    const duration = Math.max(2, baseSpeed + variance);
    const delay = -Math.random() * duration;

    col.style.animationDuration = duration + 's';
    col.style.animationDelay = delay + 's';

    container.appendChild(col);

    col.addEventListener('animationiteration', () => {{
      container.removeChild(col);
      createColumn(index);
    }});
  }}

  for (let i = 0; i < numCols; i++) {{
    createColumn(i);
  }}
}})();
</script>
</body>
</html>
"""

st.components.v1.html(html, height=750, scrolling=False)

# Theme the whole app dark/green
st.markdown(
    """
    <style>
    .stApp { background-color: #000000 !important; }
    header[data-testid="stHeader"] { background-color: #000000 !important; }
    footer { display: none !important; }
    .stDeployButton { display: none !important; }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #050f05 !important;
        border-right: 1px solid #003300 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #00dd38 !important;
    }
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
