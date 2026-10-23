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
  A diferencia de los otros agentes, este SÍ usa una IA de pago (Claude) y corre en una función
  del servidor (`netlify/functions/api.mjs`), nunca en el navegador, para no exponer la clave.
- **👤 Cuentas**: registro e inicio de sesión, perfil (objetivo, personas, restricciones), recetas
  favoritas y menús guardados. Los datos se guardan en Netlify Blobs.

### Poner a funcionar las cuentas y la IA (una sola vez)

En Netlify: *Site configuration → Environment variables*:

| Variable | Para qué | Obligatoria |
|---|---|---|
| `AUTH_SECRET` | Firma las sesiones. Pon un texto largo y aleatorio (32+ caracteres) y no lo compartas. | Sí |
| `ANTHROPIC_API_KEY` | Clave de la IA (Claude). Cada consulta cuesta dinero. | Sí, para el asistente |
| `HOTMART_HOTTOK` | Token del webhook de Hotmart para activar Premium al comprar. | Para vender Premium |
| `IA_LIMITE_GRATIS_DIA` / `IA_LIMITE_PREMIUM_DIA` | Consultas con IA por día (5 y 50 por defecto). | No |
| `IA_LIMITE_GLOBAL_DIA` | Tope total de consultas al día entre todos (500). Es tu freno de gasto. | No |
| `IA_MODELO` | Modelo de IA (por defecto `claude-haiku-5-5`, el más barato). | No |

Los límites cuentan por cuenta de usuario y se guardan en la base de datos, así que no se saltan
recargando la página. Una consulta que falla no se descuenta.

### Vender el plan Premium con Hotmart

1. Crea el producto Premium en Hotmart y copia su enlace de pago en `src/app/config.ts` (`ENLACE_PREMIUM`).
2. En Hotmart: *Herramientas → Webhook (Postback)*, URL
   `https://TU-SITIO.netlify.app/.netlify/functions/api?accion=hotmart`, con los eventos de compra
   aprobada, reembolso, cancelación y contracargo. Copia el *hottok* a la variable `HOTMART_HOTTOK`.
3. Quien compre con el mismo correo de su cuenta pasa a Premium automáticamente (y vuelve a Gratis si
   hay reembolso o cancelación).

> El webhook de Hotmart está hecho según su documentación, pero no se ha probado con una compra real:
> haz una compra de prueba antes de anunciar el Premium.

### Pruebas

`npm run test:api` (lógica del servidor: cuentas, límites, IA simulada, Hotmart).

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
