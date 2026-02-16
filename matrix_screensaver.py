import streamlit as st
import random
import json

st.set_page_config(page_title="Matrix Word Rain", layout="wide", initial_sidebar_state="collapsed")

# --- Sidebar for word input ---
with st.sidebar:
    st.markdown("## ⌨️ Matrix Word Rain")
    words_input = st.text_area(
        "Enter words (one per line or space-separated):",
        value="Inessentialist\nessentialism\nof\nessentials\nwith\nthe\nessential\nessentialing\ninessentially\nessential",
        height=200,
    )
    num_columns = st.slider("Columns", 4, 30, 14)
    speed = st.slider("Speed (lower = faster)", 0.5, 5.0, 1.5, 0.1)
    font_size = st.slider("Font size (px)", 10, 24, 14)
    brightness = st.slider("Brightness", 0.3, 1.0, 0.7, 0.05)
    if st.button("🔄 Regenerate"):
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
    background: radial-gradient(ellipse at center, #001a00 0%, #000000 70%);
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
    padding: 2px 4px;
    font-size: {font_size}px;
    line-height: 1.6;
    color: #00ff41;
    text-shadow: 0 0 8px #00ff41, 0 0 2px #00cc33;
    opacity: 0.7;
    transition: opacity 0.3s;
  }}

  .word.bright {{
    color: #ffffff;
    text-shadow: 0 0 12px #00ff41, 0 0 25px #00ff41, 0 0 4px #ffffff;
    opacity: 1.0;
  }}

  .word.dim {{
    opacity: 0.25;
    color: #005a10;
    text-shadow: none;
  }}

  .word.mid {{
    opacity: 0.5;
    color: #00aa30;
    text-shadow: 0 0 4px #00aa30;
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
      rgba(0,0,0,0.15) 0px,
      rgba(0,0,0,0.15) 1px,
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
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%);
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
  const speed = {speed};
  const brightness = {brightness};
  const container = document.getElementById('matrix-container');
  const containerWidth = window.innerWidth;

  // Shuffle without immediate repeats
  function getShuffledWords(count) {{
    let result = [];
    let pool = [...words];
    let last = '';
    for (let i = 0; i < count; i++) {{
      if (pool.length === 0) pool = [...words];
      // Filter out last used word if possible
      let available = pool.filter(w => w !== last);
      if (available.length === 0) available = pool;
      const idx = Math.floor(Math.random() * available.length);
      const chosen = available[idx];
      result.push(chosen);
      last = chosen;
      // Remove from pool for non-repeat cycle
      const poolIdx = pool.indexOf(chosen);
      if (poolIdx > -1) pool.splice(poolIdx, 1);
    }}
    return result;
  }}

  function createColumn(index) {{
    const col = document.createElement('div');
    col.className = 'column';

    const colWidth = containerWidth / numCols;
    col.style.left = (index * colWidth) + 'px';
    col.style.width = colWidth + 'px';

    // Random number of words per column
    const wordCount = 8 + Math.floor(Math.random() * 15);
    const shuffled = getShuffledWords(wordCount);

    shuffled.forEach((word, i) => {{
      const span = document.createElement('div');
      span.className = 'word';
      span.textContent = word;

      // Last word is bright (leading edge), first words are dim (trail)
      if (i === shuffled.length - 1) {{
        span.classList.add('bright');
      }} else if (i < 3) {{
        span.classList.add('dim');
      }} else if (i < 6) {{
        span.classList.add('mid');
      }}

      // Slight random opacity variation
      if (!span.classList.contains('bright')) {{
        span.style.opacity = (parseFloat(span.style.opacity || brightness) * (0.6 + Math.random() * 0.4)).toFixed(2);
      }}

      col.appendChild(span);
    }});

    // Animation timing
    const duration = (speed * 8) + Math.random() * (speed * 12);
    const delay = Math.random() * duration * -1; // Start at random positions

    col.style.animationDuration = duration + 's';
    col.style.animationDelay = delay + 's';

    container.appendChild(col);

    // When animation ends, recreate with new words
    col.addEventListener('animationiteration', () => {{
      container.removeChild(col);
      createColumn(index);
    }});
  }}

  // Create all columns
  for (let i = 0; i < numCols; i++) {{
    createColumn(i);
  }}
}})();
</script>
</body>
</html>
"""

# Render the matrix
st.components.v1.html(html, height=700, scrolling=False)

st.markdown(
    """
    <style>
    .stApp { background-color: #000000 !important; }
    header, footer, .stDeployButton { display: none !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; }
    [data-testid="stSidebar"] * { color: #00ff41 !important; }
    [data-testid="stSidebar"] .stTextArea textarea { 
        background-color: #001a00 !important; 
        color: #00ff41 !important; 
        border-color: #003300 !important;
        font-family: 'Courier New', monospace !important;
    }
    [data-testid="stSidebar"] .stSlider > div > div > div { background-color: #00ff41 !important; }
    [data-testid="stSidebar"] button {
        background-color: #003300 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
    }
    iframe { border: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
