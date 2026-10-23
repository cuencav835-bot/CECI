import test from 'node:test';
import assert from 'node:assert/strict';
import { manejar, leerConfig } from '../netlify/functions/lib/api.mjs';
import { crearStoreMemoria } from '../netlify/functions/lib/store.mjs';
import { firmarToken, verificarToken } from '../netlify/functions/lib/auth.mjs';
import { postprocesarReceta } from '../netlify/functions/lib/ia-core.mjs';

const config = { ...leerConfig({}), secreto: 'secreto-de-prueba', claveIA: 'k', limiteGratis: 2, limitePremium: 4, limiteGlobal: 100, hottok: 'tok' };
const RECETA = '{"nombre":"Arroz con pollo","porciones":4,"tiempoMin":40,"ingredientes":["arroz","pollo"],"pasos":["Cocinar"],"kcalPorPorcion":99999,"nota":""}';

function falsoModelo(texto, ok = true) {
  globalThis.fetch = async () => ({ ok, json: async () => ({ content: [{ type: 'text', text: texto }] }) });
}
const llamar = (store, accion, cuerpo = {}, token = '', hottok = '') => manejar({ accion, cuerpo, token, hottok }, store, config);
async function nuevoUsuario(store, email = 'ana@correo.com') {
  const r = await llamar(store, 'registro', { email, clave: 'clavesegura1', nombre: 'Ana' });
  assert.equal(r.estado, 200);
  return r.cuerpo.token;
}

test('registro, acceso y rechazo de clave incorrecta', async () => {
  const s = crearStoreMemoria();
  await nuevoUsuario(s);
  assert.equal((await llamar(s, 'registro', { email: 'ana@correo.com', clave: 'clavesegura1' })).estado, 409);
  assert.equal((await llamar(s, 'registro', { email: 'mal', clave: 'clavesegura1' })).estado, 400);
  assert.equal((await llamar(s, 'registro', { email: 'b@correo.com', clave: 'corta' })).estado, 400);
  assert.equal((await llamar(s, 'acceso', { email: 'ANA@correo.com', clave: 'clavesegura1' })).estado, 200);
  assert.equal((await llamar(s, 'acceso', { email: 'ana@correo.com', clave: 'incorrecta1' })).estado, 401);
  assert.equal((await llamar(s, 'acceso', { email: 'nadie@correo.com', clave: 'clavesegura1' })).estado, 401);
});

test('bloquea el acceso tras 5 intentos fallidos', async () => {
  const s = crearStoreMemoria();
  await nuevoUsuario(s);
  for (let k = 0; k < 5; k++) await llamar(s, 'acceso', { email: 'ana@correo.com', clave: 'incorrecta1' });
  assert.equal((await llamar(s, 'acceso', { email: 'ana@correo.com', clave: 'clavesegura1' })).estado, 429);
});

test('tokens: válido, manipulado y vencido', () => {
  const t = firmarToken('u1', 's');
  assert.equal(verificarToken(t, 's'), 'u1');
  assert.equal(verificarToken(t + 'x', 's'), null);
  assert.equal(verificarToken(t, 'otro'), null);
  assert.equal(verificarToken(firmarToken('u1', 's', 0), 's'), null);
});

test('sin sesión no se puede usar nada', async () => {
  const s = crearStoreMemoria();
  assert.equal((await llamar(s, 'yo')).estado, 401);
  assert.equal((await llamar(s, 'ia', { tipo: 'chat' }, 'falso')).estado, 401);
});

test('perfil se guarda y se sanea', async () => {
  const s = crearStoreMemoria();
  const t = await nuevoUsuario(s);
  const r = await llamar(s, 'guardarPerfil', { perfil: { objetivo: 'xx', personas: 99, restricciones: ['sin-gluten', 'raro'] } }, t);
  assert.deepEqual(r.cuerpo.usuario.perfil, { objetivo: 'mantener', personas: 10, restricciones: ['sin-gluten'], incluirSnack: true });
});

test('favoritos y menús: guardar, listar, borrar y no mezclar usuarios', async () => {
  const s = crearStoreMemoria();
  const t = await nuevoUsuario(s);
  const otro = await nuevoUsuario(s, 'luis@correo.com');
  let r = await llamar(s, 'guardarFavorito', { receta: JSON.parse(RECETA) }, t);
  assert.equal(r.cuerpo.usuario.favoritos.length, 1);
  assert.equal(r.cuerpo.usuario.favoritos[0].receta.kcalPorPorcion, 1800);
  assert.equal((await llamar(s, 'guardarFavorito', { receta: { nombre: 'x' } }, t)).estado, 400);
  r = await llamar(s, 'borrarFavorito', { id: r.cuerpo.usuario.favoritos[0].id }, t);
  assert.equal(r.cuerpo.usuario.favoritos.length, 0);
  r = await llamar(s, 'guardarMenu', { titulo: 'Semana 1', texto: 'LUNES\n- Desayuno: avena con plátano' }, t);
  assert.equal(r.cuerpo.usuario.menus.length, 1);
  assert.equal((await llamar(s, 'yo', {}, otro)).cuerpo.usuario.menus.length, 0);
  assert.equal((await llamar(s, 'guardarMenu', { texto: 'corto' }, t)).estado, 400);
});

test('IA: receta procesada, límite diario por usuario y restantes', async () => {
  const s = crearStoreMemoria();
  const t = await nuevoUsuario(s);
  falsoModelo('Claro:\n```json\n' + RECETA + '\n```');
  const pedido = { tipo: 'receta', ingredientes: ['pollo', 'arroz'] };
  let r = await llamar(s, 'ia', pedido, t);
  assert.equal(r.estado, 200);
  assert.equal(r.cuerpo.receta.nombre, 'Arroz con pollo');
  assert.equal(r.cuerpo.consultasRestantes, 1);
  assert.equal((await llamar(s, 'ia', pedido, t)).estado, 200);
  r = await llamar(s, 'ia', pedido, t);
  assert.equal(r.estado, 429);
  assert.equal(r.cuerpo.limiteAlcanzado, true);
  const otro = await nuevoUsuario(s, 'luis@correo.com');
  assert.equal((await llamar(s, 'ia', pedido, otro)).estado, 200);
});

test('IA: peticiones inválidas y fallos de la IA no gastan cupo', async () => {
  const s = crearStoreMemoria();
  const t = await nuevoUsuario(s);
  for (let k = 0; k < 4; k++) assert.equal((await llamar(s, 'ia', { tipo: 'receta', ingredientes: [] }, t)).estado, 400);
  falsoModelo('', false);
  const chat = { tipo: 'chat', mensajes: [{ rol: 'user', texto: 'hola' }] };
  for (let k = 0; k < 4; k++) {
    const r = await llamar(s, 'ia', chat, t);
    assert.equal(r.estado, 502);
    assert.ok(!/anthropic|clave/i.test(r.cuerpo.error));
  }
  falsoModelo('Come más verduras.');
  assert.equal((await llamar(s, 'ia', chat, t)).estado, 200);
});

test('tope global diario de la IA', async () => {
  const s = crearStoreMemoria();
  const t = await nuevoUsuario(s);
  falsoModelo('ok');
  const r = await manejar({ accion: 'ia', cuerpo: { tipo: 'chat', mensajes: [{ rol: 'user', texto: 'hola' }] }, token: t }, s, { ...config, limiteGlobal: 0 });
  assert.equal(r.estado, 429);
});

test('Hotmart: compra aprobada activa premium y reembolso lo quita', async () => {
  const s = crearStoreMemoria();
  const evento = tipo => ({ event: tipo, data: { buyer: { email: 'Ana@Correo.com' } } });
  assert.equal((await llamar(s, 'hotmart', evento('PURCHASE_APPROVED'), '', 'malo')).estado, 401);
  // compra antes de registrarse: el premium queda esperando a la cuenta
  assert.equal((await llamar(s, 'hotmart', evento('PURCHASE_APPROVED'), '', 'tok')).estado, 200);
  const t = await nuevoUsuario(s);
  let u = (await llamar(s, 'yo', {}, t)).cuerpo.usuario;
  assert.equal(u.plan, 'premium');
  assert.equal(u.consultasRestantes, 4);
  await llamar(s, 'hotmart', evento('PURCHASE_REFUNDED'), '', 'tok');
  u = (await llamar(s, 'yo', {}, t)).cuerpo.usuario;
  assert.equal(u.plan, 'gratis');
});

test('sin AUTH_SECRET el servidor se niega a operar', async () => {
  const r = await manejar({ accion: 'registro', cuerpo: { email: 'a@b.co', clave: 'clavesegura1' } }, crearStoreMemoria(), { ...config, secreto: '' });
  assert.equal(r.estado, 503);
});

test('postprocesar descarta lo que no es receta', () => {
  assert.equal(postprocesarReceta('no hay json'), null);
  assert.equal(postprocesarReceta('{"nombre":"x","ingredientes":[],"pasos":[]}'), null);
});

test('función completa: webhook de Hotmart por la dirección y método no permitido', async () => {
  process.env.AUTH_SECRET = 'secreto-de-prueba';
  process.env.HOTMART_HOTTOK = 'tok';
  const { default: funcion } = await import('../netlify/functions/api.mjs');
  const evento = JSON.stringify({ event: 'PURCHASE_APPROVED', data: { buyer: { email: 'compra@correo.com' } } });
  const pedir = (url, init) => funcion(new Request(url, init));

  assert.equal((await pedir('http://x/.netlify/functions/api?accion=hotmart', { method: 'POST', body: evento })).status, 401);
  assert.equal((await pedir('http://x/.netlify/functions/api?accion=hotmart', { method: 'POST', body: evento, headers: { 'X-HOTMART-HOTTOK': 'tok' } })).status, 200);
  assert.equal((await pedir('http://x/.netlify/functions/api', { method: 'GET' })).status, 405);
  assert.equal((await pedir('http://x/.netlify/functions/api', { method: 'POST', body: '{no es json' })).status, 400);
  // el cuerpo no puede hacerse pasar por el webhook sin la dirección
  assert.equal((await pedir('http://x/.netlify/functions/api', { method: 'POST', body: JSON.stringify({ accion: 'hotmart' }) })).status, 401);
});
