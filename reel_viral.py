#!/usr/bin/env python3
"""
REEL VIRAL - Estilo Facebook/TikTok
Resina Epóxica · @VeroResina · go.hotmart.com/G106175870D?ap=8534
"""
import os, sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

os.environ['IMAGEIO_FFMPEG_EXE'] = imageio_ffmpeg.get_ffmpeg_exe()
from moviepy import VideoClip, AudioArrayClip, CompositeAudioClip

OUT_DIR = "/home/user/CECI/videos_reales"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1080, 1920
FPS = 30
SR = 44100

# ── COLORES ──────────────────────────────────────────────────────────────────
BG_DARK   = (8, 6, 18)
TEAL      = (0, 220, 200)
GOLD      = (255, 200, 40)
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
PINK      = (255, 80, 160)
ACCENT    = TEAL
HOT_RED   = (220, 30, 60)

# ── TIPOGRAFÍA ────────────────────────────────────────────────────────────────
FONT_DIR = "/root/.claude/skills/canvas-design/canvas-fonts"
def load_font(size, bold=False):
    candidates = [
        "Montserrat-ExtraBold.ttf","Montserrat-Bold.ttf",
        "BebasNeue-Regular.ttf","Anton-Regular.ttf",
        "Oswald-Bold.ttf","Roboto-Bold.ttf",
    ]
    if not bold:
        candidates += ["Montserrat-Regular.ttf","Roboto-Regular.ttf"]
    for name in candidates:
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ── MÚSICA VIRAL (120 BPM, energética) ───────────────────────────────────────
def gen_music(duration):
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    bpm = 120
    beat = 60 / bpm

    def note(freq, start, dur, amp=0.18):
        s = int(start * SR); e = int((start + dur) * SR)
        seg = np.sin(2 * np.pi * freq * t[s:e]) * amp
        fade = min(int(0.05 * SR), len(seg) // 4)
        if fade > 0:
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
        return s, e, seg

    audio = np.zeros(len(t))

    # Am pentatónico - loop de 4 beats
    chords = [
        (220.0, 0), (261.6, 1), (293.7, 2), (349.2, 3),
        (220.0, 4), (261.6, 5), (293.7, 6), (392.0, 7),
        (174.6, 8), (220.0, 9), (261.6, 10),(293.7,11),
        (220.0,12), (261.6,13),(349.2,14),(392.0,15),
    ]
    beats_total = int(duration / beat) + 1
    for i in range(beats_total):
        ci = i % len(chords)
        freq, _ = chords[ci]
        s, e, seg = note(freq, i * beat, beat * 0.9, amp=0.12)
        audio[s:e] += seg

    # Kick drum cada beat
    for i in range(beats_total):
        s = int(i * beat * SR)
        kick_len = min(int(0.12 * SR), len(audio) - s)
        if kick_len > 0:
            env = np.exp(-np.linspace(0, 10, kick_len))
            kick = np.sin(2 * np.pi * np.linspace(80, 40, kick_len)) * env * 0.35
            audio[s:s+kick_len] += kick

    # Hi-hat cada medio beat
    for i in range(beats_total * 2):
        s = int(i * beat * SR / 2)
        hh_len = min(int(0.03 * SR), len(audio) - s)
        if hh_len > 0:
            hh = np.random.randn(hh_len) * 0.06 * np.exp(-np.linspace(0, 15, hh_len))
            audio[s:s+hh_len] += hh

    # Bass line
    bass_notes = [110, 87.3, 130.8, 110]
    for i in range(beats_total):
        bn = bass_notes[i % 4]
        s, e, seg = note(bn, i * beat, beat * 0.8, amp=0.2)
        seg2 = np.sin(2 * np.pi * bn * 2 * t[s:e]) * 0.05
        audio[s:e] += seg + seg2[:len(seg)]

    # Fade in/out
    fi = min(int(0.5 * SR), len(audio) // 4)
    fo = min(int(1.0 * SR), len(audio) // 4)
    audio[:fi] *= np.linspace(0, 1, fi)
    audio[-fo:] *= np.linspace(1, 0, fo)
    audio = np.clip(audio, -1, 1)
    return np.column_stack([audio, audio])

# ── TTS VOZ ───────────────────────────────────────────────────────────────────
def gen_tts(text, path):
    try:
        subprocess.run(
            ["espeak-ng","-v","es-419","-s","130","-p","55","-a","200",
             text, "-w", path],
            check=True, capture_output=True
        )
        return True
    except:
        return False

# ── HELPERS VISUALES ──────────────────────────────────────────────────────────
def draw_rounded_rect(draw, xy, fill, radius=18, alpha=None):
    x1,y1,x2,y2 = xy
    if alpha is not None:
        tmp = Image.new("RGBA",(x2-x1,y2-y1),(0,0,0,0))
        d = ImageDraw.Draw(tmp)
        d.rounded_rectangle([0,0,x2-x1,y2-y1], radius=radius, fill=(*fill,alpha))
        return tmp, (x1,y1)
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def centered_text(draw, text, y, font, color=WHITE, stroke=True, stroke_color=BLACK):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x = (W - tw) // 2
    if stroke:
        for dx in [-2,2]:
            for dy in [-2,2]:
                draw.text((x+dx, y+dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=color)

def pulsate(t, base=1.0, amp=0.04, freq=2.0):
    return base + amp * math.sin(2 * math.pi * freq * t)

# ── PARTÍCULAS BRILLANTES ─────────────────────────────────────────────────────
rng = random.Random(42)
PARTICLES = [
    {
        "x": rng.randint(50, W-50),
        "y": rng.randint(100, H-100),
        "r": rng.uniform(2, 8),
        "vx": rng.uniform(-15, 15),
        "vy": rng.uniform(-40, -10),
        "c": rng.choice([TEAL, GOLD, PINK, WHITE]),
        "phase": rng.uniform(0, 6.28)
    }
    for _ in range(60)
]

def draw_particles(img, t):
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for p in PARTICLES:
        x = (p["x"] + p["vx"] * t) % W
        y = (p["y"] + p["vy"] * t) % H
        alpha = int(180 * abs(math.sin(t * 1.5 + p["phase"])))
        r = p["r"] * pulsate(t, 1.0, 0.3, 1.5 + p["phase"])
        od.ellipse([x-r, y-r, x+r, y+r], fill=(*p["c"], alpha))
    img.paste(overlay, mask=overlay)

# ── FONDO ANIMADO (resina líquida) ────────────────────────────────────────────
def resin_bg(t):
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Ondas de resina fluidas
    for i in range(8):
        phase = t * 0.4 + i * 0.7
        cx = int(W/2 + math.sin(phase) * 300 + i * 60)
        cy = int(H/2 + math.cos(phase * 0.7) * 400 - i * 100)
        r = int(200 + 80 * math.sin(phase * 1.3))
        alpha = int(35 + 20 * math.sin(phase))
        c = TEAL if i % 2 == 0 else GOLD
        blob = Image.new("RGBA", (W, H), (0,0,0,0))
        bd = ImageDraw.Draw(blob)
        bd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*c, alpha))
        blurred = blob.filter(ImageFilter.GaussianBlur(radius=80))
        img = Image.alpha_composite(img.convert("RGBA"), blurred).convert("RGB")

    # Brillo central
    glow_r = int(350 + 50 * math.sin(t * 0.8))
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W//2-glow_r, H//2-glow_r, W//2+glow_r, H//2+glow_r],
               fill=(20, 180, 160, 20))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    # Grano de película
    noise = (np.random.rand(H, W, 3) * 12).astype(np.uint8)
    img_arr = np.array(img)
    img = Image.fromarray(np.clip(img_arr + noise - 6, 0, 255).astype(np.uint8))

    return img

# ── SECCIONES DEL REEL ────────────────────────────────────────────────────────
# Duración total ≈ 30s
# Hook (0-4s) → Problema (4-9s) → Solución (9-15s) → Prueba (15-21s) → CTA (21-30s)

SECTIONS = [
    # (inicio, fin, tipo, texto_grande, texto_pequeño, color_acento, emojis)
    (0,  4,  "hook",    "¿QUIERES GANAR\nDINERO DESDE\nCASA? 🔥",
                         "Mira esto 👇",                    GOLD, ["✨","💫","🔥"]),
    (4,  9,  "problem", "¿SIENTES QUE\nTU TIEMPO\nNO ALCANZA?",
                         "El 87% de mamás lo sienten",     PINK, ["😤","😩","💔"]),
    (9,  15, "solution","RESINA EPÓXICA\nES EL NEGOCIO\nQUE NECESITAS",
                         "Arte que se convierte en dinero 💰", TEAL, ["🎨","✨","💎"]),
    (15, 21, "proof",   "ALUMNAS\nGANAN $500-\n$3,000/MES",
                         "Con solo 2 horas al día",         GOLD, ["💸","🏆","⭐"]),
    (21, 30, "cta",     "¡INSCRÍBETE\nAHORA!",
                         "↓ Link en la descripción ↓",      HOT_RED, ["👆","🎯","🚀"]),
]

# Karaoke por sección
KARAOKE = {
    "hook":    [("¿QUIERES",0.5),("GANAR",1.0),("DINERO",1.5),("DESDE CASA?",2.0),("MIRA ESTO",3.0)],
    "problem": [("TIEMPO",4.5),("NO ALCANZA",5.2),("¿VERDAD?",6.2),("YO TAMBIÉN",7.0),("LO SENTÍ",7.8)],
    "solution":[("RESINA",9.3),("EPÓXICA",10.0),("EL NEGOCIO",11.0),("QUE BUSCABAS",12.0),("¡ES REAL!",13.5)],
    "proof":   [("ALUMNAS",15.5),("REALES",16.3),("GANANDO",17.0),("500 A",17.8),("3,000/MES",18.5),("TÚ TAMBIÉN",19.5),("PUEDES",20.2)],
    "cta":     [("¡ÚNETE",21.5),("AL CURSO",22.3),("AHORA!",23.0),("LINK",24.5),("ABAJO",25.0),("👆",25.8),("¡VAMOS!",27.0)],
}

def get_section(t):
    for s in SECTIONS:
        if s[0] <= t < s[1]:
            return s
    return SECTIONS[-1]

def get_active_word(t):
    for sec_key, words in KARAOKE.items():
        for word, wt in words:
            if abs(t - wt) < 0.55:
                return word
    return None

# ── RENDERIZADOR DE FRAMES ─────────────────────────────────────────────────────
f_big   = None
f_med   = None
f_small = None
f_tiny  = None

def init_fonts():
    global f_big, f_med, f_small, f_tiny
    f_big   = load_font(110, bold=True)
    f_med   = load_font(72,  bold=True)
    f_small = load_font(52,  bold=True)
    f_tiny  = load_font(36,  bold=False)

def make_frame(t):
    sec = get_section(t)
    _, _, sec_type, big_text, small_text, accent, emojis = sec

    img = resin_bg(t)
    draw = ImageDraw.Draw(img)

    # Partículas
    draw_particles(img, t)
    draw = ImageDraw.Draw(img)  # redraw after paste

    # ── TOP BAR (@VeroResina) ──
    bar_h = 90
    top_bar = Image.new("RGBA", (W, bar_h), (*accent, 220))
    img.paste(Image.fromarray(np.array(top_bar)[:,:,:3]), (0,0))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "🎨 @VeroResina  |  Resina Epóxica PRO", font=f_tiny, fill=BLACK)

    # ── EMOJI FLOTANTE ──
    ei = int(t * 2) % len(emojis)
    ey = int(H*0.35 + 30*math.sin(t*2))
    draw.text((W-140, ey), emojis[ei], font=load_font(80), fill=WHITE)

    # ── TEXTO PRINCIPAL (zona central) ──
    lines = big_text.split("\n")
    scale = pulsate(t, 1.0, 0.02, 1.8) if sec_type in ("hook","cta") else 1.0
    y_start = H // 2 - len(lines) * 70

    for i, line in enumerate(lines):
        # Sombra de fondo
        bb = draw.textbbox((0,0), line, font=f_big)
        tw = bb[2]-bb[0]
        x = (W - int(tw*scale)) // 2
        y = y_start + i * 130

        # Caja de color detrás del texto
        pad = 24
        box_w = int(tw * scale) + pad*2
        box_h = int((bb[3]-bb[1]) * scale) + pad
        bx1 = (W - box_w) // 2
        overlay = Image.new("RGBA", (W,H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle([bx1, y-pad//2, bx1+box_w, y+box_h],
                              radius=20, fill=(*accent, 200))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        # Texto
        draw.text((x, y), line, font=f_big, fill=BLACK if accent==GOLD else WHITE)

    # ── KARAOKE ACTIVO (abajo) ──
    word = get_active_word(t)
    if word:
        wb = draw.textbbox((0,0), word, font=f_med)
        ww = wb[2]-wb[0]
        wx = (W - ww) // 2
        wy = H - 320
        # Caja karaoke
        overlay2 = Image.new("RGBA", (W,H), (0,0,0,0))
        od2 = ImageDraw.Draw(overlay2)
        od2.rounded_rectangle([wx-20, wy-10, wx+ww+20, wy+(wb[3]-wb[1])+10],
                               radius=14, fill=(255,220,0,230))
        img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.text((wx, wy), word, font=f_med, fill=BLACK)

    # ── TEXTO PEQUEÑO ──
    centered_text(draw, small_text, H//2 + len(lines)*130 + 30, f_small,
                  color=WHITE, stroke=True)

    # ── PROGRESS BAR ──
    total_dur = SECTIONS[-1][1]
    prog = t / total_dur
    bar_y = H - 16
    draw.rectangle([0, bar_y, W, H], fill=(30,30,30))
    draw.rectangle([0, bar_y, int(W*prog), H], fill=accent)

    # ── CTA ESPECIAL ──
    if sec_type == "cta":
        pulse = pulsate(t, 1.0, 0.08, 3.0)
        cta_w = int(700 * pulse)
        cta_h = 110
        cx = (W - cta_w) // 2
        cy = H - 220

        overlay3 = Image.new("RGBA", (W,H), (0,0,0,0))
        od3 = ImageDraw.Draw(overlay3)
        od3.rounded_rectangle([cx, cy, cx+cta_w, cy+cta_h],
                               radius=40, fill=(220,30,60,240))
        img = Image.alpha_composite(img.convert("RGBA"), overlay3).convert("RGB")
        draw = ImageDraw.Draw(img)
        cta_text = "🔥 CURSO AHORA → HOTMART"
        bb = draw.textbbox((0,0), cta_text, font=f_small)
        tx = (W - (bb[2]-bb[0])) // 2
        ty = cy + (cta_h - (bb[3]-bb[1])) // 2
        draw.text((tx, ty), cta_text, font=f_small, fill=WHITE)

        # URL
        centered_text(draw, "go.hotmart.com/G106175870D", cy+cta_h+20, f_tiny,
                      color=GOLD, stroke=False)

    return np.array(img)

# ── AUDIO ─────────────────────────────────────────────────────────────────────
def build_audio(total_dur):
    music = gen_music(total_dur)

    # Voz en off
    voz_script = (
        "¿Quieres ganar dinero desde casa haciendo arte? "
        "El negocio de resina epóxica está creciendo. "
        "Mis alumnas ganan entre 500 y 3000 dólares al mes. "
        "Solo necesitas dos horas al día. "
        "Inscríbete ahora en el curso. El link está abajo."
    )
    voz_path = "/tmp/reel_voz.wav"
    clips_audio = [AudioArrayClip(music, fps=SR).with_duration(total_dur)]

    if gen_tts(voz_script, voz_path) and os.path.exists(voz_path):
        from moviepy import AudioFileClip
        voz_clip = AudioFileClip(voz_path)
        voz_arr = voz_clip.to_soundarray(fps=SR)
        if voz_arr.ndim == 1:
            voz_arr = np.column_stack([voz_arr, voz_arr])
        # Ajustar volumen voz más alto que música
        voz_arr = voz_arr * 1.4
        music_low = music * 0.45
        voz_dur = min(voz_arr.shape[0] / SR, total_dur - 0.5)
        clips_audio = [
            AudioArrayClip(music_low, fps=SR).with_duration(total_dur),
            AudioArrayClip(voz_arr, fps=SR).with_duration(voz_dur),
        ]
        print(f"  ✅ Voz TTS añadida ({voz_dur:.1f}s)")
    else:
        print("  ⚠️  Sin TTS, solo música")

    return CompositeAudioClip(clips_audio).with_duration(total_dur)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    init_fonts()
    total_dur = float(SECTIONS[-1][1])  # 30s
    print(f"🎬 Generando REEL VIRAL ({total_dur}s, {FPS}fps)...")

    video = VideoClip(make_frame, duration=total_dur).with_fps(FPS)
    audio = build_audio(total_dur)
    video = video.with_audio(audio)

    out_path = os.path.join(OUT_DIR, "ReelViral_VeroResina.mp4")
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    video.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=["-crf","23","-preset","fast","-pix_fmt","yuv420p"],
        logger="bar"
    )
    print(f"\n✅ REEL VIRAL → {out_path}")
    size_mb = os.path.getsize(out_path) / 1e6
    print(f"   Tamaño: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
