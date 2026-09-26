# CLAUDE.md — Manual de este espacio de trabajo

Este repositorio es el **sistema operativo de trabajo de Ceci** (Verónica Cecilia). No es solo un proyecto de código: es el lugar donde vive su contexto personal/de negocio, sus proyectos activos y sus plantillas reutilizables. Todo lo que Claude haga aquí debe partir de esta base, no de suposiciones.

## Qué es cada carpeta

```
MI SISTEMA OPERATIVO/
  CONTEXTO/     → quién es Ceci, su estilo, sus prioridades. Base de todo.
  PROYECTOS/    → cada negocio/proyecto concreto en el que trabaja.
  SKILL/        → plantillas y procesos reutilizables (recetas ya probadas).
```

- **CONTEXTO/**: información estable sobre Ceci como persona y como emprendedora. No es de un proyecto en concreto, es transversal a todos.
  - `perfil.md` — quién es, su trabajo actual, sus negocios/proyectos activos, qué vende.
  - `cliente-ideal.md` — a quién le vende (cuando aplique de forma general; si es por proyecto, se detalla también dentro de `PROYECTOS/<proyecto>/`).
  - `estilo-comunicacion.md` — tono y forma de comunicarse.
  - `prioridades.md` — en qué está enfocada ahora mismo.
- **PROYECTOS/**: una subcarpeta por cada proyecto/negocio activo (ej. `fun-kiss-youtube/`, `hotmart-resina/`). Cada uno documenta su propio estado, cliente ideal y pendientes.
- **SKILL/**: cosas reutilizables entre proyectos — plantillas de guiones, estructuras de copy, checklists, frameworks que ya funcionaron.

## Qué debe consultar Claude antes de ayudar

Antes de generar cualquier contenido, copy, estrategia o material para Ceci, Claude debe leer, en este orden:

1. **`MI SISTEMA OPERATIVO/CONTEXTO/`** completo (los 4 archivos) — para saber quién es Ceci, su estilo y sus prioridades actuales.
2. **La carpeta del proyecto específico** dentro de `MI SISTEMA OPERATIVO/PROYECTOS/` al que corresponde la tarea — para no repetir cliente ideal, estado o pendientes ya definidos, y para no contradecirlos.
3. **`MI SISTEMA OPERATIVO/SKILL/`** — para ver si ya existe una plantilla o proceso reutilizable aplicable, en vez de empezar desde cero.

Si la tarea no encaja claramente en ningún proyecto existente, preguntar a Ceci si es un proyecto nuevo (y crear su carpeta en `PROYECTOS/`) o si es solo una prueba puntual.

## Cómo usar el contexto (CONTEXTO/)

- Es la fuente de verdad sobre Ceci. Todo el contenido que se genere (guiones, textos, estrategias) debe ser coherente con su estilo (`estilo-comunicacion.md`) y no contradecir su `perfil.md` ni sus `prioridades.md`.
- **Nunca inventar** datos que falten en estos archivos (ej. cliente ideal no definido, tono para un proyecto específico). Si falta algo importante para hacer bien el trabajo, preguntarle a Ceci directamente en vez de asumir.
- Cuando Ceci dé información nueva o corrija algo, actualizar el archivo correspondiente en `CONTEXTO/` (no dejarlo solo en el chat) para que quede disponible en el futuro.
- Los archivos marcados como "pendiente" son campos abiertos: antes de asumir un valor, preguntar.

## Cómo tratar los proyectos activos (PROYECTOS/)

- Cada proyecto es independiente: tiene su propio cliente ideal, estado y pendientes, aunque comparta el `CONTEXTO/` general de Ceci.
- Antes de producir algo para un proyecto, revisar su README dentro de `PROYECTOS/<proyecto>/` para no repetir preguntas ya respondidas ni contradecir decisiones ya tomadas.
- Al avanzar en un proyecto (definir cliente ideal, cerrar un pendiente, tomar una decisión), actualizar el README de esa carpeta — no dejar el avance solo en la conversación.
- Si surge un proyecto nuevo, crear su carpeta en `PROYECTOS/<nombre-del-proyecto>/` con un README que documente: estado, cliente ideal, qué se vende, y pendientes.

## Cómo usar SKILL/

- `SKILL/` guarda procesos y plantillas que ya se probaron y funcionan (estructura de guion, framework de copy, checklist de lanzamiento, etc.), para reutilizarlos en distintos proyectos sin reinventar cada vez.
- Antes de crear un formato nuevo desde cero (un guion, un email, una landing), revisar si ya hay una plantilla aplicable en `SKILL/`.
- Cuando un proceso de un proyecto concreto resulte útil y repetible, extraerlo de `PROYECTOS/<proyecto>/` y guardarlo como plantilla genérica en `SKILL/`, quitando lo específico de ese proyecto.

## Regla general

No inventar información importante sobre Ceci, sus proyectos o sus clientes. Si no está en `CONTEXTO/` o en la carpeta del proyecto, y hace falta para avanzar bien, preguntar antes de asumir.
