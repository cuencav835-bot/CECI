"""
Editor de video VeroResina
Toma el video original y produce versiones listas para publicar
en TikTok, Instagram Reels y Facebook.
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

INPUT = "/root/.claude/uploads/e53a79e8-4dea-557c-b336-e5482ebcc79c/0175ef1d-lv_0_20260721085442.mp4"
OUTPUT_DIR = "/home/user/CECI/videos_publicar"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Colores VeroResina ───────────────────────────────────────────────
TEAL       = (78, 205, 196)
DARK       = (6, 8, 10)
CREAM      = (240, 250, 248)
GOLD       = (247, 201, 72)
TRANSPARENT = (0, 0, 0, 0)

# ── Fuentes (sistema) ────────────────────────────────────────────────
def get_font(size, bold=False):
    paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_text_overlay(width, height, lines, font_sizes, colors, y_positions,
                       bg_color=None, bg_alpha=180, pill=False):
    """Crea una imagen RGBA con texto para superponer al video."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for text, size, color, y in zip(lines, font_sizes, colors, y_positions):
        font = get_font(size, bold=(size >= 40))
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2

        if bg_color:
            pad = 14
            rect = [x - pad, y - pad, x + tw + pad, y + (bbox[3] - bbox[1]) + pad]
            if pill:
                draw.rounded_rectangle(rect, radius=20,
                                       fill=(*bg_color, bg_alpha))
            else:
                draw.rectangle(rect, fill=(*bg_color, bg_alpha))

        # Sombra
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 160))
        draw.text((x, y), text, font=font, fill=(*color, 255))

    return img


def frame_to_pil(frame):
    return Image.fromarray(frame.astype(np.uint8), "RGB")


def overlay_to_frame(frame, overlay_pil):
    """Pega overlay RGBA sobre frame RGB."""
    base = frame_to_pil(frame).convert("RGBA")
    base.paste(overlay_pil, (0, 0), overlay_pil)
    return np.array(base.convert("RGB"))


# ══════════════════════════════════════════════════════════════════════
# 1. Cargar y recortar video (quitar barras negras, dejar 9:16)
# ══════════════════════════════════════════════════════════════════════
print("📹 Cargando video original...")
clip = VideoFileClip(INPUT)
W, H = clip.size          # 1920 x 1080

# El contenido real está centrado; detectamos el ancho del contenido
# En 1080p landscape con contenido vertical: ancho ≈ H * 9/16 = 607
content_w = int(H * 9 / 16)   # ~607
x1 = (W - content_w) // 2
x2 = x1 + content_w

print(f"  Original: {W}x{H} — Recorte: {x1}:{x2} x 0:{H}")
clip_v = clip.cropped(x1=x1, y1=0, x2=x2, y2=H)   # 607x1080
# Escalar a 1080x1920 (estándar TikTok/Reels)
clip_v = clip_v.resized((1080, 1920))
VW, VH = 1080, 1920

print(f"  Resultado vertical: {VW}x{VH}, {clip_v.duration:.1f}s")


# ══════════════════════════════════════════════════════════════════════
# 2. Función genérica: aplica overlay estático a todo el clip
# ══════════════════════════════════════════════════════════════════════
def apply_overlay(clip, overlay_pil):
    ov_arr = np.array(overlay_pil)
    def process(frame):
        base = Image.fromarray(frame.astype(np.uint8), "RGB").convert("RGBA")
        ov   = Image.fromarray(ov_arr, "RGBA")
        base.paste(ov, (0, 0), ov)
        return np.array(base.convert("RGB"))
    return clip.image_transform(process)


# ══════════════════════════════════════════════════════════════════════
# 3. VIDEO A — "¿Cuánto vale esta mesa?"  (TikTok / Reels)
# ══════════════════════════════════════════════════════════════════════
print("\n🎬 Creando Video A — ¿Cuánto vale esta mesa?")

ovA = make_text_overlay(
    VW, VH,
    lines      = ["@VeroResina", "¿CUÁNTO VALE", "ESTA MESA?", "👇 Link en bio"],
    font_sizes = [32,            72,              72,           36],
    colors     = [TEAL,          CREAM,           GOLD,         TEAL],
    y_positions= [60,            VH-420,          VH-330,       VH-120],
    bg_color   = DARK, bg_alpha=160, pill=True
)

clip_A = apply_overlay(clip_v, ovA)
out_A = f"{OUTPUT_DIR}/A_cuanto_vale_tiktok.mp4"
clip_A.write_videofile(out_A, fps=30, codec="libx264",
                        audio_codec="aac", logger=None,
                        preset="fast", bitrate="4000k")
print(f"  ✅ Guardado: {out_A}")


# ══════════════════════════════════════════════════════════════════════
# 4. VIDEO B — "Aprende desde cero"  (TikTok / Reels)
# ══════════════════════════════════════════════════════════════════════
print("\n🎬 Creando Video B — Aprende desde cero")

ovB = make_text_overlay(
    VW, VH,
    lines      = ["@VeroResina", "APRENDE RESINA", "EPÓXICA", "DESDE CERO", "✦ Curso en bio"],
    font_sizes = [32,            64,                64,         64,           36],
    colors     = [TEAL,          CREAM,             TEAL,       CREAM,        GOLD],
    y_positions= [60,            VH-520,            VH-440,     VH-360,       VH-120],
    bg_color   = DARK, bg_alpha=160, pill=True
)

clip_B = apply_overlay(clip_v, ovB)
out_B = f"{OUTPUT_DIR}/B_aprende_desde_cero_tiktok.mp4"
clip_B.write_videofile(out_B, fps=30, codec="libx264",
                        audio_codec="aac", logger=None,
                        preset="fast", bitrate="4000k")
print(f"  ✅ Guardado: {out_B}")


# ══════════════════════════════════════════════════════════════════════
# 5. VIDEO C — "Gana desde casa"  (TikTok / Reels)
# ══════════════════════════════════════════════════════════════════════
print("\n🎬 Creando Video C — Gana desde casa")

ovC = make_text_overlay(
    VW, VH,
    lines      = ["@VeroResina", "GANA $10,000 MXN", "HACIENDO", "RESINA EN CASA", "👆 Link en bio"],
    font_sizes = [32,            58,                  58,          58,               36],
    colors     = [TEAL,          GOLD,                CREAM,       CREAM,            TEAL],
    y_positions= [60,            VH-540,              VH-465,      VH-390,           VH-120],
    bg_color   = DARK, bg_alpha=160, pill=True
)

clip_C = apply_overlay(clip_v, ovC)
out_C = f"{OUTPUT_DIR}/C_gana_desde_casa_tiktok.mp4"
clip_C.write_videofile(out_C, fps=30, codec="libx264",
                        audio_codec="aac", logger=None,
                        preset="fast", bitrate="4000k")
print(f"  ✅ Guardado: {out_C}")


# ══════════════════════════════════════════════════════════════════════
# 6. VIDEO D — Versión cuadrada para feed de Instagram (1:1)
# ══════════════════════════════════════════════════════════════════════
print("\n🎬 Creando Video D — Feed Instagram (1080x1080)")

clip_sq = clip_v.cropped(x1=0, y1=(VH - VW)//2, x2=VW, y2=(VH + VW)//2)

ovD = make_text_overlay(
    VW, VW,
    lines      = ["@VeroResina", "RESINA EPÓXICA", "Link en bio →"],
    font_sizes = [36,             60,               36],
    colors     = [TEAL,           CREAM,            GOLD],
    y_positions= [40,             VW-200,           VW-110],
    bg_color   = DARK, bg_alpha=150, pill=True
)

clip_D = apply_overlay(clip_sq, ovD)
out_D = f"{OUTPUT_DIR}/D_feed_instagram_cuadrado.mp4"
clip_D.write_videofile(out_D, fps=30, codec="libx264",
                        audio_codec="aac", logger=None,
                        preset="fast", bitrate="3000k")
print(f"  ✅ Guardado: {out_D}")


# ══════════════════════════════════════════════════════════════════════
# 7. Cerrar y resumen
# ══════════════════════════════════════════════════════════════════════
clip.close()

print("\n" + "="*55)
print("🌿 VIDEOS LISTOS PARA PUBLICAR:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    size = os.path.getsize(f"{OUTPUT_DIR}/{f}") / 1_000_000
    print(f"  📱 {f}  ({size:.1f} MB)")
print("="*55)
print("Súbelos directamente a TikTok, Instagram Reels y Facebook.")
