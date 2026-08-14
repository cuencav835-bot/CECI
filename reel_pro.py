#!/usr/bin/env python3
"""
REEL PRO - Resina Epóxica   ·   @VeroResina
Arte generativo ultra-realista + cinemático
"""
import os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import imageio_ffmpeg

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
from moviepy import VideoClip, AudioArrayClip, AudioFileClip, CompositeAudioClip

OUT = "/home/user/CECI/videos_reales"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
FPS  = 30
SR   = 44100

# ── PALETAS ───────────────────────────────────────────────────────────────────
PALETTES = [
    [(0,18,30),(0,140,160),(20,220,200),(255,200,40),(255,255,255)],   # OCEAN
    [(15,5,30),(120,40,180),(200,80,220),(255,160,60),(255,230,180)],  # PURPLE-GOLD
    [(30,10,5),(180,60,20),(220,120,40),(255,200,80),(255,240,200)],   # COPPER
    [(5,20,10),(20,140,80),(40,200,120),(180,240,100),(240,255,200)],  # EMERALD
    [(20,5,5),(160,20,40),(220,60,80),(255,120,60),(255,220,180)],     # RUBY
    [(5,5,30),(30,50,160),(60,100,220),(120,200,255),(220,240,255)],   # SAPPHIRE
]

FONT_DIR = "/root/.claude/skills/canvas-design/canvas-fonts"
def F(size, bold=True):
    names = (["Montserrat-ExtraBold.ttf","BebasNeue-Regular.ttf",
               "Oswald-Bold.ttf","Anton-Regular.ttf"] if bold else
              ["Montserrat-Regular.ttf","Oswald-Regular.ttf"])
    for n in names:
        p = os.path.join(FONT_DIR, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ════════════════════════════════════════════════════════════════════════════════
# GENERADOR DE ARTE RESINA (marbling procedural)
# ════════════════════════════════════════════════════════════════════════════════
def sinusoidal_marble(img_arr, ax=0.12, ay=0.08, bx=0.07, by=0.15, phase=0):
    """Deformación marmoleada usando funciones seno apiladas."""
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    # 3 capas de ondas
    d  = np.sin(ax*X + ay*Y + phase)
    d += 0.5*np.sin(bx*X - by*Y + phase*1.3)
    d += 0.25*np.sin(0.05*X + 0.1*Y + phase*0.7)
    d  = (d + 1.75) / 3.5   # normalizar 0-1
    return d

def resin_frame(t, palette_idx, pour_t=None):
    """Genera un frame de arte en resina."""
    pal = PALETTES[palette_idx % len(PALETTES)]
    bg, c1, c2, c3, hi = [np.array(c, np.float32) for c in pal]

    # Marmoleado animado
    phase   = t * 0.25
    d       = sinusoidal_marble(None, 0.11, 0.09, 0.06, 0.14, phase)
    d2      = sinusoidal_marble(None, 0.04, 0.12, 0.09, 0.05, phase+1.5)

    # Mezclar capas
    c_arr = np.zeros((H, W, 3), np.float32)
    m1  = d[..., None]
    m2  = d2[..., None]
    blend = m1 * m2

    c_arr  = bg * (1-m1)    + c1 * m1
    c_arr  = c_arr*(1-m2*0.6) + c2 * (m2*0.6)
    c_arr  = c_arr*(1-blend*0.5) + c3*(blend*0.5)

    # Highlights (venas brillantes)
    veins  = np.abs(np.sin(d*8 + phase*0.5))
    vein_m = (veins > 0.85).astype(np.float32)[..., None]
    c_arr  = c_arr*(1-vein_m*0.7) + hi*vein_m*0.7

    # Brillo central
    cx, cy = W//2, H//2
    Y, X  = np.mgrid[0:H, 0:W]
    dist  = np.sqrt(((X-cx)/W)**2 + ((Y-cy)/H)**2)
    glow  = np.exp(-dist*3)*0.25
    c_arr[:,:,0] = np.clip(c_arr[:,:,0] + hi[0]*glow, 0, 255)
    c_arr[:,:,1] = np.clip(c_arr[:,:,1] + hi[1]*glow, 0, 255)
    c_arr[:,:,2] = np.clip(c_arr[:,:,2] + hi[2]*glow, 0, 255)

    img = Image.fromarray(np.clip(c_arr,0,255).astype(np.uint8))

    # Vignette
    vig = Image.new("RGBA",(W,H),(0,0,0,0))
    vd  = ImageDraw.Draw(vig)
    for r in range(400,0,-8):
        a = int(160*(1-r/400)**2.5)
        vd.ellipse([W//2-r*1.4,H//2-r, W//2+r*1.4,H//2+r],fill=(0,0,0,a))
    img = Image.alpha_composite(img.convert("RGBA"),vig).convert("RGB")

    # Película grain
    grain = (np.random.randn(H,W,3)*6).astype(np.int16)
    arr   = np.clip(np.array(img).astype(np.int16)+grain,0,255).astype(np.uint8)
    return Image.fromarray(arr)

def add_bokeh_bubbles(img, t, pal_idx):
    """Círculos de bokeh flotantes como gotas de resina."""
    pal  = PALETTES[pal_idx % len(PALETTES)]
    ov   = Image.new("RGBA",(W,H),(0,0,0,0))
    rng2 = random.Random(pal_idx*100)
    for i in range(18):
        cx = rng2.randint(60,W-60)
        cy = rng2.randint(60,H-60)
        r  = rng2.randint(25,90)
        vx = rng2.uniform(-8,8)
        vy = rng2.uniform(-15,-3)
        c  = rng2.choice(pal[1:])
        x  = int((cx + vx*t) % W)
        y  = int((cy + vy*t) % H)
        a  = int(40 + 25*math.sin(t*1.2+i))
        # Dibujar bokeh difuso
        tmp = Image.new("RGBA",(r*2+4,r*2+4),(0,0,0,0))
        td  = ImageDraw.Draw(tmp)
        for rr in range(r,0,-2):
            aa = int(a*(rr/r))
            td.ellipse([r-rr,r-rr,r+rr,r+rr],fill=(*c,aa))
        blurred = tmp.filter(ImageFilter.GaussianBlur(r//3))
        xx = x-r-2; yy = y-r-2
        ov.paste(blurred,(xx,yy),blurred)
    img = Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
    return img

# ════════════════════════════════════════════════════════════════════════════════
# OVERLAYS DE TEXTO
# ════════════════════════════════════════════════════════════════════════════════
def lerp(a,b,t): return a + (b-a)*t
def ease(t): return t*t*(3-2*t)

def text_block(img, title, sub, accent, t_local, dur, kar_word=None):
    img  = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    fi    = min(1.0, t_local/0.4)
    fo    = 1.0 if t_local < dur-0.45 else max(0.0,(dur-t_local)/0.45)
    alpha = ease(fi)*fo

    f_title = F(108, bold=True)
    f_sub   = F(50,  bold=False)
    f_tiny  = F(32,  bold=False)
    f_kar   = F(76,  bold=True)

    # Gradiente oscuro en zona de texto (abajo)
    grad = Image.new("RGBA",(W,600),(0,0,0,0))
    gd   = ImageDraw.Draw(grad)
    for yy in range(600):
        a = int(220*(yy/600)*alpha)
        gd.rectangle([0,yy,W,yy+1],fill=(0,0,0,a))
    img.paste(grad,(0,H-600),grad)

    # Barra superior
    top = Image.new("RGBA",(W,72),(*accent,int(200*alpha)))
    img.paste(top,(0,0),top)
    draw = ImageDraw.Draw(img)
    draw.text((20,16),"🎨 @VeroResina  ·  Resina Epóxica PRO",
              font=f_tiny, fill=(0,0,0,200))

    # Letterbox
    img  = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    for yy in [0, H-52]:
        draw.rectangle([0,yy,W,yy+52],fill=(0,0,0))

    # Título
    lines = title.split("\n")
    y0    = H - 320 - len(lines)*116
    for line in lines:
        bb = draw.textbbox((0,0),line,font=f_title)
        tw,th = bb[2]-bb[0], bb[3]-bb[1]
        x  = (W-tw)//2
        # Sombra difusa
        shadow = Image.new("RGBA",(W,H),(0,0,0,0))
        sd     = ImageDraw.Draw(shadow)
        for dx in range(-4,5):
            for dy in range(-4,5):
                sd.text((x+dx,y0+dy),line,font=f_title,
                        fill=(0,0,0,int(60*alpha)))
        img = Image.alpha_composite(img.convert("RGBA"),shadow).convert("RGB")
        draw = ImageDraw.Draw(img)
        # Texto
        a_int = int(255*alpha)
        draw.text((x,y0),line,font=f_title,fill=(*accent,a_int))
        y0 += th+12

    # Subtítulo
    bb2 = draw.textbbox((0,0),sub,font=f_sub)
    tw2 = bb2[2]-bb2[0]
    draw.text(((W-tw2)//2+2,y0+6),sub,font=f_sub,
              fill=(0,0,0,int(160*alpha)))
    draw.text(((W-tw2)//2,y0+4),sub,font=f_sub,
              fill=(255,255,255,int(220*alpha)))

    # Karaoke
    if kar_word:
        ov2 = Image.new("RGBA",(W,H),(0,0,0,0))
        od2 = ImageDraw.Draw(ov2)
        bb3 = od2.textbbox((0,0),kar_word,font=f_kar)
        tw3,th3 = bb3[2]-bb3[0], bb3[3]-bb3[1]
        ky  = H-270
        od2.rounded_rectangle(
            [(W-tw3)//2-22, ky-10, (W+tw3)//2+22, ky+th3+10],
            radius=14, fill=(255,210,0,int(235*alpha))
        )
        img = Image.alpha_composite(img.convert("RGBA"),ov2).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.text(((W-tw3)//2,ky),kar_word,font=f_kar,fill=(0,0,0))

    return img

def cta_overlay(img, t, accent=(220,40,60)):
    f_cta  = F(58, bold=True)
    f_url  = F(30, bold=False)
    pulse  = 1+0.05*math.sin(t*3.5)
    bw,bh  = int(720*pulse), 96
    bx,by  = (W-bw)//2, H-230
    ov     = Image.new("RGBA",(W,H),(0,0,0,0))
    od     = ImageDraw.Draw(ov)
    od.rounded_rectangle([bx,by,bx+bw,by+bh],radius=36,fill=(*accent,240))
    img    = Image.alpha_composite(img.convert("RGBA"),ov).convert("RGB")
    draw   = ImageDraw.Draw(img)
    ct     = "🔥  INSCRÍBETE AHORA  →  HOTMART"
    bb     = draw.textbbox((0,0),ct,font=f_cta)
    tx     = (W-(bb[2]-bb[0]))//2
    ty     = by+(bh-(bb[3]-bb[1]))//2
    draw.text((tx,ty),ct,font=f_cta,fill=(255,255,255))
    url_t  = "go.hotmart.com/G106175870D?ap=8534"
    draw.text(((W-draw.textbbox((0,0),url_t,font=f_url)[2])//2,by+bh+14),
              url_t, font=f_url, fill=(255,200,40))
    return img

def progress_bar(img, t, total):
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,H-14,W,H],fill=(20,20,20))
    draw.rectangle([0,H-14,int(W*t/total),H],fill=(255,200,40))
    return img

# ════════════════════════════════════════════════════════════════════════════════
# MÚSICA 110 BPM
# ════════════════════════════════════════════════════════════════════════════════
def gen_music(dur):
    t   = np.linspace(0,dur,int(SR*dur),endpoint=False)
    bt  = 60/110
    def note(f,s,d,a=0.11):
        s0,e0 = int(s*SR), min(int((s+d)*SR),len(t))
        sg = np.sin(2*np.pi*f*t[s0:e0])*a
        fa = min(int(0.04*SR),len(sg)//4)
        if fa>0: sg[:fa]*=np.linspace(0,1,fa); sg[-fa:]*=np.linspace(1,0,fa)
        return s0,e0,sg
    aud = np.zeros(len(t))
    prog= [(220,.85),(174.6,.85),(261.6,.85),(196.,.85)]
    for bar in range(int(dur/(bt*4))+2):
        for bi,(f,r) in enumerate(prog):
            st=(bar*4+bi)*bt
            if st>=dur: break
            s,e,sg=note(f,st,bt*r); aud[s:e]+=sg
            s,e,sg=note(f*1.498,st,bt*r*.7,.04); aud[s:e]+=sg
    for i in range(int(dur/bt)+2):
        s=int(i*bt*SR)
        kl=min(int(.12*SR),len(aud)-s)
        if kl>0:
            env=np.exp(-np.linspace(0,9,kl))
            aud[s:s+kl]+=np.sin(2*np.pi*np.linspace(85,40,kl))*env*.3
        if i%2==1:
            sl=min(int(.07*SR),len(aud)-s)
            if sl>0:
                aud[s:s+sl]+=np.random.randn(sl)*.12*np.exp(-np.linspace(0,20,sl))
    for i in range(int(dur/bt)*2+2):
        s=int(i*bt*SR/2)
        hl=min(int(.022*SR),len(aud)-s)
        if hl>0:
            aud[s:s+hl]+=np.random.randn(hl)*.038*np.exp(-np.linspace(0,18,hl))
    bass=[110,87.3,130.8,98]
    for bar in range(int(dur/(bt*4))+2):
        for bi,bf in enumerate(bass):
            st=(bar*4+bi)*bt
            if st>=dur: break
            s,e,sg=note(bf,st,bt*.8,.20); aud[s:e]+=sg
    fi=min(int(.8*SR),len(aud)//4); fo=min(int(2*SR),len(aud)//4)
    aud[:fi]*=np.linspace(0,1,fi); aud[-fo:]*=np.linspace(1,0,fo)
    return np.clip(aud,-1,1)

# ════════════════════════════════════════════════════════════════════════════════
# TTS  (espeak con pitchmod para más naturalidad)
# ════════════════════════════════════════════════════════════════════════════════
def gen_tts(text, path, speed=125, pitch=48):
    try:
        subprocess.run(["espeak-ng","-v","es-419",
                        f"-s{speed}",f"-p{pitch}","-a200",
                        text,"-w",path],
                       check=True,capture_output=True)
        return os.path.exists(path) and os.path.getsize(path)>500
    except: return False

# ════════════════════════════════════════════════════════════════════════════════
# ESCENAS
# ════════════════════════════════════════════════════════════════════════════════
SCENES = [
    # (dur, palette, title, sub, accent_rgb, karaoke_words, narr)
    dict(dur=10, pal=0,
         title="¿QUIERES\nGANAR DINERO\nDESDÉ CASA?",
         sub="Sigue viendo... 👇",
         accent=(0,210,190),
         kwords=[("¿QUIERES",0.4),("GANAR",1.0),("DINERO",1.6),("DESDE CASA?",2.3),
                 ("MIRA ESTO",3.2),("👇",4.0)],
         narr="¿Sabías que puedes ganar dinero desde casa haciendo arte con resina epóxica?"),
    dict(dur=11, pal=1,
         title="RESINA\nEPÓXICA\nES UN NEGOCIO",
         sub="Rentable y creativo 🎨",
         accent=(200,80,220),
         kwords=[("RESINA",0.3),("EPÓXICA",1.0),("UN NEGOCIO",1.7),
                 ("REAL",2.5),("RENTABLE",3.3),("💰",4.1)],
         narr="La resina epóxica es uno de los materiales más versátiles y rentables del mercado artesanal."),
    dict(dur=10, pal=2,
         title="CHAROLAS\n$50 – $200",
         sub="Las más vendidas en redes ✨",
         accent=(255,180,40),
         kwords=[("CHAROLAS",0.3),("$50",1.1),("HASTA",1.7),("$200",2.2),
                 ("¡SE VENDEN!",3.0),("✨",3.8)],
         narr="Con ella puedes hacer charolas que se venden entre cincuenta y doscientos dólares."),
    dict(dur=10, pal=3,
         title="CUADROS\nHASTA $500",
         sub="Arte único que pagan muy bien 💎",
         accent=(40,200,120),
         kwords=[("CUADROS",0.3),("ÚNICOS",1.0),("$100",1.7),("A $500",2.3),
                 ("¡ARTE!",3.1),("💎",3.8)],
         narr="Puedes hacer cuadros de arte que se venden entre cien y quinientos dólares."),
    dict(dur=10, pal=4,
         title="JOYERÍA\n$20 – $80\nPOR PIEZA",
         sub="Fácil de hacer, fácil de vender 💍",
         accent=(220,80,100),
         kwords=[("JOYERÍA",0.3),("ARTESANAL",1.0),("$20",1.8),("A $80",2.4),
                 ("POR PIEZA",3.0),("💍",3.8)],
         narr="Joyería artesanal entre veinte y ochenta dólares por pieza."),
    dict(dur=11, pal=5,
         title="+2,000\nALUMNAS\nYA LO LOGRARON",
         sub="¿Vas a ser la siguiente? 🏆",
         accent=(80,140,255),
         kwords=[("+2,000",0.4),("ALUMNAS",1.1),("REALES",1.8),
                 ("GANANDO",2.5),("TODOS LOS MESES",3.2),("🏆",4.1)],
         narr="Más de dos mil alumnas ya transformaron su vida. Ganan entre quinientos y tres mil dólares al mes."),
    dict(dur=13, pal=0,
         title="¡INSCRÍBETE\nAHORA!",
         sub="Link en la descripción ↓ 🔥",
         accent=(220,40,60),
         kwords=[("¡INSCRÍBETE",0.3),("HOY",1.0),("LINK",1.8),
                 ("ABAJO",2.5),("👆",3.2),("¡VAMOS!",4.0)],
         narr="Inscríbete hoy. El link está abajo. ¡No te lo pierdas!"),
]
TOTAL_DUR = sum(s["dur"] for s in SCENES)

# ════════════════════════════════════════════════════════════════════════════════
# RENDER
# ════════════════════════════════════════════════════════════════════════════════
def get_scene_and_local(t_global):
    acc = 0.0
    for sc in SCENES:
        if t_global < acc + sc["dur"]:
            return sc, t_global - acc
        acc += sc["dur"]
    return SCENES[-1], t_global - (TOTAL_DUR - SCENES[-1]["dur"])

def get_kword(sc, t_local):
    for word, wt in sc["kwords"]:
        if wt <= t_local < wt + 0.58:
            return word
    return None

def make_frame(t):
    sc, tl = get_scene_and_local(t)
    dur    = sc["dur"]

    base   = resin_frame(t, sc["pal"])
    base   = add_bokeh_bubbles(base, t, sc["pal"])

    is_cta = sc["title"].startswith("¡INSCR")
    if is_cta:
        img = text_block(base, sc["title"], sc["sub"], sc["accent"], tl, dur)
        img = cta_overlay(img, t, sc["accent"])
    else:
        img = text_block(base, sc["title"], sc["sub"], sc["accent"],
                         tl, dur, get_kword(sc, tl))

    img = progress_bar(img, t, TOTAL_DUR)
    return np.array(img)

# ════════════════════════════════════════════════════════════════════════════════
# AUDIO
# ════════════════════════════════════════════════════════════════════════════════
NARR_FULL = (
    "¿Sabías que puedes ganar dinero desde casa haciendo arte con resina epóxica? "
    "La resina es uno de los materiales más versátiles y rentables del mercado artesanal. "
    "Con ella puedes hacer charolas que se venden entre cincuenta y doscientos dólares. "
    "Cuadros de arte entre cien y quinientos. "
    "Joyería artesanal entre veinte y ochenta dólares por pieza. "
    "Más de dos mil alumnas ya transformaron su vida. "
    "Ganan entre quinientos y tres mil dólares al mes, trabajando solo dos horas al día. "
    "Inscríbete hoy en mi curso. "
    "El link está abajo."
)

def build_audio():
    music   = gen_music(TOTAL_DUR)
    voz_ok  = gen_tts(NARR_FULL, "/tmp/reel_pro_voz.wav")
    clips   = [AudioArrayClip(np.column_stack([music*.35,music*.35]),fps=SR).with_duration(TOTAL_DUR)]
    if voz_ok:
        vc  = AudioFileClip("/tmp/reel_pro_voz.wav")
        va  = vc.to_soundarray(fps=SR)
        if va.ndim == 1: va = np.column_stack([va,va])
        va  = va * 1.6
        vd  = min(va.shape[0]/SR, TOTAL_DUR-.5)
        clips.append(AudioArrayClip(va,fps=SR).with_duration(vd))
        print("  ✅ Narración añadida")
    return CompositeAudioClip(clips).with_duration(TOTAL_DUR)

# ════════════════════════════════════════════════════════════════════════════════
# MAIN — genera 2 videos (mismo contenido, paletas distintas para variar)
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    total = TOTAL_DUR
    print(f"🎬 Generando Reel PRO ({total:.0f}s) ...")
    audio = build_audio()
    video = VideoClip(make_frame, duration=total).with_fps(FPS).with_audio(audio)
    out   = os.path.join(OUT,"ReelPRO_VeroResina.mp4")
    video.write_videofile(out,fps=FPS,codec="libx264",audio_codec="aac",
                          ffmpeg_params=["-crf","20","-preset","fast",
                                         "-pix_fmt","yuv420p"],logger="bar")
    sz = os.path.getsize(out)/1e6
    print(f"\n✅  {out}  ({sz:.1f} MB)")
