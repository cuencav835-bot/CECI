# Requisitos para producir videos del canal (con herramientas gratuitas primero)

Fecha de verificación: 2026-09-30. Los límites gratuitos cambian a menudo y las cifras de abajo salen de comparativas de terceros, no de pruebas propias: **confírmalas en la web de cada herramienta antes de planificar**.

## 1. Flujo de producción (qué hace cada agente)

| Paso | Agente (`.claude/agents/`) | Resultado |
|---|---|---|
| 1. Guion y narración | `guionista-infantil` | `guion.md`, `subtitulos.srt` |
| 2. Prompts e imágenes de referencia | `director-de-prompts` | `prompts.md` |
| 3. Generar clips | `generador-de-video` | `registro-clips.md` + clips |
| 4. Montaje, voz, música, subtítulos | `editor-audio-subtitulos` | `montaje.md`, `licencias.md`, MP4 final |
| 5. Publicación | `publicador-youtube` | `youtube.md` |

Límite importante: los agentes escriben archivos y planifican. **Las herramientas gratuitas se usan desde su web, con tu cuenta**; no puedo iniciar sesión ni generar en ellas desde aquí.

## 2. Herramientas gratuitas

### Video (texto/imagen → video)
| Herramienta | Qué ofrece gratis (según comparativas, verificar) |
|---|---|
| Kling AI | 66 créditos diarios, descargas sin marca de agua a 720p; texto→video e imagen→video |
| Google Flow | 50 créditos diarios para cuentas sin plan de pago |
| Hailuo AI | 3–5 generaciones diarias a 720p |
| Pika | 80 créditos al mes, sin marca de agua |
| Luma Dream Machine | unas 30 generaciones al mes |

Consejos:
- Con cuotas pequeñas, genera **clips de 5–6 s** y usa la **misma imagen de referencia** en todos.
- Reparte los clips en varios días y en 2–3 herramientas; el estilo puede variar entre herramientas, así que dedica **una herramienta por canción/episodio** para mantener la consistencia.
- Una cuenta = una persona. No crees cuentas múltiples para saltarte límites: va contra las condiciones de uso.

### Imágenes de referencia (personajes)
Usa el generador de imágenes gratuito de tu elección (Google Flow, Leonardo AI o similar) y guarda las hojas de personajes en `canal-infantil/referencias/`.

### Voz (narración)
- CapCut: locución con IA incluida en el plan gratuito.
- KidsStoryteller.ai: unos 3.000 caracteres al mes, más de 30 voces, MP3 sin marca de agua (según comparativa).
- SpeechGen: voces infantiles con descarga MP3 (verificar condiciones).
Para el canal completo de 18–20 min calcula ~3.000–4.000 palabras de narración por video, más de lo que alcanza una cuota gratuita mensual: planifica varios meses o usa CapCut/DaVinci con su voz integrada.

### Música
Generadores de música gratuitos con licencia comercial (p. ej. Sonauto, Mubert, MusicFX): **lee la licencia de cada uno** y guárdala en `licencias.md`. Pide "instrumental infantil, ukelele y xilófono, tempo ~100 bpm, sin voz".

### Edición y subtítulos
- **DaVinci Resolve (gratis):** 4K, sin marca de agua, sin límite de tiempo; edición, color y audio.
- **CapCut (gratis):** subtítulos automáticos, música y voz IA; exportación a 1080p.
- **YouTube Studio:** subir `.srt` (Subtítulos → Añadir idioma → Subir archivo).
- **Canva:** miniaturas (tu herramienta de diseño preferida).

## 3. Lista de requisitos antes de empezar

**Cuentas y equipo**
- [ ] Cuenta de Google (Flow, YouTube Studio, Drive para respaldo).
- [ ] Cuentas gratuitas en 2–3 generadores de video.
- [ ] Cuenta gratuita en un generador de imágenes.
- [ ] DaVinci Resolve y/o CapCut instalados.
- [ ] Canva.
- [ ] Ordenador con ~20 GB libres y buena conexión.

**Contenido y derechos**
- [ ] Biblia de personajes cerrada (`biblia-de-personajes.md`).
- [ ] Letras y música **originales** (no copiar canciones infantiles con derechos).
- [ ] Licencia de cada herramienta de voz/música guardada en `licencias.md`.
- [ ] Hojas de personajes descargadas y respaldadas (los enlaces temporales caducan).

**YouTube**
- [ ] Canal con verificación de teléfono.
- [ ] Marcar cada video como "contenido para niños".
- [ ] Declarar contenido alterado o generado con IA.
- [ ] Revisar las políticas vigentes de contenido infantil, IA y monetización (cambian).
- [ ] Miniatura y subtítulos `.srt` listos.

## 4. Tiempo y volumen estimados
- Video de 18–20 min: ~75–80 clips de 15 s, o ~200 clips de 5–6 s.
- Con ~66 créditos diarios de Kling (2–6 videos al día según resolución) son semanas por video largo: prioriza videos de **5–8 min** al empezar.
- Estrategia sugerida: un episodio = una canción (~3 min, 36 clips de 5 s), publicar uno por semana.

## 5. Herramienta de pago ya conectada (opcional)
Magnific está conectado en esta sesión (generación de video, imágenes, voz, música, unión de clips y mezcla de audio). Es de pago por créditos: un clip de 15 s a 720p costó 6.600 créditos, una narración de una escena unos 25 créditos, música de 5 min 6.000. No se usa sin tu autorización.

## Fuentes consultadas
- [Free AI Video Limits 2026: Kling 66/Day, Runway, Luma & Pika](https://whichoneisreal.com/compare/best-free-ai-video/)
- [Best Free AI Video Generators in 2026: What 9 Plans Actually Give You](https://novoads.ai/en/blog/best-free-ai-video-generators)
- [Best Free Video Editing Software 2026 Review](https://www.freevisuals.net/post/best-video-editing-software-in-2026-the-honest-guide-for-every-creator)
- [Best Free Text to Speech Tools in 2026](https://kidsstoryteller.ai/blog/best-free-text-to-speech-tools-2026)
- [8 Best Free AI Music Generators in 2026](https://www.elser.ai/blog/8-best-free-ai-music-generators-in-2026)
