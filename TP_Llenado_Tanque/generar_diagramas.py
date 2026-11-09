#!/usr/bin/env python3
"""Genera los diagramas simples del TP (SVG y PNG)."""
import os
import cairosvg

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "img")
os.makedirs(IMG, exist_ok=True)

FONT = "Arial, Helvetica, sans-serif"
INK = "#1a1a1a"
GRAY = "#666666"
LIGHT = "#f2f2f2"
BLUE = "#dbeafe"


def header(w, h, title=None):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
    s += '''
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#1a1a1a" />
  </marker>
  <marker id="arrowGray" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#666666" />
  </marker>
</defs>
'''
    s += f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>'
    if title:
        s += text(40, 42, title, 21, weight="bold")
    return s


def text(x, y, s, size=14, anchor="start", weight="normal", fill=INK, style="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" font-style="{style}">{s}</text>')


def rect(x, y, w, h, fill="none", stroke=INK, rx=0, dash=None, width=2):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" rx="{rx}"{d}/>'


def line(x1, y1, x2, y2, stroke=INK, width=2, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{d}{m}/>'


def arrow(x1, y1, x2, y2, stroke=INK, width=2, dash=None, marker="arrow"):
    return line(x1, y1, x2, y2, stroke=stroke, width=width, dash=dash, marker=marker)


def junction(x, y, r=4, fill=INK):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def contact(x, y, tag, nc=False, w=78, label_below=None):
    """Contacto horizontal de x a x+w, centrado en y."""
    cx = x + w / 2
    parts = [line(x, y, cx - 11, y), line(cx + 11, y, x + w, y),
             line(cx - 11, y - 16, cx - 11, y + 16),
             line(cx + 11, y - 16, cx + 11, y + 16)]
    if nc:
        parts.append(line(cx - 13, y - 16, cx + 13, y + 16, width=2))
    parts.append(text(cx, y - 24, tag, 13, anchor="middle", weight="bold"))
    if label_below:
        parts.append(text(cx, y + 34, label_below, 11, anchor="middle", fill=GRAY))
    return "".join(parts)


def fuse(x, y, tag, w=78, label_below=None):
    """Fusible horizontal de x a x+w, centrado en y."""
    cx = x + w / 2
    return (line(x, y, cx - 22, y) + line(cx + 22, y, x + w, y) +
            rect(cx - 22, y - 10, 44, 20, fill="#ffffff", width=2) +
            line(cx - 22, y, cx + 22, y, width=2) +
            text(cx, y - 24, tag, 13, anchor="middle", weight="bold") +
            (text(cx, y + 28, label_below, 11, anchor="middle", fill=GRAY) if label_below else ""))


def coil(x, y, tag, w=86, h=38):
    """Bobina de x a x+w, centrada en y."""
    return (rect(x, y - h / 2, w, h, fill="#ffffff", rx=4, width=2) +
            text(x + w / 2, y + 6, tag, 13, anchor="middle", weight="bold"))


def lamp(x, y, tag, r=17):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
            + line(x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7, width=2)
            + line(x - r * 0.7, y + r * 0.7, x + r * 0.7, y - r * 0.7, width=2)
            + text(x, y - r - 8, tag, 13, anchor="middle", weight="bold"))


def valve_symbol(x, y, label):
    """Válvula simplificada: dos triángulos enfrentados."""
    s = ''
    s += f'<polygon points="{x-18},{y-16} {x-18},{y+16} {x},{y}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
    s += f'<polygon points="{x+18},{y-16} {x+18},{y+16} {x},{y}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
    s += line(x, y - 22, x, y - 16, width=2)
    s += line(x, y + 16, x, y + 22, width=2)
    s += text(x + 30, y + 5, label, 13, weight="bold")
    return s


# ---------------------------------------------------------------- 1. PROCESO
def diagrama_proceso():
    w, h = 1000, 620
    s = header(w, h, "Estación de llenado y vaciado de tanque")
    s += text(40, 72, "Esquema de la planta (simplificado, no a escala)", 13, fill=GRAY, style="italic")

    # Tanque
    tx, ty, tw, th = 360, 130, 250, 280
    s += rect(tx, ty, tw, th, fill="#ffffff", width=3)
    s += rect(tx + 4, 240, tw - 8, th - 114, fill=BLUE, stroke="none", width=0)
    s += line(tx + 4, 240, tx + tw - 4, 240, stroke="#60a5fa", width=2)
    s += text(tx + tw / 2, ty - 16, "Tanque", 16, anchor="middle", weight="bold")

    # Flotantes y etiquetas dentro del tanque
    s += line(tx + 80, 190, tx + 80, 220, width=2)
    s += f'<circle cx="{tx+80}" cy="226" r="9" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
    s += rect(tx + 105, 198, 105, 30, fill="#ffffff", stroke="none", width=0)
    s += text(tx + 110, 218, "N2 (máximo)", 13, weight="bold")
    s += text(tx + 110, 234, "contacto NC", 10, fill=GRAY)

    s += line(tx + 80, 320, tx + 80, 350, width=2)
    s += f'<circle cx="{tx+80}" cy="356" r="9" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
    s += rect(tx + 105, 330, 105, 30, fill="#ffffff", stroke="none", width=0)
    s += text(tx + 110, 350, "N1 (mínimo)", 13, weight="bold")
    s += text(tx + 110, 366, "contacto NC", 10, fill=GRAY)

    # Bomba
    px, py, pr = 170, 430, 38
    s += f'<circle cx="{px}" cy="{py}" r="{pr}" fill="#f9fafb" stroke="{INK}" stroke-width="3"/>'
    s += text(px, py + 7, "M1", 18, anchor="middle", weight="bold")
    s += text(px, py + pr + 26, "Bomba", 14, anchor="middle", weight="bold")
    s += text(px, py + pr + 44, "monofásica 220 V", 11, anchor="middle", fill=GRAY)

    # Tubería de llenado: bomba -> tanque por arriba
    s += line(px, py - pr, px, 100, width=4)
    s += line(px, 100, tx, 100, width=4)
    s += line(tx, 100, tx, ty, width=4)
    s += arrow(tx + 20, ty, tx + 20, ty + 34, width=3)
    s += text(px + 14, 90, "Agua de entrada", 13, fill=GRAY)

    # Válvula de vaciado
    vx, vy = 500, 490
    s += line(vx, ty + th, vx, vy - 22, width=4)
    s += valve_symbol(vx, vy, "YV1")
    s += line(vx, vy + 22, vx, 570, width=4)
    s += arrow(vx, 545, vx, 570, width=3)
    s += text(vx + 30, vy + 30, "Vaciado", 12, fill=GRAY)

    # Lógica de mando
    cx, cy, cw, ch = 720, 130, 230, 170
    s += rect(cx, cy, cw, ch, fill=LIGHT, width=2)
    s += text(cx + cw / 2, cy + 32, "Lógica de mando", 15, anchor="middle", weight="bold")
    s += text(cx + cw / 2, cy + 56, "KM1 + contacto auxiliar", 11, anchor="middle", fill=GRAY)
    s += text(cx + cw / 2, cy + 74, "Selector SA1", 11, anchor="middle", fill=GRAY)
    s += text(cx + cw / 2, cy + 92, "S0 / S1 / S2 / F1", 11, anchor="middle", fill=GRAY)
    s += text(cx + cw / 2, cy + 116, "Salidas: KM1 → M1, YV1", 11, anchor="middle", fill=GRAY)
    s += text(cx + cw / 2, cy + 146, "220 V AC", 13, anchor="middle", weight="bold")

    # Señal de nivel
    s += line(tx + tw, 270, cx, 270, width=1.8, dash="7,5", stroke=GRAY, marker="arrowGray")
    s += text(tx + tw + 55, 258, "N1 / N2", 12, anchor="middle", weight="bold", fill=GRAY)

    # Alimentación
    s += rect(60, 130, 150, 58, fill=LIGHT, width=2)
    s += text(135, 156, "Alimentación", 13, anchor="middle", weight="bold")
    s += text(135, 175, "220 V AC", 12, anchor="middle", fill=GRAY)
    s += line(135, 188, 135, 392, width=2)
    s += line(135, 392, px, 392, width=2)
    s += arrow(135, 350, 135, 382, width=2)
    s += text(145, 300, "potencia", 11, fill=GRAY)

    # Leyenda
    s += line(60, 595, 130, 595, width=2)
    s += text(140, 600, "potencia / tubería", 12, fill=GRAY)
    s += line(310, 595, 380, 595, width=1.8, dash="7,5", stroke=GRAY)
    s += text(390, 600, "señal de nivel", 12, fill=GRAY)
    s += '</svg>'
    return s


# ---------------------------------------------------------------- 2. BLOQUES
def diagrama_bloques():
    w, h = 1100, 500
    s = header(w, h, "Diagrama en bloques del sistema")
    s += text(40, 72, "Información: pulsadores y sensores → lógica → bobinas.  Energía: 220 V AC → potencia.", 13, fill=GRAY, style="italic")

    # Alimentación
    s += rect(40, 110, 190, 72, fill=LIGHT, rx=6)
    s += text(135, 140, "Alimentación", 15, anchor="middle", weight="bold")
    s += text(135, 160, "220 V AC", 12, anchor="middle", fill=GRAY)

    # Entradas
    s += rect(40, 250, 210, 160, fill="#ffffff", rx=6)
    s += text(145, 280, "ENTRADAS", 15, anchor="middle", weight="bold")
    for i, t in enumerate(["S0  emergencia (NC)", "S1  marcha (NA)", "S2  paro (NC)", "SA1  selector", "N1 / N2  flotantes", "F1  térmico (NC)"]):
        s += text(58, 304 + i * 17, t, 11, fill="#333333")

    # Proceso
    s += rect(350, 250, 230, 160, fill=LIGHT, rx=6)
    s += text(465, 280, "PROCESO", 15, anchor="middle", weight="bold")
    for i, t in enumerate(["Lógica de contactos", "Enclavamiento KM1", "Selector SA1", "Protecciones en serie"]):
        s += text(465, 306 + i * 19, t, 11, anchor="middle", fill="#333333")

    # Salidas
    s += rect(680, 250, 210, 160, fill="#ffffff", rx=6)
    s += text(785, 280, "SALIDAS", 15, anchor="middle", weight="bold")
    for i, t in enumerate(["KM1 → motor M1", "YV1 → válvula", "H1  bomba en marcha", "H2  válvula abierta"]):
        s += text(785, 306 + i * 19, t, 11, anchor="middle", fill="#333333")

    # Planta
    s += rect(980, 250, 90, 160, fill=LIGHT, rx=6)
    s += text(1025, 280, "PLANTA", 13, anchor="middle", weight="bold")
    for i, t in enumerate(["Tanque", "Bomba", "Válvula"]):
        s += text(1025, 306 + i * 19, t, 10, anchor="middle", fill="#333333")

    # Flechas horizontales
    s += arrow(250, 330, 345, 330, width=2.5)
    s += text(297, 320, "señales", 11, anchor="middle", fill=GRAY)
    s += arrow(580, 330, 675, 330, width=2.5)
    s += text(627, 320, "órdenes", 11, anchor="middle", fill=GRAY)
    s += arrow(890, 330, 975, 330, width=2.5)
    s += text(932, 320, "potencia", 11, anchor="middle", fill=GRAY)

    # Energía: desde la alimentación hacia proceso y salidas
    s += line(230, 146, 465, 146, width=2)
    s += line(465, 146, 465, 245, width=2, marker="arrow")
    s += line(465, 146, 785, 146, width=2)
    s += line(785, 146, 785, 245, width=2, marker="arrow")
    s += text(340, 136, "energía", 11, fill=GRAY)

    # Realimentación
    fb_y = 455
    s += line(1025, 410, 1025, fb_y, width=2, marker="arrow")
    s += line(1025, fb_y, 145, fb_y, width=2, marker="arrow")
    s += line(145, fb_y, 145, 410, width=2, marker="arrow")
    s += text(585, fb_y + 20, "realimentación: nivel medido por N1 y N2", 12, anchor="middle", fill=GRAY)

    s += '</svg>'
    return s


# ---------------------------------------------------------------- 3. POTENCIA
def circuito_potencia():
    w, h = 760, 500
    s = header(w, h, "Circuito de potencia")
    s += text(40, 72, "Esquema de principio simplificado. En CADe SIMU se usan los símbolos normalizados.", 12, fill=GRAY, style="italic")

    # Rieles
    s += line(80, 110, 80, 440, width=3)
    s += line(700, 110, 700, 440, width=3)
    s += text(80, 98, "L1", 14, anchor="middle", weight="bold")
    s += text(700, 98, "N", 14, anchor="middle", weight="bold")
    s += text(80, 465, "220 V AC", 11, anchor="middle", fill=GRAY)

    # Riel superior
    y = 150
    s += line(80, y, 130, y, width=3)
    # QM1
    s += rect(130, y - 30, 120, 60, fill="#ffffff", rx=4)
    s += text(190, y - 2, "QM1", 15, anchor="middle", weight="bold")
    s += text(190, y + 16, "2P  6 A", 11, anchor="middle", fill=GRAY)
    s += line(250, y, 300, y, width=3)
    # KM1
    s += rect(300, y - 30, 120, 60, fill="#ffffff", rx=4)
    s += text(360, y - 2, "KM1", 15, anchor="middle", weight="bold")
    s += text(360, y + 16, "contacto", 11, anchor="middle", fill=GRAY)
    s += line(420, y, 470, y, width=3)
    # F1
    s += rect(470, y - 30, 110, 60, fill="#ffffff", rx=4)
    s += text(525, y - 2, "F1", 15, anchor="middle", weight="bold")
    s += text(525, y + 16, "térmico", 11, anchor="middle", fill=GRAY)
    s += line(580, y, 700, y, width=3)

    # Bajada al motor
    s += junction(580, y)
    s += line(580, y, 580, 270, width=3)
    s += f'<circle cx="580" cy="310" r="40" fill="#f9fafb" stroke="{INK}" stroke-width="3"/>'
    s += text(580, 317, "M1", 18, anchor="middle", weight="bold")
    s += text(530, 305, "Bomba", 13, anchor="end", weight="bold")
    s += text(530, 323, "monofásica", 10, anchor="end", fill=GRAY)
    s += line(580, 350, 580, 400, width=3)
    s += line(580, 400, 700, 400, width=3)
    s += junction(700, 400)

    # PE
    s += line(580, 400, 580, 455, width=2)
    s += line(560, 455, 600, 455, width=2)
    s += line(566, 463, 594, 463, width=2)
    s += line(572, 471, 588, 471, width=2)
    s += text(610, 460, "PE", 12, weight="bold")

    # Nota
    s += text(80, 520, "QM1 protege la instalación. KM1 da paso a la bomba. F1 protege el motor contra sobrecarga.", 11, fill=GRAY)
    s += '</svg>'
    return s


# ---------------------------------------------------------------- 4. MANDO
def circuito_mando():
    w, h = 1200, 600
    s = header(w, h, "Circuito de mando (ladder simplificado)")
    s += text(40, 72, "S0, S2, F1, N1 y N2 son contactos NC. SA1 NA cierra en LLENADO; SA1 NC cierra en VACIADO.", 12, fill=GRAY, style="italic")

    # Rieles
    s += line(80, 110, 80, 540, width=3)
    s += line(1120, 110, 1120, 540, width=3)
    s += text(80, 98, "L1", 14, anchor="middle", weight="bold")
    s += text(1120, 98, "N", 14, anchor="middle", weight="bold")

    # Cadena común
    y0 = 150
    s += line(80, y0, 120, y0, width=3)
    s += fuse(120, y0, "F2", w=80, label_below="2 A")
    s += contact(230, y0, "S0", nc=True, w=80, label_below="emergencia")
    s += contact(340, y0, "S2", nc=True, w=80, label_below="paro")
    s += contact(450, y0, "F1", nc=True, w=80, label_below="térmico")
    s += line(530, y0, 610, y0, width=3)
    s += junction(610, y0)
    s += line(610, y0, 610, 470, width=3)

    # Rama llenado
    y1 = 230
    s += line(610, y1, 650, y1, width=3)
    s += contact(650, y1, "SA1", nc=False, w=90, label_below="NA en LLENADO")
    s += contact(770, y1, "N2", nc=True, w=80, label_below="nivel máximo")
    s += line(850, y1, 900, y1, width=3)
    s += junction(900, y1)
    # Paralelo S1 / KM1
    s += line(900, y1, 900, y1 - 50, width=3)
    s += line(900, y1, 900, y1 + 50, width=3)
    s += contact(900, y1 - 50, "S1", nc=False, w=90, label_below=None)
    s += contact(900, y1 + 50, "KM1", nc=False, w=90, label_below="auxiliar")
    s += line(990, y1 - 50, 1030, y1 - 50, width=3)
    s += line(990, y1 + 50, 1030, y1 + 50, width=3)
    s += line(1030, y1 - 50, 1030, y1 + 50, width=3)
    s += junction(1030, y1)
    s += line(1030, y1, 1040, y1, width=3)
    s += coil(1040, y1, "KM1", w=60, h=40)
    s += line(1100, y1, 1120, y1, width=3)
    # H1 en paralelo con KM1
    s += line(1030, y1, 1030, y1 + 80, width=1.5, stroke=GRAY)
    s += line(1030, y1 + 80, 1055, y1 + 80, width=1.5, stroke=GRAY)
    s += lamp(1070, y1 + 80, "H1", r=14)
    s += line(1084, y1 + 80, 1120, y1 + 80, width=1.5, stroke=GRAY)

    # Rama vaciado
    y2 = 400
    s += line(610, y2, 650, y2, width=3)
    s += contact(650, y2, "SA1", nc=True, w=90, label_below="NC en VACIADO")
    s += contact(770, y2, "N1", nc=True, w=80, label_below="nivel mínimo")
    s += line(850, y2, 1040, y2, width=3)
    s += coil(1040, y2, "YV1", w=60, h=40)
    s += line(1100, y2, 1120, y2, width=3)
    # H2 en paralelo con YV1
    s += line(1030, y2, 1030, y2 + 80, width=1.5, stroke=GRAY)
    s += line(1030, y2 + 80, 1055, y2 + 80, width=1.5, stroke=GRAY)
    s += lamp(1070, y2 + 80, "H2", r=14)
    s += line(1084, y2 + 80, 1120, y2 + 80, width=1.5, stroke=GRAY)

    # Etiquetas de ramas
    s += text(640, 182, "LLENADO", 12, weight="bold", fill=GRAY)
    s += text(640, 352, "VACIADO", 12, weight="bold", fill=GRAY)

    # Nota
    s += text(80, 575, "H1 y H2 van en paralelo con las bobinas. F2 protege el circuito de mando.", 11, fill=GRAY)
    s += '</svg>'
    return s


def main():
    diagrams = {
        "diagrama_proceso": diagrama_proceso(),
        "diagrama_bloques": diagrama_bloques(),
        "circuito_potencia": circuito_potencia(),
        "circuito_mando": circuito_mando(),
    }
    for name, svg in diagrams.items():
        path_svg = os.path.join(IMG, name + ".svg")
        path_png = os.path.join(IMG, name + ".png")
        with open(path_svg, "w", encoding="utf-8") as f:
            f.write(svg)
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=path_png, scale=2)
        print("ok", name)


if __name__ == "__main__":
    main()
