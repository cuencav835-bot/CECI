import { BANCO_RECETAS, RecetaBanco, Restriccion } from './recetas-banco';

export interface Coincidencia {
  receta: RecetaBanco;
  faltan: string[];
  /** 0 a 1: qué parte de los ingredientes clave tienes. */
  cobertura: number;
}

const IGNORAR = new Set(['de', 'del', 'la', 'el', 'las', 'los', 'y', 'e', 'con', 'un', 'una', 'unos', 'unas', 'en',
  'mi', 'mis', 'tengo', 'hay', 'casa', 'g', 'kg', 'gr', 'gramos', 'taza', 'tazas', 'unidad', 'unidades', 'molida', 'fresco', 'fresca']);

// Palabras equivalentes entre países; todas se llevan a la que usa el banco de recetas.
const SINONIMOS: Record<string, string> = {
  patata: 'papa', patatas: 'papa', banana: 'plátano', banano: 'plátano', platano: 'plátano', platanos: 'plátano',
  palta: 'aguacate', judia: 'frijol', judias: 'frijol', habichuela: 'frijol', habichuelas: 'frijol', poroto: 'frijol',
  porotos: 'frijol', alubia: 'frijol', alubias: 'frijol', jitomate: 'tomate', pechuga: 'pollo', muslo: 'pollo', muslos: 'pollo',
  res: 'carne', ternera: 'carne', cerdo: 'carne', mani: 'maní', cacahuate: 'maní', cacahuete: 'maní', nueces: 'nuez',
  zapallo: 'calabaza', auyama: 'calabaza', ahuyama: 'calabaza', zapallito: 'calabacín', zucchini: 'calabacín',
  calabacin: 'calabacín', yogurt: 'yogur', yoghurt: 'yogur', maiz: 'maíz', brocoli: 'brócoli', atun: 'atún',
  espinacas: 'espinaca', garbanzos: 'garbanzo', lentejas: 'lenteja', huevos: 'huevo', pescados: 'pescado',
  merluza: 'pescado', tilapia: 'pescado', salmon: 'pescado', salmón: 'pescado', bacalao: 'pescado', dorada: 'pescado'
};

export function sinAcentos(texto: string): string {
  return texto.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
}

/** Reduce una palabra a su raíz para comparar singular/plural y acentos. */
function raiz(palabra: string): string {
  let p = sinAcentos(palabra);
  if (p.length > 3 && p.endsWith('s')) p = p.slice(0, -1);
  if (p.length > 3 && p.endsWith('e')) p = p.slice(0, -1);
  return p;
}

function raicesDe(texto: string): Set<string> {
  const salida = new Set<string>();
  for (const palabra of texto.toLowerCase().split(/[^a-záéíóúüñ]+/)) {
    if (!palabra || IGNORAR.has(palabra)) continue;
    salida.add(raiz(SINONIMOS[palabra] ?? palabra));
  }
  return salida;
}

function normalizarRestriccion(r: string): Restriccion | null {
  const limpia = r.trim().toLowerCase().replace(/\s+/g, '-');
  return limpia === 'vegetariano' || limpia === 'sin-lactosa' || limpia === 'sin-gluten' ? limpia : null;
}

/** Busca en el banco las recetas que mejor encajan con los ingredientes que la persona tiene. */
export function buscarRecetas(ingredientes: string[], restricciones: string[] = [], max = 3): Coincidencia[] {
  const tengo = raicesDe(ingredientes.join(' '));
  const evitar = restricciones.map(normalizarRestriccion).filter((r): r is Restriccion => r !== null);

  const coincidencias: Coincidencia[] = [];
  for (const receta of BANCO_RECETAS) {
    if (receta.evita?.some(x => evitar.includes(x))) continue;
    const faltan = receta.principales.filter(p => !tengo.has(raiz(SINONIMOS[p] ?? p)));
    const coinciden = receta.principales.length - faltan.length;
    if (coinciden < Math.min(2, receta.principales.length)) continue;
    coincidencias.push({ receta, faltan, cobertura: coinciden / receta.principales.length });
  }

  return coincidencias
    .sort((a, b) => b.cobertura - a.cobertura || a.faltan.length - b.faltan.length || b.receta.principales.length - a.receta.principales.length)
    .slice(0, max);
}

// ---------------------------------------------------------------------------
// Chat básico: respuestas generales por tema, sin IA.
// ---------------------------------------------------------------------------

interface Tema {
  /** Palabras (sin acentos) que activan el tema. */
  claves: string[];
  respuesta: string;
}

const AVISO_MEDICO =
  'Eso depende de tu caso personal y de tu salud. Lo mejor es consultarlo con tu médico o con un nutricionista, ' +
  'que puede darte una pauta segura para ti. Yo solo doy ideas generales de alimentación.';

const PALABRAS_MEDICAS = ['diabet', 'hipertens', 'embaraz', 'lactancia', 'medicament', 'enfermedad', 'alergi', 'anorexi',
  'bulimi', 'cancer', 'renal', 'rinon', 'tiroid', 'colesterol', 'gastritis', 'celiaquia', 'intoleranc', 'trastorno'];

const TEMAS: Tema[] = [
  {
    claves: ['cena', 'cenar', 'ligero', 'ligera', 'noche'],
    respuesta: 'Para una cena ligera: una sopa o crema de verduras, una tortilla con ensalada, o pescado a la plancha con verduras al vapor. ' +
      'Procura cenar 2 o 3 horas antes de dormir y no te pases con las porciones. Si quieres, escribe tus ingredientes en "Receta con mis ingredientes".'
  },
  {
    claves: ['desayuno', 'desayunar', 'manana'],
    respuesta: 'Un buen desayuno combina proteína y fibra: avena con fruta, huevos con tomate, yogur con nueces o una tostada integral con aguacate. ' +
      'Evita depender solo de azúcar (jugos, pan dulce) porque te da hambre pronto.'
  },
  {
    claves: ['almuerzo', 'almorzar', 'comida', 'mediodia'],
    respuesta: 'Una regla fácil para el almuerzo: la mitad del plato de verduras, un cuarto de proteína (pollo, pescado, huevo, legumbres) y un cuarto de cereal o tubérculo (arroz, papa, pasta integral).'
  },
  {
    claves: ['snack', 'merienda', 'picar', 'entre comidas', 'colacion'],
    respuesta: 'Meriendas sencillas: una fruta, un puñado de almendras o nueces, zanahoria con hummus, yogur natural o un huevo cocido. ' +
      'Mejor porciones pequeñas que paquetes ultraprocesados.'
  },
  {
    claves: ['bajar', 'adelgazar', 'peso', 'grasa', 'quemar', 'dieta'],
    respuesta: 'Para bajar de peso de forma sana: come más verduras y proteína, reduce bebidas azucaradas y ultraprocesados, cuida las porciones, ' +
      'duerme bien y muévete a diario. Evita dietas extremas o muy bajas en calorías: rebotan y cansan. Los cambios graduales duran más. ' +
      'Prueba el "Menú semanal" con el objetivo "Bajar de peso".'
  },
  {
    claves: ['musculo', 'masa muscular', 'ganar', 'proteina', 'proteinas', 'gimnasio', 'entrenar'],
    respuesta: 'Para ganar masa muscular necesitas entrenar con constancia y comer suficiente: incluye proteína en cada comida (huevos, pollo, pescado, lácteos, ' +
      'legumbres, tofu), carbohidratos como arroz, avena o papa para tener energía, y descansa bien. Prueba el "Menú semanal" con el objetivo "Ganar masa muscular".'
  },
  {
    claves: ['vegetariano', 'vegetariana', 'vegano', 'vegana', 'sin carne'],
    respuesta: 'Proteína sin carne: huevos, lácteos, legumbres (lentejas, garbanzos, frijoles), tofu, quinoa y frutos secos. ' +
      'Combinar legumbres con cereales (por ejemplo frijoles con arroz) es una gran opción. Marca "Vegetariano" en el menú y en las recetas.'
  },
  {
    claves: ['agua', 'hidratar', 'hidratacion', 'beber', 'sed'],
    respuesta: 'Bebe agua a lo largo del día, sobre todo si hace calor o haces ejercicio. Una pista: orina de color amarillo claro suele indicar buena hidratación. ' +
      'Cambia refrescos y jugos azucarados por agua, infusiones sin azúcar o agua con limón.'
  },
  {
    claves: ['antojo', 'antojos', 'dulce', 'dulces', 'azucar', 'chocolate'],
    respuesta: 'Para los antojos de dulce: fruta, yogur con canela, un cuadradito de chocolate negro o plátano al horno con canela. ' +
      'Comer suficiente proteína y no saltarte comidas ayuda a que los antojos sean menos fuertes.'
  },
  {
    claves: ['ayuno', 'saltar', 'saltarme', 'no desayunar', 'una comida'],
    respuesta: 'Saltarse comidas puede darte mucha hambre después y llevarte a comer de más. Si quieres probar ayunos, conviene hablarlo antes con un profesional ' +
      'de la salud, sobre todo si tomas medicación o tienes alguna condición.'
  },
  {
    claves: ['calorias', 'kcal', 'cuanto debo comer', 'cuantas calorias'],
    respuesta: 'Las calorías que necesitas dependen de tu edad, tamaño, actividad y objetivo. Como referencia muy general, el menú de la app usa unas ' +
      '1600 kcal al día para bajar de peso, 2000 para mantener y 2400 para ganar masa. Son orientativas: un nutricionista puede calcularlas para ti.'
  },
  {
    claves: ['restaurante', 'fuera', 'comer fuera', 'delivery', 'pizza', 'hamburguesa', 'comida rapida'],
    respuesta: 'Si comes fuera: elige platos a la plancha, al horno o en sopa, pide ensalada o verduras de acompañamiento, comparte los postres y cambia el refresco por agua. ' +
      'Un día de comida fuera no arruina nada; lo importante es el hábito de toda la semana.'
  },
  {
    claves: ['compra', 'supermercado', 'planificar', 'semana', 'organizar'],
    respuesta: 'Planificar ayuda mucho. Entra en "Menú semanal", genera tu menú y tendrás también la lista de la compra agrupada por secciones del supermercado. ' +
      'Con tu cuenta puedes guardarlo y volver a verlo cuando quieras.'
  },
  {
    claves: ['ejercicio', 'deporte', 'caminar', 'actividad'],
    respuesta: 'Moverte a diario, aunque sea caminar 30 minutos, ayuda mucho a tu salud, a tu ánimo y a controlar el peso. Aumenta poco a poco y elige algo que disfrutes para mantenerlo.'
  },
  {
    claves: ['hola', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches', 'ayuda'],
    respuesta: 'Hola, soy el asistente básico de +Salud. Puedes preguntarme por desayunos, almuerzos, cenas, meriendas, bajar de peso, ganar músculo, proteínas, ' +
      'comidas vegetarianas, agua, antojos o cómo planificar tu semana.'
  }
];

export const SUGERENCIAS_CHAT = ['¿Qué puedo cenar ligero?', '¿Qué desayuno es saludable?', '¿Cómo bajar de peso sin dietas extremas?',
  '¿Qué proteínas hay sin carne?', '¿Cómo controlar los antojos de dulce?'];

export const RESPUESTA_NO_ENTENDIDA =
  'No estoy seguro de entender esa pregunta. Pregúntame por desayunos, almuerzos, cenas, meriendas, bajar de peso, ganar músculo, ' +
  'proteínas, comida vegetariana, hidratación o antojos. También puedes crear una receta con tus ingredientes.';

/** Responde por palabras clave con consejos generales. No sustituye a un profesional. */
export function responderBasico(pregunta: string): string {
  const texto = ' ' + sinAcentos(pregunta) + ' ';
  if (PALABRAS_MEDICAS.some(p => texto.includes(p))) return AVISO_MEDICO;

  let mejor: Tema | null = null;
  let mejorPuntos = 0;
  for (const tema of TEMAS) {
    let puntos = 0;
    for (const clave of tema.claves) {
      if (clave.includes(' ') ? texto.includes(clave) : new RegExp(`\\b${clave}`).test(texto)) puntos += 1;
    }
    if (puntos > mejorPuntos) {
      mejor = tema;
      mejorPuntos = puntos;
    }
  }
  return mejor ? mejor.respuesta : RESPUESTA_NO_ENTENDIDA;
}
