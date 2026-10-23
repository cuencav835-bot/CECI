'use strict';

const { procesar } = require('./lib/ia-core');

const json = (estado, cuerpo) => ({
  statusCode: estado,
  headers: { 'content-type': 'application/json; charset=utf-8' },
  body: JSON.stringify(cuerpo)
});

exports.handler = async event => {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Método no permitido.' });
  if ((event.body || '').length > 8000) return json(413, { error: 'Petición demasiado grande.' });

  let cuerpo;
  try { cuerpo = JSON.parse(event.body || '{}'); } catch { return json(400, { error: 'Petición inválida.' }); }

  const ip = event.headers['x-nf-client-connection-ip'] || event.headers['x-forwarded-for'] || 'desconocido';
  const r = await procesar(cuerpo, String(ip).split(',')[0].trim());
  return json(r.estado, r.cuerpo);
};
