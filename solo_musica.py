"""
Agrega música ambient a los 4 videos de VeroResina.
La voz en off se agrega después en CapCut (instrucciones al final).
"""

import os
import numpy as np
from scipy.io import wavfile
from moviepy import VideoFileClip, AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip

SRC_DIR = "/home/user/CECI/videos_publicar"
OUT_DIR = "/home/user/CECI/videos_con_audio"
os.makedirs(OUT_DIR, exist_ok=True)

SR = 44100

def make_ambient(duration_s, bpm=88):
    t = np.linspace(0, duration_s, int(SR * duration_s), endpoint=False)
    beat = 60 / bpm
    bar  = beat * 4

    # Chord progression Am → C → F → G (teal/organic feel)
    chords = [
        [220.00, 261.63, 329.63],
        [261.63, 329.63, 392.00],
        [174.61, 220.00, 261.63],
        [196.00, 246.94, 293.66],
    ]

    mix = np.zeros_like(t)

    # Pads
    bars_total = int(np.ceil(duration_s / bar))
    for b in range(bars_total):
        freqs = chords[b % 4]
        start, end = b * bar, min((b + 1) * bar, duration_s)
        mask = (t >= start) & (t < end)
        for f in freqs:
            sine = np.sin(2 * np.pi * f * t)
            tri  = 2 * np.arcsin(np.clip(np.sin(2 * np.pi * f * t), -1, 1)) / np.pi
            mix[mask] += 0.055 * (0.65 * sine[mask] + 0.35 * tri[mask])

    # Kick each beat
    for bt in np.arange(0, duration_s, beat):
        k_len = int(0.10 * SR)
        k_t   = np.linspace(0, 0.10, k_len)
        k_sig = np.sin(2 * np.pi * 65 * k_t) * np.exp(-35 * k_t)
        idx = int(bt * SR)
        end = min(idx + k_len, len(mix))
        mix[idx:end] += 0.16 * k_sig[:end - idx]

    # Hi-hat each half-beat
    for ht in np.arange(0, duration_s, beat / 2):
        h_len = int(0.03 * SR)
        h_env = np.exp(-100 * np.linspace(0, 0.03, h_len))
        h_sig = np.random.randn(h_len) * h_env
        idx = int(ht * SR)
        end = min(idx + h_len, len(mix))
        mix[idx:end] += 0.04 * h_sig[:end - idx]

    # Sub bass (root note each bar)
    roots = [110.0, 130.8, 87.3, 98.0]
    for b in range(bars_total):
        f = roots[b % 4]
        start, end = b * bar, min((b + 1) * bar, duration_s)
        mask = (t >= start) & (t < end)
        mix[mask] += 0.12 * np.sin(2 * np.pi * f * t[mask])

    # Fade in / out
    fade = int(1.5 * SR)
    mix[:fade]  *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)

    # Normalize
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.72

    return mix.astype(np.float32)


videos = [
    "A_cuanto_vale_tiktok.mp4",
    "B_aprende_desde_cero_tiktok.mp4",
    "C_gana_desde_casa_tiktok.mp4",
    "D_feed_instagram_cuadrado.mp4",
]

for fname in videos:
    src = f"{SRC_DIR}/{fname}"
    out = f"{OUT_DIR}/{fname.replace('.mp4', '_MUSICA.mp4')}"

    print(f"\n🎵 Procesando: {fname}")
    clip = VideoFileClip(src)
    dur  = clip.duration

    music = make_ambient(dur + 1)
    stereo = np.stack([music, music], axis=1)
    music_clip = AudioArrayClip(stereo, fps=SR).with_duration(dur).with_volume_scaled(0.35)

    final = clip.with_audio(music_clip)
    final.write_videofile(out, fps=30, codec="libx264",
                          audio_codec="aac", audio_fps=SR,
                          logger=None, preset="fast", bitrate="4000k")
    clip.close()
    mb = os.path.getsize(out) / 1_000_000
    print(f"  ✅ {os.path.basename(out)} ({mb:.1f} MB)")

print("\n" + "="*55)
print("🌿 VIDEOS CON MÚSICA LISTOS EN: videos_con_audio/")
print("="*55)
