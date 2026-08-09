"""
Editor de videos virales — Resina Epóxica VeroResina
Agrega: subtítulos karaoke animados, emojis, barra progreso, CTA animado
Formatos: 9:16 TikTok/Reels, 1:1 Instagram feed
"""

import os, math, random, struct, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips, CompositeVideoClip
from moviepy.audio.AudioClip import AudioArrayClip

random.seed(42); np.random.seed(42)

FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
IN    = "/home/user/CECI/videos_semana"
OUT   = "/home/user/CECI/videos_virales"
TMP   = "/tmp/virales_tmp"
SR    = 44100
VW, VH = 1080, 1920

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

def fnt(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

def centered(draw, text, y, font, color, W=VW, stroke=0, stroke_color=BLACK):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x  = (W-tw)//2
    if stroke > 0:
        for dx in range(-stroke, stroke+1):
            for dy in range(-stroke, stroke+1):
                if dx!=0 or dy!=0:
                    draw.text((x+dx, y+dy), text, font=font, fill=stroke_color+(220,))
    draw.text((x, y), text, font=font, fill=color)
    return tw

# ── Música ambient ──────────────────────────────────────────────────────
def ambient_music(dur, bpm=90):
    t = np.linspace(0, dur, int(SR*dur), endpoint=False)
    freqs = [[261.63,329.63,392],[220,261.63,329.63],[174.61,220,261.63],[196,246.94,293.66]]
    beats = int(dur*bpm/60)
    beat_t = 60/bpm
    pad = np.zeros(len(t))
    for b in range(beats):
        ch = freqs[b%4]; st=b*beat_t; en=min(st+beat_t*3.5,dur)
        m=(t>=st)&(t<en); seg=np.where(m)[0]
        if not len(seg): continue
        nt=t[m]-st
        env=np.zeros(len(t))
        env[m]=np.where(nt<.05,nt/.05,np.where(nt<beat_t*3,.85,np.clip(1-(nt-beat_t*3)/(beat_t*.5+.01),0,1)))
        pad+=sum(.16*np.sin(2*np.pi*f*t) for f in ch)*env
    kick=np.zeros(len(t))
    for b in range(beats):
        ki=int(b*beat_t*SR); kl=int(.08*SR); ke=min(ki+kl,len(t)); kn=ke-ki
        if kn<=0: continue
        kick[ki:ke]+=.5*np.exp(-30*np.linspace(0,.08,kn))*np.sin(2*np.pi*60*np.linspace(0,.08,kn))
    hihat=np.zeros(len(t))
    for i in range(int(dur/(60/bpm/2))):
        hi=int(i*(60/bpm/2)*SR); hl=int(.025*SR); he=min(hi+hl,len(t))
        hihat[hi:he]+=.02*np.random.randn(he-hi)*np.exp(-120*np.linspace(0,.025,he-hi))
    mix=pad+kick+hihat
    fade=int(2*SR); mix[:fade]*=np.linspace(0,1,fade); mix[-fade:]*=np.linspace(1,0,fade)
    p=np.max(np.abs(mix)); return (mix/p*.6 if p>0 else mix).astype(np.float32)

def arr_to_clip(arr):
    return AudioArrayClip(np.stack([arr,arr],axis=1), fps=SR)

def frames_to_clip(frames, fps=30):
    dur=len(frames)/fps
    return VideoClip(frame_function=lambda t: frames[min(int(t*fps),len(frames)-1)], duration=dur)

# ── Subtítulos karaoke estilo TikTok ────────────────────────────────────
def make_subtitle_frame(words, active_idx, W=VW, max_chars=30):
    """Renderiza subtítulos con palabra activa resaltada"""
    img = Image.new("RGBA", (W, 200), (0,0,0,0))
    d   = ImageDraw.Draw(img)
    f_word = fnt("InstrumentSans-Bold.ttf", 62)
    f_act  = fnt("BigShoulders-Bold.ttf",   72)

    # Agrupa palabras en línea de max_chars
    line, lines = [], []
    for w in words:
        if sum(len(x)+1 for x in line)+len(w) <= max_chars:
            line.append(w)
        else:
            if line: lines.append(line)
            line = [w]
    if line: lines.append(line)

    # Encuentra línea activa
    count = 0
    active_line = 0
    for li, ln in enumerate(lines):
        if count + len(ln) > active_idx:
            active_line = li
            break
        count += len(ln)

    if active_line >= len(lines):
        return img

    ln = lines[active_line]
    local_idx = active_idx - count

    # Calcula ancho total de la línea
    total_w = sum(d.textbbox((0,0), w, font=f_word)[2] + 12 for w in ln)
    x = (W - total_w) // 2
    y = 60

    for wi, word in enumerate(ln):
        is_active = (wi == local_idx)
        font = f_act if is_active else f_word
        color = GOLD + (255,) if is_active else WHITE + (230,)
        stroke_c = (0,0,0)
        bb = d.textbbox((0,0), word, font=font)
        ww = bb[2]-bb[0]

        if is_active:
            # Caja resaltada detrás de palabra activa
            pad = 8
            d.rounded_rectangle([x-pad, y-pad, x+ww+pad, y+bb[3]-bb[1]+pad],
                               radius=10, fill=(247,201,72,60))

        # Stroke negro
        for dx in [-3,-2,-1,0,1,2,3]:
            for dy in [-3,-2,-1,0,1,2,3]:
                if dx or dy:
                    d.text((x+dx, y+dy), word, font=font, fill=(0,0,0,200))
        d.text((x, y), word, font=font, fill=color)
        x += ww + 12

    return img

# ── Barra de progreso ────────────────────────────────────────────────────
def draw_progress_bar(draw, progress, y=VH-35, W=VW, color=TEAL):
    bar_w = int(W * 0.92)
    bx    = (W - bar_w) // 2
    # fondo
    draw.rounded_rectangle([bx, y, bx+bar_w, y+8], radius=4, fill=(255,255,255,40))
    # progreso
    filled = max(0, int(bar_w * progress))
    if filled > 4:
        draw.rounded_rectangle([bx, y, bx+filled, y+8], radius=4, fill=color+(220,))
    # bolita
    cx = bx + filled
    draw.ellipse([cx-8, y-4, cx+8, y+12], fill=GOLD+(230,))

# ── Emoji burst animado ──────────────────────────────────────────────────
EMOJI_FRAMES = {}

def get_emoji_img(emoji_char, size=80):
    key = f"{emoji_char}_{size}"
    if key not in EMOJI_FRAMES:
        try:
            f = fnt("NotoEmoji-Bold.ttf", size)
        except:
            f = fnt("BigShoulders-Bold.ttf", size)
        img = Image.new("RGBA", (size+20, size+20), (0,0,0,0))
        d   = ImageDraw.Draw(img)
        d.text((10,10), emoji_char, font=f, fill=(255,255,255,255))
        EMOJI_FRAMES[key] = img
    return EMOJI_FRAMES[key]

# ── Banner de marca ──────────────────────────────────────────────────────
def draw_brand_bar(draw, accent):
    # barra superior
    draw.rectangle([0,0,VW,90], fill=DARK+(200,))
    f_brand = fnt("Italiana-Regular.ttf", 44)
    f_tag   = fnt("DMMono-Regular.ttf",   24)
    centered(draw, "VeroResina", 18, f_brand, accent+(220,))
    centered(draw, "@VeroResina  •  @RPResina  •  @PXResina", 62, f_tag, CREAM+(150,))

# ── CTA animado final ────────────────────────────────────────────────────
def make_cta_frames(accent, fps=30, dur=5.0):
    total = int(fps*dur)
    frames = []
    f1 = fnt("BigShoulders-Bold.ttf",   96)
    f2 = fnt("InstrumentSans-Bold.ttf", 52)
    f3 = fnt("InstrumentSans-Regular.ttf", 36)
    fu = fnt("DMMono-Regular.ttf",      28)
    fb = fnt("Italiana-Regular.ttf",    46)

    for fi in range(total):
        prog  = fi/total
        alpha = int(255*min(1.0, prog*3))
        pulse = 1 + 0.05*math.sin(prog*math.pi*8)

        img = Image.new("RGBA", (VW,VH), DARK+(255,))
        d   = ImageDraw.Draw(img)

        # fondo con blobs
        for cx,cy,r,col in [(200,500,280,accent),(880,900,240,GOLD),(540,1500,300,accent)]:
            pts = [(cx+(r+random.uniform(-r*.3,r*.3))*math.cos(2*math.pi*i/60),
                    cy+(r+random.uniform(-r*.3,r*.3))*math.sin(2*math.pi*i/60)) for i in range(60)]
            d.polygon(pts, fill=col+(50,))

        centered(d, "¿Lista para", 420, f2, CREAM+(alpha,), stroke=2)
        centered(d, "empezar?", 490, f2, CREAM+(alpha,), stroke=2)
        centered(d, "APRENDE",  610, f1, CREAM+(alpha,), stroke=3)
        centered(d, "RESINA",   710, f1, accent+(alpha,), stroke=3)
        centered(d, "EPÓXICA",  810, f1, GOLD+(alpha,), stroke=3)

        # botón pulsante
        bw = int(780*pulse); bh = int(110*pulse)
        bx = (VW-bw)//2; by = 960
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=30, fill=GOLD+(alpha,))
        centered(d, "👉  INGRESA AL CURSO", by+22, f2, DARK+(255,))

        centered(d, "go.hotmart.com/G106175870D", by+125, fu, CREAM+(int(alpha*.7),))
        centered(d, "🎓 Certificado incluido", by+185, f3, TEAL+(alpha,))
        centered(d, "💰 Empieza a vender esta semana", by+235, f3, GOLD+(alpha,))
        centered(d, "VeroResina", VH-70, fb, accent+(int(alpha*.6),))

        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Procesar video con subtítulos karaoke ───────────────────────────────
def make_viral_video(video_path, script_words, accent, archivo, emojis="✨🎨💎"):
    print(f"   📖  Procesando subtítulos ({len(script_words)} palabras)...")

    src = VideoFileClip(video_path)
    total_dur = src.duration + 5.0  # +CTA

    words_per_sec = len(script_words) / src.duration
    fps = 30

    emoji_list = list(emojis)

    def make_frame(t):
        # Frame del video fuente
        vt = min(t, src.duration - 1/fps)
        frame = src.get_frame(vt)
        img   = Image.fromarray(frame.astype(np.uint8), "RGB").convert("RGBA")

        d = ImageDraw.Draw(img)
        progress = t / total_dur

        # ── Gradiente inferior para subtítulos
        ov = Image.new("RGBA", (VW,VH), (0,0,0,0))
        dov = ImageDraw.Draw(ov)
        for i in range(400):
            a = int(190*(i/400)**1.8)
            dov.rectangle([0, VH-400+i, VW, VH-399+i], fill=(0,0,0,a))
        img = Image.alpha_composite(img, ov)
        d2 = ImageDraw.Draw(img)

        # ── Barra de marca superior
        draw_brand_bar(d2, accent)

        # ── Barra de progreso
        draw_progress_bar(d2, progress)

        # ── Subtítulos karaoke
        word_idx = int(t * words_per_sec)
        word_idx = min(word_idx, len(script_words)-1)
        sub_img  = make_subtitle_frame(script_words, word_idx)
        img.paste(sub_img, (0, VH-260), sub_img)

        # ── Emoji animado flotante cada 8 segundos
        cycle = t % 8
        if cycle < 2.0:
            em  = emoji_list[int(t/8) % len(emoji_list)]
            ey  = int(VH*0.65 - cycle*60)
            ea  = int(255*(1-cycle/2))
            es  = int(80 + cycle*20)
            try:
                ei = get_emoji_img(em, es)
                ex = VW//2 - ei.width//2 + int(30*math.sin(t*3))
                ei_fade = ei.copy()
                alpha_ch = ei_fade.split()[3]
                alpha_ch = alpha_ch.point(lambda p: int(p*ea/255))
                ei_fade.putalpha(alpha_ch)
                img.paste(ei_fade, (ex, ey), ei_fade)
            except: pass

        return np.array(img.convert("RGB"))

    # Clip del video con overlay
    video_clip = VideoClip(frame_function=make_frame, duration=src.duration)

    # CTA final
    cta_frames = make_cta_frames(accent)
    cta_clip   = frames_to_clip(cta_frames, fps=fps)

    # Unir
    final = concatenate_videoclips([video_clip, cta_clip], method="compose")

    # Música
    music = ambient_music(final.duration)[:int(final.duration*SR)]
    audio = arr_to_clip(music)
    final = final.with_audio(audio)

    out_path = f"{OUT}/{archivo}_VIRAL.mp4"
    print(f"   💾  Exportando → {out_path}")
    final.write_videofile(out_path, fps=fps, codec="libx264",
                         audio_codec="aac", bitrate="5000k",
                         logger=None, threads=4)
    src.close()
    print(f"   ✅  ¡Listo!")
    return out_path

# ── Scripts de cada video ────────────────────────────────────────────────
VIDEOS = [
    {
        "archivo": "Lunes_inspiracion",
        "accent":  TEAL,
        "emojis":  "✨🎨💎",
        "words":   "¿Sabías que puedes convertir tu pasión en un negocio rentable desde casa? La resina epóxica está cambiando la vida de miles de mujeres. Hoy te cuento cómo empezar desde cero. Aprende crea y vende. El curso completo está en el link de mi bio. ¡Te espero adentro!".split()
    },
    {
        "archivo": "Martes_tips",
        "accent":  PINK,
        "emojis":  "⚠️💡🔥",
        "words":   "Tres errores que arruinan tu resina y cómo evitarlos. Primero no medir bien la proporción. Segundo mezclar demasiado rápido y crear burbujas. Tercero no proteger la superficie. Evita estos errores y tus piezas quedarán perfectas. Aprende todas las técnicas en el curso del link.".split()
    },
    {
        "archivo": "Miercoles_tecnica",
        "accent":  TEAL,
        "emojis":  "🌡️⏱️🧪",
        "words":   "El secreto de la resina perfecta está en la temperatura y el tiempo. La resina debe estar a 22 o 25 grados. Mezcla durante tres minutos raspando los lados. Luego espera el tiempo de curado correcto. Con estas claves cada pieza será un éxito. Aprende más en el curso del enlace.".split()
    },
    {
        "archivo": "Jueves_dinero",
        "accent":  GREEN,
        "emojis":  "💰💸🤑",
        "words":   "¿Cuánto puedes ganar con resina epóxica? Una joya desde 50 hasta 300 pesos. Un cuadro desde 500 hasta tres mil pesos. Una mesa de resina desde tres mil hasta quince mil pesos. Con cinco ventas al mes generas ingresos reales desde casa. El curso te enseña todo. Link en bio.".split()
    },
    {
        "archivo": "Viernes_ventas",
        "accent":  GOLD,
        "emojis":  "📱🛍️📸",
        "words":   "¿Quieres vender tus piezas de resina pero no sabes cómo? Paso uno fotografía con buena luz natural. Paso dos publica con descripciones que conecten. Paso tres usa el precio correcto que refleje tu tiempo y talento. El curso te enseña también a vender desde cero. Entra por el link.".split()
    },
    {
        "archivo": "Sabado_tutorial",
        "accent":  PINK,
        "emojis":  "🎨✨🔮",
        "words":   "Tutorial completo de resina. Mezcla en proporción dos a uno. Agrega pigmento de tu color favorito. Vierte en el molde con movimientos circulares para crear patrones únicos. Espera veinticuatro horas y desmolda con cuidado. Tu obra de arte está lista para venderse. Aprende en el curso del link.".split()
    },
    {
        "archivo": "Domingo_comunidad",
        "accent":  TEAL,
        "emojis":  "🌟💜🤝",
        "words":   "¡Bienvenida a nuestra comunidad resinera! Aquí compartimos técnicas inspiración y logros. Tú también puedes crear piezas únicas y construir tu negocio desde casa. Somos miles de mujeres que ya lo lograron. ¿Te unes? Ingresa por el link de mi bio y empieza hoy. ¡Te esperamos!".split()
    },
]

# ── Ejecutar ────────────────────────────────────────────────────────────
print("🚀 Iniciando edición viral de videos...\n")
for i, v in enumerate(VIDEOS):
    src_path = f"{IN}/{v['archivo']}.mp4"
    if not os.path.exists(src_path):
        print(f"⚠️  No encontrado: {src_path}")
        continue
    print(f"🎬 [{i+1}/7] {v['archivo']}")
    try:
        make_viral_video(src_path, v['words'], v['accent'], v['archivo'], v['emojis'])
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n🎉 ¡Todos los videos virales completados!")
print(f"📁 Carpeta: {OUT}/")
