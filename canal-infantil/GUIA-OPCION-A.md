# Guía Opción A — videos gratis: tú generas los clips, el equipo monta todo

Video de partida: `videos/patitos-colores-animales/` (25 escenas). Todo lo demás (voz, música, subtítulos, montaje) sale del script.

## Paso 0 — Preparar el ordenador (una sola vez, ~15 min)
1. Instala **Python 3.10+** (python.org; en Windows marca "Add Python to PATH").
2. Descarga este repositorio (rama `claude/confident-hamilton-iuvvjx`) o clónalo.
3. En una terminal dentro de la carpeta del repositorio:
   ```
   pip install -r canal-infantil/herramientas/requirements.txt
   ```
4. Prueba el montaje sin internet (debe crear `canal-infantil/ejemplo/video_final.mp4`):
   ```
   python canal-infantil/herramientas/producir.py canal-infantil/ejemplo --voz-falsa
   ```
5. Prueba la voz real con una sola frase (si falla, dímelo y cambiamos de voz):
   ```
   python -m edge_tts --voice es-MX-DaliaNeural --text "Hola pequeños, bienvenidos." --write-media prueba.mp3
   ```

## Paso 1 — Cuentas gratuitas (una por persona)
Crea cuenta en 2–3 de: Kling AI, Google Flow, Hailuo, Pika, Luma. No crees cuentas múltiples para saltarte límites.
Cifras de las comparativas (verifícalas en cada web el día que empieces): Kling ≈ 66 créditos/día, Flow ≈ 50/día, Hailuo 3–5 videos/día, Pika ≈ 80 créditos/mes, Luma ≈ 30 generaciones/mes.

## Paso 2 — Imágenes de referencia (día 1)
Con `prompts-gratis.md` genera R1–R5 en un generador de imágenes gratuito o en el propio Flow/Kling. Guarda las 5 en `videos/patitos-colores-animales/referencias/`. Elige la mejor de cada grupo; **todas las escenas usan esa misma imagen**.

## Paso 3 — Generar los 25 clips (≈ 7–10 días con cuotas gratuitas)
| Día | Clips |
|---|---|
| 1 | Referencias + E01–E03 |
| 2 | E04–E07 |
| 3 | E08–E11 |
| 4 | E12–E15 |
| 5 | E16–E19 |
| 6 | E20–E23 |
| 7 | E24–E25 + repetir los que fallaron |

Ajustes en cada herramienta: 16:9, 720p, 5–6 s, **sin audio**, modo imagen-a-video con la referencia del grupo (columna "Ref" de `prompts-gratis.md`).
Revisa cada clip: personajes iguales a la referencia, conteo correcto (E03 = 4 patitos), sin texto ni cosas raras. Si falla, repite ese clip.
Guarda como `clips/E01.mp4 … E25.mp4` dentro de la carpeta del video. **Descarga el clip al terminar**: los enlaces caducan.

## Paso 4 — Música (licencia comercial)
Genera una pista instrumental infantil (ukelele, xilófono, ~100 bpm, sin voz) en un generador con licencia comercial, de unos 6–7 min (o dos pistas unidas). Guárdala como `musica.mp3` en la carpeta del video y **apunta la licencia** en `licencias.md`.

## Paso 5 — Comprobar y montar
```
python canal-infantil/herramientas/verificar.py canal-infantil/videos/patitos-colores-animales
python canal-infantil/herramientas/producir.py canal-infantil/videos/patitos-colores-animales
```
Resultado en esa carpeta: `video_final.mp4` (1080p, voz, música baja, subtítulos pegados) y `subtitulos.srt` (tiempos reales).
Escucha el video entero antes de subirlo: sincronía voz/imagen, música, sin cortes raros.

## Paso 6 — Publicar
1. Miniatura en Canva (personaje grande, 2–3 palabras).
2. Sube el MP4 a YouTube Studio; marca **"Sí, es contenido para niños"** y declara contenido generado con IA.
3. Título, descripción y etiquetas: están en los mensajes anteriores de esta conversación (ES/EN) o pídeselos al agente `publicador-youtube`.
4. Opcional: sube `subtitulos.srt` si prefieres subtítulos de YouTube en vez de los pegados (usa `--sin-quemar`).

## Si algo falla
- *La voz da error de conexión:* el servicio gratuito de voz puede haber cambiado; usa CapCut (voz IA) o KidsStoryteller para las narraciones y guárdalas como `_trabajo/voz_001.mp3 …` (el script las reutiliza si ya existen).
- *Personajes distintos entre clips:* usa siempre la misma referencia y una sola herramienta por bloque de escenas.
- *Quedan huecos por cuota:* publica un video más corto (p. ej. solo las escenas E01–E10).
