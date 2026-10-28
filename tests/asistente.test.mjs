import test from 'node:test';
import assert from 'node:assert/strict';
import { build } from 'esbuild';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

// Compila el TypeScript de la app (sin Angular) a un módulo que Node pueda importar.
const salida = join(mkdtempSync(join(tmpdir(), 'asistente-')), 'asistente.mjs');
await build({
  stdin: {
    contents: "export * from './src/app/services/asistente-basico'; export * from './src/app/services/recetas-banco';",
    resolveDir: process.cwd(), loader: 'ts'
  },
  bundle: true, format: 'esm', outfile: salida, logLevel: 'silent'
});
const { buscarRecetas, responderBasico, BANCO_RECETAS, RESPUESTA_NO_ENTENDIDA, sinAcentos } = await import(pathToFileURL(salida).href);

test('banco: cada receta es completa y coherente', () => {
  const nombres = new Set();
  for (const r of BANCO_RECETAS) {
    assert.ok(!nombres.has(r.nombre), `nombre repetido: ${r.nombre}`);
    nombres.add(r.nombre);
    assert.ok(r.pasos.length >= 1 && r.ingredientes.length >= 2, r.nombre);
    assert.ok(r.kcalPorPorcion >= 50 && r.kcalPorPorcion <= 800, r.nombre);
    const texto = sinAcentos(r.ingredientes.join(' '));
    for (const p of r.principales) {
      assert.ok(texto.includes(sinAcentos(p).slice(0, 3)), `${r.nombre}: "${p}" no aparece en los ingredientes`);
    }
  }
  assert.ok(BANCO_RECETAS.length >= 30);
});

test('pollo, arroz, zanahoria encuentra el arroz con pollo sin faltantes', () => {
  const [primera] = buscarRecetas(['pollo', 'arroz', 'zanahoria']);
  assert.equal(primera.receta.nombre, 'Arroz con pollo y zanahoria');
  assert.deepEqual(primera.faltan, []);
});

test('entiende plurales, acentos y sinónimos', () => {
  const r = buscarRecetas(['Pechuga de pollo', 'Patatas', 'cebollas']);
  assert.equal(r[0].receta.nombre, 'Pollo al horno con papas');
  const h = buscarRecetas(['huevos', 'Tomates']);
  assert.ok(h.some(x => x.receta.nombre === 'Huevos revueltos con tomate'));
  assert.ok(buscarRecetas(['palta', 'pan', 'huevo']).some(x => x.receta.nombre === 'Tostada de aguacate con huevo'));
});

test('respeta las restricciones', () => {
  const veg = buscarRecetas(['pollo', 'arroz', 'zanahoria', 'huevo', 'tomate'], ['vegetariano'], 10);
  assert.ok(veg.length > 0 && veg.every(x => !x.receta.evita?.includes('vegetariano')));
  const sinGluten = buscarRecetas(['pasta', 'atún', 'tomate', 'arroz', 'pollo'], ['sin gluten'], 10);
  assert.ok(sinGluten.every(x => !x.receta.evita?.includes('sin-gluten')));
  const sinLactosa = buscarRecetas(['yogur', 'manzana', 'nueces'], ['sin lactosa'], 10);
  assert.ok(sinLactosa.every(x => !x.receta.evita?.includes('sin-lactosa')));
});

test('muestra qué ingredientes faltan y ordena por cobertura', () => {
  const r = buscarRecetas(['pollo', 'arroz']);
  assert.ok(r.length > 0 && r[0].cobertura >= r[r.length - 1].cobertura);
  assert.ok(r.some(x => x.faltan.length > 0));
});

test('sin coincidencias devuelve lista vacía', () => {
  assert.deepEqual(buscarRecetas(['chocolate', 'galletas']), []);
  assert.deepEqual(buscarRecetas([]), []);
  assert.deepEqual(buscarRecetas(['pollo']), []); // un solo ingrediente no alcanza
});

test('chat: responde por tema', () => {
  assert.match(responderBasico('¿Qué puedo cenar ligero?'), /cena ligera/i);
  assert.match(responderBasico('Quiero ganar masa muscular'), /proteína/i);
  assert.match(responderBasico('Hola'), /asistente básico/i);
  assert.match(responderBasico('¿Cuánta agua debo beber?'), /agua/i);
});

test('chat: temas médicos se derivan a un profesional', () => {
  for (const p of ['Tengo diabetes, ¿qué como?', 'Estoy embarazada y quiero bajar de peso', '¿Qué dieta para el colesterol?']) {
    assert.match(responderBasico(p), /médico o con un nutricionista/);
  }
});

test('chat: lo que no entiende lo dice y ofrece temas', () => {
  assert.equal(responderBasico('asdf qwer'), RESPUESTA_NO_ENTENDIDA);
});
