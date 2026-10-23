import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CuentaService } from '../../services/cuenta.service';

@Component({
  selector: 'app-acceso',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './acceso.component.html',
  styleUrl: './acceso.component.css'
})
export class AccesoComponent {
  modoRegistro = false;
  nombre = '';
  email = '';
  clave = '';
  error = '';
  enviando = false;

  constructor(private cuenta: CuentaService, private router: Router) {}

  async enviar(): Promise<void> {
    if (this.enviando) return;
    this.enviando = true;
    this.error = this.modoRegistro
      ? await this.cuenta.registro(this.nombre, this.email, this.clave)
      : await this.cuenta.acceso(this.email, this.clave);
    this.enviando = false;
    if (!this.error) this.router.navigateByUrl('/cuenta');
  }
}
