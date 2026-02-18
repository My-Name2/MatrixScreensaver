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
color_mode = st.sidebar.radio("Color Mode", ["Classic Green", "Solid Color", "Rainbow"])

solid_color = "#00ff41"
rainbow_speed = 3.0

if color_mode == "Solid Color":
    solid_color = st.sidebar.color_picker("Pick a color", "#00ff41")
elif color_mode == "Rainbow":
    rainbow_speed = st.sidebar.slider("Rainbow cycle speed (sec)", 0.5, 10.0, 3.0, 0.5)

if st.sidebar.button("🔄 Regenerate", use_container_width=True):
    st.rerun()

# Parse words
raw = words_input.replace("\n", " ").split()
words = [w.strip() for w in raw if w.strip()]
if not words:
    words = ["essential"]

words_json = json.dumps(words)

# Convert hex color to RGB for JS
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b

r, g, b = hex_to_rgb(solid_color)

color_mode_js = "green"
if color_mode == "Solid Color":
    color_mode_js = "solid"
elif color_mode == "Rainbow":
    color_mode_js = "rainbow"

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
  #fsBtn {{
    position: fixed;
    bottom: 18px;
    right: 18px;
    z-index: 100;
    background: rgba(0,20,0,0.75);
    border: 1px solid #00ff41;
    color: #00ff41;
    font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 12px;
    padding: 7px 13px;
    cursor: pointer;
    border-radius: 3px;
    letter-spacing: 0.08em;
    text-shadow: 0 0 8px #00ff41;
    box-shadow: 0 0 10px rgba(0,255,65,0.2);
    transition: background 0.15s, box-shadow 0.15s;
    user-select: none;
  }}
  #fsBtn:hover {{
    background: rgba(0,40,0,0.9);
    box-shadow: 0 0 18px rgba(0,255,65,0.45);
  }}
  #fsHint {{
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    color: rgba(0,255,65,0.45);
    font-family: 'Share Tech Mono', 'Courier New', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.4s;
  }}
  :fullscreen #fsBtn {{ bottom: 22px; right: 22px; }}
  :-webkit-full-screen #fsBtn {{ bottom: 22px; right: 22px; }}
</style>
</head>
<body>
<div id="matrix"></div>
<button id="fsBtn" title="Fullscreen (F)">⛶ FULLSCREEN</button>
<div id="fsHint">press ESC to exit fullscreen</div>
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

  // Color mode settings
  const COLOR_MODE = '{color_mode_js}';
  const SOLID_R = {r};
  const SOLID_G = {g};
  const SOLID_B = {b};
  const RAINBOW_SPEED = {rainbow_speed}; // seconds per full cycle

  // Assign a hue offset per column for rainbow
  function getColumnHue(colIndex, now) {{
    const base = (now / 1000 / RAINBOW_SPEED * 360) % 360;
    return (base + colIndex * (360 / numCols)) % 360;
  }}

  function hslToRgb(h, s, l) {{
    h /= 360; s /= 100; l /= 100;
    let r, g, b;
    if (s === 0) {{ r = g = b = l; }}
    else {{
      const hue2rgb = (p, q, t) => {{
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      }};
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }}
    return [Math.round(r*255), Math.round(g*255), Math.round(b*255)];
  }}

  // Returns {{head, bright, mid, dim}} color strings for a given column + time
  function getColors(colIndex, now) {{
    if (COLOR_MODE === 'green') {{
      return {{
        head: '#fff',
        headShadow: '0 0 14px #00ff41,0 0 30px #00ff41,0 0 5px #fff',
        bright: '#00ff41',
        brightShadow: '0 0 10px #00ff41,0 0 3px #00cc33',
        mid: '#00aa30',
        midShadow: '0 0 4px #00882a',
        dim: '#005a15'
      }};
    }} else if (COLOR_MODE === 'solid') {{
      const rr = SOLID_R, gg = SOLID_G, bb = SOLID_B;
      const full = `rgb(${{rr}},${{gg}},${{bb}})`;
      const mid_r = Math.round(rr*0.67), mid_g = Math.round(gg*0.67), mid_b = Math.round(bb*0.67);
      const dim_r = Math.round(rr*0.35), dim_g = Math.round(gg*0.35), dim_b = Math.round(bb*0.35);
      return {{
        head: '#fff',
        headShadow: `0 0 14px ${{full}},0 0 30px ${{full}},0 0 5px #fff`,
        bright: full,
        brightShadow: `0 0 10px ${{full}},0 0 3px rgb(${{mid_r}},${{mid_g}},${{mid_b}})`,
        mid: `rgb(${{mid_r}},${{mid_g}},${{mid_b}})`,
        midShadow: `0 0 4px rgb(${{dim_r}},${{dim_g}},${{dim_b}})`,
        dim: `rgb(${{dim_r}},${{dim_g}},${{dim_b}})`
      }};
    }} else {{
      // Rainbow
      const hue = getColumnHue(colIndex, now);
      const [rr, gg, bb] = hslToRgb(hue, 100, 50);
      const [mr, mg, mb] = hslToRgb(hue, 90, 35);
      const [dr, dg, db] = hslToRgb(hue, 80, 18);
      const full = `rgb(${{rr}},${{gg}},${{bb}})`;
      return {{
        head: '#fff',
        headShadow: `0 0 14px ${{full}},0 0 30px ${{full}},0 0 5px #fff`,
        bright: full,
        brightShadow: `0 0 10px ${{full}},0 0 3px rgb(${{mr}},${{mg}},${{mb}})`,
        mid: `rgb(${{mr}},${{mg}},${{mb}})`,
        midShadow: `0 0 4px rgb(${{dr}},${{dg}},${{db}})`,
        dim: `rgb(${{dr}},${{dg}},${{db}})`
      }};
    }}
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

    const colors = getColors(this.colIndex, now);

    for (let i = this.drops.length - 1; i >= 0; i--) {{
      const d = this.drops[i];
      const dist = (this.headY - d.y) / lnH;

      if (dist <= 0.5) {{
        d.el.style.color = colors.head;
        d.el.style.textShadow = colors.headShadow;
        d.el.style.opacity = '1';
      }} else if (dist <= trailLen * 0.25) {{
        d.el.style.color = colors.bright;
        d.el.style.textShadow = colors.brightShadow;
        d.el.style.opacity = (bri * 0.95).toFixed(2);
      }} else if (dist <= trailLen * 0.6) {{
        const f = (dist - trailLen * 0.25) / (trailLen * 0.35);
        d.el.style.color = colors.mid;
        d.el.style.textShadow = colors.midShadow;
        d.el.style.opacity = Math.max(0.08, bri * (0.7 - f * 0.4)).toFixed(2);
      }} else if (dist <= trailLen) {{
        const f = (dist - trailLen * 0.6) / (trailLen * 0.4);
        d.el.style.color = colors.dim;
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
    const t = new Trail(this.x, index);
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
        const t = new Trail(this.x, this.index);
        t.headY = -lnH;
        t.lastSpawn = now;
        this.trails.push(t);
      }}
    }}

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
    const dt = (now - lt) / 1000;
    lt = now;
    for (let i = 0; i < columns.length; i++) {{
      columns[i].update(now, dt);
    }}
    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);

  // --- Fullscreen via postMessage to parent ---
  const fsBtn = document.getElementById('fsBtn');
  const fsHint = document.getElementById('fsHint');
  let isFullscreen = false;
  let hintTimer = null;

  function showHint() {{
    fsHint.style.opacity = '1';
    clearTimeout(hintTimer);
    hintTimer = setTimeout(() => {{ fsHint.style.opacity = '0'; }}, 2800);
  }}

  function toggleFS() {{
    if (!isFullscreen) {{
      window.parent.postMessage({{ type: 'MATRIX_FS_OPEN' }}, '*');
      isFullscreen = true;
      fsBtn.textContent = '✕ EXIT FULL';
      showHint();
    }} else {{
      window.parent.postMessage({{ type: 'MATRIX_FS_CLOSE' }}, '*');
      isFullscreen = false;
      fsBtn.textContent = '⛶ FULLSCREEN';
      fsHint.style.opacity = '0';
    }}
  }}

  // Listen for ESC from parent overlay
  window.addEventListener('message', (e) => {{
    if (e.data && e.data.type === 'MATRIX_FS_CLOSED') {{
      isFullscreen = false;
      fsBtn.textContent = '⛶ FULLSCREEN';
      fsHint.style.opacity = '0';
    }}
  }});

  fsBtn.addEventListener('click', toggleFS);
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'f' || e.key === 'F') toggleFS();
  }});
}})();
</script>
</body>
</html>
"""

st.components.v1.html(html, height=750, scrolling=False)

parent_fs_script = f"""
<style>
.stApp {{ background-color: #000000 !important; }}
header[data-testid="stHeader"] {{ background-color: #000000 !important; }}
footer {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}
section[data-testid="stSidebar"] {{
    background-color: #050f05 !important;
    border-right: 1px solid #003300 !important;
}}
section[data-testid="stSidebar"] * {{ color: #00dd38 !important; }}
section[data-testid="stSidebar"] textarea {{
    background-color: #001a00 !important;
    color: #00ff41 !important;
    border-color: #003300 !important;
    font-family: 'Courier New', monospace !important;
}}
section[data-testid="stSidebar"] button {{
    background-color: #002200 !important;
    color: #00ff41 !important;
    border: 1px solid #00ff41 !important;
}}
section[data-testid="stSidebar"] button:hover {{
    background-color: #003300 !important;
}}
iframe {{ border: none !important; }}
#matrix-fs-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: 999999;
    background: #000;
}}
#matrix-fs-overlay.active {{ display: block; }}
#matrix-fs-overlay iframe {{
    width: 100%; height: 100%;
    border: none;
}}
#matrix-fs-close {{
    position: fixed;
    bottom: 22px; right: 22px;
    z-index: 9999999;
    background: rgba(0,20,0,0.85);
    border: 1px solid #00ff41;
    color: #00ff41;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    padding: 8px 14px;
    cursor: pointer;
    border-radius: 3px;
    letter-spacing: 0.08em;
    text-shadow: 0 0 8px #00ff41;
    display: none;
}}
#matrix-fs-close.active {{ display: block; }}
</style>

<div id="matrix-fs-overlay"></div>
<button id="matrix-fs-close" onclick="closeMatrixFS()">✕ EXIT FULL</button>

<script>
(function() {{
  // The standalone matrix HTML — a self-contained copy that runs independently
  const WORDS = {words_json};
  const NUM_COLS = {num_columns};
  const FONT_SIZE = {font_size};
  const TRAILS_PER_COL = {trails_per_col};
  const GAP_WORDS = {gap_words};
  const BASE_SPEED = {base_speed};
  const SPEED_VAR = {speed_variance};
  const SPAWN_RATE = {spawn_rate};
  const BRIGHTNESS = {brightness};
  const TRAIL_LEN = {trail_length};
  const COLOR_MODE = '{color_mode_js}';
  const SOLID_R = {r};
  const SOLID_G = {g};
  const SOLID_B = {b};
  const RAINBOW_SPEED = {rainbow_speed};

  function buildStandaloneHTML() {{
    return `<!DOCTYPE html><html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body,html{{width:100%;height:100%;overflow:hidden;background:#000;font-family:'Share Tech Mono','Courier New',monospace;}}
#matrix{{position:relative;width:100%;height:100vh;overflow:hidden;background:radial-gradient(ellipse at center,#000d00 0%,#000 70%);}}
.w{{position:absolute;white-space:nowrap;font-size:${{FONT_SIZE}}px;line-height:1;pointer-events:none;}}
#matrix::after{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,0.12) 0px,rgba(0,0,0,0.12) 1px,transparent 1px,transparent 3px);pointer-events:none;z-index:10;}}
#matrix::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at center,transparent 40%,rgba(0,0,0,0.5) 100%);pointer-events:none;z-index:11;}}
</style></head><body>
<div id="matrix"></div>
<script>
(function(){{
  const words=${{JSON.stringify(WORDS)}};
  const numCols=${{NUM_COLS}};
  const maxTrails=${{TRAILS_PER_COL}};
  const gapWords=${{GAP_WORDS}};
  const baseSpeed=${{BASE_SPEED}};
  const speedVar=${{SPEED_VAR}};
  const bri=${{BRIGHTNESS}};
  const trailLen=${{TRAIL_LEN}};
  const spawnMs=${{SPAWN_RATE}}*1000;
  const COLOR_MODE='${{COLOR_MODE}}';
  const SOLID_R=${{SOLID_R}};const SOLID_G=${{SOLID_G}};const SOLID_B=${{SOLID_B}};
  const RAINBOW_SPEED=${{RAINBOW_SPEED}};
  const C=document.getElementById('matrix');
  const H=window.innerHeight||800;
  const W=window.innerWidth||1400;
  const colW=W/numCols;
  const lnH=FONT_SIZE*1.6;
  const gapPx=gapWords*lnH;
  function getColumnHue(i,now){{return((now/1000/RAINBOW_SPEED*360)+(i*(360/numCols)))%360;}}
  function hslToRgb(h,s,l){{h/=360;s/=100;l/=100;let r,g,b;if(s===0){{r=g=b=l;}}else{{const h2=(p,q,t)=>{{if(t<0)t+=1;if(t>1)t-=1;if(t<1/6)return p+(q-p)*6*t;if(t<1/2)return q;if(t<2/3)return p+(q-p)*(2/3-t)*6;return p;}};const q=l<0.5?l*(1+s):l+s-l*s;const p=2*l-q;r=h2(p,q,h+1/3);g=h2(p,q,h);b=h2(p,q,h-1/3);}}return[Math.round(r*255),Math.round(g*255),Math.round(b*255)];}}
  function getColors(ci,now){{if(COLOR_MODE==='green'){{return{{head:'#fff',headShadow:'0 0 14px #00ff41,0 0 30px #00ff41,0 0 5px #fff',bright:'#00ff41',brightShadow:'0 0 10px #00ff41,0 0 3px #00cc33',mid:'#00aa30',midShadow:'0 0 4px #00882a',dim:'#005a15'}};}}else if(COLOR_MODE==='solid'){{const rr=SOLID_R,gg=SOLID_G,bb=SOLID_B;const full=\`rgb(${{rr}},${{gg}},${{bb}})\`;const mr=Math.round(rr*.67),mg=Math.round(gg*.67),mb=Math.round(bb*.67);const dr=Math.round(rr*.35),dg=Math.round(gg*.35),db=Math.round(bb*.35);return{{head:'#fff',headShadow:\`0 0 14px ${{full}},0 0 30px ${{full}},0 0 5px #fff\`,bright:full,brightShadow:\`0 0 10px ${{full}},0 0 3px rgb(${{mr}},${{mg}},${{mb}})\`,mid:\`rgb(${{mr}},${{mg}},${{mb}})\`,midShadow:\`0 0 4px rgb(${{dr}},${{dg}},${{db}})\`,dim:\`rgb(${{dr}},${{dg}},${{db}})\`}};}}else{{const hue=getColumnHue(ci,now);const[rr,gg,bb]=hslToRgb(hue,100,50);const[mr,mg,mb]=hslToRgb(hue,90,35);const[dr,dg,db]=hslToRgb(hue,80,18);const full=\`rgb(${{rr}},${{gg}},${{bb}})\`;return{{head:'#fff',headShadow:\`0 0 14px ${{full}},0 0 30px ${{full}},0 0 5px #fff\`,bright:full,brightShadow:\`0 0 10px ${{full}},0 0 3px rgb(${{mr}},${{mg}},${{mb}})\`,mid:\`rgb(${{mr}},${{mg}},${{mb}})\`,midShadow:\`0 0 4px rgb(${{dr}},${{dg}},${{db}})\`,dim:\`rgb(${{dr}},${{dg}},${{db}})\`}};}}}}
  function pick(last){{let w=words[Math.floor(Math.random()*words.length)];let t=0;while(w===last&&words.length>1&&t++<10)w=words[Math.floor(Math.random()*words.length)];return w;}}
  function Trail(x,ci){{const v=(Math.random()-.5)*2*speedVar;this.x=x;this.colIndex=ci;this.headY=-lnH;this.speed=H/Math.max(.5,baseSpeed+v);this.drops=[];this.lastWord='';this.lastSpawn=0;this.maxTravel=H*(.4+Math.random()*1.0);this.traveled=0;this.done=false;this.dead=false;}}
  Trail.prototype.tailY=function(){{return this.drops.length===0?this.headY:this.drops[0].y;}};
  Trail.prototype.update=function(now,dt){{const mv=this.speed*dt;this.headY+=mv;this.traveled+=mv;if(!this.done&&now-this.lastSpawn>=spawnMs*(.7+Math.random()*.6)){{const word=pick(this.lastWord);this.lastWord=word;const el=document.createElement('div');el.className='w';el.textContent=word;el.style.left=this.x+'px';el.style.top=this.headY+'px';C.appendChild(el);this.drops.push({{el,y:this.headY}});this.lastSpawn=now;}}if(!this.done&&this.traveled>=this.maxTravel)this.done=true;const colors=getColors(this.colIndex,now);for(let i=this.drops.length-1;i>=0;i--){{const d=this.drops[i];const dist=(this.headY-d.y)/lnH;if(dist<=.5){{d.el.style.color=colors.head;d.el.style.textShadow=colors.headShadow;d.el.style.opacity='1';}}else if(dist<=trailLen*.25){{d.el.style.color=colors.bright;d.el.style.textShadow=colors.brightShadow;d.el.style.opacity=(bri*.95).toFixed(2);}}else if(dist<=trailLen*.6){{const f=(dist-trailLen*.25)/(trailLen*.35);d.el.style.color=colors.mid;d.el.style.textShadow=colors.midShadow;d.el.style.opacity=Math.max(.08,bri*(.7-f*.4)).toFixed(2);}}else if(dist<=trailLen){{const f=(dist-trailLen*.6)/(trailLen*.4);d.el.style.color=colors.dim;d.el.style.textShadow='none';d.el.style.opacity=Math.max(.02,.15-f*.13).toFixed(2);}}else{{d.el.remove();this.drops.splice(i,1);}}}}if(this.done&&this.drops.length===0)this.dead=true;}};
  function Column(idx){{this.index=idx;this.x=idx*colW;this.trails=[];const t=new Trail(this.x,idx);t.headY=Math.random()*H;t.lastSpawn=-Math.random()*spawnMs*3;this.trails.push(t);}}
  Column.prototype.update=function(now,dt){{for(let i=this.trails.length-1;i>=0;i--){{this.trails[i].update(now,dt);if(this.trails[i].dead)this.trails.splice(i,1);}}if(this.trails.length<maxTrails){{let ok=true;if(this.trails.length>0){{let lh=-Infinity;for(let i=0;i<this.trails.length;i++)if(this.trails[i].headY>lh)lh=this.trails[i].headY;if(lh-trailLen*lnH<gapPx)ok=false;}}if(ok){{const t=new Trail(this.x,this.index);t.headY=-lnH;t.lastSpawn=now;this.trails.push(t);}}}}if(this.trails.length===0){{const t=new Trail(this.x,this.index);t.headY=-lnH;t.lastSpawn=now;this.trails.push(t);}}}};
  const cols=[];for(let i=0;i<numCols;i++)cols.push(new Column(i));
  let lt=performance.now();
  function frame(now){{const dt=(now-lt)/1000;lt=now;for(let i=0;i<cols.length;i++)cols[i].update(now,dt);requestAnimationFrame(frame);}}
  requestAnimationFrame(frame);
  // ESC key closes overlay
  document.addEventListener('keydown',(e)=>{{if(e.key==='Escape')window.parent.postMessage({{type:'MATRIX_FS_CLOSE_FROM_OVERLAY'}},'*');}});
}})();
<\\/script></body></html>`;
  }}

  let overlay = null;
  let closeBtn = null;

  window.closeMatrixFS = function() {{
    if (overlay) {{ overlay.classList.remove('active'); }}
    if (closeBtn) {{ closeBtn.classList.remove('active'); }}
    // Notify the inner iframe it was closed
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach(f => f.contentWindow && f.contentWindow.postMessage({{type: 'MATRIX_FS_CLOSED'}}, '*'));
  }};

  window.addEventListener('message', (e) => {{
    if (!e.data) return;
    if (e.data.type === 'MATRIX_FS_OPEN') {{
      if (!overlay) {{
        overlay = document.getElementById('matrix-fs-overlay');
        closeBtn = document.getElementById('matrix-fs-close');
      }}
      // Build the standalone HTML and load it into the overlay iframe
      const html = buildStandaloneHTML();
      let fsIframe = overlay.querySelector('iframe');
      if (!fsIframe) {{
        fsIframe = document.createElement('iframe');
        fsIframe.setAttribute('allowfullscreen', '');
        overlay.appendChild(fsIframe);
      }}
      const blob = new Blob([html], {{type: 'text/html'}});
      fsIframe.src = URL.createObjectURL(blob);
      overlay.classList.add('active');
      closeBtn.classList.add('active');
      // Also try native fullscreen on the overlay element
      const rq = overlay.requestFullscreen || overlay.webkitRequestFullscreen;
      if (rq) rq.call(overlay);
    }} else if (e.data.type === 'MATRIX_FS_CLOSE' || e.data.type === 'MATRIX_FS_CLOSE_FROM_OVERLAY') {{
      window.closeMatrixFS();
      const ex = document.exitFullscreen || document.webkitExitFullscreen;
      if (ex && (document.fullscreenElement || document.webkitFullscreenElement)) ex.call(document);
    }}
  }});

  // ESC key on parent page
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') window.closeMatrixFS();
  }});
}})();
</script>
"""

st.markdown(parent_fs_script, unsafe_allow_html=True)
