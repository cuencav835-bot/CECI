import { createHash, createHmac, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';

const DURACION_TOKEN_MS = 30 * 24 * 60 * 60 * 1000;

export const uidDe = email => createHash('sha256').update(email).digest('hex').slice(0, 24);

export function hashearClave(clave) {
  const sal = randomBytes(16).toString('hex');
  return { sal, hash: scryptSync(clave, sal, 64).toString('hex') };
}

export function claveCorrecta(clave, sal, hash) {
  const a = scryptSync(clave, sal, 64);
  const b = Buffer.from(hash, 'hex');
  return a.length === b.length && timingSafeEqual(a, b);
}

const b64 = s => Buffer.from(s).toString('base64url');

export function firmarToken(uid, secreto, ahora = Date.now()) {
  const cuerpo = b64(JSON.stringify({ uid, exp: ahora + DURACION_TOKEN_MS }));
  const firma = createHmac('sha256', secreto).update(cuerpo).digest('base64url');
  return `${cuerpo}.${firma}`;
}

export function verificarToken(token, secreto, ahora = Date.now()) {
  if (typeof token !== 'string' || !secreto) return null;
  const [cuerpo, firma] = token.split('.');
  if (!cuerpo || !firma) return null;
  const esperada = createHmac('sha256', secreto).update(cuerpo).digest('base64url');
  const a = Buffer.from(firma);
  const b = Buffer.from(esperada);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  try {
    const datos = JSON.parse(Buffer.from(cuerpo, 'base64url').toString());
    return datos.exp > ahora && typeof datos.uid === 'string' ? datos.uid : null;
  } catch {
    return null;
  }
}
