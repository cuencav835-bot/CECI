#!/usr/bin/env python3
"""Ensambla un video infantil completo con herramientas 100 % gratuitas.

Entrada: una carpeta de proyecto con `escenas.json` (ver ../ejemplo/escenas.json).
Cada escena aporta una imagen o un clip de video (generado en cualquier herramienta
gratuita) y una línea de narración. El script:
  1. Sintetiza la voz de cada escena con edge-tts (voces neuronales gratuitas de Microsoft Edge).
  2. Convierte cada escena en un clip 1920x1080 (imagen con zoom suave, o video recortado/en bucle)
     con la duración exacta de su narración.
  3. Escribe subtitulos.srt con tiempos REALES (medidos de la voz) y, si se pide, los quema en el video.
  4. Une todo y mezcla música de fondo a bajo volumen.

Uso:
  python producir.py ../ejemplo                 # video con subtítulos quemados
  python producir.py PROYECTO --sin-quemar      # solo .srt aparte
  python producir.py PROYECTO --voz-falsa       # prueba sin internet (silencio); no usar para publicar
"""
import argparse, asyncio, json, math, os, re, subprocess, sys, tempfile
from pathlib import Path

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

W, H, FPS = 1920, 1080, 30


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg falló:\n{' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def duration(path):
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        sys.exit(f"No pude leer la duración de {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def make_voice(text, out, voice, rate, fake):
    if out.exists() and out.stat().st_size > 0:
        return
    if fake:
        secs = max(2.0, len(text.split()) / 2.6)
        run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", f"{secs:.2f}", "-c:a", "libmp3lame", str(out)])
        return
    import edge_tts
    async def go():
        await edge_tts.Communicate(text, voice, rate=rate).save(str(out))
    asyncio.run(go())


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def split_cues(text, start, dur):
    sents = [s.strip() for s in re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", text) if s.strip()]
    words = [max(1, len(s.split())) for s in sents]
    tot = sum(words); t = start; out = []
    for s, w in zip(sents, words):
        d = dur * w / tot
        out.append((t, t + d - 0.05, s)); t += d
    return out


def scene_clip(scene, voice_mp3, dur, out, base):
    media = scene.get("clip") or scene.get("imagen")
    media = (base / media) if media else None
    vf_tail = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps={FPS},format=yuv420p"
    if media and media.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
        inp = ["-stream_loop", "-1", "-i", str(media)]
        vf = vf_tail
    elif media:
        frames = int(math.ceil(dur * FPS))
        inp = ["-loop", "1", "-framerate", str(FPS), "-i", str(media)]
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='min(zoom+0.0006,1.12)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
              f"setsar=1,format=yuv420p")
    else:  # sin medio: tarjeta de color
        inp = ["-f", "lavfi", "-i", f"color=c=0xFFE9A8:s={W}x{H}:r={FPS}"]
        vf = "format=yuv420p"
    run([FFMPEG, "-y", *inp, "-i", str(voice_mp3), "-t", f"{dur:.3f}",
         "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-af", "apad", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(out)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("--sin-quemar", action="store_true", help="no quemar subtítulos (solo .srt)")
    ap.add_argument("--voz-falsa", action="store_true", help="silencio en vez de voz (solo pruebas)")
    ap.add_argument("--musica-vol", type=float, default=0.18)
    a = ap.parse_args()

    base = Path(a.proyecto).resolve()
    cfg = json.loads((base / "escenas.json").read_text(encoding="utf-8"))
    voice = cfg.get("voz", "es-MX-DaliaNeural"); rate = cfg.get("velocidad", "-5%")
    pausa = float(cfg.get("pausa_final", 0.6))
    work = base / "_trabajo"; work.mkdir(exist_ok=True)

    clips, cues, t = [], [], 0.0
    for i, sc in enumerate(cfg["escenas"], 1):
        vmp3 = work / f"voz_{i:03}.mp3"
        make_voice(sc["narracion"], vmp3, voice, rate, a.voz_falsa)
        d = max(duration(vmp3) + pausa, float(sc.get("duracion_min", 3)))
        clip = work / f"clip_{i:03}.mp4"
        scene_clip(sc, vmp3, d, clip, base)
        clips.append(clip)
        cues += split_cues(sc["narracion"], t + 0.2, duration(vmp3))
        t += d
        print(f"escena {i}/{len(cfg['escenas'])}: {d:.1f}s")

    srt = base / "subtitulos.srt"
    srt.write_text("\n".join(f"{n}\n{ts(s)} --> {ts(e)}\n{tx}\n" for n, (s, e, tx) in enumerate(cues, 1)),
                   encoding="utf-8")

    listf = work / "lista.txt"
    listf.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    bruto = work / "bruto.mp4"
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(bruto)])

    current = bruto
    if not a.sin_quemar:
        quem = work / "subs.mp4"
        style = "FontName=DejaVu Sans,FontSize=26,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=50"
        esc = str(srt).replace("\\", "/").replace(":", r"\:")
        run([FFMPEG, "-y", "-i", str(bruto), "-vf", f"subtitles='{esc}':force_style='{style}'",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy", str(quem)])
        current = quem

    final = base / "video_final.mp4"
    musica = cfg.get("musica")
    if musica and (base / musica).exists():
        total = duration(current)
        run([FFMPEG, "-y", "-i", str(current), "-stream_loop", "-1", "-i", str(base / musica),
             "-filter_complex",
             f"[1:a]volume={a.musica_vol},afade=t=out:st={max(0,total-3):.2f}:d=3[m];"
             f"[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-t", f"{total:.2f}", str(final)])
    else:
        run([FFMPEG, "-y", "-i", str(current), "-c", "copy", str(final)])
    print(f"\nListo: {final}  ({duration(final)/60:.1f} min)\nSubtítulos: {srt}")


if __name__ == "__main__":
    main()
