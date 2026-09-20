import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DatosCuento, GeneradorService, GuionCuento } from '../../services/generador.service';

@Component({
  selector: 'app-agente-cuentos',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './agente-cuentos.component.html',
  styleUrl: './agente-cuentos.component.css'
})
export class AgenteCuentosComponent {
  datos: DatosCuento = {
    titulo: '',
    personaje: '',
    moraleja: '',
    duracion: '10'
  };

  guion: GuionCuento | null = null;
  copiado = false;

  constructor(private generador: GeneradorService) {}

  get formularioValido(): boolean {
    return this.datos.titulo.trim().length > 0 &&
      this.datos.personaje.trim().length > 0 &&
      this.datos.moraleja.trim().length > 0;
  }

  generar(): void {
    if (!this.formularioValido) return;
    this.guion = this.generador.generarGuionCuento(this.datos);
  }

  textoCompleto(): string {
    if (!this.guion) return '';
    const partes = this.guion.escenas.map(
      (e) => `## ${e.nombre}\n${e.texto}\n(Imagen sugerida: ${e.imagenSugerida})`
    );
    return `# ${this.guion.titulo}\n\n${partes.join('\n\n')}`;
  }

  copiar(): void {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(this.textoCompleto()).then(() => {
        this.copiado = true;
        setTimeout(() => (this.copiado = false), 1500);
      });
    }
  }
}
