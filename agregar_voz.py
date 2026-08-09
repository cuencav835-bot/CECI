"""
Agrega voz en off + subtítulos sincronizados a los videos editados.
Genera los 4 videos con todo incluido: música + voz + subtítulos karaoke.
"""

import os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip

FONTS   = "/root/.claude/skills/canvas-design/canvas-fonts"
UPLOADS = "/root/.claude/uploads/e53a79e8-4dea-557c-b336-e5482ebcc79c"
OUT     = "/home/user/CECI/videos_finales"
TMP     = "/tmp/voz_tmp"
SR      = 44100
VW, VH  = 1080, 1920
FPS     = 30

os.makedirs(OUT,  exist_ok=True)
os.makedirs(TMP,  exist_ok=True)

DARK   = (5,  10,  12)
TEAL   = (78, 205, 196)
GOLD   = (247, 201, 72)
CREAM  = (240, 250, 248)
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
PINK   = (255, 100, 180)
GREEN  = (60,  220, 120)
PURPLE = (160, 80, 220)

def fnt(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

def centered_text(draw, text, y, font, color, W=VW, stroke=3):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x  = (W-tw)//2
    for dx in range(-stroke, stroke+1):
        for dy in range(-stroke, stroke+1):
            if dx!=0 or dy!=0:
                draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,220))
    draw.text((x, y), text, font=font, fill=color)

def gen_music(duration, bpm=80):
    t   = np.linspace(0, duration, int(SR*duration), endpoint=False)
    beat = 60/bpm
    chord_freqs = [
        [220.00, 261.63, 329.63],
        [174.61, 220.00, 261.63],
        [261.63, 329.63, 392.00],
        [196.00, 246.94, 293.66],
    ]
    audio = np.zeros(len(t))
    bars  = int(duration/(beat*4))+1
    for bar in range(bars):
        chord = chord_freqs[bar%4]
        t0, t1 = bar*beat*4, (bar+1)*beat*4
        mask = (t>=t0)&(t<min(t1,duration))
        seg  = t[mask]-t0
        wav  = sum(0.2*np.sin(2*np.pi*f*seg) + 0.06*np.sin(4*np.pi*f*seg) for f in chord)
        fade = int(0.1*SR)
        env  = np.ones(len(seg))
        env[:fade] = np.linspace(0,1,fade)
        env[-fade:] = np.linspace(1,0,fade)
        audio[mask] += wav*env
    # kick
    for i in range(int(duration/beat)+1):
        idx = int(i*beat*SR)
        kl  = int(0.08*SR)
        if idx+kl < len(audio):
            k = np.linspace(1,0,kl)**2 * np.sin(2*np.pi*60*np.linspace(0,0.08,kl))*0.25
            audio[idx:idx+kl] += k
    audio = audio/(np.max(np.abs(audio))+1e-9)*0.35
    stereo = np.stack([audio,audio],axis=1).astype(np.float32)
    return AudioArrayClip(stereo, fps=SR)

def gen_tts(text, out_wav, speed=140, pitch=55):
    """Genera voz con espeak-ng en español latinoamericano."""
    subprocess.run([
        "espeak-ng", "-v", "es-419",
        "-s", str(speed), "-p", str(pitch), "-a", "200",
        text, "-w", out_wav
    ], check=True, capture_output=True)
    return out_wav

def make_subtitle_overlay(words, t, total_dur, accent, emojis):
    """Frame de overlay con subtítulos karaoke + marca + progreso + emojis."""
    img = Image.new("RGBA", (VW, VH), (0,0,0,0))
    d   = ImageDraw.Draw(img)
    progress = t / total_dur

    # Barra de progreso
    bw = int(VW * progress)
    d.rectangle([0, VH-28, VW, VH], fill=(0,0,0,120))
    d.rectangle([0, VH-28, bw, VH], fill=TEAL+(200,))
    if bw > 12:
        d.ellipse([bw-12, VH-34, bw+12, VH], fill=GOLD+(255,))

    # Barra de marca top
    d.rectangle([0, 0, VW, 58], fill=(0,0,0,170))
    centered_text(d, "@VeroResina  •  @RPResina  •  @PXResina", 13,
                  fnt("InstrumentSans-Bold.ttf", 30), TEAL)

    # Subtítulos karaoke: 3-4 palabras por grupo, sincronizadas con tiempo
    n_groups = max(1, len(words)//3)
    group_dur = total_dur / n_groups
    group_idx = min(int(t / group_dur), n_groups-1)
    group_progress = (t - group_idx * group_dur) / group_dur

    start = group_idx * 3
    group_words = words[start:start+3]
    if not group_words:
        group_words = words[-3:]

    f_sub = fnt("BigShoulders-Bold.ttf", 62)
    f_act = fnt("BigShoulders-Bold.ttf", 70)

    line = " ".join(group_words)
    # Fondo caja subtítulo
    bb    = d.textbbox((0,0), line, font=f_sub)
    tw    = bb[2]-bb[0]
    pad   = 24
    bx    = (VW-tw)//2 - pad
    sub_y = VH - 200
    d.rounded_rectangle([bx, sub_y-10, bx+tw+pad*2, sub_y+80],
                        radius=18, fill=(0,0,0,int(200)))

    # Renderizar palabra activa resaltada
    x = bx + pad
    active_word_idx = min(int(group_progress * len(group_words)), len(group_words)-1)
    for wi, word in enumerate(group_words):
        wb = d.textbbox((0,0), word+" ", font=f_sub)
        ww = wb[2]-wb[0]
        if wi == active_word_idx:
            # Caja dorada detrás de la palabra activa
            d.rounded_rectangle([x-6, sub_y-8, x+ww+2, sub_y+72],
                                 radius=12, fill=GOLD+(200,))
            d.text((x, sub_y-4), word, font=f_act, fill=DARK)
        else:
            d.text((x, sub_y), word, font=f_sub, fill=WHITE)
        x += ww

    # Emoji flotante
    if emojis:
        ec = int(t/4) % len(emojis)
        et = t % 4
        if et < 2:
            ea = int(255 * min(1, et * 2))
            ey = int(VH*0.38 - et*55)
            ex = int(VW*(0.12 + (ec%3)*0.37))
            try:
                d.text((ex, ey), emojis[ec], font=fnt("NotoEmoji-Bold.ttf", 85),
                       fill=WHITE+(ea,))
            except:
                pass

    return np.array(img)

def make_intro(hook1, hook2, accent, dur=3.0):
    n = int(dur*FPS)
    fh1 = fnt("BigShoulders-Bold.ttf", 90)
    fh2 = fnt("BigShoulders-Bold.ttf", 68)
    fb  = fnt("InstrumentSans-Bold.ttf", 32)
    frames = []
    for i in range(n):
        p = i/(n-1)
        img = Image.new("RGBA",(VW,VH),DARK+(255,))
        d   = ImageDraw.Draw(img)
        # Fondo animado
        import random; random.seed(i)
        for _ in range(60):
            rx,ry = random.randint(0,VW), random.randint(0,VH)
            r = random.randint(3,12)
            al = int(30+30*math.sin(p*math.pi*2+random.random()*5))
            d.ellipse([rx-r,ry-r,rx+r,ry+r], fill=accent+(al,))
        # Barras laterales
        d.rectangle([0,0,8,int(VH*p)], fill=accent+(200,))
        d.rectangle([VW-8,VH-int(VH*p),VW,VH], fill=GOLD+(200,))
        # Texto con slide-up
        sl = int((1-min(1,p*2))*70)
        d.rounded_rectangle([60,VH//2-170,VW-60,VH//2+100], radius=28,
                             fill=(0,0,0,int(180*min(1,p*3))))
        centered_text(d, hook1, VH//2-145+sl, fh1, accent)
        centered_text(d, hook2, VH//2-38+sl,  fh2, CREAM)
        # Emoji pulsante
        pulse = 1+0.25*math.sin(p*math.pi*5)
        try:
            d.text((VW//2-40, VH//2+80), "👇",
                   font=fnt("NotoEmoji-Bold.ttf",int(75*pulse)), fill=WHITE+(255,))
        except:
            pass
        centered_text(d, "@VeroResina • @RPResina • @PXResina", VH-55, fb, TEAL)
        frames.append(np.array(img.convert("RGB")))
    return frames

def make_cta(accent, dur=5.0):
    n   = int(dur*FPS)
    f1  = fnt("BigShoulders-Bold.ttf", 82)
    f2  = fnt("InstrumentSans-Bold.ttf", 48)
    f3  = fnt("InstrumentSans-Regular.ttf", 38)
    fu  = fnt("DMMono-Regular.ttf", 30)
    fbr = fnt("Italiana-Regular.ttf", 46)
    frames = []
    for i in range(n):
        p   = i/(n-1)
        img = Image.new("RGBA",(VW,VH),DARK+(255,))
        d   = ImageDraw.Draw(img)
        for ci in range(5):
            ang = p*math.pi*2+ci*1.2
            cx  = VW//2+int(math.cos(ang)*VW*0.38)
            cy  = VH//2+int(math.sin(ang)*VH*0.22)
            r   = int(VW*0.18+math.sin(p*math.pi*3+ci)*25)
            d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=accent+(28,))
        d.rectangle([0,0,VW,8],       fill=accent+(180,))
        d.rectangle([0,VH-8,VW,VH],   fill=GOLD+(180,))
        centered_text(d,"¿LISTA PARA EMPEZAR?",  VH//2-340, f1, GOLD)
        centered_text(d,"Curso de Resina Epóxica",VH//2-240, f2, CREAM)
        sep = (VW-400)//2
        d.rectangle([sep,VH//2-185,sep+400,VH//2-182], fill=TEAL+(200,))
        for bi,ben in enumerate(["✅ Desde cero, a tu ritmo",
                                  "✅ Con certificado incluido",
                                  "✅ Comunidad de apoyo"]):
            centered_text(d, ben, VH//2-160+bi*70, f3, CREAM)
        pulse = 1+0.07*math.sin(p*math.pi*8)
        bw,bh = int(820*pulse),int(112*pulse)
        bx    = (VW-bw)//2; by = VH//2+80
        d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=32, fill=GOLD+(245,))
        centered_text(d,"👉  QUIERO EL CURSO", by+24, f2, DARK, stroke=0)
        centered_text(d,"go.hotmart.com/G106175870D", by+132, fu, TEAL)
        centered_text(d,"VeroResina", VH-90, fbr, GOLD)
        frames.append(np.array(img.convert("RGB")))
    return frames

# ── Configuración de videos ──────────────────────────────────────────────
CONFIGS = [
    {
        "input":  f"{UPLOADS}/349ee520-WhatsApp_Video_20260807_at_09.17.16_1.mp4",
        "nombre": "Video1_Tecnica",
        "hook1":  "¿SABES HACER ESTO?",
        "hook2":  "con resina epóxica 🎨",
        "texto":  "¿Sabes hacer esto con resina epóxica? La resina te permite crear piezas únicas que se venden muy bien. Solo necesitas los materiales correctos y la técnica adecuada. Mezcla en proporción exacta, agrega tus pigmentos y el resultado habla por sí solo. Y tú puedes aprenderlo desde casa. Entra al curso completo en Hotmart y empieza hoy.",
        "words":  "¿Sabes hacer esto con resina epóxica? La resina te permite crear piezas únicas que se venden muy bien. Solo necesitas los materiales correctos y la técnica adecuada. Mezcla en proporción exacta agrega tus pigmentos y el resultado habla por sí solo. ¡Y tú puedes aprenderlo desde casa!".split(),
        "accent": TEAL,
        "emojis": ["✨","🎨","💎","🔥","⭐"],
    },
    {
        "input":  f"{UPLOADS}/bdecf2ed-WhatsApp_Video_20260807_at_09.20.58_1.mp4",
        "nombre": "Video2_Proceso",
        "hook1":  "ASÍ SE HACE",
        "hook2":  "una pieza de resina 💎",
        "texto":  "¿Quieres saber cómo se hace una pieza de resina epóxica? El proceso paso a paso es más fácil de lo que crees. Primero prepara tu molde y tus pigmentos favoritos. Mezcla la resina con cuidado sin burbujas. Agrega tus colores y crea diseños únicos. Espera veinticuatro horas desmolda y listo. Tu primera creación. Aprende todo esto en el curso de Vero Resina.",
        "words":  "¿Quieres saber cómo se hace una pieza de resina? El proceso es más fácil de lo que crees. Prepara tu molde y pigmentos. Mezcla la resina sin burbujas. Agrega colores crea diseños únicos. Desmolda y listo ¡tu primera creación!".split(),
        "accent": PINK,
        "emojis": ["💡","🧪","✨","🌈","💎"],
    },
    {
        "input":  f"{UPLOADS}/f78517f1-WhatsApp_Video_20260807_at_09.18.50_2.mp4",
        "nombre": "Video3_Resultado",
        "hook1":  "MIRA ESTE RESULTADO",
        "hook2":  "¿lo puedes creer? 🤩",
        "texto":  "¡Mira este resultado! ¿Puedes creerlo? Piezas así se venden de quinientos a cinco mil pesos mexicanos, y se hacen en menos de dos horas de trabajo. Las clientas las buscan en Instagram y en Facebook todos los días. Tú puedes tener tu propio negocio desde casa. Aprende las técnicas profesionales en el curso de resina epóxica. Disponible ahora en Hotmart.",
        "words":  "¡Mira este resultado! Piezas así se venden de $500 a $5,000 pesos. Se hacen en menos de 2 horas. Las clientas las buscan en redes todos los días. Tú puedes tener tu negocio desde casa. Disponible ahora en Hotmart.".split(),
        "accent": GOLD,
        "emojis": ["🤑","💰","🛍️","⭐","🏆"],
    },
    {
        "input":  f"{UPLOADS}/d5d0b683-WhatsApp_Video_20260807_at_09.21.53_1.mp4",
        "nombre": "Video4_Inspiracion",
        "hook1":  "¿QUIERES HACER ESTO?",
        "hook2":  "¡YO TE ENSEÑO! 💪",
        "texto":  "¿Quieres hacer esto? ¡Yo te enseño! Yo empecé sin saber absolutamente nada sobre resina epóxica. En pocas semanas ya tenía mis primeras ventas. La resina cambió mi vida: trabajo desde casa, a mi ritmo, sin jefe. Tú también puedes lograrlo. No necesitas experiencia previa ni mucho dinero para empezar. Entra hoy al curso y transforma tu vida.",
        "words":  "¿Quieres hacer esto? ¡Yo te enseño! Empecé sin saber nada. En pocas semanas tenía mis primeras ventas. La resina cambió mi vida trabajo desde casa a mi ritmo sin jefe. ¡Tú también puedes lograrlo!".split(),
        "accent": PURPLE,
        "emojis": ["💜","🌟","🏠","💪","🎯"],
    },
]

def procesar(cfg):
    nombre = cfg["nombre"]
    print(f"\n🎬 {nombre}")

    # 1. Cargar video original
    clip = VideoFileClip(cfg["input"])
    ow, oh = clip.size
    dur    = clip.duration

    # 2. Escalar a 9:16
    if ow/oh > VW/VH:
        scale = VH/oh; nw,nh = int(ow*scale),VH
    else:
        scale = VW/ow; nw,nh = VW,int(oh*scale)
    clip = clip.resized((nw,nh))
    xo,yo = (nw-VW)//2,(nh-VH)//2
    clip  = clip.cropped(x1=xo,y1=yo,x2=xo+VW,y2=yo+VH)

    # 3. TTS voz en off
    print("   🎙️ Generando voz...")
    voz_wav = f"{TMP}/{nombre}_voz.wav"
    gen_tts(cfg["texto"], voz_wav, speed=135, pitch=58)
    voz_clip = AudioFileClip(voz_wav)

    # Ajustar velocidad del video al largo de la voz si necesario
    voz_dur = voz_clip.duration
    total_video_dur = 3.0 + max(dur, voz_dur) + 5.0  # intro + video/voz + cta
    video_dur = max(dur, voz_dur)

    # Si la voz es más larga que el video, loop el video
    if voz_dur > dur:
        loops = math.ceil(voz_dur / dur)
        from moviepy import concatenate_videoclips
        clip = concatenate_videoclips([clip]*loops).subclipped(0, voz_dur)
    else:
        clip = clip.subclipped(0, dur)

    # 4. Overlay con subtítulos
    print("   💬 Aplicando subtítulos...")
    words = cfg["words"]
    accent = cfg["accent"]
    emojis = cfg["emojis"]

    def overlay_frame(t):
        base = clip.get_frame(min(t, clip.duration-0.01))
        base_img = Image.fromarray(base.astype(np.uint8))
        ov = Image.fromarray(make_subtitle_overlay(words, t, clip.duration, accent, emojis))
        base_img.paste(ov, (0,0), ov)
        return np.array(base_img)

    video_ov = VideoClip(frame_function=overlay_frame, duration=clip.duration)

    # 5. Intro y CTA
    print("   🎬 Intro y CTA...")
    intro_frames = make_intro(cfg["hook1"], cfg["hook2"], accent)
    intro_clip   = VideoClip(frame_function=lambda t,f=intro_frames: f[min(int(t*FPS),len(f)-1)], duration=3.0)

    cta_frames = make_cta(accent)
    cta_clip   = VideoClip(frame_function=lambda t,f=cta_frames: f[min(int(t*FPS),len(f)-1)], duration=5.0)

    # 6. Concatenar
    final_video = concatenate_videoclips([intro_clip, video_ov, cta_clip])

    # 7. Audio: música + voz sincronizada (empieza en segundo 3 = después del intro)
    print("   🎵 Mezclando audio...")
    music = gen_music(final_video.duration).with_volume_scaled(0.28)

    # Voz empieza en t=3 (después de intro)
    from moviepy.audio.AudioClip import AudioArrayClip
    # Crear silencio de 3s antes de la voz
    silence_samples = int(3.0 * SR)
    silence = np.zeros((silence_samples, 2), dtype=np.float32)
    silence_clip = AudioArrayClip(silence, fps=SR)

    # Leer voz como array
    voz_arr = voz_clip.to_soundarray(fps=SR)
    if voz_arr.ndim == 1:
        voz_arr = np.stack([voz_arr, voz_arr], axis=1)
    voz_arr = voz_arr.astype(np.float32) * 1.4  # boost voz

    # Rellenar para que cubra duración total
    total_samples = int(final_video.duration * SR)
    voz_padded = np.zeros((total_samples, 2), dtype=np.float32)
    voz_start  = silence_samples
    voz_end    = voz_start + len(voz_arr)
    if voz_end > total_samples:
        voz_arr = voz_arr[:total_samples - voz_start]
        voz_end = total_samples
    voz_padded[voz_start:voz_end] = voz_arr

    voz_timed = AudioArrayClip(voz_padded, fps=SR)
    audio_final = CompositeAudioClip([music, voz_timed])

    final = final_video.with_audio(audio_final)

    # 8. Exportar
    out = f"{OUT}/{nombre}_FINAL.mp4"
    print(f"   📤 Exportando {out}")
    final.write_videofile(out, fps=FPS, codec="libx264",
                          audio_codec="aac", preset="fast", logger=None)
    final.close(); clip.close(); voz_clip.close()
    print(f"   ✅ {nombre}_FINAL.mp4")
    return out

print("🚀 Generando videos FINALES con voz + subtítulos + música...\n")
resultados = []
for cfg in CONFIGS:
    try:
        out = procesar(cfg)
        resultados.append(out)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback; traceback.print_exc()

print(f"\n🎉 {len(resultados)}/4 videos FINALES listos en {OUT}/")
