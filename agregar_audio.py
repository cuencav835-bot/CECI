"""
Agrega voz en off (TTS español) + música ambient a los videos de VeroResina.
Produce versiones finales listas para publicar con audio completo.
"""

import os
import numpy as np
from scipy.io import wavfile
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioArrayClip

SRC_DIR = "/home/user/CECI/videos_publicar"
OUT_DIR = "/home/user/CECI/videos_con_audio"
TMP_DIR = "/tmp/vero_audio"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

SR = 44100   # sample rate

# ──────────────────────────────────────────────────────────────────────
# 1. GENERAR MÚSICA AMBIENT (tono teal/orgánico, sin copyright)
# ──────────────────────────────────────────────────────────────────────
def make_ambient_music(duration_s, bpm=90):
    """
    Crea una pista ambient con:
    - Pad de acordes suaves (Am → C → F → G)
    - Kick sutil cada beat
    - Hi-hat cada medio beat
    """
    t = np.linspace(0, duration_s, int(SR * duration_s), endpoint=False)
    beat = 60 / bpm          # segundos por beat
    bar  = beat * 4

    # ── Chord pads (sine + triangle blend) ────────────────────────────
    # Am: A3 C4 E4 | C: C4 E4 G4 | F: F3 A3 C4 | G: G3 B3 D4
    chords = [
        [220.00, 261.63, 329.63],   # Am
        [261.63, 329.63, 392.00],   # C
        [174.61, 220.00, 261.63],   # F
        [196.00, 246.94, 293.66],   # G
    ]
    pad = np.zeros_like(t)
    for i, freqs in enumerate(chords):
        start = i * bar
        end   = (i + 1) * bar
        mask  = (t >= start) & (t < end)
        for f in freqs:
            sine = np.sin(2 * np.pi * f * t)
            tri  = 2 * np.arcsin(np.sin(2 * np.pi * f * t)) / np.pi
            pad[mask] += 0.06 * (0.7 * sine[mask] + 0.3 * tri[mask])
    # Repeat chord progression to fill duration
    bars_total = int(np.ceil(duration_s / bar))
    pad_full = np.zeros_like(t)
    for b in range(bars_total):
        chord_idx = b % 4
        start = b * bar
        end   = (b + 1) * bar
        mask  = (t >= start) & (t < min(end, duration_s))
        freqs = chords[chord_idx]
        for f in freqs:
            sine = np.sin(2 * np.pi * f * t)
            tri  = 2 * np.arcsin(np.sin(2 * np.pi * f * t)) / np.pi
            pad_full[mask] += 0.06 * (0.7 * sine[mask] + 0.3 * tri[mask])

    # ── Kick (burst of low sine ~60Hz, short decay) ───────────────────
    kick = np.zeros_like(t)
    beat_times = np.arange(0, duration_s, beat)
    for bt in beat_times:
        k_len = int(0.12 * SR)
        k_t   = np.linspace(0, 0.12, k_len)
        k_sig = np.sin(2 * np.pi * 60 * k_t) * np.exp(-30 * k_t)
        idx   = int(bt * SR)
        end   = min(idx + k_len, len(kick))
        kick[idx:end] += 0.18 * k_sig[:end - idx]

    # ── Hi-hat (white noise burst, very short) ────────────────────────
    hihat = np.zeros_like(t)
    hh_times = np.arange(0, duration_s, beat / 2)
    for ht in hh_times:
        h_len = int(0.04 * SR)
        h_sig = np.random.randn(h_len) * np.exp(-80 * np.linspace(0, 0.04, h_len))
        idx   = int(ht * SR)
        end   = min(idx + h_len, len(hihat))
        hihat[idx:end] += 0.05 * h_sig[:end - idx]

    # ── Mix ───────────────────────────────────────────────────────────
    mix = pad_full + kick + hihat

    # Fade in/out (2 s)
    fade = int(2 * SR)
    mix[:fade]  *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)

    # Normalize
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.7

    return mix.astype(np.float32)


# ──────────────────────────────────────────────────────────────────────
# 2. VOZ EN OFF con gTTS (español México)
# ──────────────────────────────────────────────────────────────────────
def make_voiceover(text, filename):
    """Genera MP3 con voz femenina en español y devuelve la ruta."""
    path = f"{TMP_DIR}/{filename}.mp3"
    tts = gTTS(text=text, lang="es", tld="com.mx", slow=False)
    tts.save(path)
    return path


# ──────────────────────────────────────────────────────────────────────
# 3. Combinar video + voz + música
# ──────────────────────────────────────────────────────────────────────
def build_video(src_mp4, out_mp4, voice_text, vol_music=0.25, vol_voice=1.0):
    print(f"\n🎬 Procesando: {os.path.basename(src_mp4)}")

    clip = VideoFileClip(src_mp4)
    dur  = clip.duration
    print(f"   Duración: {dur:.1f}s")

    # — Música —
    print("   🎵 Generando música ambient...")
    music_arr = make_ambient_music(dur + 2)
    stereo    = np.stack([music_arr, music_arr], axis=1)   # mono → stereo
    music_clip = AudioArrayClip(stereo, fps=SR).with_duration(dur) \
                                                .with_volume_scaled(vol_music)

    # — Voz en off —
    print(f"   🗣  Generando voz: '{voice_text[:40]}...'")
    voice_mp3 = make_voiceover(voice_text, os.path.basename(out_mp4))
    voice_clip = AudioFileClip(voice_mp3).with_volume_scaled(vol_voice)

    # Si la voz es más larga que el video, la recortamos
    if voice_clip.duration > dur:
        voice_clip = voice_clip.with_duration(dur)

    # — Mix: música de fondo + voz encima —
    final_audio = CompositeAudioClip([music_clip, voice_clip])
    final_clip  = clip.with_audio(final_audio)

    print(f"   💾 Exportando → {os.path.basename(out_mp4)}")
    final_clip.write_videofile(
        out_mp4, fps=30, codec="libx264",
        audio_codec="aac", audio_fps=SR,
        logger=None, preset="fast", bitrate="4000k"
    )
    clip.close()
    voice_clip.close()
    print(f"   ✅ Listo!")


# ──────────────────────────────────────────────────────────────────────
# 4. Procesar los 4 videos
# ──────────────────────────────────────────────────────────────────────

videos = [
    {
        "src":  f"{SRC_DIR}/A_cuanto_vale_tiktok.mp4",
        "out":  f"{OUT_DIR}/A_cuanto_vale_CON_AUDIO.mp4",
        "voz":  (
            "¿Cuánto crees que vale esta mesa? "
            "Los materiales cuestan ochocientos pesos. "
            "Pero el precio de venta supera los ocho mil pesos. "
            "Eso es diez veces tu inversión en cada pieza. "
            "Aprende a hacerlo tú mismo. "
            "El enlace está en mi bio."
        ),
    },
    {
        "src":  f"{SRC_DIR}/B_aprende_desde_cero_tiktok.mp4",
        "out":  f"{OUT_DIR}/B_aprende_CON_AUDIO.mp4",
        "voz":  (
            "No necesitas ser artista. "
            "Solo necesitas la técnica correcta. "
            "Con resina epóxica puedes crear mesas, cuadros, joyería y charolas. "
            "Todo se vende, todo genera ingresos. "
            "Aprende desde cero con el curso que recomiendo. "
            "El enlace está en mi bio."
        ),
    },
    {
        "src":  f"{SRC_DIR}/C_gana_desde_casa_tiktok.mp4",
        "out":  f"{OUT_DIR}/C_gana_CON_AUDIO.mp4",
        "voz":  (
            "¿Sabías que puedes ganar diez mil pesos al mes "
            "haciendo resina desde tu casa? "
            "Sin inventario, sin tienda, sin salir. "
            "Solo necesitas el material y la técnica. "
            "Una alumna del curso recuperó su inversión "
            "vendiendo su primera pieza en dos semanas. "
            "El enlace del curso está en mi bio."
        ),
    },
    {
        "src":  f"{SRC_DIR}/D_feed_instagram_cuadrado.mp4",
        "out":  f"{OUT_DIR}/D_feed_CON_AUDIO.mp4",
        "voz":  (
            "Resina epóxica. "
            "El negocio más creativo del momento. "
            "Piezas únicas que la gente paga con gusto. "
            "Aprende cómo. "
            "El enlace está en mi bio."
        ),
    },
]

for v in videos:
    build_video(v["src"], v["out"], v["voz"])

print("\n" + "="*55)
print("🌿 TODOS LOS VIDEOS CON AUDIO LISTOS:")
for f in sorted(os.listdir(OUT_DIR)):
    mb = os.path.getsize(f"{OUT_DIR}/{f}") / 1_000_000
    print(f"  📱 {f}  ({mb:.1f} MB)")
print("="*55)
