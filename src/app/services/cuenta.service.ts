import { Injectable, signal } from '@angular/core';
import { DatosMenu } from './menu.service';

export interface RecetaIA {
  nombre: string;
  porciones: number;
  tiempoMin: number;
  ingredientes: string[];
  pasos: string[];
  kcalPorPorcion: number;
  nota: string;
}

export interface Usuario {
  email: string;
  nombre: string;
  plan: 'gratis' | 'premium';
  perfil: DatosMenu;
  favoritos: { id: string; fecha: number; receta: RecetaIA }[];
  menus: { id: string; fecha: number; titulo: string; texto: string }[];
  consultasRestantes: number;
}

export interface Respuesta {
  ok: boolean;
  datos: any;
}

const CLAVE_TOKEN = 'ceci_token';
const ENDPOINT = '/.netlify/functions/api';

@Injectable({ providedIn: 'root' })
export class CuentaService {
  usuario = signal<Usuario | null>(null);
  cargando = signal(true);
  private token = this.leerToken();

  /** Restaura la sesión guardada al abrir la app. */
  async iniciar(): Promise<void> {
    if (this.token) {
      const r = await this.llamar('yo');
      if (r.ok) this.usuario.set(r.datos.usuario);
      else if (r.datos.sesionVencida) this.salir();
    }
    this.cargando.set(false);
  }

  async registro(nombre: string, email: string, clave: string): Promise<string> {
    return this.entrar(await this.llamar('registro', { nombre, email, clave }));
  }

  async acceso(email: string, clave: string): Promise<string> {
    return this.entrar(await this.llamar('acceso', { email, clave }));
  }

  salir(): void {
    this.token = '';
    this.usuario.set(null);
    try { localStorage.removeItem(CLAVE_TOKEN); } catch { /* sin almacenamiento */ }
  }

  /** Acciones que devuelven el usuario actualizado (perfil, favoritos, menús). */
  async actualizar(accion: string, datos: object = {}): Promise<string> {
    const r = await this.llamar(accion, datos);
    if (r.ok) this.usuario.set(r.datos.usuario);
    return r.ok ? '' : r.datos.error;
  }

  async llamar(accion: string, datos: object = {}): Promise<Respuesta> {
    try {
      const resp = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'content-type': 'application/json', ...(this.token ? { authorization: `Bearer ${this.token}` } : {}) },
        body: JSON.stringify({ accion, ...datos })
      });
      const cuerpo = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        return { ok: false, datos: { ...cuerpo, error: cuerpo.error || 'No se pudo completar la acción.', sesionVencida: resp.status === 401 } };
      }
      return { ok: true, datos: cuerpo };
    } catch {
      return { ok: false, datos: { error: 'No hay conexión con el servidor. Inténtalo de nuevo.' } };
    }
  }

  private entrar(r: Respuesta): string {
    if (!r.ok) return r.datos.error;
    this.token = r.datos.token;
    try { localStorage.setItem(CLAVE_TOKEN, this.token); } catch { /* sin almacenamiento */ }
    this.usuario.set(r.datos.usuario);
    return '';
  }

  private leerToken(): string {
    try { return localStorage.getItem(CLAVE_TOKEN) || ''; } catch { return ''; }
  }
}
