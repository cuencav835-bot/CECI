"""
Genera los 4 videos finales usando videos ya escalados a 1080x1920.
Incluye: voz espeak-ng, subtítulos karaoke, música, intro, CTA.
"""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip
import imageio_ffmpeg
os.environ['IMAGEIO_FFMPEG_EXE'] = imageio_ffmpeg.get_ffmpeg_exe()

FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
OUT   = "/home/user/CECI/videos_finales"
TMP   = "/tmp/voz_tmp"
SR=44100; VW,VH=1080,1920; FPS=30
DARK=(5,10,12); TEAL=(78,205,196); GOLD=(247,201,72)
CREAM=(240,250,248); WHITE=(255,255,255); BLACK=(0,0,0)
PINK=(255,100,180); GREEN=(60,220,120); PURPLE=(160,80,220)
os.makedirs(OUT, exist_ok=True)

def fnt(n, s):
    try: return ImageFont.truetype(os.path.join(FONTS, n), s)
    except: return ImageFont.load_default()

def ct(draw, text, y, font, color, W=VW, st=3):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]; x = (W-tw)//2
    for dx in range(-st, st+1):
        for dy in range(-st, st+1):
            if dx or dy: draw.text((x+dx, y+dy), text, font=font, fill=(0,0,0,200))
    draw.text((x, y), text, font=font, fill=color)

def gen_music(duration):
    t = np.linspace(0, duration, int(SR*duration), endpoint=False)
    beat = 60/80
    chords = [[220.,261.63,329.63],[174.61,220.,261.63],[261.63,329.63,392.],[196.,246.94,293.66]]
    audio = np.zeros(len(t))
    for bar in range(int(duration/(beat*4))+1):
        ch = chords[bar%4]; t0=bar*beat*4; t1=(bar+1)*beat*4
        mask=(t>=t0)&(t<min(t1,duration)); seg=t[mask]-t0
        wav = sum(0.2*np.sin(2*np.pi*f*seg)+0.06*np.sin(4*np.pi*f*seg) for f in ch)
        fade=int(0.1*SR); env=np.ones(len(seg))
        env[:fade]=np.linspace(0,1,fade); env[-fade:]=np.linspace(1,0,fade)
        audio[mask] += wav*env
    audio = audio/(np.max(np.abs(audio))+1e-9)*0.32
    return AudioArrayClip(np.stack([audio,audio],axis=1).astype(np.float32), fps=SR)

def ov_frame(t, clip, dur, words, accent, emojis):
    base = clip.get_frame(min(t, clip.duration-0.02))
    bi = Image.fromarray(base.astype(np.uint8))
    ov = Image.new('RGBA',(VW,VH),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # progress bar
    pr=t/dur; bw=int(VW*pr)
    d.rectangle([0,VH-28,VW,VH], fill=(0,0,0,120))
    d.rectangle([0,VH-28,bw,VH], fill=TEAL+(200,))
    if bw>12: d.ellipse([bw-12,VH-34,bw+12,VH], fill=GOLD+(255,))
    # brand bar
    d.rectangle([0,0,VW,58], fill=(0,0,0,170))
    ct(d,'@VeroResina  •  @RPResina  •  @PXResina', 13, fnt('InstrumentSans-Bold.ttf',30), TEAL)
    # subtítulos karaoke
    ng=max(1,len(words)//3); gd=dur/ng; gi=min(int(t/gd),ng-1); gp=(t-gi*gd)/gd
    gw = words[gi*3:gi*3+3] or words[-3:]
    fs=fnt('BigShoulders-Bold.ttf',62); fa=fnt('BigShoulders-Bold.ttf',70)
    ln=' '.join(gw); bb=d.textbbox((0,0),ln,font=fs); tw=bb[2]-bb[0]; pad=24
    bxs=(VW-tw)//2-pad; sy=VH-200
    d.rounded_rectangle([bxs,sy-10,bxs+tw+pad*2,sy+80], radius=18, fill=(0,0,0,200))
    x=bxs+pad; ai=min(int(gp*len(gw)),len(gw)-1)
    for wi,word in enumerate(gw):
        wb=d.textbbox((0,0),word+' ',font=fs); ww=wb[2]-wb[0]
        if wi==ai:
            d.rounded_rectangle([x-6,sy-8,x+ww+2,sy+72], radius=12, fill=GOLD+(200,))
            d.text((x,sy-4), word, font=fa, fill=DARK)
        else:
            d.text((x,sy), word, font=fs, fill=WHITE)
        x += ww
    # emoji flotante
    if emojis:
        ec=int(t/4)%len(emojis); et=t%4
        if et<2:
            ea=int(255*min(1,et*2)); ey=int(VH*0.38-et*55); ex=int(VW*(0.12+(ec%3)*0.37))
            try: d.text((ex,ey), emojis[ec], font=fnt('NotoEmoji-Bold.ttf',85), fill=WHITE+(ea,))
            except: pass
    bi.paste(ov,(0,0),ov); return np.array(bi)

def make_intro(hook1, hook2, accent):
    def f(t):
        p=min(1,t/3.0); img=Image.new('RGBA',(VW,VH),DARK+(255,)); d=ImageDraw.Draw(img)
        import random; random.seed(int(t*30))
        for _ in range(50):
            rx,ry=random.randint(0,VW),random.randint(0,VH); r=random.randint(3,10)
            al=int(25+25*math.sin(p*math.pi*2+random.random()*5))
            d.ellipse([rx-r,ry-r,rx+r,ry+r], fill=accent+(al,))
        d.rectangle([0,0,8,int(VH*p)], fill=accent+(200,))
        d.rectangle([VW-8,VH-int(VH*p),VW,VH], fill=GOLD+(200,))
        sl=int((1-min(1,p*2))*70)
        d.rounded_rectangle([60,VH//2-170,VW-60,VH//2+110], radius=28, fill=(0,0,0,int(180*min(1,p*3))))
        ct(d, hook1, VH//2-145+sl, fnt('BigShoulders-Bold.ttf',88), accent)
        ct(d, hook2, VH//2-38+sl,  fnt('BigShoulders-Bold.ttf',66), CREAM)
        ct(d,'@VeroResina • @RPResina • @PXResina', VH-55, fnt('InstrumentSans-Bold.ttf',32), TEAL)
        return np.array(img.convert('RGB'))
    return VideoClip(frame_function=f, duration=3.0)

def make_cta(accent):
    def f(t):
        p=min(1,t/5.0); img=Image.new('RGBA',(VW,VH),DARK+(255,)); d=ImageDraw.Draw(img)
        for ci in range(5):
            ang=p*math.pi*2+ci*1.2; cx=VW//2+int(math.cos(ang)*VW*0.38); cy=VH//2+int(math.sin(ang)*VH*0.22)
            r=int(VW*0.18+math.sin(p*math.pi*3+ci)*25); d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=accent+(28,))
        d.rectangle([0,0,VW,8], fill=accent+(180,)); d.rectangle([0,VH-8,VW,VH], fill=GOLD+(180,))
        ct(d,'¿LISTA PARA EMPEZAR?',  VH//2-340, fnt('BigShoulders-Bold.ttf',82), GOLD)
        ct(d,'Curso de Resina Epóxica',VH//2-240, fnt('InstrumentSans-Bold.ttf',48), CREAM)
        sep=(VW-400)//2; d.rectangle([sep,VH//2-185,sep+400,VH//2-182], fill=TEAL+(200,))
        for bi2,ben in enumerate(['✅ Desde cero, a tu ritmo','✅ Con certificado','✅ Comunidad de apoyo']):
            ct(d, ben, VH//2-160+bi2*72, fnt('InstrumentSans-Regular.ttf',40), CREAM)
        pulse=1+0.07*math.sin(p*math.pi*8); bw2,bh2=int(820*pulse),int(112*pulse)
        bx2=(VW-bw2)//2; by2=VH//2+88
        d.rounded_rectangle([bx2,by2,bx2+bw2,by2+bh2], radius=32, fill=GOLD+(245,))
        ct(d,'👉  QUIERO EL CURSO', by2+24, fnt('InstrumentSans-Bold.ttf',48), DARK, st=0)
        ct(d,'go.hotmart.com/G106175870D', by2+132, fnt('DMMono-Regular.ttf',30), TEAL)
        ct(d,'VeroResina', VH-90, fnt('Italiana-Regular.ttf',46), GOLD)
        return np.array(img.convert('RGB'))
    return VideoClip(frame_function=f, duration=5.0)

CONFIGS = [
    {
        "scaled": "/tmp/voz_tmp/v1_scaled.mp4",
        "nombre": "Video1_Tecnica",
        "hook1": "¿SABES HACER ESTO?",
        "hook2": "con resina epóxica",
        "tts": "Sabes hacer esto con resina epóxica. La resina te permite crear piezas únicas que se venden muy bien. Solo necesitas los materiales correctos y la técnica adecuada. Mezcla en proporción exacta, agrega tus pigmentos y el resultado habla por sí solo. Y tú puedes aprenderlo desde casa. Entra al curso completo en Hotmart y empieza hoy.",
        "words": "¿Sabes hacer esto con resina epóxica? La resina te permite crear piezas únicas que se venden muy bien. Solo necesitas los materiales correctos y la técnica. Mezcla en proporción exacta agrega tus pigmentos y el resultado habla por sí solo. Aprenderlo desde casa es posible con el curso".split(),
        "accent": TEAL, "emojis": ["✨","🎨","💎","🔥","⭐"],
    },
    {
        "scaled": "/tmp/voz_tmp/v2_scaled.mp4",
        "nombre": "Video2_Proceso",
        "hook1": "ASÍ SE HACE",
        "hook2": "una pieza de resina",
        "tts": "Quieres saber cómo se hace una pieza de resina epóxica. El proceso paso a paso es más fácil de lo que crees. Primero prepara tu molde y tus pigmentos favoritos. Mezcla la resina con cuidado sin burbujas. Agrega tus colores y crea diseños únicos. Espera veinticuatro horas, desmolda y listo. Tu primera creación. Aprende todo esto en el curso de Vero Resina.",
        "words": "Así se hace una pieza de resina epóxica. El proceso paso a paso es más fácil de lo que crees. Prepara tu molde y pigmentos favoritos. Mezcla la resina sin burbujas. Agrega colores y crea diseños únicos. Desmolda y listo tu primera creación. Aprende en el curso de VeroResina".split(),
        "accent": PINK, "emojis": ["💡","🧪","✨","🌈","💎"],
    },
    {
        "scaled": "/tmp/voz_tmp/v3_scaled.mp4",
        "nombre": "Video3_Resultado",
        "hook1": "MIRA ESTE RESULTADO",
        "hook2": "¿lo puedes creer?",
        "tts": "Mira este resultado. ¿Puedes creerlo? Piezas así se venden de quinientos a cinco mil pesos mexicanos, y se hacen en menos de dos horas de trabajo. Las clientas las buscan en Instagram y en Facebook todos los días. Tú puedes tener tu propio negocio desde casa. Aprende las técnicas profesionales en el curso de resina epóxica. Disponible ahora en Hotmart.",
        "words": "Mira este resultado. ¿Puedes creerlo? Piezas así se venden de $500 a $5,000 pesos. Se hacen en menos de 2 horas. Las clientas las buscan en redes todos los días. Tú puedes tener tu negocio desde casa. Aprende técnicas profesionales ahora en Hotmart".split(),
        "accent": GOLD, "emojis": ["🤑","💰","🛍️","⭐","🏆"],
    },
    {
        "scaled": "/tmp/voz_tmp/v4_scaled.mp4",
        "nombre": "Video4_Inspiracion",
        "hook1": "¿QUIERES HACER ESTO?",
        "hook2": "¡YO TE ENSEÑO!",
        "tts": "Quieres hacer esto. Yo te enseño. Yo empecé sin saber absolutamente nada sobre resina epóxica. En pocas semanas ya tenía mis primeras ventas. La resina cambió mi vida: trabajo desde casa, a mi ritmo, sin jefe. Tú también puedes lograrlo. No necesitas experiencia previa ni mucho dinero para empezar. Entra hoy al curso y transforma tu vida.",
        "words": "¿Quieres hacer esto? Yo te enseño. Empecé sin saber absolutamente nada. En pocas semanas tenía mis primeras ventas. La resina cambió mi vida trabajo desde casa a mi ritmo sin jefe. Tú también puedes lograrlo. Entra hoy al curso y transforma tu vida".split(),
        "accent": PURPLE, "emojis": ["💜","🌟","🏠","💪","🎯"],
    },
]

def procesar(cfg):
    nombre = cfg["nombre"]
    print(f"\n🎬 {nombre}")

    clip = VideoFileClip(cfg["scaled"])
    dur  = clip.duration
    print(f"   Cargado: {clip.size} {dur:.1f}s")

    # TTS
    print("   🎙️ Voz...")
    voz_wav = f"{TMP}/{nombre}.wav"
    subprocess.run(['espeak-ng','-v','es-419','-s','135','-p','58','-a','200',
                    cfg["tts"], '-w', voz_wav], check=True, capture_output=True)
    voz_clip = AudioFileClip(voz_wav)
    voz_dur  = voz_clip.duration

    # Si la voz dura más que el video, loop el video
    if voz_dur > dur:
        loops = math.ceil(voz_dur / dur)
        clip  = concatenate_videoclips([clip]*loops).subclipped(0, voz_dur)
        dur   = clip.duration

    # Video con overlay
    print("   💬 Subtítulos...")
    words  = cfg["words"]
    accent = cfg["accent"]
    emojis = cfg["emojis"]
    ov = VideoClip(
        frame_function=lambda t: ov_frame(t, clip, dur, words, accent, emojis),
        duration=dur
    )

    # Intro + video + CTA
    print("   🎬 Ensamblando...")
    intro = make_intro(cfg["hook1"], cfg["hook2"], accent)
    cta   = make_cta(accent)
    final_v = concatenate_videoclips([intro, ov, cta])

    # Audio
    print("   🎵 Mezclando audio...")
    music   = gen_music(final_v.duration).with_duration(final_v.duration)
    voz_arr = voz_clip.to_soundarray(fps=SR).astype(np.float32) * 1.5
    if voz_arr.ndim == 1:
        voz_arr = np.stack([voz_arr, voz_arr], axis=1)
    total_s = int(final_v.duration * SR)
    vp = np.zeros((total_s, 2), dtype=np.float32)
    vs = int(3*SR); ve = min(vs+len(voz_arr), total_s)
    vp[vs:ve] = voz_arr[:ve-vs]
    vt = AudioArrayClip(vp, fps=SR).with_duration(final_v.duration)
    audio_f = CompositeAudioClip([music, vt]).with_duration(final_v.duration)
    final_v = final_v.with_audio(audio_f)

    # Exportar
    out = f"{OUT}/{nombre}_FINAL.mp4"
    print(f"   📤 Exportando...")
    final_v.write_videofile(out, fps=FPS, codec='libx264',
                            audio_codec='aac', preset='fast', logger=None)
    final_v.close(); clip.close(); voz_clip.close()
    print(f"   ✅ Listo: {out}")
    return out

print("🚀 Generando 4 videos FINALES...\n")
resultados = []
for cfg in CONFIGS:
    try:
        resultados.append(procesar(cfg))
    except Exception as e:
        print(f"   ❌ {cfg['nombre']}: {e}")
        import traceback; traceback.print_exc()

print(f"\n🎉 {len(resultados)}/4 videos listos en {OUT}/")
