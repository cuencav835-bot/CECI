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
