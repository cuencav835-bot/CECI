import { claveCorrecta, firmarToken, hashearClave, uidDe, verificarToken } from './auth.mjs';
import { consultarIA, limpiar, normalizarReceta, validarPeticionIA } from './ia-core.mjs';

const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,255}\.[^\s@]{2,}$/;
const OBJETIVOS = ['bajar', 'mantener', 'subir'];
const RESTRICCIONES = ['vegetariano', 'sin-lactosa', 'sin-gluten'];
const MAX_FAVORITOS = 100;
const MAX_MENUS = 20;
const MAX_INTENTOS = 5;
const BLOQUEO_MS = 15 * 60 * 1000;
const EVENTOS_ALTA = ['PURCHASE_APPROVED', 'PURCHASE_COMPLETE'];
const EVENTOS_BAJA = ['PURCHASE_CANCELED', 'PURCHASE_REFUNDED', 'PURCHASE_CHARGEBACK', 'SUBSCRIPTION_CANCELLATION'];

export function leerConfig(env = process.env) {
  return {
    secreto: env.AUTH_SECRET || '',
    claveIA: env.ANTHROPIC_API_KEY || '',
    modelo: env.IA_MODELO || 'claude-haiku-5-5',
    limiteGratis: Number(env.IA_LIMITE_GRATIS_DIA || 5),
    limitePremium: Number(env.IA_LIMITE_PREMIUM_DIA || 50),
    limiteGlobal: Number(env.IA_LIMITE_GLOBAL_DIA || 500),
    hottok: env.HOTMART_HOTTOK || ''
  };
}

const ok = (cuerpo = {}) => ({ estado: 200, cuerpo });
const fallo = (estado, error) => ({ estado, cuerpo: { error } });
const claveUsuario = uid => `u/${uid}`;
const hoy = () => new Date().toISOString().slice(0, 10);
const id = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36);

function validarPerfil(p) {
  if (!p || typeof p !== 'object') return null;
  return {
    objetivo: OBJETIVOS.includes(p.objetivo) ? p.objetivo : 'mantener',
    personas: Math.min(10, Math.max(1, Math.floor(Number(p.personas)) || 1)),
    restricciones: (Array.isArray(p.restricciones) ? p.restricciones : []).filter(r => RESTRICCIONES.includes(r)),
    incluirSnack: p.incluirSnack !== false
  };
}

async function esPremium(store, uid) {
  return Boolean((await store.get(`premium/${uid}`))?.activo);
}

async function vistaUsuario(store, usuario, uid, config) {
  const premium = await esPremium(store, uid);
  const limite = premium ? config.limitePremium : config.limiteGratis;
  const usadas = (await store.get(`cupo/${uid}/${hoy()}`))?.n || 0;
  return {
    email: usuario.email,
    nombre: usuario.nombre,
    plan: premium ? 'premium' : 'gratis',
    perfil: usuario.perfil,
    favoritos: usuario.favoritos,
    menus: usuario.menus,
    consultasRestantes: Math.max(0, limite - usadas)
  };
}

async function registro(store, cuerpo, config) {
  const email = limpiar(cuerpo.email).toLowerCase();
  const nombre = limpiar(cuerpo.nombre).slice(0, 60);
  const clave = String(cuerpo.clave ?? '');
  if (!EMAIL.test(email)) return fallo(400, 'Escribe un correo válido.');
  if (clave.length < 8 || clave.length > 100) return fallo(400, 'La contraseña debe tener al menos 8 caracteres.');
  const uid = uidDe(email);
  if (await store.get(claveUsuario(uid))) return fallo(409, 'Ese correo ya tiene una cuenta. Inicia sesión.');
  const usuario = {
    email, nombre: nombre || email.split('@')[0], ...hashearClave(clave),
    perfil: { objetivo: 'mantener', personas: 1, restricciones: [], incluirSnack: true },
    favoritos: [], menus: [], intentos: { n: 0, hasta: 0 }
  };
  await store.set(claveUsuario(uid), usuario);
  return ok({ token: firmarToken(uid, config.secreto), usuario: await vistaUsuario(store, usuario, uid, config) });
}

async function acceso(store, cuerpo, config) {
  const email = limpiar(cuerpo.email).toLowerCase();
  const uid = uidDe(email);
  const usuario = await store.get(claveUsuario(uid));
  const generico = fallo(401, 'Correo o contraseña incorrectos.');
  if (!usuario) return generico;
  if (usuario.intentos.hasta > Date.now()) return fallo(429, 'Demasiados intentos. Espera unos minutos.');
  if (!claveCorrecta(String(cuerpo.clave ?? ''), usuario.sal, usuario.hash)) {
    usuario.intentos.n += 1;
    if (usuario.intentos.n >= MAX_INTENTOS) usuario.intentos = { n: 0, hasta: Date.now() + BLOQUEO_MS };
    await store.set(claveUsuario(uid), usuario);
    return generico;
  }
  usuario.intentos = { n: 0, hasta: 0 };
  await store.set(claveUsuario(uid), usuario);
  return ok({ token: firmarToken(uid, config.secreto), usuario: await vistaUsuario(store, usuario, uid, config) });
}

async function consultaIA(store, usuario, uid, cuerpo, config) {
  const v = validarPeticionIA(cuerpo);
  if (v.error) return fallo(400, v.error);

  const dia = hoy();
  const global = (await store.get(`cupo/global/${dia}`))?.n || 0;
  if (global >= config.limiteGlobal) return fallo(429, 'El servicio está muy solicitado hoy. Inténtalo mañana.');
  const limite = (await esPremium(store, uid)) ? config.limitePremium : config.limiteGratis;
  const usadas = (await store.get(`cupo/${uid}/${dia}`))?.n || 0;
  if (usadas >= limite) {
    return { estado: 429, cuerpo: { error: 'Llegaste al límite de consultas de hoy.', limiteAlcanzado: true } };
  }

  // Se descuenta antes de llamar a la IA para que no se pueda saltar el límite con peticiones paralelas lentas.
  await store.set(`cupo/${uid}/${dia}`, { n: usadas + 1 });
  await store.set(`cupo/global/${dia}`, { n: global + 1 });
  try {
    const r = await consultarIA(v, config);
    return ok({ ...r, consultasRestantes: limite - usadas - 1 });
  } catch (e) {
    // La consulta fallida no cuenta contra el usuario.
    await store.set(`cupo/${uid}/${dia}`, { n: usadas });
    return fallo(e.estado || 500, e.message || 'Error inesperado.');
  }
}

async function hotmart(store, cuerpo, hottok, config) {
  if (!config.hottok || hottok !== config.hottok) return fallo(401, 'No autorizado.');
  const email = limpiar(cuerpo?.data?.buyer?.email).toLowerCase();
  if (!EMAIL.test(email)) return fallo(400, 'Evento sin correo.');
  const uid = uidDe(email);
  if (EVENTOS_ALTA.includes(cuerpo.event)) await store.set(`premium/${uid}`, { activo: true, desde: Date.now() });
  else if (EVENTOS_BAJA.includes(cuerpo.event)) await store.set(`premium/${uid}`, { activo: false, hasta: Date.now() });
  return ok();
}

export async function manejar({ accion, cuerpo = {}, token, hottok }, store, config = leerConfig()) {
  if (accion === 'hotmart') return hotmart(store, cuerpo, hottok, config);
  if (!config.secreto) return fallo(503, 'El servidor no está configurado todavía.');
  if (accion === 'registro') return registro(store, cuerpo, config);
  if (accion === 'acceso') return acceso(store, cuerpo, config);

  const uid = verificarToken(token, config.secreto);
  const usuario = uid && (await store.get(claveUsuario(uid)));
  if (!usuario) return fallo(401, 'Inicia sesión para continuar.');
  const guardar = () => store.set(claveUsuario(uid), usuario);
  const vista = async () => ok({ usuario: await vistaUsuario(store, usuario, uid, config) });

  switch (accion) {
    case 'yo':
      return vista();
    case 'guardarPerfil': {
      const perfil = validarPerfil(cuerpo.perfil);
      if (!perfil) return fallo(400, 'Perfil inválido.');
      usuario.perfil = perfil;
      await guardar();
      return vista();
    }
    case 'guardarFavorito': {
      const receta = normalizarReceta(cuerpo.receta);
      if (!receta) return fallo(400, 'Receta inválida.');
      if (usuario.favoritos.length >= MAX_FAVORITOS) return fallo(400, 'Llegaste al máximo de recetas guardadas.');
      usuario.favoritos.unshift({ id: id(), fecha: Date.now(), receta });
      await guardar();
      return vista();
    }
    case 'borrarFavorito':
      usuario.favoritos = usuario.favoritos.filter(f => f.id !== cuerpo.id);
      await guardar();
      return vista();
    case 'guardarMenu': {
      const texto = String(cuerpo.texto ?? '').slice(0, 8000);
      if (texto.length < 20) return fallo(400, 'Menú inválido.');
      if (usuario.menus.length >= MAX_MENUS) usuario.menus.pop();
      usuario.menus.unshift({ id: id(), fecha: Date.now(), titulo: limpiar(cuerpo.titulo).slice(0, 80) || 'Menú semanal', texto });
      await guardar();
      return vista();
    }
    case 'borrarMenu':
      usuario.menus = usuario.menus.filter(m => m.id !== cuerpo.id);
      await guardar();
      return vista();
    case 'ia':
      return consultaIA(store, usuario, uid, cuerpo, config);
    default:
      return fallo(400, 'Acción no válida.');
  }
}
