import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DatosVentaFacebook, GeneradorService, PostFacebook } from '../../services/generador.service';

@Component({
  selector: 'app-agente-ventas',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './agente-ventas.component.html',
  styleUrl: './agente-ventas.component.css'
})
export class AgenteVentasComponent {
  datos: DatosVentaFacebook = {
    producto: '',
    beneficio: '',
    precioOferta: '',
    enlace: '',
    publico: ''
  };

  posts: PostFacebook[] = [];
  copiadoIndex: number | null = null;

  constructor(private generador: GeneradorService) {}

  get formularioValido(): boolean {
    return this.datos.producto.trim().length > 0 &&
      this.datos.beneficio.trim().length > 0 &&
      this.datos.enlace.trim().length > 0;
  }

  generar(): void {
    if (!this.formularioValido) return;
    this.posts = this.generador.generarPostsFacebook(this.datos, 5);
  }

  textoCompleto(post: PostFacebook): string {
    return `${post.gancho}\n\n${post.cuerpo}\n\n${post.llamadaAccion}\n\n${post.hashtags}`;
  }

  copiar(post: PostFacebook, index: number): void {
    const texto = this.textoCompleto(post);
    if (navigator.clipboard) {
      navigator.clipboard.writeText(texto).then(() => {
        this.copiadoIndex = index;
        setTimeout(() => (this.copiadoIndex = null), 1500);
      });
    }
  }
}
