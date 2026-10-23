'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');

process.env.IA_LIMITE_USUARIO_DIA = '2';
process.env.ANTHROPIC_API_KEY = 'clave-de-prueba';
const core = require('../netlify/functions/lib/ia-core');

function falsoModelo(texto, ok = true) {
  globalThis.fetch = async () => ({ ok, json: async () => ({ content: [{ type: 'text', text: texto }] }) });
}

test.beforeEach(() => core.reiniciarContadores());

test('valida: receta necesita al menos 2 ingredientes', () => {
  assert.ok(core.validar({ accion: 'receta', ingredientes: ['pollo'] }).error);
  assert.equal(core.validar({ accion: 'receta', ingredientes: ['pollo', 'arroz'] }).ingredientes.length, 2);
});

test('valida: el chat debe terminar en pregunta del usuario', () => {
  assert.ok(core.validar({ accion: 'chat', mensajes: [{ rol: 'assistant', texto: 'hola' }] }).error);
  assert.equal(core.validar({ accion: 'chat', mensajes: [{ rol: 'user', texto: '¿Qué ceno?' }] }).mensajes.length, 1);
});

test('postprocesa JSON envuelto en texto y limita valores', () => {
  const r = core.postprocesarReceta('Aquí va:\n```json\n{"nombre":"Arroz con pollo","porciones":4,"tiempoMin":40,' +
    '"ingredientes":["arroz","pollo"],"pasos":["Cocinar"],"kcalPorPorcion":99999,"nota":""}\n```');
  assert.equal(r.nombre, 'Arroz con pollo');
  assert.equal(r.kcalPorPorcion, 1800);
});

test('descarta respuestas que no son una receta válida', () => {
  assert.equal(core.postprocesarReceta('no hay json'), null);
  assert.equal(core.postprocesarReceta('{"nombre":"x","ingredientes":[],"pasos":[]}'), null);
});

test('límite por usuario: la tercera llamada recibe 429', async () => {
  falsoModelo('Come más verduras.');
  const pedido = { accion: 'chat', mensajes: [{ rol: 'user', texto: 'hola' }] };
  assert.equal((await core.procesar(pedido, 'u1')).estado, 200);
  assert.equal((await core.procesar(pedido, 'u1')).estado, 200);
  assert.equal((await core.procesar(pedido, 'u1')).estado, 429);
  assert.equal((await core.procesar(pedido, 'u2')).estado, 200);
});

test('las peticiones inválidas no gastan cupo', async () => {
  falsoModelo('x');
  for (let k = 0; k < 5; k++) await core.procesar({ accion: 'receta', ingredientes: [] }, 'u1');
  assert.equal((await core.procesar({ accion: 'chat', mensajes: [{ rol: 'user', texto: 'hola' }] }, 'u1')).estado, 200);
});

test('si la IA falla devuelve error sin filtrar detalles', async () => {
  falsoModelo('', false);
  const r = await core.procesar({ accion: 'chat', mensajes: [{ rol: 'user', texto: 'hola' }] }, 'u1');
  assert.equal(r.estado, 502);
  assert.ok(!/api\.anthropic|clave/i.test(r.cuerpo.error));
});
