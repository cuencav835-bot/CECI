"""
Videos historia para afiliado de curso de Resina Epóxica
Hotmart: https://go.hotmart.com/G106175870D?ap=8534
Formato: 9:16 vertical, ~90 segundos, estilo storytelling educativo
"""

import os, math, random, struct, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy import VideoClip
from moviepy.audio.AudioClip import AudioArrayClip

random.seed(42)
np.random.seed(42)

FONTS  = "/root/.claude/skills/canvas-design/canvas-fonts"
INPUT  = "/root/.claude/uploads/e53a79e8-4dea-557c-b336-e5482ebcc79c/0175ef1d-lv_0_20260721085442.mp4"
OUT    = "/home/user/CECI/videos_historia"
TMP    = "/tmp/historia_tmp"
SR     = 44100
VW, VH = 1080, 1920
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ── Paletas ──────────────────────────────────────────────────────────────
DARK   = (5,  10,  12)
TEAL   = (78, 205, 196)
GOLD   = (247, 201, 72)
CREAM  = (240, 250, 248)
RED    = (220,  60,  80)
GREEN  = ( 60, 200, 120)
PURPLE = (160,  80, 220)
CORAL  = (255, 120,  80)

def fnt(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def centered(draw, text, y, font, color, W=VW, shadow=True):
    bb  = draw.textbbox((0,0), text, font=font)
    tw  = bb[2]-bb[0]
    x   = (W-tw)//2
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill=(0,0,0,160))
    draw.text((x, y), text, font=font, fill=color)

def add_noise(img, s=4):
    a = np.array(img).astype(np.float32)
    a = np.clip(a + np.random.randn(*a.shape)*s, 0, 255).astype(np.uint8)
    return Image.fromarray(a)

# ── Blobs de resina decorativos ──────────────────────────────────────────
def draw_resin_blob(draw, cx, cy, r, color, alpha=180):
    pts = []
    for i in range(60):
        ang = 2*math.pi*i/60
        ri  = r + random.uniform(-r*.3, r*.3)
        pts.append((cx + ri*math.cos(ang), cy + ri*math.sin(ang)))
    c = color + (alpha,)
    draw.polygon(pts, fill=c)

def make_bg(accent, variant=0):
    img = Image.new("RGBA", (VW, VH), DARK+(255,))
    d   = ImageDraw.Draw(img)
    # blobs decorativos
    positions = [(200,400),(900,800),(500,1400),(150,1600),(950,300)]
    colors    = [accent, TEAL, GOLD, accent, TEAL]
    radii     = [220, 180, 260, 150, 200]
    for (cx,cy),col,r in zip(positions, colors, radii):
        draw_resin_blob(d, cx, cy, r, col, alpha=60+variant*10)
    # vignette
    for i in range(80):
        a = int(140*(i/80)**2)
        d.rectangle([i,i,VW-i,VH-i], outline=(0,0,0,a))
    img = add_noise(img, 3)
    return img

# ── Música ambient ──────────────────────────────────────────────────────
def ambient_music(dur, bpm=82):
    t   = np.linspace(0, dur, int(SR*dur), endpoint=False)
    # acordes motivacionales: C→Am→F→G
    freqs = [[261.63,329.63,392.00],
             [220.00,261.63,329.63],
             [174.61,220.00,261.63],
             [196.00,246.94,293.66]]
    beats   = int(dur*bpm/60)
    beat_t  = 60/bpm
    pad     = np.zeros(len(t))
    for b in range(beats):
        ch = freqs[b % len(freqs)]
        st = b*beat_t; en = min(st+beat_t*3.5, dur)
        m  = (t>=st)&(t<en)
        env= np.zeros(len(t))
        seg= np.where(m)[0]
        if len(seg)==0: continue
        nt = t[m]-st
        env[m] = np.where(nt<0.05, nt/0.05,
                 np.where(nt<beat_t*3, 0.9,
                 np.clip(1-(nt-beat_t*3)/(beat_t*.5+.01),0,1)))
        wave_sum = sum(0.18*np.sin(2*np.pi*f*t) for f in ch)
        wave_sum += sum(0.06*np.sin(2*np.pi*f*2*t) for f in ch)
        pad += wave_sum*env
    # kick
    kick = np.zeros(len(t))
    for b in range(beats):
        bt = b*beat_t
        kl = int(.08*SR); ki = int(bt*SR); ke = min(ki+kl, len(t))
        kn = ke-ki
        if kn<=0: continue
        kenv = np.exp(-30*np.linspace(0,.08,kn))
        kick[ki:ke] += 0.5*kenv*np.sin(2*np.pi*60*np.linspace(0,.08,kn))
    # hihat suave
    hihat = np.zeros(len(t))
    spb   = 60/bpm/2
    nhi   = int(dur/spb)
    for i in range(nhi):
        ht = i*spb; hl=int(.025*SR)
        hs = np.random.randn(hl)*np.exp(-120*np.linspace(0,.025,hl))
        hi = int(ht*SR); he = min(hi+hl, len(t))
        hihat[hi:he] += 0.025*hs[:he-hi]
    mix = pad+kick+hihat
    fade= int(2*SR)
    mix[:fade]  *= np.linspace(0,1,fade)
    mix[-fade:] *= np.linspace(1,0,fade)
    p = np.max(np.abs(mix))
    mix = mix/p*0.65 if p>0 else mix
    return mix.astype(np.float32)

def arr_to_clip(arr, sr=SR):
    stereo = np.stack([arr, arr], axis=1)
    return AudioArrayClip(stereo, fps=sr)

def frames_to_clip(frames, fps=30):
    dur = len(frames)/fps
    return VideoClip(frame_function=lambda t: frames[min(int(t*fps), len(frames)-1)], duration=dur)

# ── Pantalla de texto animada ────────────────────────────────────────────
def make_text_screen(lines, accent, fps=30, dur=4.0, bg_variant=0, show_progress=False, step=0, total=0):
    """
    lines = lista de (texto, tamaño, color, y_offset_rel)
    """
    total_frames = int(fps*dur)
    bg = make_bg(accent, bg_variant)
    frames = []
    f_big   = fnt("BigShoulders-Bold.ttf",   100)
    f_med   = fnt("InstrumentSans-Bold.ttf",   54)
    f_sm    = fnt("InstrumentSans-Regular.ttf",38)
    f_brand = fnt("Italiana-Regular.ttf",       40)

    font_map = {"big": f_big, "med": f_med, "sm": f_sm, "brand": f_brand}

    for fi in range(total_frames):
        prog = fi/total_frames
        img  = bg.copy()
        d    = ImageDraw.Draw(img)

        for text, size_key, color, y_rel in lines:
            font = font_map.get(size_key, f_med)
            y    = int(VH * y_rel)
            alpha_mult = min(1.0, prog*4)
            slide = int((1-min(1.0, prog*3))*40)
            tmp = Image.new("RGBA", (VW, VH), (0,0,0,0))
            td  = ImageDraw.Draw(tmp)
            # normalizar color a 3 elementos y añadir alpha
            c3 = color[:3] if len(color) >= 3 else color
            rgba = c3 + (int(255*alpha_mult),)
            centered(td, text, y-slide, font, rgba, shadow=False)
            img = Image.alpha_composite(img, tmp)

        # barra de progreso del paso
        if show_progress and total > 0:
            bar_w = int(VW * 0.7)
            bar_h = 8
            bx    = (VW-bar_w)//2
            by    = VH - 120
            d2    = ImageDraw.Draw(img)
            d2.rounded_rectangle([bx,by,bx+bar_w,by+bar_h], radius=4, fill=(255,255,255,40))
            filled = int(bar_w * step/total)
            if filled > 0:
                d2.rounded_rectangle([bx,by,bx+filled,by+bar_h], radius=4, fill=accent+(200,))

        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Pantalla con emoji grande + texto ────────────────────────────────────
def make_emoji_screen(emoji, headline, subtext, accent, fps=30, dur=3.5):
    total_f = int(fps*dur)
    bg      = make_bg(accent)
    frames  = []
    f_emoji = fnt("NotoEmoji-Bold.ttf",        180) if os.path.exists(os.path.join(FONTS,"NotoEmoji-Bold.ttf")) else fnt("BigShoulders-Bold.ttf", 180)
    f_hl    = fnt("BigShoulders-Bold.ttf",     90)
    f_sub   = fnt("InstrumentSans-Regular.ttf",40)

    for fi in range(total_f):
        prog = fi/total_f
        img  = bg.copy()
        d    = ImageDraw.Draw(img)
        alpha = int(255*min(1.0, prog*3))
        slide = int((1-min(1.0, prog*2))*60)
        # emoji
        try:
            centered(d, emoji, 600-slide, f_emoji, GOLD+(alpha,), shadow=False)
        except Exception:
            centered(d, "✨", 600-slide, f_hl, GOLD+(alpha,), shadow=False)
        centered(d, headline, 870-slide, f_hl, CREAM+(alpha,), shadow=False)
        centered(d, subtext,  980-slide, f_sub, accent+(alpha,), shadow=False)
        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Pantalla CTA final ───────────────────────────────────────────────────
def make_cta_screen(fps=30, dur=8.0, accent=TEAL):
    total_f = int(fps*dur)
    frames  = []
    f_big   = fnt("BigShoulders-Bold.ttf",   88)
    f_med   = fnt("InstrumentSans-Bold.ttf",  52)
    f_sm    = fnt("InstrumentSans-Regular.ttf",34)
    f_url   = fnt("DMMono-Regular.ttf",        28)
    f_brand = fnt("Italiana-Regular.ttf",       46)

    for fi in range(total_f):
        prog = fi/total_f
        bg   = make_bg(accent, variant=int(prog*3))
        d    = ImageDraw.Draw(bg)
        alpha= int(255*min(1.0, prog*2.5))
        pulse= 1 + 0.04*math.sin(prog*math.pi*6)

        centered(d, "¿Lista para empezar?", 380, f_med, GOLD+(alpha,))
        centered(d, "APRENDE RESINA",        490, f_big, CREAM+(alpha,))
        centered(d, "EPÓXICA DESDE CERO",    590, f_big, accent+(alpha,))

        # caja botón
        bw,bh = int(720*pulse), int(110*pulse)
        bx = (VW-bw)//2; by = 780
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=28,
                            fill=GOLD+(alpha,), outline=CREAM+(100,), width=2)
        centered(d, "👉  INGRESA AL CURSO", by+24, f_med, DARK+(255,))

        centered(d, "go.hotmart.com/G106175870D", by+120, f_url, CREAM+(int(alpha*.7),))

        centered(d, "🎓 Curso completo · Certificado · Soporte", 1000, f_sm, TEAL+(alpha,))
        centered(d, "💰 Gana vendiendo tus creaciones", 1060, f_sm, GOLD+(alpha,))
        centered(d, "🏠 Aprende desde casa, a tu ritmo",  1120, f_sm, CREAM+(int(alpha*.8),))

        centered(d, "VeroResina", 1700, f_brand, TEAL+(int(alpha*.6),))

        frames.append(np.array(bg.convert("RGB")))
    return frames

# ── Video de la fuente con overlay ──────────────────────────────────────
def make_overlay_clip(src_clip, text1, text2, accent, duration):
    src = src_clip.subclipped(0, min(duration, src_clip.duration))
    src = src.resized((VW, VH))

    f_big = fnt("BigShoulders-Bold.ttf",   80)
    f_sm  = fnt("InstrumentSans-Regular.ttf",36)

    def add_overlay(frame):
        img = Image.fromarray(frame.astype(np.uint8), "RGB").convert("RGBA")
        # oscurecer parte inferior
        ov  = Image.new("RGBA", (VW, VH), (0,0,0,0))
        d   = ImageDraw.Draw(ov)
        for i in range(500):
            a = int(180*(i/500)**1.5)
            d.rectangle([0, VH-500+i, VW, VH-499+i], fill=(0,0,0,a))
        img = Image.alpha_composite(img, ov)
        d2  = ImageDraw.Draw(img)
        centered(d2, text1, VH-280, f_big, GOLD+(230,))
        centered(d2, text2, VH-180, f_sm,  CREAM+(200,))
        return np.array(img.convert("RGB"))

    return src.image_transform(add_overlay)

print("📹 Cargando video base...")
base_clip = VideoFileClip(INPUT)

# ── Definición de historias ──────────────────────────────────────────────
HOTMART = "go.hotmart.com/G106175870D"

historias = [
    {
        "archivo": "historia_1_de_cero_a_vender",
        "titulo":  "De Cero a Vender con Resina",
        "accent":  TEAL,
        "screens": [
            # (líneas, dur)
            ([("¿Sabías que...", "med", GOLD, .28),
              ("puedes ganar dinero", "big", CREAM, .38),
              ("desde casa con", "big", CREAM, .47),
              ("RESINA EPÓXICA?", "big", TEAL, .56)], 4.5),
            ([("No necesitas", "med", CREAM, .30),
              ("experiencia previa", "big", GOLD, .40),
              ("ni equipo caro", "med", TEAL, .54)], 3.5),
            ([("Solo necesitas:", "med", GOLD, .28),
              ("✅  Resina epóxica",  "sm",  CREAM, .40),
              ("✅  Pigmentos de color","sm", CREAM, .48),
              ("✅  Moldes simples",   "sm",  CREAM, .56),
              ("✅  ¡Ganas de aprender!","sm", TEAL,  .64)], 5.0),
            ([("Con el curso aprenderás", "med", CREAM, .30),
              ("a hacer joyas, cuadros,", "big", TEAL, .40),
              ("mesas y accesorios", "big", TEAL, .50),
              ("que SE VENDEN", "big", GOLD, .62)], 4.5),
            ([("Alumnas empiezan a vender", "med", GOLD, .30),
              ("desde la primera semana", "big", CREAM, .42),
              ("del curso 💰", "big", TEAL, .55)], 4.0),
        ]
    },
    {
        "archivo": "historia_2_proceso_resina",
        "titulo":  "El Proceso Completo de Resina",
        "accent":  PURPLE,
        "screens": [
            ([("PASO A PASO", "big", GOLD, .30),
              ("Todo lo que necesitas saber", "med", CREAM, .45),
              ("sobre resina epóxica", "med", PURPLE, .56)], 4.0),
            ([("PASO 1", "big", GOLD, .28),
              ("Mide y mezcla", "big", CREAM, .40),
              ("la resina con el catalizador", "sm", TEAL, .54),
              ("en proporción exacta", "sm", CREAM, .63)], 4.5),
            ([("PASO 2", "big", GOLD, .28),
              ("Agrega pigmentos,", "big", CREAM, .40),
              ("brillantinas o flores", "big", PURPLE, .50),
              ("¡A tu gusto! 🎨", "med", GOLD, .62)], 4.5),
            ([("PASO 3", "big", GOLD, .28),
              ("Vierte en el molde", "big", CREAM, .40),
              ("con movimientos suaves", "sm", TEAL, .54),
              ("para crear patrones únicos", "sm", CREAM, .63)], 4.5),
            ([("PASO 4", "big", GOLD, .28),
              ("Espera 24-48 horas", "big", CREAM, .40),
              ("y desmolda tu", "med", TEAL, .54),
              ("¡OBRA DE ARTE! ✨", "big", GOLD, .65)], 4.5),
            ([("PASO 5", "big", GOLD, .28),
              ("Publica en redes,", "big", CREAM, .40),
              ("toma pedidos y", "big", PURPLE, .51),
              ("VENDE desde casa 💸", "big", TEAL, .63)], 4.5),
        ]
    },
    {
        "archivo": "historia_3_transformacion",
        "titulo":  "Transforma tu Vida con Resina",
        "accent":  CORAL,
        "screens": [
            ([("¿Buscas una forma", "med", GOLD, .28),
              ("de generar ingresos", "big", CREAM, .39),
              ("extra desde casa?", "big", CORAL, .50)], 4.0),
            ([("Miles de mujeres", "med", TEAL, .28),
              ("ya lo lograron", "big", CREAM, .39),
              ("con la resina epóxica", "big", GOLD, .50),
              ("🌟", "big", GOLD, .62)], 4.0),
            ([("Con este curso:", "med", GOLD, .28),
              ("📚  Aprendes técnicas profesionales","sm",CREAM,.40),
              ("🎯  Desarrollas tu estilo propio",    "sm",TEAL, .49),
              ("🛍️  Creas productos que se venden",   "sm",CREAM,.58),
              ("💬  Tienes soporte de instructoras",  "sm",GOLD, .67)], 5.0),
            ([("No importa si", "med", CREAM, .28),
              ("eres principiante total", "big", CORAL, .39),
              ("El curso empieza", "med", TEAL, .53),
              ("desde CERO absoluto", "big", GOLD, .63)], 4.5),
            ([("Certificado incluido", "big", GOLD, .30),
              ("para vender con confianza", "med", CREAM, .45),
              ("y posicionarte como", "med", TEAL, .56),
              ("EXPERTA en resina 🏆", "big", GOLD, .66)], 4.5),
        ]
    },
    {
        "archivo": "historia_4_cuanto_ganas",
        "titulo":  "¿Cuánto Puedes Ganar con Resina?",
        "accent":  GREEN,
        "screens": [
            ([("La pregunta que", "med", CREAM, .28),
              ("todas hacen...", "big", GOLD, .39),
              ("¿Cuánto se gana?", "big", GREEN, .52), ("💰", "big", GOLD, .64)], 4.5),
            ([("Una pieza de joyería", "med", TEAL, .28),
              ("puede venderse entre", "big", CREAM, .39),
              ("$50 - $300 MXN", "big", GOLD, .51),
              ("según el diseño", "sm", CREAM, .63)], 4.5),
            ([("Un cuadro de resina", "med", TEAL, .28),
              ("entre", "sm", CREAM, .39),
              ("$500 - $3,000 MXN", "big", GOLD, .49),
              ("¡En un solo cuadro!", "med", GREEN, .63)], 4.5),
            ([("Una mesa de resina", "med", TEAL, .28),
              ("desde", "sm", CREAM, .38),
              ("$3,000 - $15,000 MXN", "big", GOLD, .49),
              ("Sí, una sola mesa 😱", "med", CREAM, .63)], 4.5),
            ([("Con 5-10 ventas/mes", "med", GOLD, .28),
              ("puedes generar un", "big", CREAM, .40),
              ("ingreso extra real", "big", GREEN, .51),
              ("¡sin salir de casa! 🏠", "med", TEAL, .63)], 4.5),
            ([("El curso tiene todo", "med", CREAM, .28),
              ("para que empieces", "big", GOLD, .39),
              ("a vender pronto", "big", GREEN, .51),
              ("👇 Más info abajo", "med", TEAL, .64)], 4.0),
        ]
    },
]

# ── Generar cada historia ────────────────────────────────────────────────
for idx, hist in enumerate(historias):
    print(f"\n🎬 [{idx+1}/{len(historias)}] {hist['titulo']}")
    accent  = hist["accent"]
    screens = hist["screens"]
    clips   = []

    # calcular duración de video overlay
    text_total = sum(d for _,d in screens)
    overlay_dur = min(30.0, base_clip.duration)
    total_video = text_total + overlay_dur + 8.0  # +CTA

    # 1) Pantallas de historia
    for si, (lines_raw, dur) in enumerate(screens):
        print(f"   📝  Pantalla {si+1}/{len(screens)}...")
        lines_fmt = [(t, s, c+(255,) if len(c)==3 else c, y) for t,s,c,y in lines_raw]
        frames = make_text_screen(lines_fmt, accent, dur=dur, bg_variant=si,
                                  show_progress=True, step=si+1, total=len(screens))
        clips.append(frames_to_clip(frames))

    # 2) Video real con overlay
    print(f"   🎥  Video con overlay ({overlay_dur:.0f}s)...")
    ov = make_overlay_clip(base_clip, hist["titulo"], "Curso completo · go.hotmart.com/G106175870D", accent, overlay_dur)
    clips.append(ov)

    # 3) CTA final
    print(f"   📣  CTA final...")
    cta_frames = make_cta_screen(dur=8.0, accent=accent)
    clips.append(frames_to_clip(cta_frames))

    # 4) Concatenar video
    print(f"   🔗  Uniendo clips...")
    final_clip = concatenate_videoclips(clips, method="compose")
    total_dur  = final_clip.duration
    print(f"   ⏱  Duración total: {total_dur:.1f}s")

    # 5) Música
    print(f"   🎵  Generando música ({total_dur:.0f}s)...")
    music_arr = ambient_music(total_dur + 2)[:int(total_dur*SR)]
    music_clip = arr_to_clip(music_arr)

    final_clip = final_clip.with_audio(music_clip)

    # 6) Exportar
    out_path = f"{OUT}/{hist['archivo']}.mp4"
    print(f"   💾  Exportando → {out_path}")
    final_clip.write_videofile(
        out_path, fps=30, codec="libx264",
        audio_codec="aac", bitrate="4000k",
        logger=None, threads=4
    )
    print(f"   ✅  Listo: {hist['titulo']}")

print(f"\n🎉 ¡Todos los videos historia generados en {OUT}/")
print("📌 Hotmart: https://go.hotmart.com/G106175870D?ap=8534")
