---
name: video-editing-social
description: Protocolo para crear y editar vídeos para Facebook e Instagram (Reels, Stories, Feed). Aplica a cualquier tarea de edición de vídeo para redes sociales — cortar clips, montar timelines, añadir subtítulos, adaptar formatos, generar vídeos con avatar IA, hacer highlight reels. Activación automática ante "edita este vídeo", "monta un vídeo", "crea un reel", "vídeo para Instagram/Facebook", "sube subtítulos", "recorta el vídeo", "adapta el vídeo a 9:16", "haz un highlight".
---

# Edición de vídeo para Facebook e Instagram — Protocolo

Reglas de trabajo para cualquier tarea de creación/edición de vídeo destinado a Facebook o Instagram. No son sugerencias — son el protocolo a seguir siempre.

---

## A. Formatos según dónde se publica

Antes de editar, confirma dónde va a publicarse el vídeo (si no está claro, pregunta) y usa el formato correcto:

| Destino | Aspect ratio | Duración recomendada |
|---|---|---|
| Reels (IG y FB) | 9:16 (vertical) | 15-30s (máx ~90s) |
| Stories (IG y FB) | 9:16 (vertical) | 5-15s por tarjeta |
| Feed IG | 4:5 (vertical) o 1:1 (cuadrado) | 30-60s |
| Feed FB | 1:1 o 16:9 | 30-90s |

Si el material fuente viene en otro formato (ej. 16:9 de una grabación), usa `video_resize` (Adobe) para adaptarlo — nunca estires la imagen, recorta de forma inteligente centrando el sujeto.

## B. Subtítulos SIEMPRE quemados

La mayoría de la gente ve vídeos en Facebook e Instagram **sin sonido** (scrolleando en el móvil). Regla fija:

- Todo vídeo lleva subtítulos incrustados (quemados), sincronizados con la voz.
- Si el vídeo se compone con HyperFrames (`compose`), los subtítulos se generan automáticamente — verifica que estén activados en el resultado.
- Si el material es un rodaje sin locución, no hace falta subtítulo, pero sí texto en pantalla resumiendo el mensaje clave.

## C. El gancho de los primeros 3 segundos

En Reels y Stories, el algoritmo mide si la gente sigue viendo tras el primer segundo. Regla fija:

- Los primeros 3 segundos deben mostrar lo más llamativo del vídeo (no una intro con logo o silencio).
- Evita "intros" largas de marca al principio — si hay branding, va al final o como marca de agua discreta.
- Si el vídeo viene de una grabación larga, usa `video_create_quick_cut` para detectar los momentos más atractivos como candidatos de apertura.

## D. Zonas seguras (safe zones)

En formato 9:16, Instagram y Facebook superponen su propia interfaz (nombre de usuario, iconos de like/comentar, barra de progreso) sobre el vídeo. Regla fija:

- No coloques texto ni elementos importantes en el 15% superior ni en el 20% inferior del cuadro vertical — ahí es donde va la UI de la plataforma.
- Si generas el vídeo con HyperFrames, revisa el preview antes de renderizar para confirmar que ningún texto queda tapado.

## E. Herramientas disponibles en este entorno

Según el tipo de material fuente, usa la herramienta adecuada:

- **Grabación larga que hay que resumir/recortar** → `video_create_quick_cut` (highlight reel automático a partir de los momentos más atractivos).
- **Vídeo con presentador/avatar IA, subtítulos, branding y storytelling** → `HyperFrames compose` (autoría por lenguaje natural, iterativo) y `render_video` para el MP4 final.
- **Adaptar un vídeo ya existente a otro aspect ratio** → `video_resize`.
- **Montaje con timeline propio (varios clips, transiciones, audio)** → `video_render` con el documento de timeline.
- **Revisar un fotograma concreto antes de confirmar un corte** → `video_render_frame`.

No renderices el MP4 final (acción de pago, `render_video`/`video_render`) hasta que el usuario haya visto y aprobado un preview o borrador.

## F. Flujo de aprobación (igual que con contenido escrito)

1. Genera un primer borrador/preview (no el render final).
2. Enséñaselo al usuario: formato, duración, y si tiene subtítulos.
3. Pregunta si el tono/ritmo/gancho le convence.
4. Aplica ajustes concretos que pida.
5. Solo entonces, renderiza el vídeo final y entrega el link de descarga.

## G. Reporte final

Al entregar un vídeo terminado, incluye siempre:

- ✅ Formato y duración final (ej. "9:16, 22 segundos, para Reels")
- 📝 Si lleva subtítulos quemados o no
- 🔗 Link de descarga del MP4
- ⚠️ Cualquier limitación (ej. "el highlight reel se basa en atractivo visual, no en lo que se dice — revisa que el corte tenga sentido narrativo")

---

## Cómo se invoca esta skill

Se carga automáticamente al detectar tareas de edición de vídeo para redes (keywords del frontmatter). También puede invocarse manualmente con `/video-editing-social`.
