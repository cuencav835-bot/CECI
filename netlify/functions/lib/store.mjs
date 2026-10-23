// Almacén clave-valor. En Netlify usa Netlify Blobs (persistente); en local, memoria.
export function crearStoreMemoria() {
  const datos = new Map();
  return {
    async get(clave) {
      const v = datos.get(clave);
      return v ? JSON.parse(v) : null;
    },
    async set(clave, valor) {
      datos.set(clave, JSON.stringify(valor));
    }
  };
}

async function crearStoreNetlify() {
  const { getStore } = await import('@netlify/blobs');
  const almacen = getStore('ceci');
  return {
    async get(clave) {
      return (await almacen.get(clave, { type: 'json' })) ?? null;
    },
    async set(clave, valor) {
      await almacen.setJSON(clave, valor);
    }
  };
}

let guardado;
export async function obtenerStore() {
  if (!guardado) guardado = typeof globalThis.Netlify !== 'undefined' ? await crearStoreNetlify() : crearStoreMemoria();
  return guardado;
}
