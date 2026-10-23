import { Component, effect, untracked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CuentaService } from '../../services/cuenta.service';
import { DatosMenu, MenuService, MenuSemanal, Restriccion } from '../../services/menu.service';

@Component({
  selector: 'app-agente-menu',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './agente-menu.component.html',
  styleUrl: './agente-menu.component.css'
})
export class AgenteMenuComponent {
  datos: DatosMenu = { objetivo: 'bajar', personas: 1, restricciones: [], incluirSnack: true };
  menu: MenuSemanal | null = null;
  copiado = false;
  private perfilAplicado = false;
  guardado = false;
  errorGuardar = '';

  restriccionesDisponibles: { valor: Restriccion; etiqueta: string }[] = [
    { valor: 'vegetariano', etiqueta: 'Vegetariano' },
    { valor: 'sin-lactosa', etiqueta: 'Sin lactosa' },
    { valor: 'sin-gluten', etiqueta: 'Sin gluten' }
  ];

  constructor(private servicio: MenuService, public cuenta: CuentaService) {
    // La sesión puede restaurarse después de crear la pantalla (al recargar): se aplica el perfil una vez.
    effect(() => {
      const u = this.cuenta.usuario();
      if (u && !this.perfilAplicado) {
        untracked(() => (this.datos = { ...u.perfil, restricciones: [...u.perfil.restricciones] }));
        this.perfilAplicado = true;
      }
    });
  }

  alternar(r: Restriccion): void {
    const k = this.datos.restricciones.indexOf(r);
    if (k >= 0) this.datos.restricciones.splice(k, 1); else this.datos.restricciones.push(r);
  }

  generar(): void {
    this.menu = this.servicio.generarMenu(this.datos);
    this.guardado = false;
    this.errorGuardar = '';
  }

  copiar(): void {
    if (!this.menu || !navigator.clipboard) return;
    navigator.clipboard.writeText(this.servicio.textoMenu(this.menu)).then(() => {
      this.copiado = true;
      setTimeout(() => (this.copiado = false), 1500);
    });
  }

  async guardar(): Promise<void> {
    if (!this.menu || this.guardado) return;
    const etiqueta = { bajar: 'Bajar de peso', mantener: 'Mantener peso', subir: 'Ganar masa' }[this.datos.objetivo];
    this.errorGuardar = await this.cuenta.actualizar('guardarMenu', {
      titulo: `Menú ${etiqueta} (${this.datos.personas} pers.)`,
      texto: this.servicio.textoMenu(this.menu)
    });
    this.guardado = !this.errorGuardar;
  }

  imprimir(): void {
    window.print();
  }
}
