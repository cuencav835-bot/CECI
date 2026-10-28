export type Restriccion = 'vegetariano' | 'sin-lactosa' | 'sin-gluten';

export interface RecetaBanco {
  nombre: string;
  porciones: number;
  tiempoMin: number;
  kcalPorPorcion: number;
  /** Ingredientes clave: con ellos se busca la receta. */
  principales: string[];
  ingredientes: string[];
  pasos: string[];
  /** Restricciones que la receta NO cumple. */
  evita?: Restriccion[];
  nota?: string;
}

const NO_VEG: Restriccion[] = ['vegetariano'];
const NO_LAC: Restriccion[] = ['sin-lactosa'];
const NO_GLU: Restriccion[] = ['sin-gluten'];

export const BANCO_RECETAS: RecetaBanco[] = [
  // ---------- Desayunos ----------
  {
    nombre: 'Avena con plátano y canela', porciones: 1, tiempoMin: 10, kcalPorPorcion: 320,
    principales: ['avena', 'plátano'], evita: NO_GLU,
    ingredientes: ['50 g de avena', '1 plátano', '1 taza de agua o leche vegetal', '1 pizca de canela'],
    pasos: ['Cocina la avena con el agua o la leche a fuego medio unos 5 minutos, removiendo.',
      'Corta el plátano en rodajas y añádelo.', 'Espolvorea la canela y sirve caliente.']
  },
  {
    nombre: 'Huevos revueltos con tomate', porciones: 1, tiempoMin: 10, kcalPorPorcion: 250,
    principales: ['huevo', 'tomate'],
    ingredientes: ['2 huevos', '1 tomate', '1 cucharadita de aceite', 'Sal'],
    pasos: ['Pica el tomate y sofríelo 2 minutos en una sartén con el aceite.',
      'Bate los huevos con una pizca de sal y viértelos en la sartén.', 'Remueve a fuego bajo hasta que cuajen y sirve.']
  },
  {
    nombre: 'Yogur natural con manzana y nueces', porciones: 1, tiempoMin: 5, kcalPorPorcion: 280,
    principales: ['yogur', 'manzana', 'nuez'], evita: NO_LAC,
    ingredientes: ['200 g de yogur natural', '1 manzana', '20 g de nueces'],
    pasos: ['Corta la manzana en cubos pequeños.', 'Ponla sobre el yogur y añade las nueces troceadas.']
  },
  {
    nombre: 'Tostada de aguacate con huevo', porciones: 1, tiempoMin: 10, kcalPorPorcion: 380,
    principales: ['pan', 'aguacate', 'huevo'], evita: NO_GLU,
    ingredientes: ['2 rebanadas de pan integral', '½ aguacate', '1 huevo', 'Sal y pimienta'],
    pasos: ['Tuesta el pan.', 'Cuece o fríe el huevo a tu gusto.', 'Machaca el aguacate con sal y pimienta, úntalo en el pan y coloca el huevo encima.']
  },
  {
    nombre: 'Batido de avena y plátano', porciones: 1, tiempoMin: 5, kcalPorPorcion: 300,
    principales: ['avena', 'plátano', 'leche'], evita: NO_GLU,
    ingredientes: ['40 g de avena', '1 plátano', '250 ml de leche o bebida vegetal', 'Canela'],
    pasos: ['Pon todos los ingredientes en la licuadora.', 'Licúa 1 minuto hasta que quede cremoso y sirve frío.'],
    nota: 'Con bebida vegetal queda sin lactosa.'
  },
  {
    nombre: 'Tortilla de maíz con queso fresco', porciones: 1, tiempoMin: 10, kcalPorPorcion: 290,
    principales: ['maíz', 'queso'], evita: NO_LAC,
    ingredientes: ['2 tortillas de maíz', '50 g de queso fresco', '1 fruta de temporada'],
    pasos: ['Calienta las tortillas en una sartén seca.', 'Rellénalas con el queso en láminas y dóblalas.', 'Acompaña con la fruta.']
  },
  {
    nombre: 'Panqueques de plátano y avena', porciones: 2, tiempoMin: 15, kcalPorPorcion: 260,
    principales: ['plátano', 'huevo', 'avena'], evita: NO_GLU,
    ingredientes: ['1 plátano maduro', '2 huevos', '4 cucharadas de avena', '1 cucharadita de aceite'],
    pasos: ['Machaca el plátano y mézclalo con los huevos y la avena.',
      'Calienta una sartén con un poco de aceite.', 'Vierte porciones pequeñas y cocina 2 minutos por cada lado.']
  },
  // ---------- Almuerzos y cenas ----------
  {
    nombre: 'Arroz con pollo y zanahoria', porciones: 2, tiempoMin: 40, kcalPorPorcion: 520,
    principales: ['pollo', 'arroz', 'zanahoria'], evita: NO_VEG,
    ingredientes: ['300 g de pollo en trozos', '1 taza de arroz', '1 zanahoria en cubos', '½ cebolla', '2 tazas de agua', 'Sal, pimienta y aceite'],
    pasos: ['Sofríe la cebolla y el pollo con sal y pimienta hasta que dore.', 'Añade la zanahoria y el arroz y remueve 1 minuto.',
      'Agrega el agua, tapa y cocina a fuego bajo 20 minutos.', 'Deja reposar 5 minutos antes de servir.']
  },
  {
    nombre: 'Pollo a la plancha con arroz y ensalada', porciones: 1, tiempoMin: 25, kcalPorPorcion: 520,
    principales: ['pollo', 'arroz', 'lechuga', 'tomate'], evita: NO_VEG,
    ingredientes: ['150 g de pechuga de pollo', '70 g de arroz', 'Lechuga y 1 tomate', 'Limón, sal y aceite'],
    pasos: ['Cuece el arroz en agua con sal.', 'Cocina la pechuga a la plancha 5 minutos por lado.',
      'Prepara la ensalada con lechuga, tomate, limón y un hilo de aceite.', 'Sirve todo junto.']
  },
  {
    nombre: 'Lentejas guisadas con verduras', porciones: 2, tiempoMin: 40, kcalPorPorcion: 430,
    principales: ['lenteja', 'zanahoria', 'cebolla'],
    ingredientes: ['160 g de lentejas', '1 zanahoria', '1 cebolla', '1 diente de ajo', 'Sal, comino y aceite'],
    pasos: ['Sofríe la cebolla, el ajo y la zanahoria picados.', 'Añade las lentejas y cubre con agua.',
      'Cocina 30 minutos a fuego medio-bajo hasta que estén tiernas.', 'Sazona con sal y comino.']
  },
  {
    nombre: 'Pescado al horno con papas y brócoli', porciones: 1, tiempoMin: 35, kcalPorPorcion: 480,
    principales: ['pescado', 'papa', 'brócoli'], evita: NO_VEG,
    ingredientes: ['150 g de filete de pescado blanco', '150 g de papa', '100 g de brócoli', 'Limón, sal y aceite'],
    pasos: ['Corta la papa en rodajas y hornéala 15 minutos a 200 °C.', 'Añade el pescado con sal y limón y el brócoli en ramitos.',
      'Hornea 15 minutos más.']
  },
  {
    nombre: 'Bowl de quinoa y garbanzos', porciones: 1, tiempoMin: 25, kcalPorPorcion: 490,
    principales: ['quinoa', 'garbanzo', 'pepino', 'tomate'],
    ingredientes: ['60 g de quinoa', '100 g de garbanzos cocidos', '½ pepino', '1 tomate', 'Limón, sal y aceite'],
    pasos: ['Enjuaga la quinoa y cuécela 15 minutos en doble cantidad de agua.', 'Pica el pepino y el tomate.',
      'Mezcla todo con los garbanzos y aliña con limón, sal y aceite.']
  },
  {
    nombre: 'Pasta integral con tomate y atún', porciones: 1, tiempoMin: 20, kcalPorPorcion: 540,
    principales: ['pasta', 'atún', 'tomate'], evita: [...NO_VEG, ...NO_GLU],
    ingredientes: ['80 g de pasta integral', '1 lata de atún', '1 tomate maduro o 100 g de salsa de tomate', 'Ajo, sal y aceite'],
    pasos: ['Cuece la pasta según el paquete.', 'Sofríe el ajo y el tomate 5 minutos.', 'Añade el atún escurrido, mezcla con la pasta y sirve.']
  },
  {
    nombre: 'Frijoles con arroz, huevo y aguacate', porciones: 1, tiempoMin: 25, kcalPorPorcion: 530,
    principales: ['frijol', 'arroz', 'huevo', 'aguacate'],
    ingredientes: ['80 g de frijoles cocidos', '60 g de arroz', '1 huevo', '½ aguacate', 'Sal'],
    pasos: ['Cuece el arroz y calienta los frijoles.', 'Fríe o cuece el huevo.', 'Sirve el arroz con los frijoles, el huevo y el aguacate en láminas.']
  },
  {
    nombre: 'Crema de calabaza', porciones: 2, tiempoMin: 30, kcalPorPorcion: 200,
    principales: ['calabaza', 'cebolla'],
    ingredientes: ['500 g de calabaza', '1 cebolla', '1 vaso de agua', 'Sal, pimienta y aceite'],
    pasos: ['Pica la cebolla y la calabaza.', 'Sofríe la cebolla 3 minutos, añade la calabaza y el agua.',
      'Cocina 20 minutos hasta que esté blanda y tritura hasta que quede cremoso.']
  },
  {
    nombre: 'Tortilla de verduras', porciones: 1, tiempoMin: 15, kcalPorPorcion: 280,
    principales: ['huevo', 'calabacín', 'cebolla'],
    ingredientes: ['2 huevos', '½ calabacín', '¼ de cebolla', 'Sal y aceite'],
    pasos: ['Pica y saltea el calabacín y la cebolla 5 minutos.', 'Bate los huevos con sal y mézclalos con las verduras.',
      'Cuaja en la sartén 3 minutos por cada lado.']
  },
  {
    nombre: 'Ensalada de pollo y aguacate', porciones: 1, tiempoMin: 20, kcalPorPorcion: 380,
    principales: ['pollo', 'lechuga', 'aguacate'], evita: NO_VEG,
    ingredientes: ['120 g de pollo cocido', '80 g de lechuga', '½ aguacate', 'Limón, sal y aceite'],
    pasos: ['Desmenuza el pollo.', 'Mezcla la lechuga con el aguacate en cubos.', 'Añade el pollo y aliña con limón, sal y aceite.']
  },
  {
    nombre: 'Salteado de verduras con tofu', porciones: 1, tiempoMin: 20, kcalPorPorcion: 330,
    principales: ['tofu', 'pimiento', 'brócoli', 'zanahoria'],
    ingredientes: ['120 g de tofu firme', '1 pimiento', '100 g de brócoli', '1 zanahoria', '1 cucharada de salsa de soja'],
    pasos: ['Corta el tofu en cubos y dóralos en una sartén con un poco de aceite.', 'Añade las verduras en trozos y saltea 6 minutos.',
      'Agrega la salsa de soja y mezcla.'],
    evita: NO_GLU, nota: 'Con salsa de soja sin trigo (tamari) es apto sin gluten.'
  },
  {
    nombre: 'Sopa de verduras con huevo', porciones: 2, tiempoMin: 25, kcalPorPorcion: 200,
    principales: ['zanahoria', 'calabacín', 'huevo'],
    ingredientes: ['1 zanahoria', '1 calabacín', '2 huevos', '4 tazas de agua', 'Sal'],
    pasos: ['Pica las verduras y cuécelas en el agua con sal 15 minutos.', 'Cuece los huevos aparte 10 minutos.', 'Sirve la sopa con el huevo picado.']
  },
  {
    nombre: 'Pescado a la plancha con verduras al vapor', porciones: 1, tiempoMin: 20, kcalPorPorcion: 350,
    principales: ['pescado', 'brócoli', 'zanahoria'], evita: NO_VEG,
    ingredientes: ['150 g de filete de pescado', '100 g de brócoli', '1 zanahoria', 'Limón, sal y aceite'],
    pasos: ['Cuece al vapor el brócoli y la zanahoria 8 minutos.', 'Cocina el pescado a la plancha 3 minutos por lado con sal y limón.', 'Sirve junto.']
  },
  {
    nombre: 'Pollo al horno con papas', porciones: 2, tiempoMin: 50, kcalPorPorcion: 500,
    principales: ['pollo', 'papa', 'cebolla'], evita: NO_VEG,
    ingredientes: ['2 muslos o 300 g de pollo', '300 g de papa', '1 cebolla', 'Sal, pimienta, ajo y aceite'],
    pasos: ['Corta las papas y la cebolla en trozos y ponlas en una bandeja con aceite y sal.', 'Sazona el pollo con ajo, sal y pimienta y colócalo encima.',
      'Hornea 40 minutos a 200 °C.']
  },
  {
    nombre: 'Arroz con carne molida y verduras', porciones: 2, tiempoMin: 35, kcalPorPorcion: 540,
    principales: ['carne', 'arroz', 'zanahoria', 'pimiento'], evita: NO_VEG,
    ingredientes: ['250 g de carne molida', '1 taza de arroz', '1 zanahoria', '1 pimiento', '2 tazas de agua', 'Sal y aceite'],
    pasos: ['Dora la carne en una olla con un poco de aceite.', 'Añade la zanahoria y el pimiento picados y sofríe 3 minutos.',
      'Agrega el arroz y el agua con sal, tapa y cocina 20 minutos.']
  },
  {
    nombre: 'Pasta con verduras salteadas', porciones: 1, tiempoMin: 20, kcalPorPorcion: 420,
    principales: ['pasta', 'calabacín', 'tomate'], evita: NO_GLU,
    ingredientes: ['80 g de pasta', '½ calabacín', '1 tomate', 'Ajo, sal y aceite'],
    pasos: ['Cuece la pasta.', 'Saltea el ajo, el calabacín y el tomate en dados 6 minutos.', 'Mezcla con la pasta y sirve.']
  },
  {
    nombre: 'Huevos al horno con espinaca y tomate', porciones: 1, tiempoMin: 20, kcalPorPorcion: 260,
    principales: ['huevo', 'espinaca', 'tomate'],
    ingredientes: ['2 huevos', 'Un puñado de espinaca', '1 tomate', 'Sal y pimienta'],
    pasos: ['Saltea la espinaca y el tomate picado 3 minutos.', 'Colócalo en un recipiente apto para horno y haz dos huecos para los huevos.',
      'Hornea 10 minutos a 180 °C.']
  },
  {
    nombre: 'Garbanzos con espinaca', porciones: 2, tiempoMin: 25, kcalPorPorcion: 350,
    principales: ['garbanzo', 'espinaca', 'cebolla', 'tomate'],
    ingredientes: ['300 g de garbanzos cocidos', '200 g de espinaca', '1 cebolla', '1 tomate', 'Ajo, comino, sal y aceite'],
    pasos: ['Sofríe la cebolla y el ajo, añade el tomate picado.', 'Incorpora los garbanzos y el comino y cocina 5 minutos.', 'Agrega la espinaca y cocina hasta que se ablande.']
  },
  {
    nombre: 'Wraps de pollo y verduras', porciones: 1, tiempoMin: 15, kcalPorPorcion: 430,
    principales: ['tortilla', 'pollo', 'lechuga', 'tomate'], evita: [...NO_VEG, ...NO_GLU],
    ingredientes: ['1 tortilla de trigo', '100 g de pollo cocido', 'Lechuga y 1 tomate', 'Yogur natural o limón'],
    pasos: ['Calienta la tortilla.', 'Rellénala con el pollo desmenuzado, la lechuga y el tomate.', 'Aliña con un poco de yogur o limón y enrolla.']
  },
  {
    nombre: 'Sopa de pollo con verduras', porciones: 2, tiempoMin: 40, kcalPorPorcion: 330,
    principales: ['pollo', 'zanahoria', 'papa', 'cebolla'], evita: NO_VEG,
    ingredientes: ['250 g de pollo', '1 zanahoria', '1 papa', '1 cebolla', '5 tazas de agua', 'Sal y cilantro'],
    pasos: ['Pon el pollo con el agua y la cebolla a hervir.', 'A los 15 minutos añade la zanahoria y la papa en trozos.',
      'Cocina 20 minutos más, sazona y sirve con cilantro.']
  },
  {
    nombre: 'Ensalada de atún y garbanzos', porciones: 1, tiempoMin: 10, kcalPorPorcion: 420,
    principales: ['atún', 'garbanzo', 'tomate', 'cebolla'], evita: NO_VEG,
    ingredientes: ['1 lata de atún', '100 g de garbanzos cocidos', '1 tomate', '¼ de cebolla', 'Limón, sal y aceite'],
    pasos: ['Pica el tomate y la cebolla.', 'Mézclalos con el atún escurrido y los garbanzos.', 'Aliña con limón, sal y aceite.']
  },
  {
    nombre: 'Pimientos rellenos de arroz y frijol', porciones: 2, tiempoMin: 45, kcalPorPorcion: 380,
    principales: ['pimiento', 'arroz', 'frijol'],
    ingredientes: ['2 pimientos grandes', '100 g de arroz cocido', '100 g de frijoles cocidos', '½ cebolla', 'Sal y comino'],
    pasos: ['Corta la parte superior de los pimientos y quita las semillas.', 'Mezcla el arroz, los frijoles y la cebolla picada con sal y comino.',
      'Rellena los pimientos y hornea 30 minutos a 190 °C.']
  },
  {
    nombre: 'Pollo salteado con brócoli y arroz', porciones: 1, tiempoMin: 25, kcalPorPorcion: 510,
    principales: ['pollo', 'brócoli', 'arroz'], evita: NO_VEG,
    ingredientes: ['150 g de pechuga de pollo en tiras', '100 g de brócoli', '70 g de arroz', 'Ajo, sal y aceite'],
    pasos: ['Cuece el arroz.', 'Saltea el pollo con ajo y sal hasta que dore.', 'Añade el brócoli en ramitos y un chorrito de agua, tapa 4 minutos y sirve con el arroz.']
  },
  // ---------- Snacks ----------
  {
    nombre: 'Zanahoria con hummus', porciones: 1, tiempoMin: 5, kcalPorPorcion: 130,
    principales: ['zanahoria', 'hummus'],
    ingredientes: ['1 zanahoria', '40 g de hummus'], pasos: ['Corta la zanahoria en bastones y mójalos en el hummus.']
  },
  {
    nombre: 'Manzana con mantequilla de maní', porciones: 1, tiempoMin: 5, kcalPorPorcion: 190,
    principales: ['manzana', 'maní'],
    ingredientes: ['1 manzana', '1 cucharada de mantequilla de maní'], pasos: ['Corta la manzana en gajos y acompáñala con la mantequilla de maní.']
  },
  {
    nombre: 'Yogur con fruta', porciones: 1, tiempoMin: 5, kcalPorPorcion: 140,
    principales: ['yogur', 'fruta'], evita: NO_LAC,
    ingredientes: ['125 g de yogur natural', '1 fruta picada'], pasos: ['Mezcla el yogur con la fruta en trocitos.']
  },
  {
    nombre: 'Plátano al horno con canela', porciones: 1, tiempoMin: 15, kcalPorPorcion: 110,
    principales: ['plátano', 'canela'],
    ingredientes: ['1 plátano maduro', 'Canela'], pasos: ['Corta el plátano por la mitad a lo largo.', 'Espolvorea canela y hornea 10 minutos a 180 °C.']
  },
  {
    nombre: 'Huevo cocido con tomate', porciones: 1, tiempoMin: 12, kcalPorPorcion: 120,
    principales: ['huevo', 'tomate'],
    ingredientes: ['1 huevo', '1 tomate', 'Sal y orégano'], pasos: ['Cuece el huevo 10 minutos y pélalo.', 'Sirve con el tomate en rodajas, sal y orégano.']
  }
];
