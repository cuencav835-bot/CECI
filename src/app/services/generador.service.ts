import { Injectable } from '@angular/core';

export interface DatosVentaFacebook {
  producto: string;
  beneficio: string;
  precioOferta: string;
  enlace: string;
  publico: string;
}

export interface PostFacebook {
  gancho: string;
  cuerpo: string;
  llamadaAccion: string;
  hashtags: string;
}

export interface DatosCuento {
  titulo: string;
  personaje: string;
  moraleja: string;
  duracion: '5' | '10' | '15';
  fraseApertura: string;
}

export interface EscenaCuento {
  nombre: string;
  texto: string;
  imagenSugerida: string;
  duracionEstimadaSegundos: number;
}

export interface GuionCuento {
  titulo: string;
  escenas: EscenaCuento[];
}

@Injectable({ providedIn: 'root' })
export class GeneradorService {
  private randomDe<T>(lista: T[]): T {
    return lista[Math.floor(Math.random() * lista.length)];
  }

  private ganchosVenta = [
    (p: string) => `🚨 ¿Todavía luchando con esto? "${p}" puede ser el cambio que buscas.`,
    (p: string) => `Esto me hubiera ahorrado mucho tiempo antes de descubrir "${p}" 👇`,
    (p: string) => `No sigas leyendo si no quieres saber cómo resolver esto en pocos días 👀`,
    (p: string) => `Pará de hacer scroll 2 segundos, esto es para vos 🙋`,
    (p: string) => `La mayoría comete este error... y "${p}" lo soluciona.`
  ];

  private cuerposVenta = [
    (beneficio: string, publico: string) =>
      `Si sos ${publico || 'alguien que quiere mejorar esto'}, sabés lo frustrante que es no ver resultados. Por eso quiero contarte sobre algo que me ayudó: ${beneficio}.`,
    (beneficio: string, publico: string) =>
      `Después de probar mil cosas, encontré algo simple que realmente funciona: ${beneficio}. Ideal para ${publico || 'personas que quieren un cambio real'}.`,
    (beneficio: string, publico: string) =>
      `${beneficio}. Así de simple. Pensado para ${publico || 'quienes están cansados de promesas vacías'}.`
  ];

  private ctasVenta = [
    (oferta: string, link: string) =>
      `${oferta ? `Hoy con ${oferta}. ` : ''}Mirá todo acá 👉 ${link}`,
    (oferta: string, link: string) =>
      `${oferta ? `Oferta especial: ${oferta}. ` : ''}Entrá y enterate cómo 👉 ${link}`,
    (oferta: string, link: string) =>
      `Quedan pocos cupos${oferta ? ` con ${oferta}` : ''}. Info acá 👉 ${link}`
  ];

  private bancoHashtags = [
    '#emprendimiento', '#negociodigital', '#ingresoextra', '#trabajardesdecasa',
    '#productosdigitales', '#ventasonline', '#marketingdigital', '#exito',
    '#motivacion', '#hotmart', '#dineroextra', '#libertadfinanciera'
  ];

  generarPostsFacebook(datos: DatosVentaFacebook, cantidad = 5): PostFacebook[] {
    const posts: PostFacebook[] = [];
    for (let i = 0; i < cantidad; i++) {
      const gancho = this.randomDe(this.ganchosVenta)(datos.producto);
      const cuerpo = this.randomDe(this.cuerposVenta)(datos.beneficio, datos.publico);
      const llamadaAccion = this.randomDe(this.ctasVenta)(datos.precioOferta, datos.enlace);
      const hashtags = this.elegirHashtags(4).join(' ');
      posts.push({ gancho, cuerpo, llamadaAccion, hashtags });
    }
    return posts;
  }

  private elegirHashtags(cantidad: number): string[] {
    const copia = [...this.bancoHashtags];
    const elegidos: string[] = [];
    for (let i = 0; i < cantidad && copia.length > 0; i++) {
      const idx = Math.floor(Math.random() * copia.length);
      elegidos.push(copia.splice(idx, 1)[0]);
    }
    return elegidos;
  }

  private duracionAEscenas(duracion: string): number {
    if (duracion === '5') return 4;
    if (duracion === '10') return 6;
    return 8;
  }

  private duracionSegundos(texto: string): number {
    const palabras = texto.trim().split(/\s+/).length;
    const palabrasPorSegundo = 2.3;
    return Math.max(3, Math.ceil(palabras / palabrasPorSegundo));
  }

  generarGuionCuento(datos: DatosCuento): GuionCuento {
    type EscenaSinDuracion = Omit<EscenaCuento, 'duracionEstimadaSegundos'>;
    const crudas: EscenaSinDuracion[] = [];

    const gancho = datos.fraseApertura.trim() ||
      `¡Hola, amiguitos! Hoy les voy a contar la historia de ${datos.personaje}, y les prometo que el final los va a sorprender. ¿Están listos? ¡Vamos con "${datos.titulo}"!`;

    crudas.push({
      nombre: 'Gancho inicial (grábalo primero, es lo primero que ven)',
      texto: gancho,
      imagenSugerida: `Imagen colorida y alegre de ${datos.personaje} saludando directo a la cámara, fondo llamativo.`
    });

    crudas.push({
      nombre: 'Presentación del personaje',
      texto: `${datos.personaje} vivía tranquilo en su hogar, hasta que un día pasó algo que cambiaría todo.`,
      imagenSugerida: `${datos.personaje} en su lugar habitual (casa, bosque, ciudad), mostrando su rutina normal.`
    });

    const totalDesarrollo = this.duracionAEscenas(datos.duracion) - 4;
    for (let i = 1; i <= totalDesarrollo; i++) {
      crudas.push({
        nombre: `Desarrollo de la historia (parte ${i})`,
        texto: `${datos.personaje} se encontró con un nuevo desafío. Tuvo que pensar, ser valiente y no rendirse para seguir adelante.`,
        imagenSugerida: `Escena de acción o descubrimiento con ${datos.personaje} enfrentando el desafío, expresión de esfuerzo o sorpresa.`
      });
    }

    crudas.push({
      nombre: 'Clímax (el momento más emocionante)',
      texto: `Justo cuando parecía que todo se complicaba, ${datos.personaje} encontró la manera de resolverlo, usando lo que había aprendido en el camino.`,
      imagenSugerida: `Primer plano de ${datos.personaje} con cara de determinación, luz brillante o efecto especial de "momento importante".`
    });

    crudas.push({
      nombre: 'Resolución y moraleja',
      texto: `Al final, todo se solucionó. Y ${datos.personaje} aprendió algo muy importante: ${datos.moraleja}.`,
      imagenSugerida: `${datos.personaje} sonriendo, rodeado de amigos o en su hogar, ambiente cálido y feliz.`
    });

    crudas.push({
      nombre: 'Cierre y llamada a la acción',
      texto: `Y así termina la historia de hoy. Cuéntanos en los comentarios qué habrías hecho tú en el lugar de ${datos.personaje}. Si te gustó, dale like, suscríbete y activa la campanita para más cuentos como este. ¡Nos vemos en el próximo video!`,
      imagenSugerida: `Texto en pantalla "SUSCRÍBETE" con animación, personaje despidiéndose con la mano.`
    });

    const escenas: EscenaCuento[] = crudas.map((e) => ({
      ...e,
      duracionEstimadaSegundos: this.duracionSegundos(e.texto)
    }));

    return { titulo: datos.titulo, escenas };
  }
}
