"""
2 videos cinematográficos de 75-90 segundos para redes sociales.
Estilo: cine oscuro + teal/dorado + partículas + luz dramática + voz + subtítulos karaoke.
Formato: 1080x1920 (9:16) TikTok/Reels/Stories.

Video A: "El Arte de la Resina" — historia emocional de transformación personal
Video B: "Cómo Generar Ingresos" — documental-estilo sobre el negocio
"""

import os, math, random, struct, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip
import subprocess, imageio_ffmpeg

os.environ['IMAGEIO_FFMPEG_EXE'] = imageio_ffmpeg.get_ffmpeg_exe()

FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
OUT   = "/home/user/CECI/videos_cinematicos"
TMP   = "/tmp/cine_tmp"
SR    = 44100
VW, VH = 1080, 1920
FPS   = 30

os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# Paleta cinematográfica (teal & orange, estilo Hollywood)
DARK    = (4,  8,  10)
TEAL    = (60, 190, 180)
GOLD    = (240, 190, 60)
ORANGE  = (220, 110, 40)
CREAM   = (238, 248, 245)
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
EMBER   = (200, 80,  30)
DEEP    = (15,  25,  35)

def fnt(name, size):
    try: return ImageFont.truetype(os.path.join(FONTS, name), size)
    except: return ImageFont.load_default()

def ct(draw, text, y, font, color, W=VW, st=4):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]; x = (W-tw)//2
    for dx in range(-st, st+1):
        for dy in range(-st, st+1):
            if dx or dy: draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,200))
    draw.text((x, y), text, font=font, fill=color)

# ── Partículas flotantes ─────────────────────────────────────────────────
def draw_particles(draw, t, color, n=40, seed=0):
    random.seed(seed)
    for i in range(n):
        phase = random.random() * math.pi * 2
        speed = 0.3 + random.random() * 0.7
        ox    = random.randint(0, VW)
        oy    = random.randint(0, VH)
        rx    = int(ox + 60*math.sin(t*speed + phase))
        ry    = int(oy - t*30*speed % VH)
        r     = random.randint(2, 6)
        al    = int(60 + 40*math.sin(t*2 + phase))
        draw.ellipse([rx-r, ry-r, rx+r, ry+r], fill=color+(al,))

# ── Gradiente de fondo cinematográfico ──────────────────────────────────
def cine_bg(t, palette_shift=0):
    img = Image.new("RGBA", (VW, VH), DARK+(255,))
    d   = ImageDraw.Draw(img)
    # Gradiente vertical: muy oscuro abajo, ligeramente menos oscuro arriba
    for y in range(0, VH, 4):
        alpha = int(30 * (1 - y/VH))
        d.rectangle([0, y, VW, y+4], fill=DEEP+(alpha,))
    # Luz ambiental dramática (círculo difuso lateral)
    cx = int(VW*0.15 + VW*0.1*math.sin(t*0.3 + palette_shift))
    cy = int(VH*0.3)
    for r in range(300, 0, -30):
        al = int(12 * (1 - r/300))
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=TEAL+(al,))
    cx2 = int(VW*0.85 + VW*0.08*math.sin(t*0.2))
    cy2 = int(VH*0.6)
    for r in range(250, 0, -25):
        al = int(10 * (1 - r/250))
        d.ellipse([cx2-r, cy2-r, cx2+r, cy2+r], fill=GOLD+(al,))
    draw_particles(d, t, TEAL, n=35, seed=42)
    draw_particles(d, t, GOLD, n=20, seed=99)
    # Film grain (ruido sutil)
    arr = np.array(img).astype(np.float32)
    np.random.seed(int(t*1000) % 10000)
    arr += np.random.randn(*arr.shape) * 5
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

# ── Barras de cine (letterbox) ───────────────────────────────────────────
def letterbox(draw, bar_h=60):
    draw.rectangle([0, 0, VW, bar_h], fill=(0,0,0,255))
    draw.rectangle([0, VH-bar_h, VW, VH], fill=(0,0,0,255))

# ── Luz de destello (lens flare) ─────────────────────────────────────────
def lens_flare(draw, t, intensity=0.5):
    fl = 0.3 + 0.7*abs(math.sin(t*0.4))
    x  = int(VW*0.8 + VW*0.1*math.sin(t*0.15))
    y  = int(VH*0.2)
    for r in [180, 90, 40, 15]:
        al = int(20 * fl * intensity * (40/r))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=GOLD+(al,))

# ── Música cinematográfica (70 BPM, menor dramático) ────────────────────
def gen_cine_music(duration):
    t    = np.linspace(0, duration, int(SR*duration), endpoint=False)
    beat = 60/70
    # Progresión Am - F - C - E (dramática)
    chords = [
        [220.00, 261.63, 329.63],  # Am
        [174.61, 220.00, 261.63],  # F
        [261.63, 329.63, 392.00],  # C
        [164.81, 220.00, 329.63],  # E
    ]
    audio = np.zeros(len(t))
    bars  = int(duration / (beat*4)) + 1
    for bar in range(bars):
        chord = chords[bar%4]; t0=bar*beat*4; t1=(bar+1)*beat*4
        mask=(t>=t0)&(t<min(t1,duration)); seg=t[mask]-t0
        if len(seg)==0: continue
        wav = sum(0.18*np.sin(2*np.pi*f*seg) +
                  0.07*np.sin(4*np.pi*f*seg) +
                  0.03*np.sin(6*np.pi*f*seg) for f in chord)
        # Pad con bajo suave
        bass = chord[0]/2
        wav += 0.12*np.sin(2*np.pi*bass*seg) * np.exp(-seg*0.5)
        fade = min(int(0.15*SR), len(seg)//4)
        env  = np.ones(len(seg))
        if fade > 0:
            env[:fade]  = np.linspace(0,1,fade)
            env[-fade:] = np.linspace(1,0,fade)
        audio[mask] += wav*env
    # Bombo sutil cada 2 beats
    for i in range(int(duration/beat/2)+1):
        idx = int(i*beat*2*SR); kl = int(0.12*SR)
        if idx+kl < len(audio):
            k = np.linspace(1,0,kl)**2 * np.sin(2*np.pi*55*np.linspace(0,0.12,kl))*0.2
            audio[idx:idx+kl] += k
    # Fade in/out global
    fi = min(int(2*SR), len(audio)//4)
    audio[:fi]  *= np.linspace(0,1,fi)
    audio[-fi:] *= np.linspace(1,0,fi)
    audio = audio/(np.max(np.abs(audio))+1e-9)*0.38
    return AudioArrayClip(np.stack([audio,audio],axis=1).astype(np.float32), fps=SR)

# ── Subtítulos karaoke ───────────────────────────────────────────────────
def karaoke_overlay(draw, words, t, total_dur, accent, lb=60):
    ng  = max(1, len(words)//4); gd = total_dur/ng
    gi  = min(int(t/gd), ng-1); gp = (t-gi*gd)/gd
    gw  = words[gi*4:gi*4+4] or words[-4:]
    fs  = fnt("BigShoulders-Bold.ttf", 58)
    fa  = fnt("BigShoulders-Bold.ttf", 65)
    ln  = " ".join(gw)
    bb  = draw.textbbox((0,0), ln, font=fs); tw=bb[2]-bb[0]; pad=20
    bxs = (VW-tw)//2 - pad; sy = VH - lb - 160
    draw.rounded_rectangle([bxs, sy-8, bxs+tw+pad*2, sy+75],
                            radius=16, fill=(0,0,0,210))
    x   = bxs+pad; ai = min(int(gp*len(gw)), len(gw)-1)
    for wi, word in enumerate(gw):
        wb  = draw.textbbox((0,0), word+" ", font=fs); ww=wb[2]-wb[0]
        if wi == ai:
            draw.rounded_rectangle([x-5, sy-6, x+ww, sy+70],
                                    radius=10, fill=accent+(200,))
            draw.text((x, sy-3), word, font=fa, fill=DARK)
        else:
            draw.text((x, sy), word, font=fs, fill=WHITE)
        x += ww

# ══════════════════════════════════════════════════════════════════════════
# VIDEO A: "El Arte de la Resina" — historia emocional, 80 segundos
# ══════════════════════════════════════════════════════════════════════════

SCRIPT_A = """Había una vez una mujer que buscaba algo más.
Algo que pudiera llamar suyo.
Un arte que transformara simples materiales en piezas de valor.
La resina epóxica le dio esa respuesta.
Una mezcla de química y creatividad.
Un proceso que convierte lo ordinario en extraordinario.
Cada gota de pigmento, una decisión artística.
Cada pieza terminada, una victoria personal.
Hoy miles de mujeres en México generan ingresos con este arte.
Desde casa. A su ritmo. Sin jefe.
El curso de Vero Resina te enseña todo desde cero.
Técnicas profesionales. Estrategias de venta.
Comunidad de apoyo y certificado incluido.
Tu historia de transformación comienza aquí.
Entra hoy en Hotmart y empieza a crear tu futuro."""

WORDS_A = SCRIPT_A.replace("\n"," ").split()

SCENES_A = [
    # (t_start, t_end, titulo, subtitulo, accent)
    (0,   12,  "HABÍA UNA VEZ",       "una mujer que buscaba más...",    TEAL),
    (12,  26,  "EL ARTE",             "de la resina epóxica",            GOLD),
    (26,  42,  "QUÍMICA",             "+ CREATIVIDAD",                    TEAL),
    (42,  56,  "MILES DE MUJERES",    "generan ingresos desde casa",      GOLD),
    (56,  70,  "EL CURSO",            "que lo cambia todo",              TEAL),
    (70,  80,  "TU HISTORIA",         "empieza aquí 👇",                 GOLD),
]

def frame_video_a(t):
    total = 80.0
    lb    = 65  # letterbox height

    img = cine_bg(t, palette_shift=0)
    d   = ImageDraw.Draw(img)

    # Barra de cine
    letterbox(d, lb)

    # Destello dramático
    lens_flare(d, t, intensity=0.6)

    # Escena actual
    scene = next((s for s in SCENES_A if s[0] <= t < s[1]), SCENES_A[-1])
    t_local = t - scene[0]; dur_s = scene[1]-scene[0]
    sp      = t_local/dur_s

    # Transición entrada (fade-in en 1s)
    fade_in  = min(1.0, t_local/1.0)
    fade_out = min(1.0, (dur_s-t_local)/0.8) if t_local > dur_s-0.8 else 1.0
    alpha    = int(255 * fade_in * fade_out)

    # Línea decorativa lateral izquierda
    lh = int((VH-lb*2) * sp)
    d.rectangle([0, lb, 5, lb+lh], fill=scene[4]+(180,))

    # Titulo grande
    f1 = fnt("BigShoulders-Bold.ttf", 96)
    f2 = fnt("InstrumentSans-Bold.ttf", 52)
    f3 = fnt("DMMono-Regular.ttf", 28)
    fb = fnt("Italiana-Regular.ttf", 40)

    # Caja semi-transparente central
    box_y = VH//2 - 220
    slide = int((1-fade_in)*50)
    d.rounded_rectangle([60, box_y+slide, VW-60, box_y+200+slide],
                        radius=24, fill=(0,0,0,int(170*fade_in)))

    # Texto de escena
    ct(d, scene[2], box_y+20+slide, f1, scene[4])
    ct(d, scene[3], box_y+120+slide, f2, CREAM)

    # Separador animado
    sep_w = int((VW-160)*min(1.0, t_local/0.8))
    sx    = (VW-sep_w)//2
    d.rectangle([sx, box_y+190+slide, sx+sep_w, box_y+193+slide], fill=scene[4]+(160,))

    # Forma orgánica decorativa (círculo con textura)
    for ring in range(5, 0, -1):
        r     = 80 + ring*25 + int(15*math.sin(t*0.8+ring))
        alpha2 = int(15*(5-ring+1)*fade_in)
        cx, cy = VW//2, VH//2+180
        d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=scene[4]+(alpha2,), width=2)

    # Subtítulos karaoke
    karaoke_overlay(d, WORDS_A, t, total, scene[4], lb=lb)

    # Marca
    d.rectangle([0, lb, VW, lb+48], fill=(0,0,0,150))
    ct(d, "@VeroResina  •  @RPResina  •  @PXResina", lb+10,
       fnt("InstrumentSans-Bold.ttf", 28), TEAL)

    # Progress bar
    bw = int(VW*(t/total))
    d.rectangle([0, VH-lb, VW, VH-lb+6], fill=(0,0,0,120))
    d.rectangle([0, VH-lb, bw, VH-lb+6], fill=scene[4]+(200,))
    if bw > 8: d.ellipse([bw-8, VH-lb-3, bw+8, VH-lb+9], fill=GOLD+(255,))

    # Link en escena final
    if t > 68:
        a_link = int(255*min(1, (t-68)/2))
        ct(d, "go.hotmart.com/G106175870D", VH//2+340,
           fnt("DMMono-Regular.ttf", 34), TEAL)

    return np.array(img.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════════
# VIDEO B: "Cómo Generar Ingresos" — documental de negocio, 90 segundos
# ══════════════════════════════════════════════════════════════════════════

SCRIPT_B = """¿Sabías que el mercado de artesanías en México mueve miles de millones de pesos al año?
Y una parte enorme de ese mercado es la resina epóxica.
Joyería. Cuadros decorativos. Mesas. Lámparas. Charolas.
Todo hecho a mano. Todo con un alto valor percibido.
Una pulsera de resina puede venderse desde cien pesos.
Un cuadro decorativo desde dos mil.
Una mesa de resina puede superar los quince mil pesos.
¿Y cuánto cuesta empezar? Menos de quinientos pesos en materiales.
Eso es un margen de ganancia enorme.
Y no necesitas una tienda física. Solo redes sociales.
Instagram, Facebook, TikTok te dan acceso a millones de clientes.
El curso de Vero Resina te enseña desde cero a dominar todo esto.
La técnica. Los materiales. La fotografía de producto.
Cómo fijar precios. Cómo vender por redes. Cómo escalar tu negocio.
Más de mil alumnas ya generan ingresos con lo que aprendieron.
La pregunta es: ¿cuándo empiezas tú?"""

WORDS_B = SCRIPT_B.replace("\n"," ").split()

DATOS = [
    (0,   14,  "EL MERCADO",          "$MILLONES en artesanías/año",     GOLD),
    (14,  28,  "RESINA EPÓXICA",       "alta demanda — alta ganancia",    TEAL),
    (28,  42,  "PRECIOS REALES",        "$100 — $15,000 MXN por pieza",   GOLD),
    (42,  56,  "INVERSIÓN MÍNIMA",      "menos de $500 para empezar",     TEAL),
    (56,  70,  "REDES SOCIALES",        "son tu tienda gratuita",         GOLD),
    (70,  82,  "+1,000 ALUMNAS",        "ya generan ingresos",            TEAL),
    (82,  90,  "¿CUÁNDO EMPIEZAS TÚ?", "Entra hoy en Hotmart 👇",        GOLD),
]

def frame_video_b(t):
    total = 90.0; lb = 65
    img = cine_bg(t, palette_shift=1.0)
    d   = ImageDraw.Draw(img)
    letterbox(d, lb)
    lens_flare(d, t*1.1, intensity=0.7)

    scene = next((s for s in DATOS if s[0] <= t < s[1]), DATOS[-1])
    t_local = t-scene[0]; dur_s=scene[1]-scene[0]
    fade_in  = min(1.0, t_local/1.0)
    fade_out = min(1.0, (dur_s-t_local)/0.8) if t_local>dur_s-0.8 else 1.0

    # Línea vertical animada
    lh = int((VH-lb*2)*(t_local/dur_s))
    d.rectangle([VW-6, lb, VW, lb+lh], fill=scene[4]+(180,))

    f1 = fnt("BigShoulders-Bold.ttf", 90)
    f2 = fnt("InstrumentSans-Bold.ttf", 50)
    f3 = fnt("DMMono-Regular.ttf", 32)

    box_y = VH//2 - 200
    slide = int((1-fade_in)*60)
    d.rounded_rectangle([50, box_y+slide, VW-50, box_y+220+slide],
                        radius=22, fill=(0,0,0,int(175*fade_in)))

    ct(d, scene[2], box_y+18+slide, f1, scene[4])
    ct(d, scene[3], box_y+118+slide, f2, CREAM)

    # Número grande animado (para escenas de datos)
    if "PRECIOS" in scene[2]:
        # Barra de precios estilo infográfico
        precios = [("Pulsera",100), ("Cuadro",2000), ("Lámpara",4000), ("Mesa",15000)]
        py = VH//2+60
        max_v = 15000
        for nombre, valor in precios:
            bw2 = int((VW-180) * (valor/max_v) * min(1.0, t_local/1.5))
            d.rectangle([90, py, 90+bw2, py+38], fill=scene[4]+(int(180*fade_in),))
            d.text((100, py+6), f"{nombre}: ${valor:,}", font=fnt("InstrumentSans-Bold.ttf",30), fill=WHITE)
            py += 58
    elif "ALUMNAS" in scene[2]:
        # Contador animado
        count = int(min(1000, 1000 * min(1.0, t_local/2.0)))
        ct(d, f"+{count} alumnas", VH//2+100,
           fnt("BigShoulders-Bold.ttf", 82), scene[4])
        ct(d, "y tú puedes ser la siguiente", VH//2+200,
           fnt("InstrumentSans-Regular.ttf", 42), CREAM)

    # Separador
    sep_w = int((VW-160)*min(1.0, t_local/0.8))
    sx    = (VW-sep_w)//2
    d.rectangle([sx, box_y+200+slide, sx+sep_w, box_y+203+slide], fill=scene[4]+(160,))

    # Karaoke
    karaoke_overlay(d, WORDS_B, t, total, scene[4], lb=lb)

    # Marca
    d.rectangle([0, lb, VW, lb+48], fill=(0,0,0,150))
    ct(d, "@VeroResina  •  @RPResina  •  @PXResina", lb+10,
       fnt("InstrumentSans-Bold.ttf", 28), TEAL)

    # Progress
    bw = int(VW*(t/total))
    d.rectangle([0, VH-lb, VW, VH-lb+6], fill=(0,0,0,120))
    d.rectangle([0, VH-lb, bw, VH-lb+6], fill=scene[4]+(200,))
    if bw > 8: d.ellipse([bw-8, VH-lb-3, bw+8, VH-lb+9], fill=GOLD+(255,))

    # CTA final
    if t > 78:
        a_link = min(1.0, (t-78)/2)
        pulse  = 1 + 0.06*math.sin(t*math.pi*6)
        bw3,bh3 = int(780*pulse), int(100*pulse)
        bx3 = (VW-bw3)//2; by3 = VH//2+300
        d.rounded_rectangle([bx3, by3, bx3+bw3, by3+bh3], radius=28,
                            fill=GOLD+(int(230*a_link),))
        ct(d, "👉  QUIERO EL CURSO", by3+18,
           fnt("InstrumentSans-Bold.ttf", 46), DARK)
        ct(d, "go.hotmart.com/G106175870D", by3+112,
           fnt("DMMono-Regular.ttf", 30), TEAL)

    return np.array(img.convert("RGB"))


# ── CTA final compartido (5s) ────────────────────────────────────────────
def make_cta(accent):
    def f(t):
        p   = min(1.0, t/5.0)
        img = cine_bg(t, 0.5)
        d   = ImageDraw.Draw(img)
        letterbox(d)
        lens_flare(d, t)
        for ci in range(6):
            ang = p*math.pi*2+ci*1.05
            cx  = VW//2+int(math.cos(ang)*VW*0.35)
            cy  = VH//2+int(math.sin(ang)*VH*0.18)
            r   = int(VW*0.17+math.sin(p*math.pi*3+ci)*20)
            d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=accent+(22,))
        d.rectangle([0,65,VW,8+65], fill=accent+(180,))
        ct(d,"TRANSFORMA TU VIDA",      VH//2-320, fnt("BigShoulders-Bold.ttf",88), GOLD)
        ct(d,"con la resina epóxica",   VH//2-215, fnt("InstrumentSans-Bold.ttf",50), CREAM)
        sep=(VW-420)//2; d.rectangle([sep,VH//2-165,sep+420,VH//2-162], fill=TEAL+(200,))
        for bi,ben in enumerate(["✅ Aprende desde cero","✅ Certificado incluido",
                                  "✅ Comunidad de apoyo","✅ Empieza a vender ya"]):
            ct(d,ben,VH//2-140+bi*70,fnt("InstrumentSans-Regular.ttf",40),CREAM)
        pulse=1+0.08*math.sin(p*math.pi*8)
        bw,bh=int(840*pulse),int(115*pulse); bx=(VW-bw)//2; by=VH//2+120
        d.rounded_rectangle([bx,by,bx+bw,by+bh],radius=32,fill=GOLD+(245,))
        ct(d,"👉  QUIERO EL CURSO",by+22,fnt("InstrumentSans-Bold.ttf",50),DARK,st=0)
        ct(d,"go.hotmart.com/G106175870D",by+132,fnt("DMMono-Regular.ttf",32),TEAL)
        ct(d,"VeroResina",VH-125,fnt("Italiana-Regular.ttf",50),GOLD)
        return np.array(img.convert("RGB"))
    return VideoClip(frame_function=f, duration=5.0)


# ── TTS ──────────────────────────────────────────────────────────────────
def gen_tts(text, path):
    subprocess.run(["espeak-ng","-v","es-419","-s","130","-p","60","-a","200",
                    text, "-w", path], check=True, capture_output=True)
    return AudioFileClip(path)


# ── Exportar video completo ───────────────────────────────────────────────
def exportar(nombre, frame_func, script, total_dur, accent):
    print(f"\n🎬 {nombre} ({total_dur}s)")

    # Video principal
    main_clip = VideoClip(frame_function=frame_func, duration=total_dur)

    # CTA
    cta_clip = make_cta(accent)
    final_v  = concatenate_videoclips([main_clip, cta_clip])
    full_dur = final_v.duration

    # TTS
    print("   🎙️ Generando voz...")
    voz_wav = f"{TMP}/{nombre}.wav"
    voz_clip = gen_tts(script, voz_wav)

    # Música
    print("   🎵 Generando música...")
    music = gen_cine_music(full_dur).with_duration(full_dur)

    # Mezclar audio
    voz_arr = voz_clip.to_soundarray(fps=SR).astype(np.float32)*1.4
    if voz_arr.ndim==1: voz_arr=np.stack([voz_arr,voz_arr],axis=1)
    total_s = int(full_dur*SR)
    vp = np.zeros((total_s,2),dtype=np.float32)
    vs = int(1.5*SR); ve = min(vs+len(voz_arr),total_s)
    vp[vs:ve] = voz_arr[:ve-vs]
    vt = AudioArrayClip(vp, fps=SR).with_duration(full_dur)
    audio_f = CompositeAudioClip([music, vt]).with_duration(full_dur)
    final_v = final_v.with_audio(audio_f)

    out = f"{OUT}/{nombre}.mp4"
    print(f"   📤 Exportando {full_dur:.0f}s...")
    final_v.write_videofile(out, fps=FPS, codec="libx264",
                            audio_codec="aac", preset="medium", logger=None)
    final_v.close(); voz_clip.close()
    print(f"   ✅ {nombre}.mp4")
    return out


print("🚀 Creando 2 videos cinematográficos...\n")

resultados = []

try:
    out = exportar(
        "VideoA_ElArte",
        frame_video_a,
        SCRIPT_A.replace("\n", " "),
        80.0,
        TEAL
    )
    resultados.append(out)
except Exception as e:
    print(f"❌ VideoA: {e}")
    import traceback; traceback.print_exc()

try:
    out = exportar(
        "VideoB_ComoGanar",
        frame_video_b,
        SCRIPT_B.replace("\n", " "),
        90.0,
        GOLD
    )
    resultados.append(out)
except Exception as e:
    print(f"❌ VideoB: {e}")
    import traceback; traceback.print_exc()

print(f"\n🎉 {len(resultados)}/2 videos cinematográficos en {OUT}/")
