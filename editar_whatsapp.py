"""
Editor de videos reales de resina para redes sociales.
Toma los 4 videos de WhatsApp y les agrega:
  - Upscale a 1080x1920 (9:16 TikTok/Reels/Stories)
  - Intro animada (3s) con hook de atención
  - Música de fondo generativa (inspiracional, 80 BPM)
  - Subtítulos/texto educativo animado por fases
  - Emojis flotantes animados
  - Marca VeroResina en todo momento
  - Barra de progreso
  - CTA final animado (5s)
"""

import os, math, random, struct, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips
from moviepy.audio.AudioClip import AudioArrayClip

random.seed(7); np.random.seed(7)

UPLOADS = "/root/.claude/uploads/e53a79e8-4dea-557c-b336-e5482ebcc79c"
FONTS   = "/root/.claude/skills/canvas-design/canvas-fonts"
OUT     = "/home/user/CECI/videos_reales"
TMP     = "/tmp/reales_tmp"
SR      = 44100
VW, VH  = 1080, 1920
FPS     = 30

os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ── Paleta ──────────────────────────────────────────────────────────────
DARK   = (5,  10,  12)
TEAL   = (78, 205, 196)
GOLD   = (247, 201, 72)
CREAM  = (240, 250, 248)
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
PINK   = (255, 100, 180)
GREEN  = (60,  220, 120)
PURPLE = (160, 80, 220)

def fnt(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

def centered_text(draw, text, y, font, color, W=VW, stroke=3):
    bb   = draw.textbbox((0,0), text, font=font)
    tw   = bb[2] - bb[0]
    x    = (W - tw) // 2
    for dx in range(-stroke, stroke+1):
        for dy in range(-stroke, stroke+1):
            if dx!=0 or dy!=0:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,200))
    draw.text((x, y), text, font=font, fill=color)

def wrap_text(text, max_chars=28):
    words = text.split()
    lines, line = [], ""
    for w in words:
        if len(line) + len(w) + 1 <= max_chars:
            line = (line + " " + w).strip()
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

# ── Música inspiracional (80 BPM, Am pentatónica) ───────────────────────
def gen_music(duration):
    t   = np.linspace(0, duration, int(SR * duration), endpoint=False)
    bpm = 80
    beat = 60 / bpm

    # Acordes Am → F → C → G (loop)
    chord_freqs = [
        [220.00, 261.63, 329.63],  # Am
        [174.61, 220.00, 261.63],  # F
        [261.63, 329.63, 392.00],  # C
        [196.00, 246.94, 293.66],  # G
    ]
    bars   = int(duration / (beat * 4)) + 1
    audio  = np.zeros(len(t))

    for bar in range(bars):
        chord = chord_freqs[bar % 4]
        t0 = bar * beat * 4
        t1 = t0 + beat * 4
        mask = (t >= t0) & (t < min(t1, duration))
        seg  = t[mask] - t0
        wave_sum = np.zeros(len(seg))
        for freq in chord:
            # Fundamental + harmonic leve
            wave_sum += 0.25 * np.sin(2*np.pi*freq*seg)
            wave_sum += 0.08 * np.sin(2*np.pi*freq*2*seg)
        # Suavizado de inicio/fin del acorde
        fade = 0.1
        fade_samp = int(fade * SR)
        env = np.ones(len(seg))
        env[:fade_samp] = np.linspace(0, 1, fade_samp)
        env[-fade_samp:] = np.linspace(1, 0, fade_samp)
        audio[mask] += wave_sum * env

    # Kick sutil cada beat
    for i in range(int(duration / beat) + 1):
        ts = i * beat
        idx = int(ts * SR)
        kick_len = int(0.08 * SR)
        if idx + kick_len < len(audio):
            k = np.linspace(1, 0, kick_len)**2 * np.sin(2*np.pi*60*np.linspace(0, 0.08, kick_len)) * 0.3
            audio[idx:idx+kick_len] += k

    audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.55
    stereo = np.stack([audio, audio], axis=1).astype(np.float32)
    return AudioArrayClip(stereo, fps=SR)

# ── Intro animada (3s) ───────────────────────────────────────────────────
def make_intro_frames(hook_line1, hook_line2, accent, fps=FPS, dur=3.0):
    n = int(dur * fps)
    frames = []
    f1 = fnt("BigShoulders-Bold.ttf", 88)
    f2 = fnt("BigShoulders-Bold.ttf", 68)
    fbrand = fnt("InstrumentSans-Bold.ttf", 36)

    for i in range(n):
        progress = i / (n - 1)
        img = Image.new("RGBA", (VW, VH), DARK + (255,))
        d   = ImageDraw.Draw(img)

        # Fondo con gradiente de puntos animados
        for _ in range(80):
            rx = random.randint(0, VW)
            ry = random.randint(0, VH)
            r  = random.randint(2, 8)
            alpha = int(40 + 40 * math.sin(progress * math.pi * 2 + random.random() * 6))
            d.ellipse([rx-r, ry-r, rx+r, ry+r], fill=accent+(alpha,))

        # Línea decorativa lateral
        line_h = int(VH * progress)
        d.rectangle([0, 0, 6, line_h], fill=accent+(200,))
        d.rectangle([VW-6, VH-line_h, VW, VH], fill=GOLD+(200,))

        # Hook text con entrada slide-up
        slide = int((1 - progress) * 80) if progress < 0.4 else 0
        alpha_text = min(255, int(progress * 3 * 255))

        # Caja semi-transparente detrás del texto
        box_y = VH//2 - 160
        d.rounded_rectangle([80, box_y, VW-80, box_y+240], radius=30,
                             fill=(0,0,0,int(160*min(1,progress*3))))

        centered_text(d, hook_line1, VH//2 - 140 + slide, f1, accent)
        centered_text(d, hook_line2, VH//2 - 40  + slide, f2, CREAM)

        # Emoji de atención animado
        pulse = 1 + 0.2 * math.sin(progress * math.pi * 6)
        emoji_font = fnt("NotoEmoji-Bold.ttf", int(80 * pulse))
        centered_text(d, "👇", VH//2 + 100, emoji_font, WHITE)

        # Marca
        centered_text(d, "@VeroResina • @RPResina • @PXResina", VH - 60, fbrand, TEAL)

        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Overlay frame sobre el video real ───────────────────────────────────
def make_overlay_frame(t, total_dur, texto_fases, accent, emojis_list):
    img = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    progress = t / total_dur

    # Barra de progreso (abajo)
    bar_y = VH - 28
    bw    = int(VW * progress)
    d.rectangle([0, bar_y, VW, VH], fill=(0,0,0,100))
    d.rectangle([0, bar_y, bw, VH], fill=TEAL+(200,))
    # Punto en el progreso
    if bw > 10:
        d.ellipse([bw-12, bar_y-6, bw+12, bar_y+VH-bar_y+6], fill=GOLD+(255,))

    # Marca top
    f_brand = fnt("InstrumentSans-Bold.ttf", 32)
    d.rectangle([0, 0, VW, 55], fill=(0,0,0,160))
    centered_text(d, "@VeroResina  •  @RPResina  •  @PXResina", 12, f_brand, TEAL)

    # Texto educativo por fases
    fase_dur = total_dur / len(texto_fases)
    fase_idx = min(int(t / fase_dur), len(texto_fases) - 1)
    fase_progress = (t - fase_idx * fase_dur) / fase_dur

    texto = texto_fases[fase_idx]
    lines = wrap_text(texto, 26)

    # Caja de subtítulo
    f_sub  = fnt("InstrumentSans-Bold.ttf", 52)
    line_h = 65
    box_h  = len(lines) * line_h + 40
    box_y  = VH - 180 - box_h

    # Entrada deslizante
    slide_in = max(0, min(1, fase_progress * 5))
    box_y_anim = int(box_y + (1 - slide_in) * 60)

    d.rounded_rectangle([40, box_y_anim, VW-40, box_y_anim+box_h],
                        radius=20, fill=(0,0,0,int(200*slide_in)))

    for li, line in enumerate(lines):
        ty = box_y_anim + 20 + li * line_h
        # Resaltar palabras clave en dorado
        keywords = ["resina", "curso", "vender", "dinero", "epóxica", "gratis",
                    "aprende", "negocio", "ganas", "técnica", "fácil", "rápido"]
        color = GOLD if any(k in line.lower() for k in keywords) else CREAM
        centered_text(d, line, ty, f_sub, color, stroke=2)

    # Emoji flotante cada 5 segundos
    emoji_cycle = int(t / 5) % len(emojis_list)
    emoji_t = t % 5
    if emoji_t < 2.5:
        e_alpha = int(255 * min(1, emoji_t * 2))
        e_y = int(VH * 0.4 - emoji_t * 60)
        e_x = int(VW * (0.15 + (emoji_cycle % 3) * 0.35))
        try:
            f_emoji = fnt("NotoEmoji-Bold.ttf", 90)
            d.text((e_x, e_y), emojis_list[emoji_cycle], font=f_emoji,
                   fill=WHITE+(e_alpha,))
        except:
            pass

    return np.array(img)

# ── CTA final (5s) ──────────────────────────────────────────────────────
def make_cta_frames(accent, fps=FPS, dur=5.0):
    n = int(dur * fps)
    frames = []
    f1   = fnt("BigShoulders-Bold.ttf", 82)
    f2   = fnt("InstrumentSans-Bold.ttf", 48)
    f3   = fnt("InstrumentSans-Regular.ttf", 38)
    furl = fnt("DMMono-Regular.ttf", 30)
    fbr  = fnt("Italiana-Regular.ttf", 44)

    for i in range(n):
        p    = i / (n - 1)
        img  = Image.new("RGBA", (VW, VH), DARK + (255,))
        d    = ImageDraw.Draw(img)

        # Fondo animado
        for ci in range(5):
            angle = p * math.pi * 2 + ci * 1.2
            cx = VW//2 + int(math.cos(angle) * VW * 0.4)
            cy = VH//2 + int(math.sin(angle) * VH * 0.25)
            r  = int(VW * 0.2 + math.sin(p*math.pi*3 + ci) * 30)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=accent+(30,))

        # Líneas decorativas
        d.rectangle([0, 0, VW, 8],    fill=accent+(180,))
        d.rectangle([0, VH-8, VW, VH], fill=GOLD+(180,))

        # Texto principal
        centered_text(d, "¿LISTA PARA EMPEZAR?", VH//2 - 340, f1, GOLD)
        centered_text(d, "Curso de Resina Epóxica", VH//2 - 240, f2, CREAM)

        sep_x = VW // 2 - 200
        d.rectangle([sep_x, VH//2 - 185, sep_x + 400, VH//2 - 182], fill=TEAL+(200,))

        beneficios = ["✅ Desde cero, a tu ritmo", "✅ Con certificado incluido",
                      "✅ Comunidad de apoyo"]
        for bi, ben in enumerate(beneficios):
            centered_text(d, ben, VH//2 - 160 + bi*70, f3, CREAM)

        # Botón pulsante
        pulse = 1 + 0.06 * math.sin(p * math.pi * 8)
        bw, bh = int(820*pulse), int(110*pulse)
        bx = (VW - bw) // 2
        by = VH//2 + 80
        d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=32, fill=GOLD+(240,))
        centered_text(d, "👉  QUIERO EL CURSO", by + 22, f2, DARK, stroke=0)

        centered_text(d, "go.hotmart.com/G106175870D", by + 130, furl, TEAL)
        centered_text(d, "VeroResina", VH - 90, fbr, GOLD)

        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Procesador principal ─────────────────────────────────────────────────
def editar_video(input_path, nombre, hook1, hook2, fases_texto, accent, emojis):
    print(f"\n🎬 Procesando: {nombre}")

    # 1. Cargar video original
    clip = VideoFileClip(input_path)
    orig_w, orig_h = clip.size
    dur = clip.duration
    print(f"   Original: {orig_w}x{orig_h} {dur:.1f}s")

    # 2. Reescalar a 9:16 1080x1920 (crop centrado)
    target_ratio = VW / VH
    orig_ratio   = orig_w / orig_h

    if orig_ratio > target_ratio:
        # Más ancho: escalar por altura
        scale = VH / orig_h
        nw    = int(orig_w * scale)
        nh    = VH
    else:
        # Más alto: escalar por ancho
        scale = VW / orig_w
        nw    = VW
        nh    = int(orig_h * scale)

    clip_scaled = clip.resized((nw, nh))

    # Crop centrado
    x_off = (nw - VW) // 2
    y_off = (nh - VH) // 2
    clip_cropped = clip_scaled.cropped(x1=x_off, y1=y_off, x2=x_off+VW, y2=y_off+VH)

    # 3. Intro frames
    print("   Generando intro...")
    intro_frames = make_intro_frames(hook1, hook2, accent)
    intro_clip   = VideoClip(
        frame_function=lambda t, f=intro_frames: f[min(int(t*FPS), len(f)-1)],
        duration=len(intro_frames)/FPS
    )

    # 4. Overlay animado sobre el video
    print("   Aplicando overlay...")
    def frame_with_overlay(t):
        base = clip_cropped.get_frame(min(t, clip_cropped.duration - 0.01))
        base_img = Image.fromarray(base.astype(np.uint8))
        overlay  = Image.fromarray(make_overlay_frame(t, dur, fases_texto, accent, emojis))
        base_img.paste(overlay, (0, 0), overlay)
        return np.array(base_img)

    video_con_overlay = VideoClip(frame_function=frame_with_overlay, duration=dur)

    # 5. CTA frames
    print("   Generando CTA...")
    cta_frames = make_cta_frames(accent)
    cta_clip   = VideoClip(
        frame_function=lambda t, f=cta_frames: f[min(int(t*FPS), len(f)-1)],
        duration=len(cta_frames)/FPS
    )

    # 6. Concatenar intro + video + CTA
    final = concatenate_videoclips([intro_clip, video_con_overlay, cta_clip])

    # 7. Música
    print("   Generando música...")
    music = gen_music(final.duration).with_volume_scaled(0.4)
    final = final.with_audio(music)

    # 8. Exportar
    out_path = f"{OUT}/{nombre}_EDITED.mp4"
    print(f"   Exportando → {out_path}")
    final.write_videofile(out_path, fps=FPS, codec="libx264",
                          audio_codec="aac", preset="medium",
                          logger=None)
    final.close(); clip.close()
    print(f"   ✅ {nombre}_EDITED.mp4")
    return out_path

# ── Configuración de cada video ──────────────────────────────────────────
VIDEOS = [
    {
        "path":   f"{UPLOADS}/349ee520-WhatsApp_Video_20260807_at_09.17.16_1.mp4",
        "nombre": "Video1_Tecnica",
        "hook1":  "¿SABES HACER ESTO?",
        "hook2":  "con resina epóxica 🎨",
        "fases":  [
            "La resina epóxica te permite crear piezas únicas",
            "Solo necesitas los materiales correctos",
            "Mezcla en proporción exacta 1:1",
            "El resultado habla por sí solo",
            "¡Y tú puedes aprenderlo desde casa!",
            "El curso completo en Hotmart 👇",
        ],
        "accent": TEAL,
        "emojis": ["✨","🎨","💎","🔥","⭐"],
    },
    {
        "path":   f"{UPLOADS}/bdecf2ed-WhatsApp_Video_20260807_at_09.20.58_1.mp4",
        "nombre": "Video2_Proceso",
        "hook1":  "ASÍ SE HACE",
        "hook2":  "una pieza de resina 💎",
        "fases":  [
            "El proceso paso a paso es más fácil de lo que crees",
            "Primero: prepara tu molde y pigmentos",
            "Mezcla la resina con cuidado y sin burbujas",
            "Agrega tus colores favoritos 🎨",
            "Espera 24h y desmolda tu creación",
            "¡Aprende todo esto en el curso!",
        ],
        "accent": PINK,
        "emojis": ["💡","🧪","✨","🌈","💎"],
    },
    {
        "path":   f"{UPLOADS}/f78517f1-WhatsApp_Video_20260807_at_09.18.50_2.mp4",
        "nombre": "Video3_Resultado",
        "hook1":  "MIRA ESTE RESULTADO",
        "hook2":  "¿lo puedes creer? 🤩",
        "fases":  [
            "Piezas así se venden de $500 a $5,000 MXN",
            "Y se hacen en menos de 2 horas de trabajo",
            "Clientes las buscan en Instagram y Facebook",
            "Tú puedes tener tu propio negocio",
            "Aprende las técnicas profesionales",
            "Curso disponible ahora en Hotmart 👇",
        ],
        "accent": GOLD,
        "emojis": ["🤑","💰","🛍️","⭐","🏆"],
    },
    {
        "path":   f"{UPLOADS}/d5d0b683-WhatsApp_Video_20260807_at_09.21.53_1.mp4",
        "nombre": "Video4_Inspiracion",
        "hook1":  "¿QUIERES HACER ESTO?",
        "hook2":  "¡YO TE ENSEÑO! 💪",
        "fases":  [
            "Empecé sin saber absolutamente nada",
            "En semanas ya tenía mis primeras ventas",
            "La resina epóxica cambió mi vida",
            "Desde casa, a mi ritmo, sin jefe",
            "Tú también puedes lograrlo",
            "Empieza hoy en go.hotmart.com 👇",
        ],
        "accent": PURPLE,
        "emojis": ["💜","🌟","🏠","💪","🎯"],
    },
]

# ── Ejecutar ─────────────────────────────────────────────────────────────
print("🚀 Editando 4 videos reales de resina...\n")
resultados = []
for cfg in VIDEOS:
    try:
        out = editar_video(
            cfg["path"], cfg["nombre"],
            cfg["hook1"], cfg["hook2"],
            cfg["fases"], cfg["accent"], cfg["emojis"]
        )
        resultados.append(out)
    except Exception as e:
        print(f"   ❌ Error en {cfg['nombre']}: {e}")
        import traceback; traceback.print_exc()

print(f"\n🎉 ¡Listo! {len(resultados)}/4 videos editados en {OUT}/")
