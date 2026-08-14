#!/usr/bin/env python3
"""
REEL CINEMATOGRÁFICO CON IMÁGENES AI + VOZ NATURAL
Ejecuta este script en tu computadora para crear el reel final.

REQUISITOS:
  pip install moviepy pillow numpy requests

INSTRUCCIONES:
  1. Ejecuta: python3 crear_reel_cinematico.py
  2. Espera ~3-5 minutos
  3. El video quedará en: reel_final/ReelCinematico_VeroResina.mp4
"""

import os, math, requests, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from moviepy import (VideoClip, AudioFileClip, ImageClip,
                     concatenate_videoclips, CompositeVideoClip,
                     AudioArrayClip, CompositeAudioClip)

OUT_DIR = Path("reel_final")
OUT_DIR.mkdir(exist_ok=True)
TMP = Path("reel_tmp")
TMP.mkdir(exist_ok=True)

W, H = 1080, 1920
FPS  = 30
SR   = 44100

# ─────────────────────────────────────────────────────────
# ASSETS DE MAGNIFIC AI (válidos 24h)
# Si los links expiran, vuelve a ejecutar reel_actualizar_links.py
# ─────────────────────────────────────────────────────────
AUDIO_URL = (
    "https://pikaso.cdnpk.net/private/production/5169378914/audio.mp3"
    "?token=exp=1786924800~hmac=853cf28013a5cae7a5a67217984a659dbfaa0f4de91c51f9ba8d6bc3b6ae1516"
)

IMAGES = [
    {
        "name": "01_manos_resina",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169380262/render.jpg"
            "?token=exp=1786924800~hmac=fec568687023420d14ae840539424305c6f0c91528b9a9b6591cddfb4cc75638"
        ),
        "caption": "¿QUIERES GANAR\nDINERO DESDE CASA? 🔥",
        "sub": "Con resina epóxica puedes",
        "accent": (0, 210, 190),   # teal
        "duration": 11,
    },
    {
        "name": "02_charola_ocean",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169381219/render.jpg"
            "?token=exp=1786924800~hmac=553b0437b101f8c5c833de976de990f29e2c1c8727b45a578e9e4e381350d305"
        ),
        "caption": "CHAROLAS\nDESDE $50",
        "sub": "Las más vendidas en redes 💰",
        "accent": (255, 200, 40),   # gold
        "duration": 10,
    },
    {
        "name": "03_arte_marmol",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169382785/render.jpg"
            "?token=exp=1786924800~hmac=d818c5dbbc7c5a45c8532f0adc48eaa3174ab1a876f098ed13d8aa9ca050f194"
        ),
        "caption": "CUADROS\nHASTA $500",
        "sub": "Arte único que se vende solo ✨",
        "accent": (180, 80, 220),   # purple
        "duration": 10,
    },
    {
        "name": "04_mujer_exitosa",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169383558/render.jpg"
            "?token=exp=1786924800~hmac=b8e1a0dbbfd15a1beb3ab9f8b7b6371a331bc68002dcdbf12d2516fe27dcf42f"
        ),
        "caption": "JOYERÍA\nARTESANAL",
        "sub": "$20-$80 por pieza 💎",
        "accent": (255, 80, 140),   # pink
        "duration": 10,
    },
    {
        "name": "05_materiales",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169384718/render.jpg"
            "?token=exp=1786924800~hmac=f5c59a33127790d42a47173fd3109b9b20f884cd77323b356d48e41a3714bf50"
        ),
        "caption": "+2,000\nALUMNAS",
        "sub": "Ya transformaron su vida 🏆",
        "accent": (40, 210, 100),   # green
        "duration": 11,
    },
    {
        "name": "06_dinero_celular",
        "url": (
            "https://pikaso.cdnpk.net/private/production/5169386280/render.jpg"
            "?token=exp=1786924800~hmac=0a93776280c1feefca07f0b94a35835324fac88bb2aa64bfcc52a81bc6b7e5d9"
        ),
        "caption": "¡INSCRÍBETE\nAHORA! 🚀",
        "sub": "Link en la descripción ↓",
        "accent": (220, 40, 60),    # red
        "duration": 13,
    },
]

# ─────────────────────────────────────────────────────────
# TIPOGRAFÍA  (ajusta la ruta según tu OS)
# ─────────────────────────────────────────────────────────
def find_font(size, bold=True):
    candidates = []
    if sys.platform == "darwin":
        base = "/Library/Fonts"
        candidates = [
            f"{base}/Helvetica Neue Bold.ttf",
            f"{base}/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    elif sys.platform.startswith("linux"):
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:  # Windows
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ─────────────────────────────────────────────────────────
# DESCARGA DE ASSETS
# ─────────────────────────────────────────────────────────
def download(url, path):
    print(f"  ⬇  Descargando {path.name}...")
    r = requests.get(url, timeout=30, stream=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    print(f"     ✅ {path.stat().st_size//1024} KB")

# ─────────────────────────────────────────────────────────
# PROCESADO DE IMAGEN  (9:16 crop + color grading)
# ─────────────────────────────────────────────────────────
def prep_image(img: Image.Image) -> Image.Image:
    """Crop center a 9:16 y aplica color grading cinematográfico."""
    iw, ih = img.size
    target_ratio = W / H
    img_ratio = iw / ih
    if img_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        x = (iw - new_w) // 2
        img = img.crop((x, 0, x + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        y = (ih - new_h) // 2
        img = img.crop((0, y, iw, y + new_h))
    img = img.resize((W, H), Image.LANCZOS)

    # Teal-Orange color grading (cinematográfico)
    arr = np.array(img).astype(np.float32)
    # Realzar shadows (teal) y highlights (orange/warm)
    lum = 0.2126*arr[:,:,0] + 0.7152*arr[:,:,1] + 0.0722*arr[:,:,2]
    mask_shadow = np.clip(1 - lum/255, 0, 1)[:,:,np.newaxis]
    mask_hi     = np.clip(lum/255, 0, 1)[:,:,np.newaxis]
    arr[:,:,0] += mask_hi[:,:,0]    * 8   # +red en highlights
    arr[:,:,2] += mask_shadow[:,:,0]* 12  # +blue en shadows
    arr[:,:,1] += mask_shadow[:,:,0]* 8   # +green en shadows
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    # Vignette
    img = Image.fromarray(arr)
    vig  = Image.new("RGBA", (W,H), (0,0,0,0))
    vd   = ImageDraw.Draw(vig)
    for r in range(350, 0, -10):
        alpha = int(130 * (1 - r/350)**2)
        vd.ellipse([W//2-r*1.3, H//2-r, W//2+r*1.3, H//2+r],
                   fill=(0,0,0,alpha))
    img  = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")

    # Ligero grano de película
    grain = (np.random.randn(H,W,3)*5).astype(np.int16)
    arr2  = np.clip(np.array(img).astype(np.int16) + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr2)

# ─────────────────────────────────────────────────────────
# KEN BURNS  (pan + zoom lento)
# ─────────────────────────────────────────────────────────
def ken_burns(img: Image.Image, t: float, dur: float,
              zoom_start=1.0, zoom_end=1.08,
              pan_x=0.0, pan_y=-0.03) -> np.ndarray:
    prog  = t / dur
    zoom  = zoom_start + (zoom_end - zoom_start) * prog
    iw,ih = int(W*zoom), int(H*zoom)
    frame = img.resize((iw, ih), Image.BILINEAR)
    ox    = int((iw - W) * (0.5 + pan_x * prog))
    oy    = int((ih - H) * (0.5 + pan_y * prog))
    ox    = max(0, min(ox, iw - W))
    oy    = max(0, min(oy, ih - H))
    return np.array(frame.crop((ox, oy, ox+W, oy+H)))

# ─────────────────────────────────────────────────────────
# OVERLAY DE TEXTO CINEMATOGRÁFICO
# ─────────────────────────────────────────────────────────
def text_overlay(base_arr: np.ndarray, t: float, dur: float,
                 caption: str, sub: str, accent: tuple) -> np.ndarray:
    img  = Image.fromarray(base_arr).convert("RGBA")

    # Fade in/out
    fade_dur = 0.5
    alpha_f  = min(1.0, t / fade_dur)
    if t > dur - fade_dur:
        alpha_f = min(alpha_f, (dur - t) / fade_dur)
    alpha_f  = max(0.0, alpha_f)

    f_big   = find_font(96, bold=True)
    f_small = find_font(46, bold=False)
    f_tiny  = find_font(32, bold=False)
    draw    = ImageDraw.Draw(img)

    # ── Barra superior @VeroResina ──
    bar_ov = Image.new("RGBA", (W,80), (*accent, int(200*alpha_f)))
    img.paste(bar_ov, (0,0), bar_ov)
    draw = ImageDraw.Draw(img)
    draw.text((22,18), "🎨 @VeroResina  •  Resina Epóxica", font=f_tiny, fill=(0,0,0,255))

    # ── Letterbox cinematic bars ──
    bar_h = 55
    for y_pos in [0, H-bar_h]:
        lb = Image.new("RGBA", (W, bar_h), (0,0,0,255))
        img.paste(lb, (0,y_pos), lb)

    img  = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── Gradiente inferior para texto ──
    grad = Image.new("RGBA", (W, 500), (0,0,0,0))
    gd   = ImageDraw.Draw(grad)
    for yy in range(500):
        a = int(200 * (yy/500) * alpha_f)
        gd.rectangle([0,yy,W,yy+1], fill=(0,0,0,a))
    img = Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── CAPTION grande ──
    lines = caption.split("\n")
    total_h = len(lines) * 108
    y = H - 340 - total_h
    for line in lines:
        bb = draw.textbbox((0,0), line, font=f_big)
        tw = bb[2]-bb[0]
        x  = (W-tw)//2
        # Sombra
        draw.text((x+3,y+3), line, font=f_big, fill=(0,0,0,200))
        # Texto con accent color
        draw.text((x,y), line, font=f_big, fill=(*accent, 255))
        y += 108

    # ── Subtítulo ──
    bb2 = draw.textbbox((0,0), sub, font=f_small)
    tw2 = bb2[2]-bb2[0]
    draw.text(((W-tw2)//2+2, y+8), sub, font=f_small, fill=(0,0,0,180))
    draw.text(((W-tw2)//2,   y+6), sub, font=f_small, fill=(255,255,255,255))

    # ── Botón CTA en últimas escenas ──
    if caption.startswith("¡INSCR"):
        pulse = 1.0 + 0.04 * math.sin(t * 4)
        bw    = int(660 * pulse)
        bh    = 90
        bx    = (W-bw)//2
        by    = H - 200
        btn   = Image.new("RGBA", (W,H), (0,0,0,0))
        bd    = ImageDraw.Draw(btn)
        bd.rounded_rectangle([bx,by,bx+bw,by+bh], radius=35,
                              fill=(220,40,60, int(240*alpha_f)))
        img   = Image.alpha_composite(img.convert("RGBA"), btn).convert("RGB")
        draw  = ImageDraw.Draw(img)
        ct    = "🔥  IR AL CURSO  →  HOTMART"
        bb3   = draw.textbbox((0,0), ct, font=f_small)
        tx    = (W-(bb3[2]-bb3[0]))//2
        ty    = by + (bh-(bb3[3]-bb3[1]))//2
        draw.text((tx,ty), ct, font=f_small, fill=(255,255,255))
        url_f = find_font(28, bold=False)
        url_t = "go.hotmart.com/G106175870D?ap=8534"
        bb4   = draw.textbbox((0,0), url_t, font=url_f)
        draw.text(((W-(bb4[2]-bb4[0]))//2, by+bh+12), url_t,
                  font=url_f, fill=(255,200,40))

    return np.array(img.convert("RGB"))

# ─────────────────────────────────────────────────────────
# MÚSICA DE FONDO (100 BPM)
# ─────────────────────────────────────────────────────────
def gen_music(duration):
    t   = np.linspace(0, duration, int(SR*duration), endpoint=False)
    bpm = 100
    bt  = 60/bpm
    def note(freq, start, dur, amp=0.10):
        s = int(start*SR); e = min(int((start+dur)*SR), len(t))
        seg = np.sin(2*np.pi*freq*t[s:e])*amp
        fa  = min(int(0.04*SR), len(seg)//4)
        if fa > 0:
            seg[:fa]  *= np.linspace(0,1,fa)
            seg[-fa:] *= np.linspace(1,0,fa)
        return s,e,seg
    audio = np.zeros(len(t))
    prog  = [220.0,174.6,261.6,196.0]
    bars  = int(duration/(bt*4))+2
    for bar in range(bars):
        for bi,freq in enumerate(prog):
            st = (bar*4+bi)*bt
            if st >= duration: break
            s,e,sg = note(freq, st, bt*0.85)
            audio[s:e] += sg
    beats = int(duration/bt)+1
    for i in range(beats):
        s = int(i*bt*SR)
        kl = min(int(0.13*SR), len(audio)-s)
        if kl > 0:
            env  = np.exp(-np.linspace(0,9,kl))
            kick = np.sin(2*np.pi*np.linspace(90,42,kl))*env*0.28
            audio[s:s+kl] += kick
        if i%2 == 1:
            sl = min(int(0.07*SR), len(audio)-s)
            if sl > 0:
                sn = np.random.randn(sl)*0.12*np.exp(-np.linspace(0,20,sl))
                audio[s:s+sl] += sn
    bass = [110.0,87.3,130.8,98.0]
    for bar in range(bars):
        for bi,bf in enumerate(bass):
            st = (bar*4+bi)*bt
            if st >= duration: break
            s,e,sg = note(bf, st, bt*0.8, amp=0.18)
            audio[s:e] += sg
    fi = min(int(0.8*SR), len(audio)//4)
    fo = min(int(2.0*SR), len(audio)//4)
    audio[:fi]  *= np.linspace(0,1,fi)
    audio[-fo:] *= np.linspace(1,0,fo)
    return np.clip(audio,-1,1)

# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
def main():
    print("\n🎬  REEL CINEMATOGRÁFICO - @VeroResina")
    print("="*50)

    # 1. Descargar audio
    audio_path = TMP / "voz_natural.mp3"
    if not audio_path.exists():
        print("\n📥  Descargando assets de Magnific AI...")
        download(AUDIO_URL, audio_path)
    else:
        print(f"\n✅  Audio ya descargado")

    # 2. Descargar imágenes
    img_paths = []
    for cfg in IMAGES:
        p = TMP / f"{cfg['name']}.jpg"
        if not p.exists():
            download(cfg["url"], p)
        img_paths.append(p)

    # 3. Pre-procesar imágenes
    print("\n🎨  Procesando imágenes con color grading cinematográfico...")
    prepped = []
    for p in img_paths:
        img = Image.open(p).convert("RGB")
        img = prep_image(img)
        prepped.append(img)
        print(f"     ✅  {p.name}")

    # 4. Construir clips de video
    print("\n🎞   Creando clips con efecto Ken Burns...")
    total_dur = sum(cfg["duration"] for cfg in IMAGES)

    def make_frame(t_global):
        # ¿qué escena corresponde?
        acc = 0
        for i, cfg in enumerate(IMAGES):
            if t_global < acc + cfg["duration"]:
                t_local = t_global - acc
                dur     = cfg["duration"]
                # Ken Burns
                frame   = ken_burns(prepped[i], t_local, dur,
                                    pan_y=(-0.03 if i%2==0 else 0.03))
                # Overlay
                frame   = text_overlay(frame, t_local, dur,
                                       cfg["caption"], cfg["sub"], cfg["accent"])
                return frame
            acc += cfg["duration"]
        return np.zeros((H, W, 3), dtype=np.uint8)

    video = VideoClip(make_frame, duration=total_dur).with_fps(FPS)

    # 5. Audio: voz + música
    print("\n🎵  Mezclando audio (voz natural + música)...")
    mus_arr = gen_music(total_dur)
    music   = AudioArrayClip(
        np.column_stack([mus_arr, mus_arr]) * 0.3,
        fps=SR
    ).with_duration(total_dur)

    voz = AudioFileClip(str(audio_path))
    voz_dur = min(voz.duration, total_dur - 0.5)
    voz = voz.with_duration(voz_dur)

    audio = CompositeAudioClip([music, voz]).with_duration(total_dur)
    video = video.with_audio(audio)

    # 6. Exportar
    out = OUT_DIR / "ReelCinematico_VeroResina.mp4"
    print(f"\n📹  Renderizando → {out}")
    print("    (puede tardar 3-5 minutos...)\n")
    video.write_videofile(
        str(out), fps=FPS, codec="libx264", audio_codec="aac",
        ffmpeg_params=["-crf","20","-preset","medium","-pix_fmt","yuv420p"],
        logger="bar"
    )
    size = out.stat().st_size / 1e6
    print(f"\n✅  ¡LISTO! → {out}  ({size:.1f} MB)")
    print("\nSUBE ESTE VIDEO A:")
    print("  📘 Facebook: @VeroResina, @RPResina, @PXResina")
    print("  🎵 TikTok, Instagram Reels")
    print("  🔗 Link Hotmart: go.hotmart.com/G106175870D?ap=8534\n")

if __name__ == "__main__":
    main()
