"""
7 videos de resina epóxica — uno por día de la semana
Cada video: Intro animada (8s) + Video principal con texto (46s) + Outro CTA (10s) = ~64s
"""

import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (VideoFileClip, ImageClip, AudioFileClip,
                     CompositeVideoClip, CompositeAudioClip,
                     concatenate_videoclips)
from moviepy.audio.AudioClip import AudioArrayClip
from gtts import gTTS
import random

random.seed(7)
np.random.seed(7)

FONTS  = "/root/.claude/skills/canvas-design/canvas-fonts"
INPUT  = "/root/.claude/uploads/e53a79e8-4dea-557c-b336-e5482ebcc79c/0175ef1d-lv_0_20260721085442.mp4"
OUT    = "/home/user/CECI/videos_semana"
TMP    = "/tmp/semana_tmp"
SR     = 44100
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ── Paleta VeroResina ────────────────────────────────────────────────
DARK  = (5, 10, 12)
TEAL  = (78, 205, 196)
GOLD  = (247, 201, 72)
CREAM = (240, 250, 248)

def fnt(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def centered_text(draw, text, y, font, color, W, shadow=True):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x  = (W - tw)//2
    if shadow:
        draw.text((x+2, y+2), text, font=font, fill=(0,0,0,140))
    draw.text((x, y), text, font=font, fill=color)

def add_noise(img, s=5):
    a = np.array(img).astype(np.float32)
    a = np.clip(a + np.random.randn(*a.shape)*s, 0, 255).astype(np.uint8)
    return Image.fromarray(a)

# ── Música ambient ────────────────────────────────────────────────────
def ambient_music(dur, bpm=88):
    t = np.linspace(0, dur, int(SR*dur), endpoint=False)
    beat = 60/bpm
    chords = [[220,261.63,329.63],[261.63,329.63,392],[174.61,220,261.63],[196,246.94,293.66]]
    pad = np.zeros_like(t)
    bar = beat*4
    bars = int(np.ceil(dur/bar))
    for b in range(bars):
        ci = b%4
        s0, s1 = b*bar, min((b+1)*bar, dur)
        m = (t>=s0)&(t<s1)
        for f in chords[ci]:
            pad[m] += 0.055*(0.7*np.sin(2*np.pi*f*t[m])
                            +0.3*(2*np.arcsin(np.clip(np.sin(2*np.pi*f*t[m]),-1,1))/np.pi))
    kick = np.zeros_like(t)
    for bt in np.arange(0,dur,beat):
        kl=int(0.12*SR); kt=np.linspace(0,.12,kl)
        ks=np.sin(2*np.pi*60*kt)*np.exp(-30*kt)
        i=int(bt*SR); e=min(i+kl,len(kick)); kick[i:e]+=0.16*ks[:e-i]
    hihat=np.zeros_like(t)
    for ht in np.arange(0,dur,beat/2):
        hl=int(.035*SR)
        hs=np.random.randn(hl)*np.exp(-90*np.linspace(0,.035,hl))
        i=int(ht*SR); e=min(i+hl,len(hihat)); hihat[i:e]+=0.045*hs[:e-i]
    mix=pad+kick+hihat
    fade=int(2*SR)
    mix[:fade]*=np.linspace(0,1,fade)
    mix[-fade:]*=np.linspace(1,0,fade)
    p=np.max(np.abs(mix)); mix=mix/p*0.68 if p>0 else mix
    return mix.astype(np.float32)

def tts(text, name):
    p=f"{TMP}/{name}.mp3"
    gTTS(text=text, lang="es", tld="com.mx", slow=False).save(p)
    return p

# ── Frames animados ───────────────────────────────────────────────────
VW, VH = 1080, 1920

def make_intro_frames(title, subtitle, day_label, accent, fps=30, dur=8):
    """Genera lista de frames PIL para la pantalla de intro."""
    frames=[]
    total=int(fps*dur)
    f_big  = fnt("BigShoulders-Bold.ttf", 110)
    f_med  = fnt("InstrumentSans-Bold.ttf", 52)
    f_sm   = fnt("InstrumentSans-Regular.ttf", 38)
    f_day  = fnt("DMMono-Regular.ttf", 32)
    f_brand= fnt("Italiana-Regular.ttf", 42)

    for fi in range(total):
        prog = fi/total
        img  = Image.new("RGB", (VW,VH), DARK)
        d    = ImageDraw.Draw(img)

        # Resin blob bg
        for _ in range(6):
            cx=random.randint(0,VW); cy=random.randint(0,VH)
            r=random.randint(80,220)
            d.ellipse([cx-r,cy-r,cx+r,cy+r],
                      fill=(*accent, 18) if len(accent)==3 else accent)

        # Animated teal sine wave
        wave_y = int(VH*0.5 + 30*math.sin(prog*4*math.pi))
        for wx in range(0, VW, 2):
            wy = wave_y + int(25*math.sin(wx/80 + prog*6*math.pi))
            d.ellipse([wx-1,wy-1,wx+1,wy+1], fill=(*accent,35))

        # Fade-in text
        alpha = min(1.0, prog*3)

        # Day label top
        centered_text(d, day_label, int(VH*0.12), f_day,
                      (*accent, int(200*alpha)), VW, shadow=False)

        # Brand
        centered_text(d, "@VeroResina", int(VH*0.18), f_brand,
                      (*CREAM, int(130*alpha)), VW, shadow=False)

        # Main title — slide in from bottom
        slide = int((1-min(1,prog*2.5)) * 80)
        ty = int(VH*0.35) + slide
        centered_text(d, title, ty, f_big,
                      (*accent, int(255*min(1,prog*2))), VW)

        # Subtitle
        for i, line in enumerate(subtitle.split("\n")):
            centered_text(d, line, int(VH*0.62)+i*62, f_med,
                          (*CREAM, int(220*alpha)), VW)

        # Bottom bar
        bar_w = int(VW * min(1.0, prog*2))
        d.rectangle([VW//2-bar_w//2, VH-6, VW//2+bar_w//2, VH], fill=accent)

        img = add_noise(img, 4)
        frames.append(np.array(img))
    return frames

def make_outro_frames(cta_line1, cta_line2, accent, fps=30, dur=10):
    frames=[]
    total=int(fps*dur)
    f_big  = fnt("BigShoulders-Bold.ttf", 86)
    f_med  = fnt("InstrumentSans-Bold.ttf", 48)
    f_sm   = fnt("DMMono-Regular.ttf", 34)

    for fi in range(total):
        prog = fi/total
        img  = Image.new("RGB",(VW,VH),DARK)
        d    = ImageDraw.Draw(img)

        # Pulsing circle bg
        pulse = 1+0.08*math.sin(prog*6*math.pi)
        r=int(320*pulse)
        cx,cy=VW//2,VH//2
        d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(*accent,22))
        r2=int(180*pulse)
        d.ellipse([cx-r2,cy-r2,cx+r2,cy+r2], fill=(*accent,18))

        # Fade-in
        alpha=min(1.0,prog*2)

        centered_text(d, cta_line1, int(VH*0.32), f_big,
                      (*GOLD, int(255*alpha)), VW)
        centered_text(d, cta_line2, int(VH*0.48), f_med,
                      (*CREAM, int(230*alpha)), VW)

        # CTA button
        btn_y=int(VH*0.62)
        btn_w=540; btn_h=80
        btn_x=(VW-btn_w)//2
        d.rounded_rectangle([btn_x,btn_y,btn_x+btn_w,btn_y+btn_h],
                             radius=16, fill=(*accent,int(230*alpha)))
        centered_text(d,"→ go.hotmart.com/G106175870D",
                      btn_y+20, fnt("DMMono-Regular.ttf",26),
                      (*DARK,255), VW, shadow=False)

        centered_text(d,"Link en bio de @VeroResina",
                      int(VH*0.80), f_sm,
                      (*CREAM,int(160*alpha)), VW, shadow=False)

        img=add_noise(img,4)
        frames.append(np.array(img))
    return frames

def frames_to_clip(frames, fps=30):
    from moviepy import VideoClip
    dur = len(frames) / fps
    return VideoClip(frame_function=lambda t: frames[min(int(t*fps), len(frames)-1)],
                     duration=dur)

# ── Video principal crop ──────────────────────────────────────────────
print("📹 Cargando video base...")
base = VideoFileClip(INPUT)
W,H  = base.size
cw   = int(H*9/16)
x1   = (W-cw)//2
clip_v = base.cropped(x1=x1,y1=0,x2=x1+cw,y2=H).resized((VW,VH))

def overlay_text_on_clip(clip, lines, ys, sizes, colors, bg_alpha=150):
    ov = Image.new("RGBA",(VW,VH),(0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for text,y,sz,col in zip(lines,ys,sizes,colors):
        f=fnt("BigShoulders-Bold.ttf" if sz>=60 else "InstrumentSans-Regular.ttf", sz)
        bb=d.textbbox((0,0),text,font=f); tw=bb[2]-bb[0]
        x=(VW-tw)//2
        pad=12
        d.rounded_rectangle([x-pad,y-pad,x+tw+pad,y+(bb[3]-bb[1])+pad],
                             radius=10,fill=(*DARK,bg_alpha))
        d.text((x+2,y+2),text,font=f,fill=(0,0,0,120))
        d.text((x,y),text,font=f,fill=(*col,255))
    ov_arr=np.array(ov)
    def proc(frame):
        base=Image.fromarray(frame.astype(np.uint8),"RGB").convert("RGBA")
        base.paste(Image.fromarray(ov_arr,"RGBA"),(0,0),Image.fromarray(ov_arr,"RGBA"))
        return np.array(base.convert("RGB"))
    return clip.image_transform(proc)

# ═══════════════════════════════════════════════════════════════════════
# DEFINICIÓN DE LOS 7 VIDEOS
# ═══════════════════════════════════════════════════════════════════════

dias = [
    dict(
        nombre="Lunes",
        archivo="Lunes_inspiracion",
        accent=TEAL,
        intro_title="LUNES DE\nINSPIRACIÓN",
        intro_sub="Empieza la semana\ncreando algo hermoso",
        day_label="LUNES · SEMANA DE RESINA CON @VERORESINA",
        overlay=["@VeroResina","LUNES DE INSPIRACIÓN","Arte en Resina Epóxica","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, TEAL, GOLD],
        voz=(
            "¡Feliz lunes! Empieza esta semana creando algo que nadie más tiene. "
            "La resina epóxica te permite hacer piezas únicas que la gente paga con gusto. "
            "Mesas, charolas, cuadros, joyería. Todo puede hacerse con resina. "
            "Y lo mejor: puedes aprenderlo desde cero, desde tu casa, "
            "sin necesitar experiencia previa. "
            "En el link de mi bio encuentras el curso que me cambió la vida. "
            "Empieza hoy. Tu primer pieza te espera."
        ),
        outro1="¡Aprende esta semana!",
        outro2="Curso completo de Resina Epóxica"
    ),
    dict(
        nombre="Martes",
        archivo="Martes_tips",
        accent=(100, 220, 180),
        intro_title="MARTES DE\nTIPS",
        intro_sub="3 errores que arruinan\ntu resina epóxica",
        day_label="MARTES · TIPS DE RESINA CON @VERORESINA",
        overlay=["@VeroResina","MARTES DE TIPS","3 Errores que debes evitar","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, TEAL, GOLD],
        voz=(
            "Martes de tips. Hoy te cuento los tres errores más comunes al trabajar con resina. "
            "Error número uno: no mezclar bien el endurecedor con la resina. "
            "Si no mezclas exactamente en la proporción correcta, la pieza no cura. "
            "Error número dos: trabajar en un cuarto frío. "
            "La resina necesita temperatura entre 20 y 25 grados para fluir bien. "
            "Error número tres: no protegerse. "
            "Siempre usa guantes y mascarilla. La resina sin curar puede irritar la piel. "
            "¿Quieres aprender todo esto correctamente desde el principio? "
            "El curso completo está en el link de mi bio."
        ),
        outro1="Evita estos errores",
        outro2="Aprende la técnica correcta desde cero"
    ),
    dict(
        nombre="Miercoles",
        archivo="Miercoles_tecnica",
        accent=(150, 180, 255),
        intro_title="MIÉRCOLES\nDE TÉCNICA",
        intro_sub="Hoy aprendes a hacer\nuna pieza perfecta",
        day_label="MIÉRCOLES · TÉCNICA CON @VERORESINA",
        overlay=["@VeroResina","MIÉRCOLES DE TÉCNICA","Paso a paso desde cero","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, (150,180,255), GOLD],
        voz=(
            "Miércoles de técnica. Hoy te explico el proceso completo de una pieza de resina. "
            "Primero preparas el molde: límpialo y aplica desmoldante. "
            "Luego mezclas la resina con el endurecedor en la proporción indicada, "
            "dos a uno generalmente. Mezcla despacio durante tres minutos completos. "
            "Agrega tus pigmentos, flores secas, o lo que quieras incluir. "
            "Vierte la mezcla lentamente al molde. "
            "Usa un soplete o pistola de calor para eliminar burbujas. "
            "Deja curar 24 horas mínimo antes de desmoldar. "
            "¿Quieres ver el proceso completo paso a paso? "
            "El curso tiene tutoriales de cada técnica. Link en mi bio."
        ),
        outro1="Aprende la técnica completa",
        outro2="Curso paso a paso disponible ahora"
    ),
    dict(
        nombre="Jueves",
        archivo="Jueves_dinero",
        accent=GOLD,
        intro_title="JUEVES DE\nNEGOCIO",
        intro_sub="¿Cuánto puedes ganar\ncon resina epóxica?",
        day_label="JUEVES · NEGOCIOS CON @VERORESINA",
        overlay=["@VeroResina","JUEVES DE NEGOCIO","Gana $10,000 MXN al mes","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, GOLD, GOLD],
        voz=(
            "Jueves de negocios. Hablemos de dinero. "
            "Una mesa de resina epóxica se vende entre ocho mil y veinte mil pesos en México. "
            "Los materiales para hacerla cuestan entre ochocientos y dos mil pesos. "
            "Eso es entre cuatro y diez veces tu inversión en cada pieza. "
            "Una charola pequeña la puedes hacer por trescientos pesos y venderla en mil quinientos. "
            "Con solo cuatro ventas al mes ya recuperas la inversión del curso completo. "
            "Muchas de mis alumnas ya generan ingresos desde el primer mes. "
            "¿Quieres empezar tú también? El link del curso está en mi bio."
        ),
        outro1="¿Listo para ganar?",
        outro2="Empieza a vender resina este mes"
    ),
    dict(
        nombre="Viernes",
        archivo="Viernes_ventas",
        accent=(255, 120, 100),
        intro_title="VIERNES DE\nVENTAS",
        intro_sub="Cómo vender tus piezas\nsin tener tienda",
        day_label="VIERNES · VENTAS CON @VERORESINA",
        overlay=["@VeroResina","VIERNES DE VENTAS","Vende sin tienda física","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, (255,120,100), GOLD],
        voz=(
            "Viernes de ventas. Te cuento cómo vender tus piezas de resina sin necesitar tienda. "
            "El primer lugar: Facebook Marketplace. Es gratis y tiene millones de compradores locales. "
            "El segundo: Instagram. Sube fotos bonitas con buena iluminación y usa hashtags de resina. "
            "El tercero: Mercado Libre. Perfecto para llegar a todo el país. "
            "El cuarto: TikTok. Muestra el proceso de fabricación, la gente ama ver cómo se hace. "
            "El quinto: grupos de WhatsApp y comunidades locales. "
            "No necesitas tienda, no necesitas inventario. "
            "Solo necesitas la técnica y las fotos correctas. "
            "El curso te enseña todo esto. Link en mi bio."
        ),
        outro1="Vende desde esta semana",
        outro2="5 canales de venta explicados en el curso"
    ),
    dict(
        nombre="Sabado",
        archivo="Sabado_tutorial",
        accent=(180, 140, 255),
        intro_title="SÁBADO DE\nTUTORIAL",
        intro_sub="Hoy hacemos una pieza\njuntos desde cero",
        day_label="SÁBADO · TUTORIAL CON @VERORESINA",
        overlay=["@VeroResina","SÁBADO DE TUTORIAL","Tutorial completo · Míralo","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, (180,140,255), GOLD],
        voz=(
            "Sábado de tutorial. ¡Hoy hacemos una pieza juntas! "
            "Para empezar necesitas: resina epóxica de dos componentes, "
            "un molde de silicona, guantes, pigmentos del color que quieras "
            "y una pistola de calor o mechero. "
            "Mezcla la resina con el endurecedor exactamente como indica el fabricante. "
            "Agrega dos gotas de pigmento teal y dos de dorado. "
            "Mezcla suavemente con un palillo haciendo movimientos de remolino. "
            "Vierte al molde desde el centro y deja que fluya solo. "
            "Pasa el calor por encima para sacar las burbujas. "
            "En 24 horas tienes tu primera pieza lista. "
            "¿Quieres el tutorial completo con todos los trucos? "
            "Está en el curso del link de mi bio."
        ),
        outro1="¡Hazlo tú también!",
        outro2="Tutorial completo disponible en el curso"
    ),
    dict(
        nombre="Domingo",
        archivo="Domingo_comunidad",
        accent=(100, 200, 150),
        intro_title="DOMINGO DE\nCOMUNIDAD",
        intro_sub="Gracias por estar aquí\n@VeroResina",
        day_label="DOMINGO · COMUNIDAD CON @VERORESINA",
        overlay=["@VeroResina","DOMINGO DE COMUNIDAD","Tú también puedes lograrlo","Link en bio 👆"],
        overlay_y=[60, VH-440, VH-360, VH-120],
        overlay_sz=[34, 68, 42, 36],
        overlay_col=[TEAL, CREAM, (100,200,150), GOLD],
        voz=(
            "Domingo de comunidad. Quiero agradecerte por estar aquí cada semana. "
            "Cuando empecé con la resina epóxica no sabía nada. "
            "Mi primera pieza quedó llena de burbujas y tuve que tirarla. "
            "Pero seguí practicando, tomé el curso adecuado, "
            "y en menos de un mes ya estaba vendiendo mis piezas. "
            "Hoy puedo trabajar desde casa, a mis tiempos, "
            "haciendo algo que me encanta y generando ingresos reales. "
            "Tú también puedes lograrlo. No importa si nunca has tocado la resina. "
            "El curso empieza desde cero y te lleva paso a paso. "
            "Esta semana es tu momento. Link en mi bio. Te espero del otro lado."
        ),
        outro1="Esta semana es tu momento",
        outro2="Únete a la comunidad de @VeroResina"
    ),
]

# ═══════════════════════════════════════════════════════════════════════
# PRODUCCIÓN
# ═══════════════════════════════════════════════════════════════════════

for i, dia in enumerate(dias):
    print(f"\n🎬 [{i+1}/7] {dia['nombre']} — {dia['archivo']}")
    acc = dia['accent']

    # — Intro frames —
    print("   📽  Generando intro...")
    intro_frames = make_intro_frames(
        dia['intro_title'], dia['intro_sub'], dia['day_label'], acc,
        fps=30, dur=8
    )
    intro_clip = frames_to_clip(intro_frames, fps=30)

    # — Main video con overlay —
    print("   🎥  Aplicando overlay al video principal...")
    ov = Image.new("RGBA",(VW,VH),(0,0,0,0))
    d  = ImageDraw.Draw(ov)
    for text,y,sz,col in zip(dia['overlay'],dia['overlay_y'],
                              dia['overlay_sz'],dia['overlay_col']):
        f=fnt("BigShoulders-Bold.ttf" if sz>=60 else "InstrumentSans-Regular.ttf",sz)
        bb=d.textbbox((0,0),text,font=f); tw=bb[2]-bb[0]
        x=(VW-tw)//2; pad=12
        d.rounded_rectangle([x-pad,y-pad,x+tw+pad,y+(bb[3]-bb[1])+pad],
                             radius=10,fill=(*DARK,148))
        d.text((x+2,y+2),text,font=f,fill=(0,0,0,100))
        d.text((x,y),text,font=f,fill=(*col,255))
    ov_arr=np.array(ov)
    def make_proc(arr):
        def proc(frame):
            base=Image.fromarray(frame.astype(np.uint8),"RGB").convert("RGBA")
            ov_img=Image.fromarray(arr,"RGBA")
            base.paste(ov_img,(0,0),ov_img)
            return np.array(base.convert("RGB"))
        return proc
    main_clip = clip_v.image_transform(make_proc(ov_arr))

    # — Outro frames —
    print("   📽  Generando outro...")
    outro_frames = make_outro_frames(dia['outro1'], dia['outro2'], acc, fps=30, dur=10)
    outro_clip = frames_to_clip(outro_frames, fps=30)

    # — Concatenar —
    full_clip = concatenate_videoclips([intro_clip, main_clip, outro_clip])
    dur = full_clip.duration
    print(f"   ⏱  Duración total: {dur:.1f}s")

    # — Voz —
    print("   🗣  Generando voz...")
    voz_path = tts(dia['voz'], dia['archivo'])
    voz_clip = AudioFileClip(voz_path)
    if voz_clip.duration > dur:
        voz_clip = voz_clip.with_duration(dur)

    # — Música —
    print("   🎵  Generando música...")
    music_arr = ambient_music(dur+2)
    stereo = np.stack([music_arr, music_arr], axis=1)
    music_clip = AudioArrayClip(stereo, fps=SR).with_duration(dur).with_volume_scaled(0.22)

    # — Mix audio —
    final_audio = CompositeAudioClip([music_clip, voz_clip.with_volume_scaled(0.95)])
    final_video = full_clip.with_audio(final_audio)

    # — Exportar —
    out_path = f"{OUT}/{dia['archivo']}.mp4"
    print(f"   💾  Exportando {out_path}...")
    final_video.write_videofile(out_path, fps=30, codec="libx264",
                                 audio_codec="aac", audio_fps=SR,
                                 logger=None, preset="fast", bitrate="4500k")
    print(f"   ✅  {dia['archivo']}.mp4 listo!")

base.close()
print("\n" + "="*55)
print("🌿 LOS 7 VIDEOS ESTÁN LISTOS:")
for f in sorted(os.listdir(OUT)):
    mb = os.path.getsize(f"{OUT}/{f}")/1_000_000
    print(f"  📱 {f}  ({mb:.1f} MB)")
print("="*55)
