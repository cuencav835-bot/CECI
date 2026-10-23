# CECI

VENTA DE PRODUCTOS DIGITALES AGENCIA DE MARKETING CON IA CREADOR DE CONTENIDO

## ¿Qué es esto?

Una pequeña app web (Angular) con "agentes" que te generan contenido listo para usar,
sin pagar nada ni necesitar cuentas de pago. Todo corre en tu navegador.

Agentes disponibles:

- **🛒 Agente de Ventas para Facebook**: escribe el nombre de tu producto de Hotmart,
  su beneficio principal y tu enlace de afiliado, y te genera 5 publicaciones distintas
  listas para pegar en tu página de Facebook.
- **📖 Agente de Cuentos para YouTube**: escribe el título, el personaje y la moraleja
  de tu cuento, y te genera el guion completo dividido en escenas, con una idea de
  imagen para cada una.
- **🥗 Agente de Menú Semanal +Salud**: elige tu objetivo (bajar, mantener o ganar masa),
  cuántas personas son y tus restricciones (vegetariano, sin lactosa, sin gluten) y te genera
  un menú de 7 días con lista de la compra agrupada, que puedes copiar o imprimir/guardar en PDF.
  Funciona sin IA de pago, con un banco de recetas propio. No sustituye a un nutricionista.
- **🤖 Asistente de Nutrición con IA**: receta con los ingredientes que tengas y chat nutricional.
  A diferencia de los otros agentes, este SÍ usa una IA de pago (Claude) y por eso corre en una
  función del servidor (`netlify/functions/ia.js`), nunca en el navegador, para no exponer la clave.

### Configurar el asistente con IA

1. En Netlify: *Site configuration → Environment variables* y crea `ANTHROPIC_API_KEY` con tu clave.
2. Opcional: `IA_LIMITE_USUARIO_DIA` (por defecto 10), `IA_LIMITE_GLOBAL_DIA` (por defecto 500, tope de gasto diario)
   e `IA_MODELO`.
3. Los límites se guardan en memoria: sirven de freno de costes pero se reinician si la función se
   recicla. Para un límite estricto por cuenta de usuario hace falta guardar los contadores en una base de datos.
4. Pruebas de la lógica: `npm run test:ia`. Para probar en tu computadora con la función: `npx netlify dev`.

## Cómo probarlo en tu computadora

1. Instala [Node.js](https://nodejs.org) (versión 18 o más nueva).
2. Abre una terminal en esta carpeta y ejecuta:
   ```
   npm install
   npm start
   ```
3. Abre tu navegador en `http://localhost:4200`.

## Cómo publicarlo gratis en internet

Cuando quieras que tu página esté disponible para todos (no solo en tu computadora),
puedes subirla gratis a [Netlify](https://www.netlify.com) o [Vercel](https://vercel.com):

1. Ejecuta `npm run build` (esto crea la carpeta `dist/ceci`).
2. Crea una cuenta gratis en Netlify o Vercel.
3. Sube la carpeta `dist/ceci` (o conecta tu repositorio de GitHub) y listo,
   tendrás un enlace público sin pagar nada.

## Notas

- No se usa ninguna API de pago: el contenido se genera con plantillas dentro
  del propio programa, así que no genera gastos.
- Las publicaciones y guiones son un buen primer borrador: revísalos y agrégales
  tu toque personal antes de publicarlos.
