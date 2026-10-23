import { Component, effect, untracked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CuentaService } from '../../services/cuenta.service';
import { Objetivo, Restriccion } from '../../services/menu.service';
import { ENLACE_PREMIUM } from '../../config';

@Component({
  selector: 'app-cuenta',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './cuenta.component.html',
  styleUrl: './cuenta.component.css'
})
export class CuentaComponent {
  enlacePremium = ENLACE_PREMIUM;
  mensaje = '';
  abierta: string | null = null;
  private perfilAplicado = false;

  objetivo: Objetivo = 'mantener';
  personas = 1;
  restricciones: Restriccion[] = [];
  incluirSnack = true;

  opciones: { valor: Restriccion; etiqueta: string }[] = [
    { valor: 'vegetariano', etiqueta: 'Vegetariano' },
    { valor: 'sin-lactosa', etiqueta: 'Sin lactosa' },
    { valor: 'sin-gluten', etiqueta: 'Sin gluten' }
  ];

  constructor(public cuenta: CuentaService, private router: Router) {
    effect(() => {
      const u = this.cuenta.usuario();
      if (u && !this.perfilAplicado) {
        untracked(() => {
          this.objetivo = u.perfil.objetivo;
          this.personas = u.perfil.personas;
          this.restricciones = [...u.perfil.restricciones];
          this.incluirSnack = u.perfil.incluirSnack;
        });
        this.perfilAplicado = true;
      }
    });
  }

  alternar(r: Restriccion): void {
    const k = this.restricciones.indexOf(r);
    if (k >= 0) this.restricciones.splice(k, 1); else this.restricciones.push(r);
  }

  async guardarPerfil(): Promise<void> {
    const error = await this.cuenta.actualizar('guardarPerfil', {
      perfil: { objetivo: this.objetivo, personas: this.personas, restricciones: this.restricciones, incluirSnack: this.incluirSnack }
    });
    this.mensaje = error || 'Perfil guardado ✅';
    setTimeout(() => (this.mensaje = ''), 2500);
  }

  borrarFavorito(id: string): void {
    this.cuenta.actualizar('borrarFavorito', { id });
  }

  borrarMenu(id: string): void {
    this.cuenta.actualizar('borrarMenu', { id });
  }

  copiar(texto: string): void {
    navigator.clipboard?.writeText(texto);
  }

  salir(): void {
    this.cuenta.salir();
    this.router.navigateByUrl('/');
  }
}
