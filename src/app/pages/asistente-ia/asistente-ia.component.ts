import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CuentaService, RecetaIA } from '../../services/cuenta.service';
import { ENLACE_PREMIUM } from '../../config';

interface Mensaje {
  rol: 'user' | 'assistant';
  texto: string;
}

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
  limiteAlcanzado = false;
  enlacePremium = ENLACE_PREMIUM;
  guardada = false;

  ingredientesTexto = '';
  restricciones: string[] = [];
  opciones = ['vegetariano', 'sin lactosa', 'sin gluten'];
  receta: RecetaIA | null = null;

  mensajes: Mensaje[] = [];
  pregunta = '';

  constructor(public cuenta: CuentaService) {}

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
    this.guardada = false;
    const datos = await this.enviar({ tipo: 'receta', ingredientes: this.ingredientes, restricciones: this.restricciones });
    if (datos?.receta) this.receta = datos.receta;
  }

  async preguntar(): Promise<void> {
    const texto = this.pregunta.trim();
    if (!texto || this.cargando) return;
    this.mensajes.push({ rol: 'user', texto });
    this.pregunta = '';
    const datos = await this.enviar({ tipo: 'chat', mensajes: this.mensajes });
    if (datos?.respuesta) this.mensajes.push({ rol: 'assistant', texto: datos.respuesta });
  }

  async guardarReceta(): Promise<void> {
    if (!this.receta || this.guardada) return;
    const error = await this.cuenta.actualizar('guardarFavorito', { receta: this.receta });
    if (error) this.error = error; else this.guardada = true;
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
