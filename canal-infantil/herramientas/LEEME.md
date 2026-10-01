# producir.py — montaje gratuito de videos infantiles

Convierte una carpeta con `escenas.json` + clips/imágenes + música en un MP4 1080p con voz, música y subtítulos.

```bash
pip install -r requirements.txt
python producir.py ../ejemplo --voz-falsa     # prueba sin internet (silencio)
python producir.py ../videos/patitos-colores-animales
```

`escenas.json`:
```json
{ "voz": "es-MX-DaliaNeural", "velocidad": "-5%", "musica": "musica.mp3", "pausa_final": 0.6,
  "escenas": [ { "clip": "clips/E01.mp4", "narracion": "Texto…", "duracion_min": 5 } ] }
```
- `clip` (video) o `imagen` (zoom suave). Sin ninguno, tarjeta de color.
- La duración de la escena = duración de la voz + `pausa_final` (mínimo `duracion_min`). Los subtítulos usan esos tiempos reales.
- Voces disponibles: `python -m edge_tts --list-voices | grep es-`.

## Probado / no probado
- Probado aquí: montaje, zoom, subtítulos quemados, música y duración (con voz falsa).
- NO probado aquí: la voz real de edge-tts (este entorno no alcanza ese servicio). Pruébala en tu ordenador con una sola escena antes de un video largo.
- edge-tts usa el servicio de voz de Microsoft Edge sin API oficial: puede cambiar o dejar de funcionar; confirma que su uso comercial te sirve antes de monetizar.
