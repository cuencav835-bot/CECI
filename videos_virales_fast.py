"""
Editor rápido de videos virales — usa FFmpeg directo para velocidad
Agrega: subtítulos, barra de marca, barra de progreso, emojis, CTA
"""
import os, sys, math, json, subprocess, struct, wave
import numpy as np
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FFPROBE = FFMPEG.replace("ffmpeg", "ffprobe") if os.path.exists(FFMPEG.replace("ffmpeg", "ffprobe")) else FFMPEG
from PIL import Image, ImageDraw, ImageFont

FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
IN    = "/home/user/CECI/videos_semana"
OUT   = "/home/user/CECI/videos_virales"
TMP   = "/tmp/virales_tmp"
SR    = 44100
VW, VH = 1080, 1920

os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

DARK  = (5,  10,  12)
TEAL  = (78, 205, 196)
GOLD  = (247, 201, 72)
CREAM = (240, 250, 248)
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
PINK  = (255, 100, 180)
GREEN = (60,  220, 120)

def fnt(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

def centered(draw, text, y, font, color, W=VW):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x  = (W-tw)//2
    for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        draw.text((x+dx, y+dy), text, font=font, fill=BLACK+(200,))
    draw.text((x, y), text, font=font, fill=color)

def make_overlay_png(script_words, accent, total_dur, emojis="✨💎🎨"):
    """Crea 3 imágenes PNG de overlay para combinar con ffmpeg:
    1. overlay_top.png — barra de marca superior
    2. overlay_subs.png — subtítulos (fondo con palabras)
    3. overlay_cta.png — pantalla CTA final (5s)
    """
    emoji_list = list(emojis)

    # ── TOP BAR (estático)
    bar = Image.new("RGBA", (VW, 80), (0,0,0,200))
    db  = ImageDraw.Draw(bar)
    fb  = fnt("DMMono-Regular.ttf", 26)
    brand = "@VeroResina  •  @RPResina  •  @PXResina"
    bb = db.textbbox((0,0), brand, font=fb)
    tw = bb[2]-bb[0]; tx = (VW-tw)//2
    db.text((tx, 22), brand, font=fb, fill=accent+(230,))
    bar.save(f"{TMP}/overlay_top.png")
    print("  ✅ overlay_top.png")

    # ── SUBTÍTULOS: crea un video de subtítulos con pillow frame a frame
    # Creamos un PNG para cada segundo de subtítulo (más eficiente)
    words_per_sec = len(script_words) / max(total_dur, 1)
    f1 = fnt("BigShoulders-Bold.ttf", 68)
    f2 = fnt("InstrumentSans-Bold.ttf", 54)
    fac= fnt("InstrumentSans-Bold.ttf", 58)

    # Build subtitle images at ~2fps to be efficient
    sub_fps = 2
    sub_frames = []
    for fi in range(int(total_dur * sub_fps)):
        t = fi / sub_fps
        wi = min(int(t * words_per_sec), len(script_words)-1)

        # Group 4 words around active word
        start = max(0, wi-1)
        end   = min(len(script_words), start+5)
        chunk = script_words[start:end]
        active_in_chunk = wi - start

        img = Image.new("RGBA", (VW, 280), (0,0,0,0))
        d   = ImageDraw.Draw(img)

        # gradient bg
        for i in range(280):
            a = int(170*(i/280)**0.8)
            d.rectangle([0,i,VW,i+1], fill=(0,0,0,a))

        # Split into 2 lines of ~2-3 words
        line1 = chunk[:3]; line2 = chunk[3:]

        def draw_line(words, y_base, active_offset):
            x = 40
            for wi2, w in enumerate(words):
                is_active = (active_offset + wi2) == active_in_chunk
                cf = fac if is_active else f2
                col = GOLD if is_active else CREAM+(200,)
                bb2 = d.textbbox((0,0), w+" ", font=cf)
                ww = bb2[2]-bb2[0]
                if is_active:
                    d.rounded_rectangle([x-6, y_base-4, x+ww+2, y_base+68], radius=10, fill=GOLD+(60,))
                for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                    d.text((x+dx, y_base+dy), w, font=cf, fill=BLACK+(180,))
                d.text((x, y_base), w, font=cf, fill=col)
                x += ww
            return x

        total_w1 = sum(d.textbbox((0,0), w+" ", font=(fac if (i)==active_in_chunk else f2))[2] for i,w in enumerate(line1))
        x1 = max(40, (VW-total_w1)//2)

        # Draw line 1
        x = x1
        for wi2, w in enumerate(line1):
            is_active = wi2 == active_in_chunk
            cf = fac if is_active else f2
            col = GOLD if is_active else CREAM+(200,)
            bb2 = d.textbbox((0,0), w+" ", font=cf)
            ww = bb2[2]-bb2[0]
            if is_active:
                d.rounded_rectangle([x-6, 30-4, x+ww+2, 30+68], radius=10, fill=GOLD+(60,))
            for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                d.text((x+dx, 30+dy), w, font=cf, fill=BLACK+(180,))
            d.text((x, 30), w, font=cf, fill=col)
            x += ww

        if line2:
            x = max(40, (VW-total_w1)//2)
            for wi2, w in enumerate(line2):
                is_active = (3 + wi2) == active_in_chunk
                cf = fac if is_active else f2
                col = GOLD if is_active else CREAM+(200,)
                bb2 = d.textbbox((0,0), w+" ", font=cf)
                ww = bb2[2]-bb2[0]
                if is_active:
                    d.rounded_rectangle([x-6, 112-4, x+ww+2, 112+68], radius=10, fill=GOLD+(60,))
                for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                    d.text((x+dx, 112+dy), w, font=cf, fill=BLACK+(180,))
                d.text((x, 112), w, font=cf, fill=col)
                x += ww

        sub_frames.append(np.array(img))

    # Write subtitle frames as raw video via ffmpeg
    sub_raw = f"{TMP}/sub_frames.raw"
    all_frames = np.array(sub_frames, dtype=np.uint8)
    all_frames.tofile(sub_raw)

    sub_video = f"{TMP}/subtitles.mp4"
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{VW}x280", "-pix_fmt", "rgba",
        "-r", str(sub_fps),
        "-i", sub_raw,
        "-vf", f"fps=30,scale={VW}:280",
        "-c:v", "libx264", "-pix_fmt", "yuva420p",
        "-t", str(total_dur),
        sub_video
    ]
    subprocess.run(cmd, capture_output=True)
    print("  ✅ subtitles.mp4")

    # ── CTA PNG (5 seconds animated — generate as video)
    cta_frames = []
    cta_fps = 15
    cta_dur = 5.0
    f_title = fnt("BigShoulders-Bold.ttf", 110)
    f_sub   = fnt("BigShoulders-Bold.ttf", 80)
    f_cta   = fnt("InstrumentSans-Bold.ttf", 52)
    f_url   = fnt("DMMono-Regular.ttf", 30)
    f_bene  = fnt("InstrumentSans-Regular.ttf", 40)

    for fi in range(int(cta_dur * cta_fps)):
        t = fi / cta_fps
        alpha = min(255, int(255 * t / 1.0))
        pulse = 1 + 0.06 * math.sin(t * math.pi * 4)

        img = Image.new("RGBA", (VW, VH), DARK+(255,))
        d   = ImageDraw.Draw(img)

        # blobs
        import random as rnd
        rnd.seed(fi)
        for cx,cy,r,col in [(200,400,300,accent),(880,800,250,GOLD),(540,1500,350,accent)]:
            pts = [(cx+(r+rnd.uniform(-r*.25,r*.25))*math.cos(2*math.pi*i/48),
                    cy+(r+rnd.uniform(-r*.25,r*.25))*math.sin(2*math.pi*i/48)) for i in range(48)]
            d.polygon(pts, fill=col+(40,))

        centered(d, "CURSO DE", 380, f_sub, GOLD+(alpha,))
        centered(d, "RESINA EPÓXICA", 470, f_title, CREAM+(alpha,))

        # pulsing button
        bw = int(820*pulse); bh = int(115*pulse)
        bx = (VW-bw)//2; by = 680
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=30, fill=GOLD+(alpha,))
        centered(d, "👉  INGRESA AL CURSO", by+25, f_cta, DARK+(255,))

        centered(d, "go.hotmart.com/G106175870D", by+140, f_url, CREAM+(int(alpha*.8),))
        centered(d, "✨ Certificado incluido", by+210, f_bene, TEAL+(alpha,))
        centered(d, "💰 Empieza a vender esta semana", by+265, f_bene, GOLD+(alpha,))
        centered(d, "🎓 Aprende desde cero", by+320, f_bene, CREAM+(alpha,))

        centered(d, "VeroResina", VH-90, fnt("Italiana-Regular.ttf", 48), accent+(int(alpha*.7),))

        cta_frames.append(np.array(img.convert("RGB")))

    cta_raw = f"{TMP}/cta_frames.raw"
    np.array(cta_frames, dtype=np.uint8).tofile(cta_raw)

    cta_video = f"{TMP}/cta.mp4"
    cmd2 = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{VW}x{VH}", "-pix_fmt", "rgb24",
        "-r", str(cta_fps),
        "-i", cta_raw,
        "-vf", "fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        cta_video
    ]
    subprocess.run(cmd2, capture_output=True)
    print("  ✅ cta.mp4")

    return f"{TMP}/overlay_top.png", sub_video, cta_video

def make_ambient_music(duration, bpm=90):
    """Generates ambient chord music as WAV"""
    SR = 44100
    t  = np.linspace(0, duration, int(SR*duration))

    chords = [
        [220.00, 261.63, 329.63],  # Am
        [261.63, 329.63, 392.00],  # C
        [174.61, 220.00, 261.63],  # F
        [196.00, 246.94, 293.66],  # G
    ]
    chord_dur = 60/bpm * 4

    music = np.zeros(len(t))
    for i, freq_set in enumerate(chords * (int(duration / chord_dur) + 2)):
        start = int(i * chord_dur * SR)
        if start >= len(t): break
        end = min(start + int(chord_dur * SR), len(t))
        seg = t[start:end] - t[start]
        for f in freq_set:
            music[start:end] += 0.06 * np.sin(2*np.pi*f*seg) * np.exp(-seg*0.3)

    music = np.tanh(music * 2) * 0.4
    fade = 2.0
    fs = int(fade*SR)
    if len(music) > fs:
        music[-fs:] *= np.linspace(1,0,fs)

    path = f"{TMP}/ambient.wav"
    pcm = np.clip(music*32767, -32767, 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(struct.pack(f'<{len(pcm)}h', *pcm))
    return path

def process_video(video_path, script_words, accent, out_name, emojis="✨💎🎨"):
    print(f"\n🎬 Procesando: {out_name}")

    # Get video duration via moviepy
    from moviepy import VideoFileClip as _VFC
    _tmp = _VFC(video_path)
    video_dur = _tmp.duration
    _tmp.close()
    total_dur = video_dur  # CTA added separately

    print(f"  📹 Duración: {video_dur:.1f}s")

    # Make overlays
    top_png, sub_vid, cta_vid = make_overlay_png(script_words, accent, video_dur, emojis)

    # Make music
    music_path = make_ambient_music(video_dur + 6.0)
    print("  ✅ ambient music")

    # Scale source video to 1080x1920 (9:16)
    scaled = f"{TMP}/scaled.mp4"
    subprocess.run([
        FFMPEG, "-y", "-i", video_path,
        "-vf", f"scale={VW}:{VH}:force_original_aspect_ratio=decrease,pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264", "-crf", "22",
        scaled
    ], capture_output=True)
    print("  ✅ scaled source")

    # Composite: source + subtitle overlay + brand bar
    main_out = f"{TMP}/main_composed.mp4"

    # Convert PNG top bar to video
    top_vid = f"{TMP}/top_bar.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1", "-i", top_png,
        "-t", str(int(video_dur)+1), "-r", "1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        top_vid
    ], capture_output=True)

    filter_complex = (
        f"[0:v][2:v]overlay=0:H-280:eof_action=repeat[v1];"
        f"[v1][1:v]overlay=0:0:eof_action=repeat[v2]"
    )

    r_compose = subprocess.run([
        FFMPEG, "-y",
        "-i", scaled,    # [0]
        "-i", top_vid,   # [1]
        "-i", sub_vid,   # [2]
        "-filter_complex", filter_complex,
        "-map", "[v2]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-t", str(video_dur),
        main_out
    ], capture_output=True)
    if r_compose.returncode != 0:
        print("  ⚠️  compose error:", r_compose.stderr.decode()[-400:])
        main_out = scaled
    print("  ✅ main composed")

    # Concatenate main + CTA, adding music
    out_path = f"{OUT}/{out_name}_VIRAL.mp4"

    # Concat list for main + cta
    concat_list = f"{TMP}/concat.txt"
    with open(concat_list, 'w') as f:
        f.write(f"file '{main_out}'\n")
        f.write(f"file '{cta_vid}'\n")

    # Intermediate concat (no audio)
    concat_noaudio = f"{TMP}/concat_noaudio.mp4"
    r1 = subprocess.run([
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-an",
        concat_noaudio
    ], capture_output=True)
    if r1.returncode != 0 or not os.path.exists(concat_noaudio):
        print("  ⚠️  concat error:", r1.stderr.decode()[-300:])
        concat_noaudio = main_out  # fallback

    # Add music
    r2 = subprocess.run([
        FFMPEG, "-y",
        "-i", concat_noaudio,
        "-i", music_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v", "-map", "1:a",
        "-shortest",
        out_path
    ], capture_output=True)
    if r2.returncode != 0 or not os.path.exists(out_path):
        print("  ⚠️  audio mix error:", r2.stderr.decode()[-300:])
        import shutil; shutil.copy(concat_noaudio, out_path)
    else:
        print("  ✅ audio added")

    size = os.path.getsize(out_path) / 1e6
    print(f"  ✅ {out_name}_VIRAL.mp4  ({size:.1f} MB)")
    return out_path


# ── Configuración de los 7 videos ──────────────────────────────────────
VIDEOS = [
    {
        "file": "Lunes_inspiracion.mp4",
        "out":  "Lunes_inspiracion",
        "accent": TEAL,
        "emojis": "✨🎨💎",
        "words": "Hoy lunes de inspiración te cuento cómo la resina epóxica cambió mi vida y la de miles de mujeres emprendedoras en México que hoy tienen su propio negocio desde casa creando piezas únicas hermosas y con mucha demanda en el mercado".split()
    },
    {
        "file": "Martes_tips.mp4",
        "out":  "Martes_tips",
        "accent": PINK,
        "emojis": "⚠️💡🔥",
        "words": "Martes de tips el error más común al empezar con resina es no medir bien las proporciones mezcla siempre en partes iguales por volumen y revuelve despacio durante dos minutos completos sin parar para evitar burbujas y obtener resultados perfectos".split()
    },
    {
        "file": "Miercoles_tecnica.mp4",
        "out":  "Miercoles_tecnica",
        "accent": TEAL,
        "emojis": "🌡️⏱️🧪",
        "words": "Miércoles de técnica hoy vemos cómo controlar la temperatura en tu espacio de trabajo lo ideal son entre veintiún y veinticuatro grados centígrados si hace mucho frío la resina no cura bien y si hace mucho calor se cura demasiado rápido planifica siempre tu sesión".split()
    },
    {
        "file": "Jueves_dinero.mp4",
        "out":  "Jueves_dinero",
        "accent": GREEN,
        "emojis": "💰💸🤑",
        "words": "Jueves de dinero ¿cuánto puedes ganar con resina epóxica una pieza de joyería vale entre cincuenta y trescientos pesos una lámpara puede venderse entre ochocientos y cuatro mil pesos y una mesa de resina llega a valer hasta quince mil pesos empieza con lo pequeño y escala".split()
    },
    {
        "file": "Viernes_ventas.mp4",
        "out":  "Viernes_ventas",
        "accent": GOLD,
        "emojis": "📱🛍️📸",
        "words": "Viernes de ventas el secreto para vender tus piezas de resina en redes sociales es mostrar el proceso no solo el resultado final graba cada paso desde mezclar hasta desmoldar a la gente le encanta ver cómo se hace y eso genera más confianza y más ventas".split()
    },
    {
        "file": "Sabado_tutorial.mp4",
        "out":  "Sabado_tutorial",
        "accent": PINK,
        "emojis": "🎨✨🔮",
        "words": "Sábado de tutorial te enseño cómo hacer joyería de resina desde cero necesitas resina moldes de silicona pigmentos y paciencia mezcla los colores agrega glitter o flores secas vierte en el molde y espera veinticuatro horas desmolda con cuidado y lija los bordes tu primera pieza lista para vender".split()
    },
    {
        "file": "Domingo_comunidad.mp4",
        "out":  "Domingo_comunidad",
        "accent": TEAL,
        "emojis": "🌟💜🤝",
        "words": "Domingo de comunidad gracias a todas las emprendedoras que ya forman parte de nuestra familia resinera más de mil alumnas han transformado su vida con el curso de resina epóxica tú también puedes ser la próxima historia de éxito únete hoy al curso completo con certificado y comunidad de apoyo".split()
    },
]

# ── Skip already-done videos ──────────────────────────────────────────
single = sys.argv[1] if len(sys.argv) > 1 else None

for cfg in VIDEOS:
    out_path = f"{OUT}/{cfg['out']}_VIRAL.mp4"
    if os.path.exists(out_path):
        print(f"⏭️  Saltando {cfg['out']} (ya existe)")
        continue
    if single and cfg['out'] != single:
        continue

    src = f"{IN}/{cfg['file']}"
    if not os.path.exists(src):
        print(f"⚠️  No encontrado: {src}")
        continue

    try:
        process_video(src, cfg['words'], cfg['accent'], cfg['out'], cfg['emojis'])
    except Exception as e:
        print(f"❌ Error en {cfg['out']}: {e}")
        import traceback; traceback.print_exc()

print("\n🎉 ¡Procesamiento completado!")
print(f"📁 Videos en: {OUT}/")
for f in sorted(os.listdir(OUT)):
    if f.endswith('.mp4'):
        size = os.path.getsize(f"{OUT}/{f}") / 1e6
        print(f"  ✅ {f} ({size:.1f} MB)")
