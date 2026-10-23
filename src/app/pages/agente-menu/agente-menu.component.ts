import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
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

  restriccionesDisponibles: { valor: Restriccion; etiqueta: string }[] = [
    { valor: 'vegetariano', etiqueta: 'Vegetariano' },
    { valor: 'sin-lactosa', etiqueta: 'Sin lactosa' },
    { valor: 'sin-gluten', etiqueta: 'Sin gluten' }
  ];

  constructor(private servicio: MenuService) {}

  alternar(r: Restriccion): void {
    const k = this.datos.restricciones.indexOf(r);
    if (k >= 0) this.datos.restricciones.splice(k, 1); else this.datos.restricciones.push(r);
  }

  generar(): void {
    this.menu = this.servicio.generarMenu(this.datos);
  }

  copiar(): void {
    if (!this.menu || !navigator.clipboard) return;
    navigator.clipboard.writeText(this.servicio.textoMenu(this.menu)).then(() => {
      this.copiado = true;
      setTimeout(() => (this.copiado = false), 1500);
    });
  }

  imprimir(): void {
    window.print();
  }
}
