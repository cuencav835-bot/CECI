"""
Imágenes promocionales para Facebook — Curso Resina Epóxica
go.hotmart.com/G106175870D?ap=8534
"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

random.seed(99); np.random.seed(99)

FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
OUT   = "/home/user/CECI/imagenes_promo"
os.makedirs(OUT, exist_ok=True)

DARK   = (5, 10, 12)
TEAL   = (78, 205, 196)
GOLD   = (247, 201, 72)
CREAM  = (240, 250, 248)
PURPLE = (160, 80, 220)
CORAL  = (255, 120, 80)
GREEN  = (60, 200, 120)

def fnt(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

def centered(draw, text, y, font, color, W=1080):
    bb = draw.textbbox((0,0), text, font=font)
    tw = bb[2]-bb[0]
    x  = (W-tw)//2
    draw.text((x+2,y+2), text, font=font, fill=(0,0,0,140))
    draw.text((x,y), text, font=font, fill=color)

def draw_blob(draw, cx, cy, r, color, alpha=80):
    pts = [(cx + (r+random.uniform(-r*.35,r*.35))*math.cos(2*math.pi*i/60),
            cy + (r+random.uniform(-r*.35,r*.35))*math.sin(2*math.pi*i/60))
           for i in range(60)]
    draw.polygon(pts, fill=color+(alpha,))

def base_bg(W, H, accent, seed=0):
    random.seed(seed); np.random.seed(seed)
    img = Image.new("RGBA", (W, H), DARK+(255,))
    d   = ImageDraw.Draw(img)
    for (cx,cy,r,col) in [
        (W*.15, H*.2,  W*.22, accent),
        (W*.85, H*.5,  W*.18, GOLD),
        (W*.5,  H*.8,  W*.25, accent),
        (W*.1,  H*.75, W*.15, TEAL),
        (W*.9,  H*.15, W*.2,  TEAL),
    ]:
        draw_blob(d, cx, cy, r, col)
    # noise
    a = np.array(img).astype(np.float32)
    a = np.clip(a + np.random.randn(*a.shape)*4, 0, 255).astype(np.uint8)
    img = Image.fromarray(a)
    # vignette
    d2 = ImageDraw.Draw(img)
    for i in range(60):
        al = int(120*(i/60)**2)
        d2.rectangle([i,i,W-i,H-i], outline=(0,0,0,al))
    return img

def separator(draw, y, W, color, alpha=120):
    lw = int(W*0.6)
    lx = (W-lw)//2
    draw.rectangle([lx, y, lx+lw, y+2], fill=color+(alpha,))

# ── POST 1: Cuadrado 1080x1080 — "¿Cuánto Ganas?" ──────────────────────
def post_cuanto_ganas():
    W,H = 1080,1080
    img = base_bg(W, H, GOLD, seed=1)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 72)
    f2  = fnt("BigShoulders-Bold.ttf", 96)
    f3  = fnt("InstrumentSans-Bold.ttf", 44)
    f4  = fnt("InstrumentSans-Regular.ttf", 32)
    furl= fnt("DMMono-Regular.ttf", 24)
    fbr = fnt("Italiana-Regular.ttf", 38)

    centered(d, "¿CUÁNTO PUEDES GANAR", 80, f1, GOLD)
    centered(d, "CON RESINA EPÓXICA?",  155, f1, CREAM)
    separator(d, 250, W, TEAL)

    items = [
        ("💍 Joyería",       "$50 - $300 c/u",   TEAL),
        ("🖼️  Cuadros",       "$500 - $3,000",    GOLD),
        ("🏮 Lámparas",      "$800 - $4,000",    PURPLE+(255,)),
        ("🪑 Mesas de resina","$3,000 - $15,000", CORAL+(255,)),
    ]
    y = 290
    for icon_txt, price, col in items:
        centered(d, icon_txt, y, f3, CREAM)
        centered(d, price,    y+50, f2, col if len(col)==4 else col+(255,))
        y += 140

    separator(d, 860, W, TEAL)
    centered(d, "Aprende todo en el curso 👇", 890, f3, CREAM)
    centered(d, "go.hotmart.com/G106175870D", 945, furl, TEAL)
    centered(d, "VeroResina", 1020, fbr, GOLD)

    img.convert("RGB").save(f"{OUT}/post_cuanto_ganas.png")
    print("✅ post_cuanto_ganas.png")

# ── POST 2: Story 1080x1920 — "Lo que aprenderás" ───────────────────────
def post_lo_que_aprenderas():
    W,H = 1080,1920
    img = base_bg(W, H, TEAL, seed=2)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 90)
    f2  = fnt("InstrumentSans-Bold.ttf", 50)
    f3  = fnt("InstrumentSans-Regular.ttf", 40)
    furl= fnt("DMMono-Regular.ttf", 28)
    fbr = fnt("Italiana-Regular.ttf", 42)

    centered(d, "LO QUE APRENDERÁS", 150, f1, GOLD)
    centered(d, "EN EL CURSO",        245, f1, TEAL)
    separator(d, 360, W, GOLD)

    temas = [
        ("🧪", "Mezcla y proporciones correctas"),
        ("🎨", "Técnicas de pigmentación"),
        ("💎", "Joyería y accesorios"),
        ("🖼️", "Arte y cuadros decorativos"),
        ("🏺", "Objetos del hogar"),
        ("📸", "Fotografía para vender"),
        ("💼", "Cómo fijar precios"),
        ("📱", "Vender por redes sociales"),
    ]
    y = 410
    for icon, tema in temas:
        centered(d, f"{icon}  {tema}", y, f3, CREAM)
        y += 80

    separator(d, y+30, W, TEAL)
    centered(d, "Curso completo con certificado", y+70, f2, GOLD)
    centered(d, "Empiezas desde CERO", y+130, f2, TEAL)

    # botón
    bw, bh = 700, 100
    bx = (W-bw)//2; by = y+220
    d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=25, fill=GOLD+(230,))
    centered(d, "👉  QUIERO EL CURSO", by+22, f2, DARK)
    centered(d, "go.hotmart.com/G106175870D", by+120, furl, CREAM)
    centered(d, "VeroResina", H-80, fbr, TEAL)

    img.convert("RGB").save(f"{OUT}/story_lo_que_aprenderas.png")
    print("✅ story_lo_que_aprenderas.png")

# ── POST 3: Cuadrado — Testimonios / Resultados ──────────────────────────
def post_resultados():
    W,H = 1080,1080
    img = base_bg(W, H, PURPLE, seed=3)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 80)
    f2  = fnt("InstrumentSans-Bold.ttf", 46)
    f3  = fnt("InstrumentSans-Regular.ttf", 36)
    furl= fnt("DMMono-Regular.ttf", 24)
    fbr = fnt("Italiana-Regular.ttf", 38)

    centered(d, "RESULTADOS REALES", 80, f1, GOLD)
    centered(d, "de alumnas del curso", 165, f2, CREAM)
    separator(d, 240, W, PURPLE)

    testimonios = [
        ("⭐⭐⭐⭐⭐", "\"Vendí mi primer arreglo\nen 3 días de publicarlo\"",  TEAL),
        ("⭐⭐⭐⭐⭐", "\"Recuperé mi inversión\nen la primera semana\"",     GOLD),
        ("⭐⭐⭐⭐⭐", "\"Ahora tengo mi propio\nnegocio desde casa\"",       TEAL),
    ]
    y = 280
    for stars, texto, col in testimonios:
        centered(d, stars, y, f3, GOLD)
        for line in texto.replace("\"","").split("\n"):
            y += 44
            centered(d, f'"{line}"', y, f3, CREAM)
        y += 80

    separator(d, y+10, W, GOLD)
    centered(d, "¡Tú también puedes lograrlo! 🌟", y+50, f2, GOLD)
    centered(d, "go.hotmart.com/G106175870D",       y+110, furl, TEAL)
    centered(d, "VeroResina", H-40, fbr, GOLD)
    img.convert("RGB").save(f"{OUT}/post_resultados.png")
    print("✅ post_resultados.png")

# ── POST 4: Story — Comparativa antes/después ────────────────────────────
def post_antes_despues():
    W,H = 1080,1920
    img = base_bg(W, H, CORAL, seed=4)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 88)
    f2  = fnt("InstrumentSans-Bold.ttf", 48)
    f3  = fnt("InstrumentSans-Regular.ttf", 38)
    furl= fnt("DMMono-Regular.ttf", 28)
    fbr = fnt("Italiana-Regular.ttf", 42)

    centered(d, "ANTES DEL CURSO", 120, f1, CREAM)
    separator(d, 215, W, CORAL)

    antes = ["❌ Sin idea de por dónde empezar",
             "❌ Miedo a desperdiciar material",
             "❌ Sin ingresos propios",
             "❌ Sin habilidades de venta"]
    y = 240
    for t in antes:
        centered(d, t, y, f3, CREAM); y += 72

    separator(d, y+20, W, GOLD)
    centered(d, "DESPUÉS DEL CURSO", y+60, f1, GOLD)
    separator(d, y+160, W, GREEN)

    despues = ["✅ Técnicas profesionales dominadas",
               "✅ Cero desperdicio de material",
               "✅ Ingresos generados desde casa",
               "✅ Clientes recurrentes en redes"]
    y2 = y+190
    for t in despues:
        centered(d, t, y2, f3, CREAM); y2 += 72

    separator(d, y2+20, W, TEAL)
    centered(d, "El curso hace la diferencia", y2+60, f2, TEAL)

    bw,bh = 720,100
    bx = (W-bw)//2; by = y2+160
    d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=25, fill=GOLD+(230,))
    centered(d, "👉  EMPIEZA HOY", by+22, f2, DARK)
    centered(d, "go.hotmart.com/G106175870D", by+115, furl, CREAM)
    centered(d, "VeroResina", H-80, fbr, TEAL)

    img.convert("RGB").save(f"{OUT}/story_antes_despues.png")
    print("✅ story_antes_despues.png")

# ── POST 5: Cuadrado — FAQ ───────────────────────────────────────────────
def post_faq():
    W,H = 1080,1080
    img = base_bg(W, H, GREEN, seed=5)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 72)
    f2  = fnt("InstrumentSans-Bold.ttf", 44)
    f3  = fnt("InstrumentSans-Regular.ttf", 33)
    furl= fnt("DMMono-Regular.ttf", 24)
    fbr = fnt("Italiana-Regular.ttf", 38)

    centered(d, "PREGUNTAS FRECUENTES", 70, f1, GOLD)
    separator(d, 155, W, GREEN)

    faqs = [
        ("¿Necesito experiencia previa?", "NO. El curso empieza desde cero."),
        ("¿Cuánto invierto para empezar?", "Muy poco. Con menos de $500 MXN."),
        ("¿Cuánto tarda el curso?", "Acceso de por vida, a tu ritmo."),
        ("¿Hay soporte de instructoras?", "Sí, comunidad y soporte incluidos."),
        ("¿Cuándo puedo empezar a vender?", "Desde la primera semana del curso."),
    ]
    y = 180
    for pregunta, respuesta in faqs:
        centered(d, f"🔹 {pregunta}", y, f2, TEAL); y += 50
        centered(d, respuesta,         y, f3, CREAM); y += 68

    separator(d, y+10, W, GOLD)
    centered(d, "¿Más dudas? ¡El curso lo resuelve todo!", y+50, f3, CREAM)
    centered(d, "go.hotmart.com/G106175870D",              y+95, furl, TEAL)
    centered(d, "VeroResina", H-38, fbr, GOLD)
    img.convert("RGB").save(f"{OUT}/post_faq.png")
    print("✅ post_faq.png")

# ── POST 6: Story — Portada del Curso ───────────────────────────────────
def post_portada_curso():
    W,H = 1080,1920
    img = base_bg(W, H, TEAL, seed=6)
    d   = ImageDraw.Draw(img)
    f1  = fnt("BigShoulders-Bold.ttf", 120)
    f2  = fnt("BigShoulders-Bold.ttf",  80)
    f3  = fnt("InstrumentSans-Bold.ttf", 50)
    f4  = fnt("InstrumentSans-Regular.ttf", 38)
    furl= fnt("DMMono-Regular.ttf", 30)
    fbr = fnt("Italiana-Regular.ttf", 48)

    centered(d, "CURSO DE",       380, f2, GOLD)
    centered(d, "RESINA",         475, f1, CREAM)
    centered(d, "EPÓXICA",        590, f1, TEAL)
    separator(d, 720, W, GOLD)
    centered(d, "De principiante a emprendedora", 760, f3, CREAM)
    separator(d, 835, W, TEAL)

    beneficios = ["✨ Online · A tu ritmo · Con certificado",
                  "🎓 Técnicas profesionales desde cero",
                  "💰 Aprende a generar ingresos"]
    y = 875
    for b in beneficios:
        centered(d, b, y, f4, CREAM); y += 65

    bw,bh = 780,110
    bx=(W-bw)//2; by=1120
    d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=28, fill=GOLD+(240,))
    centered(d, "👉  QUIERO INSCRIBIRME", by+25, f3, DARK)
    centered(d, "go.hotmart.com/G106175870D", by+130, furl, TEAL)
    centered(d, "VeroResina", H-90, fbr, TEAL)
    img.convert("RGB").save(f"{OUT}/story_portada_curso.png")
    print("✅ story_portada_curso.png")

print("🖼️  Generando imágenes promocionales...")
post_cuanto_ganas()
post_lo_que_aprenderas()
post_resultados()
post_antes_despues()
post_faq()
post_portada_curso()
print(f"\n🎉 ¡Todas las imágenes en {OUT}/")
