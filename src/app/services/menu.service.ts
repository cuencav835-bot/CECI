import { Injectable } from '@angular/core';

export type Objetivo = 'bajar' | 'mantener' | 'subir';
export type Restriccion = 'vegetariano' | 'sin-lactosa' | 'sin-gluten';
export type Categoria = 'Verduras y frutas' | 'Proteínas' | 'Cereales y legumbres' | 'Lácteos y huevos' | 'Despensa';

export interface DatosMenu {
  objetivo: Objetivo;
  personas: number;
  restricciones: Restriccion[];
  incluirSnack: boolean;
}

interface Ingrediente {
  nombre: string;
  cantidad: number;
  unidad: string;
  categoria: Categoria;
}

interface Receta {
  nombre: string;
  kcal: number;
  ingredientes: Ingrediente[];
  // restricciones que la receta NO cumple
  incompatible?: Restriccion[];
}

export interface ComidaDia {
  momento: string;
  receta: string;
  kcal: number;
}

export interface DiaMenu {
  dia: string;
  comidas: ComidaDia[];
  kcalTotal: number;
}

export interface ItemCompra {
  nombre: string;
  cantidad: string;
}

export interface GrupoCompra {
  categoria: Categoria;
  items: ItemCompra[];
}

export interface MenuSemanal {
  dias: DiaMenu[];
  compra: GrupoCompra[];
  referenciaKcal: number;
  consejo: string;
}

const i = (nombre: string, cantidad: number, unidad: string, categoria: Categoria): Ingrediente =>
  ({ nombre, cantidad, unidad, categoria });

const DESAYUNOS: Receta[] = [
  { nombre: 'Avena con plátano y canela', kcal: 320, incompatible: ['sin-gluten'],
    ingredientes: [i('Avena', 50, 'g', 'Cereales y legumbres'), i('Plátano', 1, 'unidad', 'Verduras y frutas'), i('Canela', 2, 'g', 'Despensa')] },
  { nombre: 'Huevos revueltos con tomate y pan integral', kcal: 350, incompatible: ['sin-gluten'],
    ingredientes: [i('Huevos', 2, 'unidad', 'Lácteos y huevos'), i('Tomate', 1, 'unidad', 'Verduras y frutas'), i('Pan integral', 2, 'rebanada', 'Cereales y legumbres')] },
  { nombre: 'Yogur natural con fruta y nueces', kcal: 280, incompatible: ['sin-lactosa'],
    ingredientes: [i('Yogur natural', 200, 'g', 'Lácteos y huevos'), i('Manzana', 1, 'unidad', 'Verduras y frutas'), i('Nueces', 20, 'g', 'Despensa')] },
  { nombre: 'Tostada de aguacate con huevo', kcal: 380, incompatible: ['sin-gluten'],
    ingredientes: [i('Pan integral', 2, 'rebanada', 'Cereales y legumbres'), i('Aguacate', 0.5, 'unidad', 'Verduras y frutas'), i('Huevos', 1, 'unidad', 'Lácteos y huevos')] },
  { nombre: 'Batido de avena, plátano y leche vegetal', kcal: 300, incompatible: ['sin-gluten'],
    ingredientes: [i('Avena', 40, 'g', 'Cereales y legumbres'), i('Plátano', 1, 'unidad', 'Verduras y frutas'), i('Leche vegetal', 250, 'ml', 'Despensa')] },
  { nombre: 'Arepa o tortilla de maíz con queso fresco', kcal: 340, incompatible: ['sin-lactosa'],
    ingredientes: [i('Harina de maíz', 60, 'g', 'Cereales y legumbres'), i('Queso fresco', 50, 'g', 'Lácteos y huevos'), i('Fruta de temporada', 1, 'unidad', 'Verduras y frutas')] },
];

const ALMUERZOS: Receta[] = [
  { nombre: 'Pollo a la plancha con arroz y ensalada', kcal: 520, incompatible: ['vegetariano'],
    ingredientes: [i('Pechuga de pollo', 150, 'g', 'Proteínas'), i('Arroz', 70, 'g', 'Cereales y legumbres'), i('Lechuga', 60, 'g', 'Verduras y frutas'), i('Tomate', 1, 'unidad', 'Verduras y frutas')] },
  { nombre: 'Lentejas guisadas con verduras', kcal: 480,
    ingredientes: [i('Lentejas', 80, 'g', 'Cereales y legumbres'), i('Zanahoria', 1, 'unidad', 'Verduras y frutas'), i('Cebolla', 0.5, 'unidad', 'Verduras y frutas')] },
  { nombre: 'Pescado al horno con papas y brócoli', kcal: 500, incompatible: ['vegetariano'],
    ingredientes: [i('Filete de pescado blanco', 150, 'g', 'Proteínas'), i('Papa', 150, 'g', 'Verduras y frutas'), i('Brócoli', 100, 'g', 'Verduras y frutas')] },
  { nombre: 'Bowl de quinoa, garbanzos y vegetales', kcal: 490,
    ingredientes: [i('Quinoa', 60, 'g', 'Cereales y legumbres'), i('Garbanzos cocidos', 100, 'g', 'Cereales y legumbres'), i('Pepino', 0.5, 'unidad', 'Verduras y frutas'), i('Tomate', 1, 'unidad', 'Verduras y frutas')] },
  { nombre: 'Pasta integral con salsa de tomate y atún', kcal: 540, incompatible: ['vegetariano', 'sin-gluten'],
    ingredientes: [i('Pasta integral', 80, 'g', 'Cereales y legumbres'), i('Atún en lata', 1, 'lata', 'Proteínas'), i('Tomate triturado', 100, 'g', 'Despensa')] },
  { nombre: 'Frijoles con arroz, huevo y aguacate', kcal: 530,
    ingredientes: [i('Frijoles', 80, 'g', 'Cereales y legumbres'), i('Arroz', 60, 'g', 'Cereales y legumbres'), i('Huevos', 1, 'unidad', 'Lácteos y huevos'), i('Aguacate', 0.5, 'unidad', 'Verduras y frutas')] },
];

const CENAS: Receta[] = [
  { nombre: 'Crema de calabaza con tostada', kcal: 300, incompatible: ['sin-gluten'],
    ingredientes: [i('Calabaza', 250, 'g', 'Verduras y frutas'), i('Cebolla', 0.5, 'unidad', 'Verduras y frutas'), i('Pan integral', 1, 'rebanada', 'Cereales y legumbres')] },
  { nombre: 'Tortilla de verduras con ensalada', kcal: 340,
    ingredientes: [i('Huevos', 2, 'unidad', 'Lácteos y huevos'), i('Calabacín', 0.5, 'unidad', 'Verduras y frutas'), i('Lechuga', 60, 'g', 'Verduras y frutas')] },
  { nombre: 'Ensalada de pollo, maíz y aguacate', kcal: 380, incompatible: ['vegetariano'],
    ingredientes: [i('Pechuga de pollo', 120, 'g', 'Proteínas'), i('Lechuga', 80, 'g', 'Verduras y frutas'), i('Aguacate', 0.5, 'unidad', 'Verduras y frutas')] },
  { nombre: 'Salteado de verduras con tofu', kcal: 330,
    ingredientes: [i('Tofu', 120, 'g', 'Proteínas'), i('Pimiento', 1, 'unidad', 'Verduras y frutas'), i('Brócoli', 100, 'g', 'Verduras y frutas'), i('Salsa de soja', 15, 'ml', 'Despensa')] },
  { nombre: 'Sopa de verduras con huevo cocido', kcal: 290,
    ingredientes: [i('Zanahoria', 1, 'unidad', 'Verduras y frutas'), i('Calabacín', 0.5, 'unidad', 'Verduras y frutas'), i('Huevos', 1, 'unidad', 'Lácteos y huevos')] },
  { nombre: 'Pescado a la plancha con verduras al vapor', kcal: 350, incompatible: ['vegetariano'],
    ingredientes: [i('Filete de pescado blanco', 150, 'g', 'Proteínas'), i('Brócoli', 100, 'g', 'Verduras y frutas'), i('Zanahoria', 1, 'unidad', 'Verduras y frutas')] },
];

const SNACKS: Receta[] = [
  { nombre: 'Fruta de temporada', kcal: 80, ingredientes: [i('Fruta de temporada', 1, 'unidad', 'Verduras y frutas')] },
  { nombre: 'Puñado de almendras', kcal: 120, ingredientes: [i('Almendras', 20, 'g', 'Despensa')] },
  { nombre: 'Zanahoria con hummus', kcal: 130, ingredientes: [i('Zanahoria', 1, 'unidad', 'Verduras y frutas'), i('Hummus', 40, 'g', 'Despensa')] },
  { nombre: 'Yogur natural', kcal: 100, incompatible: ['sin-lactosa'], ingredientes: [i('Yogur natural', 125, 'g', 'Lácteos y huevos')] },
];

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

const REFERENCIA: Record<Objetivo, number> = { bajar: 1600, mantener: 2000, subir: 2400 };

const CONSEJOS: Record<Objetivo, string> = {
  bajar: 'Para bajar de peso: prioriza verduras y proteína, bebe agua antes de comer y no te saltes comidas.',
  mantener: 'Para mantener tu peso: conserva horarios regulares y escucha tu hambre y saciedad.',
  subir: 'Para ganar masa muscular: añade una porción extra de proteína o cereal en cada comida y entrena con constancia.'
};

@Injectable({ providedIn: 'root' })
export class MenuService {
  generarMenu(datos: DatosMenu): MenuSemanal {
    const personas = Math.max(1, Math.min(10, Math.floor(datos.personas) || 1));
    const factor = datos.objetivo === 'bajar' ? 1 : datos.objetivo === 'mantener' ? 1.15 : 1.3;

    const desayunos = this.barajar(this.filtrar(DESAYUNOS, datos.restricciones));
    const almuerzos = this.barajar(this.filtrar(ALMUERZOS, datos.restricciones));
    const cenas = this.barajar(this.filtrar(CENAS, datos.restricciones));
    const snacks = this.barajar(this.filtrar(SNACKS, datos.restricciones));

    const usadas: { receta: Receta; veces: number }[] = [];
    const registrar = (r: Receta) => {
      const e = usadas.find(u => u.receta === r);
      if (e) e.veces++; else usadas.push({ receta: r, veces: 1 });
    };

    const dias: DiaMenu[] = DIAS.map((dia, idx) => {
      const elegidas: [string, Receta][] = [
        ['Desayuno', desayunos[idx % desayunos.length]],
        ['Almuerzo', almuerzos[idx % almuerzos.length]],
        ['Cena', cenas[idx % cenas.length]],
      ];
      if (datos.incluirSnack && snacks.length) elegidas.push(['Snack', snacks[idx % snacks.length]]);

      const comidas = elegidas.map(([momento, r]) => {
        registrar(r);
        return { momento, receta: r.nombre, kcal: Math.round((r.kcal * factor) / 10) * 10 };
      });
      return { dia, comidas, kcalTotal: comidas.reduce((s, c) => s + c.kcal, 0) };
    });

    return {
      dias,
      compra: this.listaCompra(usadas, personas, factor),
      referenciaKcal: REFERENCIA[datos.objetivo],
      consejo: CONSEJOS[datos.objetivo]
    };
  }

  textoMenu(menu: MenuSemanal): string {
    const partes = menu.dias.map(d =>
      `${d.dia.toUpperCase()} (≈${d.kcalTotal} kcal)\n` + d.comidas.map(c => `- ${c.momento}: ${c.receta}`).join('\n'));
    const compra = menu.compra.map(g =>
      `${g.categoria}:\n` + g.items.map(it => `  [ ] ${it.nombre} — ${it.cantidad}`).join('\n'));
    return `MENÚ SEMANAL\n\n${partes.join('\n\n')}\n\nLISTA DE LA COMPRA\n\n${compra.join('\n\n')}`;
  }

  private filtrar(recetas: Receta[], restricciones: Restriccion[]): Receta[] {
    const ok = recetas.filter(r => !r.incompatible?.some(x => restricciones.includes(x)));
    return ok.length ? ok : recetas;
  }

  private barajar<T>(lista: T[]): T[] {
    const copia = [...lista];
    for (let k = copia.length - 1; k > 0; k--) {
      const j = Math.floor(Math.random() * (k + 1));
      [copia[k], copia[j]] = [copia[j], copia[k]];
    }
    return copia;
  }

  private listaCompra(usadas: { receta: Receta; veces: number }[], personas: number, factor: number): GrupoCompra[] {
    const total = new Map<string, { ing: Ingrediente; cantidad: number }>();
    for (const { receta, veces } of usadas) {
      for (const ing of receta.ingredientes) {
        const clave = `${ing.nombre}|${ing.unidad}`;
        const previo = total.get(clave);
        const cant = ing.cantidad * veces * personas * (ing.unidad === 'g' || ing.unidad === 'ml' ? factor : 1);
        total.set(clave, { ing, cantidad: (previo?.cantidad ?? 0) + cant });
      }
    }
    const grupos = new Map<Categoria, ItemCompra[]>();
    for (const { ing, cantidad } of total.values()) {
      const lista = grupos.get(ing.categoria) ?? [];
      lista.push({ nombre: ing.nombre, cantidad: this.formatear(cantidad, ing.unidad) });
      grupos.set(ing.categoria, lista);
    }
    const orden: Categoria[] = ['Verduras y frutas', 'Proteínas', 'Cereales y legumbres', 'Lácteos y huevos', 'Despensa'];
    return orden.filter(c => grupos.has(c)).map(c => ({
      categoria: c,
      items: grupos.get(c)!.sort((a, b) => a.nombre.localeCompare(b.nombre))
    }));
  }

  private formatear(cantidad: number, unidad: string): string {
    if (unidad === 'g') return cantidad >= 1000 ? `${(cantidad / 1000).toFixed(1)} kg` : `${Math.round(cantidad)} g`;
    if (unidad === 'ml') return cantidad >= 1000 ? `${(cantidad / 1000).toFixed(1)} L` : `${Math.round(cantidad)} ml`;
    const n = Math.ceil(cantidad);
    return unidad === 'unidad' ? `${n} ${n === 1 ? 'unidad' : 'unidades'}`
      : unidad === 'rebanada' ? `${n} ${n === 1 ? 'rebanada' : 'rebanadas'}`
      : `${n} ${unidad}${n === 1 ? '' : 's'}`;
  }
}
