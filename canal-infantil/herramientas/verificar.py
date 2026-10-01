#!/usr/bin/env python3
"""Dice qué archivos faltan antes de montar un video.  Uso: python verificar.py CARPETA_DEL_VIDEO"""
import json, sys
from pathlib import Path

base = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
cfg = json.loads((base / "escenas.json").read_text(encoding="utf-8"))
faltan, ok = [], 0
for i, sc in enumerate(cfg["escenas"], 1):
    f = sc.get("clip") or sc.get("imagen")
    if f and (base / f).exists():
        ok += 1
    else:
        faltan.append(f"E{i:02} -> {f or '(sin clip ni imagen: saldrá tarjeta de color)'}")
m = cfg.get("musica")
print(f"Escenas con archivo: {ok}/{len(cfg['escenas'])}")
if faltan:
    print("Faltan:\n  " + "\n  ".join(faltan))
print("Música:", "OK" if m and (base / m).exists() else f"FALTA {m or '(no definida)'} -> el video saldrá sin música")
sys.exit(1 if faltan else 0)
