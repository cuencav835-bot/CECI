#!/usr/bin/env python3
"""
REELS LARGOS (60-90s) - Estilo Facebook/TikTok viral
Con narración completa + karaoke palabra por palabra
Resina Epóxica · @VeroResina
"""
import os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

os.environ['IMAGEIO_FFMPEG_EXE'] = imageio_ffmpeg.get_ffmpeg_exe()
from moviepy import VideoClip, AudioArrayClip, AudioFileClip, CompositeAudioClip

OUT_DIR = "/home/user/CECI/videos_reales"
os.makedirs(OUT_DIR, exist_ok=True)
TMP_DIR = "/tmp/reels_largos"
os.makedirs(TMP_DIR, exist_ok=True)

W, H = 1080, 1920
FPS  = 30
SR   = 44100

# ── COLORES ───────────────────────────────────────────────────────────────────
BG       = (6, 4, 16)
TEAL     = (0, 220, 200)
GOLD     = (255, 200, 40)
WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
PINK     = (255, 70, 150)
RED_HOT  = (220, 30, 60)
PURPLE   = (140, 60, 220)
GREEN    = (40, 210, 100)

FONT_DIR = "/root/.claude/skills/canvas-design/canvas-fonts"
def load_font(size, bold=True):
    for name in (["Montserrat-ExtraBold.ttf","Montserrat-Bold.ttf",
                   "BebasNeue-Regular.ttf","Anton-Regular.ttf",
                   "Oswald-Bold.ttf","Roboto-Bold.ttf"] if bold else
                  ["Montserrat-Regular.ttf","Roboto-Regular.ttf",
                   "Montserrat-Bold.ttf"]):
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ── MÚSICA 100 BPM (enérgica pero no agresiva) ───────────────────────────────
def gen_music(duration):
    t   = np.linspace(0, duration, int(SR * duration), endpoint=False)
    bpm = 100
    bt  = 60 / bpm

    def note(freq, start, dur, amp=0.13):
        s = int(start * SR); e = min(int((start + dur) * SR), len(t))
        seg = np.sin(2 * np.pi * freq * t[s:e]) * amp
        fa  = min(int(0.05 * SR), len(seg) // 4)
        if fa > 0:
            seg[:fa]  *= np.linspace(0, 1, fa)
            seg[-fa:] *= np.linspace(1, 0, fa)
        return s, e, seg

    audio = np.zeros(len(t))
    # Am-F-C-G loop
    prog = [(220.0,"Am"),(174.6,"F"),(261.6,"C"),(196.0,"G")]
    bars_total = int(duration / (bt * 4)) + 2
    for bar in range(bars_total):
        for beat_i, (freq, _) in enumerate(prog):
            st = (bar * 4 + beat_i) * bt
            if st >= duration: break
            s, e, sg = note(freq, st, bt * 0.85)
            audio[s:e] += sg
            # 3ra armónica
            s2,e2,sg2 = note(freq * 1.498, st, bt * 0.7, amp=0.05)
            audio[s2:e2] += sg2

    # Kick
    beats_total = int(duration / bt) + 1
    for i in range(beats_total):
        s = int(i * bt * SR)
        kl = min(int(0.14 * SR), len(audio) - s)
        if kl > 0:
            env  = np.exp(-np.linspace(0, 9, kl))
            kick = np.sin(2 * np.pi * np.linspace(90, 42, kl)) * env * 0.3
            audio[s:s+kl] += kick

    # Snare (beats 2 y 4)
    for i in range(beats_total):
        if i % 2 == 1:
            s = int(i * bt * SR)
            sl = min(int(0.08 * SR), len(audio) - s)
            if sl > 0:
                sn = np.random.randn(sl) * 0.15 * np.exp(-np.linspace(0, 20, sl))
                audio[s:s+sl] += sn

    # Hi-hat
    for i in range(beats_total * 2):
        s = int(i * bt * SR / 2)
        hl = min(int(0.025 * SR), len(audio) - s)
        if hl > 0:
            hh = np.random.randn(hl) * 0.045 * np.exp(-np.linspace(0, 18, hl))
            audio[s:s+hl] += hh

    # Bass
    bass = [110.0, 87.3, 130.8, 98.0]
    for bar in range(bars_total):
        for bi, bf in enumerate(bass):
            st = (bar * 4 + bi) * bt
            if st >= duration: break
            s, e, sg = note(bf, st, bt * 0.8, amp=0.22)
            audio[s:e] += sg

    fi = min(int(0.8 * SR), len(audio) // 4)
    fo = min(int(1.5 * SR), len(audio) // 4)
    audio[:fi]  *= np.linspace(0, 1, fi)
    audio[-fo:] *= np.linspace(1, 0, fo)
    audio = np.clip(audio, -1, 1)
    return np.column_stack([audio, audio])

# ── TTS ───────────────────────────────────────────────────────────────────────
def gen_tts(text, path):
    try:
        subprocess.run(
            ["espeak-ng","-v","es-419","-s","128","-p","52","-a","210",
             text,"-w",path],
            check=True, capture_output=True
        )
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception as e:
        print(f"TTS error: {e}")
        return False

# ── FONDO ANIMADO ─────────────────────────────────────────────────────────────
rng = random.Random(99)
BLOBS = [{"cx": rng.randint(100,W-100), "cy": rng.randint(200,H-200),
           "vx": rng.uniform(-20,20),   "vy": rng.uniform(-30,30),
           "r":  rng.randint(200,420),  "c":  rng.choice([TEAL,GOLD,PURPLE,PINK]),
           "ph": rng.uniform(0,6.28)} for _ in range(10)]

PARTS = [{"x": rng.randint(0,W), "y": rng.randint(0,H),
           "vx": rng.uniform(-12,12), "vy": rng.uniform(-35,-5),
           "r":  rng.uniform(2,7),    "c":  rng.choice([TEAL,GOLD,WHITE,PINK]),
           "ph": rng.uniform(0,6.28)} for _ in range(80)]

def bg_frame(t, accent):
    img  = Image.new("RGBA", (W,H), (*BG,255))
    for b in BLOBS:
        cx  = int((b["cx"] + b["vx"]*t) % W)
        cy  = int((b["cy"] + b["vy"]*t) % H)
        r   = int(b["r"] * (1 + 0.15*math.sin(t*0.5+b["ph"])))
        alp = int(28 + 12*math.sin(t*0.7+b["ph"]))
        blob = Image.new("RGBA",(W,H),(0,0,0,0))
        ImageDraw.Draw(blob).ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*b["c"],alp))
        img  = Image.alpha_composite(img, blob.filter(ImageFilter.GaussianBlur(90)))

    # Partículas
    ov = Image.new("RGBA",(W,H),(0,0,0,0))
    od = ImageDraw.Draw(ov)
    for p in PARTS:
        x  = (p["x"] + p["vx"]*t) % W
        y  = (p["y"] + p["vy"]*t) % H
        r  = p["r"] * (1 + 0.3*abs(math.sin(t*1.5+p["ph"])))
        a  = int(160*abs(math.sin(t*1.2+p["ph"])))
        od.ellipse([x-r,y-r,x+r,y+r], fill=(*p["c"],a))
    img = Image.alpha_composite(img, ov)

    # Film grain
    grain = (np.random.rand(H,W,4)*[12,12,12,0]).astype(np.uint8)
    gi    = Image.fromarray(grain,"RGBA")
    img   = Image.alpha_composite(img, gi)

    return img.convert("RGB")

# ── HELPERS ───────────────────────────────────────────────────────────────────
def centered_text(draw, text, y, font, color=WHITE, stroke_color=BLACK, stroke=2):
    bb = draw.textbbox((0,0), text, font=font)
    x  = (W - (bb[2]-bb[0])) // 2
    if stroke > 0:
        for dx in range(-stroke, stroke+1):
            for dy in range(-stroke, stroke+1):
                if dx or dy:
                    draw.text((x+dx,y+dy), text, font=font, fill=stroke_color)
    draw.text((x,y), text, font=font, fill=color)

def pill_text(img, draw, text, cy, font, bg_color, text_color=WHITE, pad_x=30, pad_y=14, radius=20):
    bb   = draw.textbbox((0,0), text, font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    bx1  = (W - tw)//2 - pad_x
    bx2  = (W + tw)//2 + pad_x
    by1  = cy - pad_y
    by2  = cy + th + pad_y
    ov   = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(ov).rounded_rectangle([bx1,by1,bx2,by2], radius=radius, fill=(*bg_color,230))
    img  = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text(((W-tw)//2, cy), text, font=font, fill=text_color)
    return img, draw

def pulsate(t, base=1.0, amp=0.05, freq=2.0):
    return base + amp * math.sin(2*math.pi*freq*t)

# ── RENDERIZADOR GENÉRICO ─────────────────────────────────────────────────────
def make_renderer(scenes, karaoke_words, accent, total_dur, title_text):
    """
    scenes: list of (t_start, t_end, big_line1, big_line2, sub_text, accent_override)
    karaoke_words: list of (word, t_show)   # absoluto
    """
    f_giant = load_font(118, bold=True)
    f_big   = load_font(82,  bold=True)
    f_med   = load_font(60,  bold=True)
    f_small = load_font(44,  bold=True)
    f_tiny  = load_font(34,  bold=False)
    f_kar   = load_font(70,  bold=True)

    def get_scene(t):
        for sc in scenes:
            if sc[0] <= t < sc[1]:
                return sc
        return scenes[-1]

    def get_kword(t):
        best = None
        for word, wt in karaoke_words:
            if wt <= t < wt + 0.6:
                best = word
        return best

    def frame(t):
        sc = get_scene(t)
        ac = sc[5] if sc[5] else accent

        img  = bg_frame(t, ac)
        img  = img.convert("RGBA")
        draw = ImageDraw.Draw(img)

        # ── TOP BAR ──
        bar = Image.new("RGBA",(W,80),(*ac,210))
        img.paste(bar, (0,0), bar)
        draw = ImageDraw.Draw(img)
        draw.text((22,18), f"🎨 @VeroResina  •  Resina Epóxica PRO", font=f_tiny, fill=BLACK)

        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        # ── TEXTO CENTRAL GRANDE ──
        lines = []
        if sc[2]: lines.append((sc[2], f_big))
        if sc[3]: lines.append((sc[3], f_med))
        total_h = sum(f.getbbox("Ag")[3]+20 for _,f in lines)
        y = H//2 - total_h//2 - 60

        for line, font in lines:
            bb   = draw.textbbox((0,0), line, font=font)
            tw,th = bb[2]-bb[0], bb[3]-bb[1]
            bx1  = (W-tw)//2 - 22
            pad_y_box = 10
            ov   = Image.new("RGBA",(W,H),(0,0,0,0))
            od   = ImageDraw.Draw(ov)
            od.rounded_rectangle([bx1, y-pad_y_box, bx1+tw+44, y+th+pad_y_box],
                                  radius=16, fill=(*ac, 195))
            img  = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text(((W-tw)//2, y), line, font=font, fill=BLACK if ac==GOLD else WHITE)
            y   += th + 28

        # ── SUBTÍTULO DE ESCENA ──
        if sc[4]:
            img, draw = pill_text(img, draw, sc[4], y+10, f_small,
                                   BLACK, WHITE, pad_x=24, pad_y=10)

        # ── KARAOKE (zona inferior) ──
        word = get_kword(t)
        if word:
            bb   = draw.textbbox((0,0), word, font=f_kar)
            tw,th = bb[2]-bb[0], bb[3]-bb[1]
            ky   = H - 340
            ov2  = Image.new("RGBA",(W,H),(0,0,0,0))
            od2  = ImageDraw.Draw(ov2)
            od2.rounded_rectangle([(W-tw)//2-24, ky-12, (W+tw)//2+24, ky+th+12],
                                   radius=16, fill=(255,210,0,240))
            img  = Image.alpha_composite(img.convert("RGBA"), ov2).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text(((W-tw)//2, ky), word, font=f_kar, fill=BLACK)

        # ── PROGRESS BAR ──
        prog = t / total_dur
        draw.rectangle([0, H-14, W, H], fill=(30,30,30))
        draw.rectangle([0, H-14, int(W*prog), H], fill=ac)

        # ── CTA botón si es la última escena ──
        if t >= total_dur - 12:
            pls = pulsate(t, 1.0, 0.06, 2.5)
            cw  = int(680 * pls)
            ch  = 105
            cx  = (W-cw)//2
            cy  = H - 220
            ov3 = Image.new("RGBA",(W,H),(0,0,0,0))
            od3 = ImageDraw.Draw(ov3)
            od3.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=38, fill=(220,30,60,245))
            img  = Image.alpha_composite(img.convert("RGBA"), ov3).convert("RGB")
            draw = ImageDraw.Draw(img)
            ct   = "🔥  INSCRÍBETE  →  HOTMART"
            bb   = draw.textbbox((0,0), ct, font=f_small)
            draw.text(((W-(bb[2]-bb[0]))//2, cy+(ch-(bb[3]-bb[1]))//2), ct, font=f_small, fill=WHITE)
            centered_text(draw, "go.hotmart.com/G106175870D?ap=8534", cy+ch+18, f_tiny,
                          color=GOLD, stroke_color=BLACK, stroke=1)

        return np.array(img)

    return frame

# ═══════════════════════════════════════════════════════════════════════════════
# REEL A — "De 0 a Negocio" (≈75 segundos)
# ═══════════════════════════════════════════════════════════════════════════════
NARR_A = (
    "¿Sabías que puedes crear un negocio rentable desde tu casa "
    "con resina epóxica? "
    "Soy Verónica, y hace dos años yo no sabía nada de esto. "
    "Hoy tengo alumnas que ganan entre quinientos y tres mil dólares al mes "
    "trabajando solo dos horas al día. "
    "El mercado de artesanías mueve millones de dólares cada año, "
    "y la resina epóxica es uno de los productos más buscados. "
    "Puedes hacer charolas, cuadros, joyería, mesas y mucho más. "
    "En mi curso aprenderás desde cero: técnicas, materiales, precios y ventas. "
    "No necesitas experiencia previa, solo ganas de aprender. "
    "Tenemos más de dos mil alumnas activas, y los resultados hablan solos. "
    "El link está abajo, inscríbete hoy y cambia tu vida."
)

SCENES_A = [
    # (t_ini, t_fin, línea1, línea2, subtítulo, acento_override)
    (0,   6,  "¿QUIERES UN",      "NEGOCIO DESDE CASA?",    "Sigue viendo... 👇",           GOLD),
    (6,   13, "HACE 2 AÑOS",       "NO SABÍA NADA",          "Y hoy lo cambié todo 🎨",      TEAL),
    (13,  20, "$500 – $3,000",     "AL MES",                 "Trabajando 2 horas al día 💸",  GOLD),
    (20,  27, "MERCADO DE",        "ARTESANÍAS",             "Mueve MILLONES cada año 📈",    TEAL),
    (27,  34, "CHAROLAS",          "CUADROS • JOYERÍA",      "Todo se puede vender ✨",       PURPLE),
    (34,  42, "CURSO DESDE CERO", "SIN EXPERIENCIA",         "Técnicas + ventas incluidas",  PINK),
    (42,  50, "+2,000",            "ALUMNAS ACTIVAS",         "Los resultados hablan solos 🏆", GOLD),
    (50,  58, "TÚ TAMBIÉN",       "PUEDES LOGRARLO",         "Solo necesitas querer hacerlo 💪", TEAL),
    (58,  75, "¡INSCRÍBETE",      "AHORA! 🔥",               "Link abajo 👆 No te lo pierdas", RED_HOT),
]

# Palabras karaoke para REEL A (sincronizadas con TTS ~128wpm)
KWORDS_A = [
    # seg 0-6
    ("¿SABÍAS",0.5),("QUE PUEDES",1.1),("CREAR",1.7),("UN NEGOCIO",2.3),("DESDE CASA",3.0),
    ("CON RESINA",3.8),("EPÓXICA?",4.5),
    # seg 6-13
    ("SOY",6.2),("VERÓNICA",6.7),("HACE DOS AÑOS",7.4),("NO SABÍA",8.2),("NADA",8.9),
    ("DE ESTO",9.5),("HOY",10.2),("TENGO ALUMNAS",10.7),("GANANDO",11.5),("$500-$3000",12.0),
    # seg 13-20
    ("TRABAJANDO",13.4),("SOLO",14.1),("DOS HORAS",14.7),("AL DÍA",15.4),
    ("EL MERCADO",16.2),("DE ARTESANÍAS",17.0),("MUEVE",17.8),("MILLONES",18.4),
    ("CADA AÑO",19.1),
    # seg 20-27
    ("RESINA",20.3),("EPÓXICA",21.0),("ES UNO",21.7),("DE LOS MÁS",22.3),("BUSCADOS",23.0),
    ("CHAROLAS",23.8),("CUADROS",24.5),("JOYERÍA",25.2),("MESAS",25.9),("¡Y MÁS!",26.5),
    # seg 27-42
    ("EN MI CURSO",27.4),("APRENDERÁS",28.2),("DESDE CERO",29.0),("TÉCNICAS",29.8),
    ("MATERIALES",30.6),("PRECIOS",31.4),("Y VENTAS",32.1),("¡TODO!",32.8),
    ("NO NECESITAS",33.7),("EXPERIENCIA",34.5),("PREVIA",35.2),("SOLO",35.9),
    ("GANAS",36.6),("DE APRENDER",37.3),
    # seg 42-58
    ("+2,000",42.5),("ALUMNAS",43.2),("ACTIVAS",43.9),("LOS RESULTADOS",44.8),
    ("HABLAN",45.7),("SOLOS",46.3),("TÚ TAMBIÉN",47.2),("PUEDES",48.0),
    ("LOGRARLO",48.7),("EL LINK",49.6),("ESTÁ ABAJO",50.3),
    # seg 58+
    ("¡INSCRÍBETE",58.5),("HOY",59.3),("Y CAMBIA",60.0),("TU VIDA!",60.7),
    ("🔥 VAMOS",61.5),("HOTMART",62.3),("ABAJO",63.0),("👆",63.8),
]

# ═══════════════════════════════════════════════════════════════════════════════
# REEL B — "El Secreto de la Resina" (≈85 segundos)
# ═══════════════════════════════════════════════════════════════════════════════
NARR_B = (
    "Te voy a revelar el secreto que pocas personas conocen "
    "sobre la resina epóxica. "
    "Es uno de los materiales más versátiles y rentables del mercado artesanal. "
    "Con ella puedes crear piezas únicas que la gente paga muy bien. "
    "Un cuadro de resina puede venderse entre cien y quinientos dólares. "
    "Una charola decorativa, entre cincuenta y doscientos. "
    "Joyería artesanal, entre veinte y ochenta dólares por pieza. "
    "Y lo mejor es que los materiales son económicos y fáciles de conseguir. "
    "En mi curso completo de resina epóxica te enseño todo paso a paso. "
    "Colores, texturas, moldes, técnicas de mármol, océano y mucho más. "
    "Más de dos mil mujeres ya transformaron su vida con esto. "
    "¿Vas a ser la siguiente? "
    "Haz clic en el link de abajo e inscríbete ahora."
)

SCENES_B = [
    (0,   7,  "EL SECRETO",        "QUE NADIE DICE",         "De la resina epóxica 🤫",       TEAL),
    (7,   15, "MATERIAL",          "MÁS VERSÁTIL",            "Del mercado artesanal 🎨",      GOLD),
    (15,  23, "CUADROS",           "$100 – $500",             "Piezas únicas, precios reales 💰",TEAL),
    (23,  30, "CHAROLAS",          "$50 – $200",              "¡Las más vendidas!",             GOLD),
    (30,  37, "JOYERÍA",           "$20 – $80 c/u",           "Fácil de hacer, fácil de vender",PINK),
    (37,  45, "MATERIALES",        "ECONÓMICOS",              "Fáciles de conseguir ✅",        GREEN),
    (45,  55, "MÁRMOL • OCÉANO",   "TEXTURAS • COLORES",      "Todo en un solo curso",         PURPLE),
    (55,  65, "+2,000 MUJERES",    "YA LO LOGRARON",          "¿Vas a ser la siguiente? 💪",    GOLD),
    (65,  85, "¡INSCRÍBETE",       "AHORA! 🚀",               "Link abajo · No esperes más",    RED_HOT),
]

KWORDS_B = [
    ("TE VOY",0.4),("A REVELAR",1.0),("EL SECRETO",1.7),("QUE POCAS",2.4),
    ("PERSONAS",3.0),("CONOCEN",3.7),("RESINA",4.5),("EPÓXICA",5.1),
    ("VERSÁTIL",6.0),("Y RENTABLE",6.8),
    ("PIEZAS ÚNICAS",7.5),("LA GENTE",8.3),("PAGA BIEN",9.0),
    ("UN CUADRO",10.0),("$100",10.8),("A $500",11.4),("DÓLARES",12.1),
    ("CHAROLA",13.0),("$50",13.8),("A $200",14.4),
    ("JOYERÍA",15.2),("$20",16.0),("A $80",16.6),("POR PIEZA",17.3),
    ("MATERIALES",18.2),("ECONÓMICOS",19.0),("FÁCILES",19.8),("DE CONSEGUIR",20.5),
    ("MI CURSO",21.5),("COMPLETO",22.2),("PASO A PASO",23.0),
    ("COLORES",24.0),("TEXTURAS",24.7),("MOLDES",25.4),
    ("MÁRMOL",26.2),("OCÉANO",26.9),("¡Y MÁS!",27.6),
    ("+2,000",28.5),("MUJERES",29.2),("TRANSFORMARON",30.0),("SU VIDA",30.8),
    ("¿VAS A SER",31.8),("LA SIGUIENTE?",32.6),
    ("HAZ CLIC",33.6),("EN EL LINK",34.3),("¡INSCRÍBETE",35.0),("¡AHORA!",35.7),
    # zona CTA larga
    ("🔥",65.5),("INSCRÍBETE",66.2),("HOY",67.0),("HOTMART",67.8),
    ("LINK",68.6),("ABAJO",69.3),("👆",70.0),("¡VAMOS!",71.0),
    ("NO ESPERES",72.0),("MÁS",72.7),("🚀",73.5),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GENERADOR
# ═══════════════════════════════════════════════════════════════════════════════
def build_reel(name, scenes, kwords, narr_text, accent, out_name):
    print(f"\n{'='*60}")
    print(f"  🎬 {name}")
    print(f"{'='*60}")

    total_dur = float(scenes[-1][1])
    print(f"  ⏱  Duración: {total_dur:.0f}s")

    # TTS
    voz_path = os.path.join(TMP_DIR, f"{out_name}_voz.wav")
    has_tts  = gen_tts(narr_text, voz_path)
    if has_tts:
        print(f"  ✅ Narración TTS generada")
    else:
        print(f"  ⚠️  Sin narración, solo música")

    # Música
    music = gen_music(total_dur)

    # Audio compuesto
    clips_aud = [AudioArrayClip(music * 0.45, fps=SR).with_duration(total_dur)]
    if has_tts:
        vc    = AudioFileClip(voz_path)
        va    = vc.to_soundarray(fps=SR)
        if va.ndim == 1:
            va = np.column_stack([va, va])
        va    = va * 1.5
        vdur  = min(va.shape[0]/SR, total_dur - 0.5)
        clips_aud.append(AudioArrayClip(va, fps=SR).with_duration(vdur))

    audio = CompositeAudioClip(clips_aud).with_duration(total_dur)

    # Video
    render = make_renderer(scenes, kwords, accent, total_dur, name)
    video  = VideoClip(render, duration=total_dur).with_fps(FPS).with_audio(audio)

    out_path = os.path.join(OUT_DIR, f"{out_name}.mp4")
    video.write_videofile(
        out_path, fps=FPS, codec="libx264", audio_codec="aac",
        ffmpeg_params=["-crf","23","-preset","fast","-pix_fmt","yuv420p"],
        logger="bar"
    )
    sz = os.path.getsize(out_path)/1e6
    print(f"\n  ✅ Guardado → {out_path}  ({sz:.1f} MB)")
    return out_path

if __name__ == "__main__":
    r1 = build_reel(
        "REEL A — De 0 a Negocio (75s)",
        SCENES_A, KWORDS_A, NARR_A,
        TEAL, "ReelLargo_A_De0ANegocio"
    )
    r2 = build_reel(
        "REEL B — El Secreto de la Resina (85s)",
        SCENES_B, KWORDS_B, NARR_B,
        GOLD, "ReelLargo_B_ElSecreto"
    )
    print("\n🏁 ¡Ambos reels listos!")
    print(f"  1️⃣  {r1}")
    print(f"  2️⃣  {r2}")
