import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CuentaService, RecetaIA } from '../../services/cuenta.service';
import { buscarRecetas, responderBasico, SUGERENCIAS_CHAT } from '../../services/asistente-basico';
import { ENLACE_PREMIUM } from '../../config';

interface Mensaje {
  rol: 'user' | 'assistant';
  texto: string;
}

interface TarjetaReceta {
  receta: RecetaIA;
  /** Ingredientes clave que te faltan (solo en el modo básico). */
  faltan: string[];
  guardada: boolean;
}

@Component({
  selector: 'app-asistente-ia',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './asistente-ia.component.html',
  styleUrl: './asistente-ia.component.css'
})
export class AsistenteIaComponent {
  /** Básico: banco de recetas de la app, gratis y sin cuenta. IA: usa el servidor y gasta consultas. */
  modo: 'basico' | 'ia' = 'basico';
  pestana: 'receta' | 'chat' = 'receta';
  cargando = false;
  error = '';
  limiteAlcanzado = false;
  enlacePremium = ENLACE_PREMIUM;

  ingredientesTexto = '';
  restricciones: string[] = [];
  opciones = ['vegetariano', 'sin lactosa', 'sin gluten'];
  recetas: TarjetaReceta[] = [];
  sinResultados = false;

  mensajes: Mensaje[] = [];
  pregunta = '';
  sugerencias = SUGERENCIAS_CHAT;

  constructor(public cuenta: CuentaService) {}

  get usaIA(): boolean {
    return this.modo === 'ia';
  }

  get puedeConsultar(): boolean {
    return !this.cargando && (!this.usaIA || !!this.cuenta.usuario());
  }

  cambiarModo(modo: 'basico' | 'ia'): void {
    this.modo = modo;
    this.error = '';
    this.limiteAlcanzado = false;
  }

  alternar(r: string): void {
    const k = this.restricciones.indexOf(r);
    if (k >= 0) this.restricciones.splice(k, 1); else this.restricciones.push(r);
  }

  get ingredientes(): string[] {
    return this.ingredientesTexto.split(/[,\n]/).map(x => x.trim()).filter(Boolean);
  }

  async generarReceta(): Promise<void> {
    if (this.ingredientes.length < 2 || !this.puedeConsultar) return;
    this.recetas = [];
    this.sinResultados = false;
    this.error = '';

    if (!this.usaIA) {
      this.recetas = buscarRecetas(this.ingredientes, this.restricciones).map(c => ({
        receta: { ...c.receta, nota: c.receta.nota ?? '' },
        faltan: c.faltan,
        guardada: false
      }));
      this.sinResultados = this.recetas.length === 0;
      return;
    }

    const datos = await this.enviar({ tipo: 'receta', ingredientes: this.ingredientes, restricciones: this.restricciones });
    if (datos?.receta) this.recetas = [{ receta: datos.receta, faltan: [], guardada: false }];
  }

  async preguntar(texto = this.pregunta): Promise<void> {
    texto = texto.trim();
    if (!texto || !this.puedeConsultar) return;
    this.mensajes.push({ rol: 'user', texto });
    this.pregunta = '';
    this.error = '';

    if (!this.usaIA) {
      this.mensajes.push({ rol: 'assistant', texto: responderBasico(texto) });
      return;
    }
    const datos = await this.enviar({ tipo: 'chat', mensajes: this.mensajes });
    if (datos?.respuesta) this.mensajes.push({ rol: 'assistant', texto: datos.respuesta });
  }

  async guardarReceta(tarjeta: TarjetaReceta): Promise<void> {
    if (tarjeta.guardada) return;
    const { nombre, porciones, tiempoMin, ingredientes, pasos, kcalPorPorcion, nota } = tarjeta.receta;
    const error = await this.cuenta.actualizar('guardarFavorito', {
      receta: { nombre, porciones, tiempoMin, ingredientes, pasos, kcalPorPorcion, nota }
    });
    if (error) this.error = error; else tarjeta.guardada = true;
  }

  private async enviar(cuerpo: object): Promise<any | null> {
    this.cargando = true;
    this.error = '';
    this.limiteAlcanzado = false;
    const r = await this.cuenta.llamar('ia', cuerpo);
    this.cargando = false;
    if (!r.ok) {
      this.error = r.datos.error;
      this.limiteAlcanzado = Boolean(r.datos.limiteAlcanzado);
      return null;
    }
    const u = this.cuenta.usuario();
    if (u) this.cuenta.usuario.set({ ...u, consultasRestantes: r.datos.consultasRestantes });
    return r.datos;
  }
}
