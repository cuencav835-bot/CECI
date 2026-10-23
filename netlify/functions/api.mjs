import { manejar } from './lib/api.mjs';
import { obtenerStore } from './lib/store.mjs';

const responder = (estado, cuerpo) =>
  new Response(JSON.stringify(cuerpo), { status: estado, headers: { 'content-type': 'application/json; charset=utf-8' } });

export default async req => {
  if (req.method !== 'POST') return responder(405, { error: 'Método no permitido.' });
  const texto = await req.text();
  if (texto.length > 20000) return responder(413, { error: 'Petición demasiado grande.' });

  let datos;
  try { datos = JSON.parse(texto || '{}'); } catch { return responder(400, { error: 'Petición inválida.' }); }

  // Hotmart envía su propio JSON (sin "accion"): su webhook se distingue por la dirección.
  const accion = new URL(req.url).searchParams.get('accion') === 'hotmart' ? 'hotmart' : datos.accion;

  const autorizacion = req.headers.get('authorization') || '';
  const r = await manejar(
    {
      accion,
      cuerpo: datos,
      token: autorizacion.startsWith('Bearer ') ? autorizacion.slice(7) : '',
      hottok: req.headers.get('x-hotmart-hottok') || ''
    },
    await obtenerStore()
  );
  return responder(r.estado, r.cuerpo);
};
