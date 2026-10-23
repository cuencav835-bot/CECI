import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

interface RecetaIA {
  nombre: string;
  porciones: number;
  tiempoMin: number;
  ingredientes: string[];
  pasos: string[];
  kcalPorPorcion: number;
  nota: string;
}

interface Mensaje {
  rol: 'user' | 'assistant';
  texto: string;
}

const ENDPOINT = '/.netlify/functions/ia';

@Component({
  selector: 'app-asistente-ia',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './asistente-ia.component.html',
  styleUrl: './asistente-ia.component.css'
})
export class AsistenteIaComponent {
  pestana: 'receta' | 'chat' = 'receta';
  cargando = false;
  error = '';
  restantes: number | null = null;

  ingredientesTexto = '';
  restricciones: string[] = [];
  opciones = ['vegetariano', 'sin lactosa', 'sin gluten'];
  receta: RecetaIA | null = null;

  mensajes: Mensaje[] = [];
  pregunta = '';

  alternar(r: string): void {
    const k = this.restricciones.indexOf(r);
    if (k >= 0) this.restricciones.splice(k, 1); else this.restricciones.push(r);
  }

  get ingredientes(): string[] {
    return this.ingredientesTexto.split(/[,\n]/).map(x => x.trim()).filter(Boolean);
  }

  async generarReceta(): Promise<void> {
    if (this.ingredientes.length < 2 || this.cargando) return;
    this.receta = null;
    const datos = await this.enviar({ accion: 'receta', ingredientes: this.ingredientes, restricciones: this.restricciones });
    if (datos?.receta) this.receta = datos.receta;
  }

  async preguntar(): Promise<void> {
    const texto = this.pregunta.trim();
    if (!texto || this.cargando) return;
    this.mensajes.push({ rol: 'user', texto });
    this.pregunta = '';
    const datos = await this.enviar({ accion: 'chat', mensajes: this.mensajes });
    if (datos?.respuesta) this.mensajes.push({ rol: 'assistant', texto: datos.respuesta });
  }

  private async enviar(cuerpo: unknown): Promise<any | null> {
    this.cargando = true;
    this.error = '';
    try {
      const resp = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(cuerpo)
      });
      const datos = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        this.error = datos.error || 'No se pudo completar la consulta.';
        return null;
      }
      this.restantes = datos.restantes ?? null;
      return datos;
    } catch {
      this.error = 'No hay conexión con el asistente. Inténtalo de nuevo.';
      return null;
    } finally {
      this.cargando = false;
    }
  }
}
