#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el informe del TP en Markdown, HTML, PDF y DOCX.
El contenido está pensado como borrador simple y editable.
"""
import os
import re
import html as html_lib

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from weasyprint import HTML

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "img")

# --------------------------------------------------------------------------
# CONTENIDO
# --------------------------------------------------------------------------

def T(headers, rows):
    return ("table", {"headers": headers, "rows": rows})


BLOCKS = [
    # ----------------------------- PORTADA
    ("cover_title", "Estación de llenado y vaciado de tanque"),
    ("cover_sub", "Trabajo Práctico de Mecatrónica II"),
    ("cover_sub2", "Modelado y simulación de un sistema mecatrónico en CADe SIMU"),
    ("cover_rule", ""),
    ("cover_meta", "Universidad Tecnológica Nacional — Facultad Regional Paraná"),
    ("cover_meta", "Tecnicatura Superior en Mecatrónica"),
    ("cover_meta", "Cátedra: Mecatrónica II"),
    ("cover_meta", "Alumno: Hugo Ariel Martinez"),
    ("cover_meta", "Profesor: [completar]"),
    ("cover_meta", "Año: 2026"),
    ("cover_meta", "Fecha: [completar]"),
    ("cover_note", "Sistema elegido de la lista de la guía: Sistema de llenado de tanque."),
    ("cover_note", "Herramienta de simulación: CADe SIMU (en lugar de FluidSIM)."),
    ("pagebreak",),

    # ----------------------------- 1
    ("h1", "1. Descripción del sistema"),
    ("p", "El sistema que elegí es una estación de llenado y vaciado de un tanque de agua. La función es mantener el nivel entre un mínimo y un máximo: una bomba llena el tanque y una electroválvula lo vacía. Dos flotantes, uno abajo y otro arriba, avisan cuándo se llegó a cada nivel."),
    ("p", "La guía lo llama “Sistema de llenado de tanque”. Le agregué el vaciado para poder repetir el ciclo y probar los dos límites. El funcionamiento es simple: con el selector en LLENADO se aprieta MARCHA y arranca la bomba. Cuando el agua llega al flotante de arriba, la bomba se detiene sola. Para vaciar, se gira el selector a VACIADO y se abre la electroválvula. Cuando el nivel baja hasta el flotante de abajo, la válvula se cierra sola. Después se vuelve a LLENADO y se aprieta MARCHA para repetir el ciclo."),
    ("p", "Lo elegí porque está en la lista de la guía, es fácil de explicar y se puede resolver con lógica eléctrica de contactos. No necesita neumática, así que lo pude simular completo en CADe SIMU. La parte mecánica es el tanque, la bomba y la válvula; la parte eléctrica es el motor y el contactor; la parte de sensores son los flotantes; y la parte de control es la lógica cableada."),
    ("p", "Aplicación: este tipo de sistema se usa en tanques de reserva de agua, en procesos de llenado de mezclas, en riego, en plantas de tratamiento y en cualquier lugar donde haya que mantener un nivel entre dos límites."),
    ("p", "Una aclaración sobre la herramienta: la guía pide FluidSIM, pero no tengo licencia. Por eso hice la simulación en CADe SIMU. Elegí un sistema eléctrico para que la simulación sea completa y no quede una parte sin probar. La lógica de contactos, el contactor, el motor y las lámparas se pueden simular bien en CADe SIMU."),
    T(["Dato", "Descripción"], [
        ["Función", "Mantener el nivel de un tanque entre un mínimo y un máximo."],
        ["Alimentación", "220 V AC, monofásica."],
        ["Control", "Lógica cableada con contactor y selector."],
        ["Protecciones", "Interruptor automático QM1, fusible F2 y relé térmico F1."],
        ["Herramienta", "CADe SIMU."],
    ]),

    # ----------------------------- 2
    ("h1", "2. Entradas, proceso y salidas"),
    ("p", "Entradas: son las órdenes del operador y las señales de los sensores. Proceso: es la lógica que decide. Salidas: son los elementos que hacen el trabajo."),
    ("h2", "2.1. Entradas"),
    T(["Tag", "Componente", "Contacto", "Función"], [
        ["S0", "Pulsador de emergencia", "NC", "Corta el mando completo."],
        ["S1", "Pulsador de marcha", "NA", "Arranca la bomba."],
        ["S2", "Pulsador de paro", "NC", "Detiene la bomba y cierra la válvula."],
        ["SA1", "Selector de 2 posiciones", "NA / NC", "Elige LLENADO o VACIADO."],
        ["N1", "Flotante de nivel mínimo", "NC", "Abre cuando el agua baja del mínimo."],
        ["N2", "Flotante de nivel máximo", "NC", "Abre cuando el tanque está lleno."],
        ["F1", "Relé térmico", "NC", "Abre si el motor se sobrecarga."],
    ]),
    ("h2", "2.2. Proceso"),
    ("p", "El proceso no tiene PLC. La lógica está hecha con el contactor KM1, su contacto auxiliar y el selector SA1. QM1 protege la alimentación general y F1 el motor. F2 protege el mando, y S0, S2 y F1 están en serie con las bobinas: si alguno se abre, se apagan KM1 y YV1."),
    ("p", "Los flotantes N1 y N2 son contactos NC. Esto es a propósito: si se corta un cable o se afloja un borne, el contacto se abre y el sistema queda detenido. Es más seguro que usar contactos NA para las paradas."),
    ("note", "QM1 y F2 no son entradas ni salidas: son protecciones. QM1 protege la instalación y el motor; F2 protege el circuito de mando."),
    ("h2", "2.3. Salidas"),
    T(["Tag", "Componente", "Función"], [
        ["KM1", "Contactor de la bomba", "Da potencia al motor M1."],
        ["M1", "Motor-bomba monofásico", "Llena el tanque."],
        ["YV1", "Electroválvula de vaciado", "Abre el desagüe cuando está energizada."],
        ["H1", "Lámpara verde", "Indica bomba en marcha."],
        ["H2", "Lámpara roja", "Indica válvula de vaciado abierta."],
    ]),

    # ----------------------------- 3
    ("h1", "3. Diagrama en bloques"),
    ("figure", {
        "svg": "img/diagrama_bloques.svg",
        "png": "img/diagrama_bloques.png",
        "caption": "Figura 1. Diagrama en bloques del sistema. La realimentación es el nivel del tanque, medido por N1 y N2.",
        "width": 15.0,
        "height": 6.82,
    }),
    ("p", "El diagrama muestra cómo se conectan las partes. La energía va de la alimentación a la potencia. La información va de los pulsadores y flotantes a la lógica, y de la lógica a las bobinas."),
    ("p", "La alimentación entrega 220 V AC. Las entradas son los pulsadores y los flotantes. El proceso es la lógica de contactos. Las salidas son el contactor, la válvula y las lámparas. La planta es el tanque, la bomba y la válvula."),
    ("p", "La realimentación es el nivel del tanque: N1 y N2 le informan a la lógica si el agua está baja o si el tanque está lleno. Sin esos dos sensores, la lógica no sabría cuándo cortar la bomba ni cuándo cerrar la válvula. Ese es el lazo cerrado del sistema."),

    # ----------------------------- 4
    ("h1", "4. Lógica de funcionamiento"),
    ("p", "Primero escribí la secuencia en palabras y después la pasé a contactos. La idea era que la bomba no dependa de que el operador esté mirando el tanque."),
    ("h2", "4.1. Secuencia"),
    ("ol", [
        "Selector en LLENADO, tanque no lleno (N2 cerrado), emergencia sin apretar (S0 cerrado), paro sin apretar (S2 cerrado) y térmico sin disparar (F1 cerrado).",
        "Se aprieta S1. Se energiza KM1 y se enclava con su contacto auxiliar. Arranca M1 y se prende H1.",
        "El tanque se llena. Cuando el agua llega a N2, el contacto NC se abre. Se desenergiza KM1, se apaga M1 y H1. La bomba queda detenida.",
        "Se gira SA1 a VACIADO. Se energiza YV1, se abre la válvula y se prende H2. El tanque se vacía.",
        "Cuando el agua baja hasta N1, el contacto NC se abre. Se desenergiza YV1, se cierra la válvula y se apaga H2.",
        "Se vuelve a LLENADO y se aprieta S1 para repetir el ciclo.",
    ]),
    ("p", "Si se aprieta S0 o S2, o si dispara F1, se corta el mando y se apagan KM1 y YV1. La válvula es normalmente cerrada: sin tensión queda cerrada."),
    ("h2", "4.2. Variables y ecuaciones"),
    ("p", "Para escribir las ecuaciones usé 1 cuando el contacto está cerrado y 0 cuando está abierto."),
    T(["Variable", "Significado", "Vale 1 cuando...", "Vale 0 cuando..."], [
        ["S0", "Emergencia", "No está apretada (NC cerrado)", "Está apretada (abierto)"],
        ["S1", "Marcha", "Está apretada (NA cerrado)", "No está apretada (abierto)"],
        ["S2", "Paro", "No está apretado (NC cerrado)", "Está apretado (abierto)"],
        ["SA1", "Selector", "Está en LLENADO", "Está en VACIADO"],
        ["N1", "Flotante mínimo", "Nivel sobre el mínimo (NC cerrado)", "Nivel en el mínimo (abierto)"],
        ["N2", "Flotante máximo", "Tanque no lleno (NC cerrado)", "Tanque lleno (abierto)"],
        ["F1", "Térmico", "Normal (NC cerrado)", "Disparado (abierto)"],
    ]),
    ("code", "KM1 = F2 · S0 · S2 · F1 · SA1 · N2 · (S1 + KM1)\nYV1 = F2 · S0 · S2 · F1 · SA1' · N1\nH1  = KM1\nH2  = YV1"),
    ("p", "SA1' es el contacto NC del selector, que está cerrado en VACIADO."),
    ("ul", [
        "**F2 · S0 · S2 · F1** es la cadena de seguridad. Si cualquiera se abre, KM1 y YV1 se apagan.",
        "**SA1** deja pasar el mando solo en LLENADO. **SA1'** deja pasar solo en VACIADO. Por eso la bomba y la válvula no pueden funcionar juntas.",
        "**N2** está cerrado mientras el tanque no está lleno. Cuando se abre, corta KM1.",
        "**(S1 + KM1)** es el enclavamiento. S1 arranca y KM1 se mantiene solo; cuando N2 se abre, se pierde el enclavamiento y hay que volver a apretar S1.",
        "**N1** está cerrado mientras hay agua por encima del mínimo. Cuando se abre, corta YV1 y evita que la válvula quede abierta con el tanque vacío.",
    ]),
    ("h2", "4.3. Ladder"),
    ("p", "El circuito de mando queda así:"),
    T(["Estado", "SA1", "N1", "N2", "KM1", "YV1", "Qué pasa"], [
        ["Reposo", "LLENADO", "1", "1", "0", "0", "Espera S1."],
        ["Llenando", "LLENADO", "1", "1", "1", "0", "Bomba en marcha."],
        ["Lleno", "LLENADO", "1", "0", "0", "0", "N2 corta la bomba."],
        ["Vaciando", "VACIADO", "1", "0/1", "0", "1", "Válvula abierta."],
        ["Mínimo", "VACIADO", "0", "1", "0", "0", "N1 cierra la válvula."],
        ["Emergencia", "—", "—", "—", "0", "0", "Todo apagado."],
    ]),
    ("note", "En la tabla, 1 significa contacto cerrado y 0 contacto abierto. En el estado LLENADO, si el operador no gira el selector, la bomba queda detenida con el tanque lleno."),
    ("figure", {
        "svg": "img/circuito_mando.svg",
        "png": "img/circuito_mando.png",
        "caption": "Figura 2. Circuito de mando simplificado. H1 va en paralelo con KM1 y H2 con YV1. SA1 NA y SA1 NC son las dos posiciones del mismo selector; los flotantes se representan con finales de carrera NC.",
        "width": 13.8,
        "height": 6.90,
    }),

    # ----------------------------- 5
    ("h1", "5. Simulación en CADe SIMU"),
    ("h2", "5.1. Circuito de potencia"),
    ("figure", {
        "svg": "img/circuito_potencia.svg",
        "png": "img/circuito_potencia.png",
        "caption": "Figura 3. Circuito de potencia. QM1 protege la instalación, KM1 da paso a la bomba y F1 protege el motor.",
        "width": 11.5,
        "height": 7.57,
    }),
    ("p", "Primero armé la potencia y la probé con el motor solo. Después agregué el mando. Así, si algo no andaba, sabía si el problema estaba en la potencia o en la lógica. Perdí un rato con el contacto auxiliar de KM1 porque al principio no lo había puesto y la bomba se apagaba al soltar S1. Después entendí que el contacto auxiliar hace el enclavamiento."),
    ("p", "El circuito de potencia es: L1 → QM1 → KM1 → F1 → M1 → N. QM1 protege la instalación, KM1 da paso a la bomba y F1 protege el motor contra sobrecarga. El motor es monofásico de 220 V."),
    ("h2", "5.2. Circuito de mando"),
    ("p", "El circuito de mando se alimenta de L1, después de QM1: L1 → F2 → S0 → S2 → F1 → ramas. La rama de LLENADO tiene SA1 NA, N2 NC, el paralelo S1/KM1 y la bobina KM1. La rama de VACIADO tiene SA1 NC, N1 NC y la bobina YV1. H1 va en paralelo con KM1 y H2 con YV1."),
    ("p", "La bobina de KM1 y la de YV1 son de 220 V AC. Las lámparas también. En una instalación real convendría usar mando a 24 V, pero para la simulación lo hice a 220 V para no agregar una fuente."),
    ("h2", "5.3. Componentes usados"),
    T(["Componente en CADe SIMU", "Tag", "Detalle"], [
        ["Alimentación F+N", "—", "220 V AC"],
        ["Interruptor automático 2P", "QM1", "6 A"],
        ["Fusible", "F2", "2 A, circuito de mando"],
        ["Contactor 2P con auxiliar NA", "KM1", "Bobina 220 V AC"],
        ["Relé térmico", "F1", "Regulado a 2 A"],
        ["Motor monofásico", "M1", "Bomba de 0,5 HP"],
        ["Pulsador NC", "S0", "Emergencia tipo seta"],
        ["Pulsador NA", "S1", "Marcha"],
        ["Pulsador NC", "S2", "Paro"],
        ["Selector 2 posiciones", "SA1", "LLENADO / VACIADO"],
        ["Final de carrera NC", "N1", "Flotante de nivel mínimo"],
        ["Final de carrera NC", "N2", "Flotante de nivel máximo"],
        ["Bobina de electroválvula", "YV1", "220 V AC, normalmente cerrada"],
        ["Lámpara verde", "H1", "220 V, bomba en marcha"],
        ["Lámpara roja", "H2", "220 V, válvula abierta"],
    ]),
    ("h2", "5.4. Pasos de armado"),
    ("ol", [
        "Abrir CADe SIMU y configurar hoja A4 horizontal. Completar el cajetín con nombre, materia y fecha.",
        "Colocar la alimentación F+N, el interruptor QM1 y el fusible F2.",
        "Armar la potencia: QM1 → KM1 → F1 → M1 → N. Conectar PE al motor.",
        "Armar la cadena de mando: F2 → S0 NC → S2 NC → F1 NC.",
        "Rama de LLENADO: SA1 NA → N2 NC → (S1 NA en paralelo con KM1 NA) → bobina KM1 → N.",
        "Rama de VACIADO: SA1 NC → N1 NC → bobina YV1 → N.",
        "Conectar H1 en paralelo con KM1 y H2 en paralelo con YV1.",
        "Etiquetar todos los componentes y verificar que no haya dos con el mismo nombre.",
        "Guardar el archivo como TP_Llenado_Tanque.cad.",
        "Pasar a modo simulación y probar la secuencia.",
    ]),
    ("p", "Detalles que me complicaron en CADe SIMU:"),
    ("ul", [
        "Los pulsadores vuelven solos. Para mantenerlos apretados hay que hacer clic y arrastrar un poco.",
        "Los finales de carrera N1 y N2 son NC: en la simulación se hace clic para abrirlos y representar el flotante actuado.",
        "Si dos componentes tienen el mismo nombre, la simulación no funciona. Hay que renombrarlos.",
        "El contactor KM1 necesita un contacto auxiliar NA para el enclavamiento. No alcanza con la bobina.",
    ]),
    ("h2", "5.5. Pruebas"),
    ("p", "Antes de entregar voy a probar estos casos. La columna Resultado la completo después de simular."),
    T(["N.º", "Prueba", "Acción", "Resultado esperado", "Resultado (completar)"], [
        ["1", "Marcha", "Apretar S1", "KM1 y M1 en marcha; H1 encendida.", ""],
        ["2", "Paro", "Apretar S2", "KM1 y M1 se detienen; H1 apagada.", ""],
        ["3", "Tanque lleno", "Abrir N2", "KM1 se detiene; H1 apagada.", ""],
        ["4", "Vaciado", "SA1 en VACIADO", "YV1 se energiza; H2 encendida.", ""],
        ["5", "Nivel mínimo", "Abrir N1", "YV1 se desenergiza; H2 apagada.", ""],
        ["6", "Emergencia", "Apretar S0", "Todo se apaga.", ""],
        ["7", "Térmico", "Disparar F1", "Todo se apaga.", ""],
        ["8", "Enclavamiento", "Apretar S1 y soltar", "KM1 queda encendido.", ""],
        ["9", "Interlock", "SA1 en VACIADO + S1", "La bomba no arranca.", ""],
        ["10", "Repetición", "N1 abierto, SA1 en LLENADO, S1", "La bomba vuelve a arrancar.", ""],
    ]),
    ("note", "Las capturas de pantalla de las pruebas están en el Anexo B."),

    # ----------------------------- 6
    ("h1", "6. Demostración y conclusión"),
    ("h2", "6.1. Guion de la demostración"),
    ("ol", [
        "Mostrar el esquema y explicar los bloques: entradas, proceso, salidas y realimentación.",
        "Arrancar la bomba con S1 y mostrar H1.",
        "Simular el tanque lleno abriendo N2 y mostrar que la bomba se detiene.",
        "Girar el selector a VACIADO y mostrar H2 y la válvula.",
        "Simular el nivel mínimo abriendo N1 y mostrar que la válvula se cierra.",
        "Probar S0 y mostrar que todo se apaga.",
        "Explicar por qué usé CADe SIMU y no FluidSIM.",
    ]),
    ("p", "Tiempo estimado: 3 minutos."),
    ("h2", "6.2. Conclusión"),
    ("p", "Lo que más me costó fue separar la potencia del mando. Al principio quería poner los flotantes en serie con el motor, pero me di cuenta de que así el contacto del flotante corta la corriente del motor con carga y no es lo correcto. La solución fue poner los flotantes en el circuito de mando, que maneja la bobina del contactor."),
    ("p", "También aprendí a usar un contacto auxiliar para el enclavamiento y a poner las protecciones en serie. El sistema quedó simple pero completo: arranca, se detiene solo cuando el tanque está lleno, se vacía y se cierra cuando llega al mínimo."),
    ("p", "No automaticé el vaciado: hay que girar el selector. Lo dejé así para que el circuito sea fácil de entender. Una mejora posible sería agregar un relé de memoria que abra la válvula cuando N2 se active y la cierre cuando N1 se active. Otra mejora sería usar mando a 24 V y agregar un piloto de tanque lleno."),
    ("p", "Usé CADe SIMU porque no tengo FluidSIM. La parte eléctrica se puede simular completa y el sistema no necesita neumática. Si la cátedra pide FluidSIM, se podría hacer una variante neumática, pero para este sistema no hace falta."),

    # ----------------------------- ANEXOS
    ("h1", "Anexo A. Lista de materiales"),
    ("ul", [
        "Tanque de 100 L con base y desagüe.",
        "Bomba monofásica de 0,5 HP, 220 V.",
        "Electroválvula normalmente cerrada de 1/2\", 220 V.",
        "Dos flotantes NC (nivel mínimo y nivel máximo).",
        "Tablero con QM1, F2, KM1, F1, S0, S1, S2, SA1, H1, H2, borneras y cables.",
    ]),
    ("h1", "Anexo B. Capturas"),
    ("p", "Acá van las capturas de CADe SIMU. La primera muestra la bomba en marcha y la segunda la válvula de vaciado abierta."),
    ("placeholder", "Captura 1: bomba en marcha (pegar captura de CADe SIMU)"),
    ("placeholder", "Captura 2: válvula de vaciado abierta (pegar captura de CADe SIMU)"),
    ("h1", "Anexo C. Cosas que corregí"),
    ("ul", [
        "Primero puse N2 en el circuito de potencia. Mal: el contacto del flotante no está pensado para cortar el motor. Lo pasé al circuito de mando.",
        "Me olvidé del contacto auxiliar de KM1 y la bomba arrancaba solo mientras tenía apretado S1. Agregué el NA en paralelo.",
        "Usé un solo contacto del selector y la válvula se abría también en LLENADO. Lo corregí usando NA para LLENADO y NC para VACIADO.",
        "Al principio las lámparas estaban en serie con las bobinas. Las puse en paralelo.",
    ]),
]

# --------------------------------------------------------------------------
# UTILIDADES DE FORMATO
# --------------------------------------------------------------------------

def inline_html(s):
    s = html_lib.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def inline_md(s):
    return s


def add_inline_docx(paragraph, text, base_size=11, color=None, italic=False):
    """Agrega texto con **negrita**, *itálica* y `código` a un párrafo DOCX."""
    pattern = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            run = paragraph.add_run(text[pos:m.start()])
            run.font.size = Pt(base_size)
            run.italic = italic
            if color:
                run.font.color.rgb = color
        token = m.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        else:
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            run.font.size = Pt(base_size - 0.5)
        run.font.size = Pt(base_size)
        if color:
            run.font.color.rgb = color
        pos = m.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        run.font.size = Pt(base_size)
        run.italic = italic
        if color:
            run.font.color.rgb = color


def shade_cell(cell, fill="EEEEEE"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def shade_paragraph(paragraph, fill="F5F5F5"):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Hugo Ariel Martinez — Mecatrónica II — 2026   ·   Página ")
    run.font.name = "Arial"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run2 = p.add_run()
    run2.font.name = "Arial"
    run2.font.size = Pt(8)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    run2._r.append(fldChar1)
    run2._r.append(instrText)
    run2._r.append(fldChar2)


# --------------------------------------------------------------------------
# RENDER HTML / PDF
# --------------------------------------------------------------------------

def render_html(use_svg=True):
    body = []
    for block in BLOCKS:
        kind = block[0]
        val = block[1] if len(block) > 1 else None
        if kind == "cover_title":
            body.append(f'<div class="cover"><h1 class="cover-title">{inline_html(val)}</h1>')
        elif kind == "cover_sub":
            body.append(f'<p class="cover-sub">{inline_html(val)}</p>')
        elif kind == "cover_sub2":
            body.append(f'<p class="cover-sub2">{inline_html(val)}</p>')
        elif kind == "cover_rule":
            body.append('<div class="cover-rule"></div>')
        elif kind == "cover_meta":
            body.append(f'<p class="cover-meta">{inline_html(val)}</p>')
        elif kind == "cover_note":
            body.append(f'<p class="cover-note">{inline_html(val)}</p>')
        elif kind == "pagebreak":
            body.append('<div class="pagebreak"></div></div>')
        elif kind == "h1":
            body.append(f"<h1>{inline_html(val)}</h1>")
        elif kind == "h2":
            body.append(f"<h2>{inline_html(val)}</h2>")
        elif kind == "h3":
            body.append(f"<h3>{inline_html(val)}</h3>")
        elif kind == "p":
            body.append(f"<p>{inline_html(val)}</p>")
        elif kind == "note":
            body.append(f'<p class="note">{inline_html(val)}</p>')
        elif kind == "ul":
            body.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in val) + "</ul>")
        elif kind == "ol":
            body.append("<ol>" + "".join(f"<li>{inline_html(x)}</li>" for x in val) + "</ol>")
        elif kind == "code":
            body.append(f"<pre><code>{html_lib.escape(val)}</code></pre>")
        elif kind == "table":
            headers = val["headers"]
            rows = val["rows"]
            html = ['<table><thead><tr>']
            html += [f"<th>{inline_html(h)}</th>" for h in headers]
            html += ["</tr></thead><tbody>"]
            for row in rows:
                html.append("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in row) + "</tr>")
            html.append("</tbody></table>")
            body.append("".join(html))
        elif kind == "figure":
            src = val["svg"] if use_svg else val["png"]
            body.append(
                f'<figure><img src="{src}" style="width:{val["width"]}cm; height:{val.get("height", "auto")}cm; max-width:100%;" />'
                f'<figcaption>{inline_html(val["caption"])}</figcaption></figure>'
            )
        elif kind == "placeholder":
            body.append(f'<div class="placeholder">{inline_html(val)}</div>')

    css = """
    @page {
      size: A4;
      margin: 20mm 18mm 18mm 18mm;
      @bottom-center {
        content: "Hugo Ariel Martinez — Mecatrónica II — 2026   ·   Página " counter(page) " de " counter(pages);
        font-family: Arial, Helvetica, sans-serif;
        font-size: 8pt;
        color: #666;
      }
    }
    @page:first {
      @bottom-center { content: none; }
    }
    * { box-sizing: border-box; }
    body {
      font-family: Arial, Helvetica, sans-serif;
      font-size: 10.8pt;
      line-height: 1.42;
      color: #111;
      margin: 0;
    }
    h1 {
      font-size: 15pt;
      margin: 18pt 0 6pt 0;
      page-break-after: avoid;
    }
    h2 {
      font-size: 12pt;
      margin: 12pt 0 4pt 0;
      page-break-after: avoid;
    }
    h3 { font-size: 11pt; margin: 10pt 0 3pt 0; page-break-after: avoid; }
    p { margin: 0 0 7pt 0; text-align: left; }
    ul, ol { margin: 0 0 8pt 0; padding-left: 18pt; }
    li { margin-bottom: 3pt; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 6pt 0 10pt 0;
      font-size: 9pt;
      page-break-inside: auto;
    }
    thead { display: table-header-group; }
    tr { page-break-inside: avoid; }
    th, td {
      border: 1px solid #777;
      padding: 3.5pt 5pt;
      vertical-align: top;
      text-align: left;
    }
    th { background: #eeeeee; font-weight: bold; }
    figure {
      margin: 8pt 0 11pt 0;
      text-align: center;
      page-break-inside: avoid;
    }
    figure img { max-width: 100%; }
    figcaption {
      font-size: 8.8pt;
      color: #444;
      margin-top: 3pt;
      font-style: italic;
    }
    pre {
      background: #f5f5f5;
      border-left: 3px solid #999;
      padding: 7pt 9pt;
      font-family: Consolas, "Courier New", monospace;
      font-size: 8.8pt;
      white-space: pre-wrap;
      page-break-inside: avoid;
      margin: 6pt 0 9pt 0;
    }
    code { font-family: Consolas, "Courier New", monospace; font-size: 9pt; }
    .note {
      font-size: 9pt;
      color: #444;
      font-style: italic;
      margin: 3pt 0 8pt 0;
    }
    .pagebreak { page-break-after: always; }
    .cover {
      text-align: center;
      padding-top: 40mm;
    }
    .cover-title {
      font-size: 25pt;
      line-height: 1.15;
      margin: 0 0 10pt 0;
    }
    .cover-sub { font-size: 14pt; margin: 0 0 4pt 0; }
    .cover-sub2 { font-size: 11.5pt; color: #333; margin: 0 0 8mm 0; }
    .cover-rule {
      width: 55mm;
      height: 1px;
      background: #333;
      margin: 8mm auto 10mm auto;
    }
    .cover-meta { font-size: 11.5pt; margin: 3pt 0; }
    .cover-note {
      font-size: 9.5pt;
      color: #444;
      margin: 5mm 0 0 0;
    }
    .placeholder {
      border: 2px dashed #999;
      padding: 18pt;
      text-align: center;
      color: #777;
      font-style: italic;
      margin: 8pt 0;
      page-break-inside: avoid;
    }
    """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>TP Mecatrónica II — Estación de llenado y vaciado de tanque</title>
<style>{css}</style>
</head>
<body>
{''.join(body)}
</body>
</html>
"""


def render_markdown():
    out = []
    for block in BLOCKS:
        kind = block[0]
        val = block[1] if len(block) > 1 else None
        if kind == "cover_title":
            out.append(f"# {val}\n")
        elif kind == "cover_sub":
            out.append(f"## {val}\n")
        elif kind == "cover_sub2":
            out.append(f"*{val}*\n")
        elif kind == "cover_rule":
            out.append("---\n")
        elif kind == "cover_meta":
            out.append(f"{val}\n")
        elif kind == "cover_note":
            out.append(f"*{val}*\n")
        elif kind == "pagebreak":
            out.append("\n---\n")
        elif kind == "h1":
            out.append(f"\n# {val}\n")
        elif kind == "h2":
            out.append(f"\n## {val}\n")
        elif kind == "h3":
            out.append(f"\n### {val}\n")
        elif kind == "p":
            out.append(f"{val}\n")
        elif kind == "note":
            out.append(f"*{val}*\n")
        elif kind == "ul":
            out.extend([f"- {x}" for x in val])
            out.append("")
        elif kind == "ol":
            out.extend([f"{i+1}. {x}" for i, x in enumerate(val)])
            out.append("")
        elif kind == "code":
            out.append(f"```\n{val}\n```\n")
        elif kind == "table":
            headers = val["headers"]
            rows = val["rows"]
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "|".join(["---"] * len(headers)) + "|")
            for row in rows:
                out.append("| " + " | ".join(str(c) for c in row) + " |")
            out.append("")
        elif kind == "figure":
            out.append(f"![{val['caption']}]({val['png']})\n")
        elif kind == "placeholder":
            out.append(f"> **[PLACEHOLDER]** {val}\n")
    return "\n".join(out)


# --------------------------------------------------------------------------
# RENDER DOCX
# --------------------------------------------------------------------------

def render_docx(path):
    doc = Document()

    # Página A4 y márgenes
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    # Estilos base
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    pf = normal.paragraph_format
    pf.space_after = Pt(6)
    pf.line_spacing = 1.15

    for style_name, size, before, after in [("Heading 1", 15, 14, 6), ("Heading 2", 12, 10, 4)]:
        st = doc.styles[style_name]
        st.font.name = "Arial"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    add_page_number_footer(section)

    cover_open = False
    for block in BLOCKS:
        kind = block[0]
        val = block[1] if len(block) > 1 else None

        if kind == "cover_title":
            cover_open = True
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(120)
            run = p.add_run(val)
            run.bold = True
            run.font.name = "Arial"
            run.font.size = Pt(24)
            run.font.color.rgb = RGBColor(0, 0, 0)
        elif kind == "cover_sub":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            run.font.size = Pt(14)
        elif kind == "cover_sub2":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            run.font.size = Pt(11.5)
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            p.paragraph_format.space_after = Pt(24)
        elif kind == "cover_rule":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pPr = p._p.get_or_add_pPr()
            pBdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "6")
            bottom.set(qn("w:space"), "1")
            bottom.set(qn("w:color"), "333333")
            pBdr.append(bottom)
            pPr.append(pBdr)
            p.paragraph_format.space_after = Pt(18)
        elif kind == "cover_meta":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            run.font.size = Pt(11.5)
            p.paragraph_format.space_after = Pt(2)
        elif kind == "cover_note":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            run.italic = True
            p.paragraph_format.space_before = Pt(8)
        elif kind == "pagebreak":
            doc.add_page_break()
            cover_open = False
        elif kind == "h1":
            doc.add_heading(val, level=1)
        elif kind == "h2":
            doc.add_heading(val, level=2)
        elif kind == "h3":
            doc.add_heading(val, level=3)
        elif kind == "p":
            p = doc.add_paragraph()
            add_inline_docx(p, val, base_size=11)
        elif kind == "note":
            p = doc.add_paragraph()
            add_inline_docx(p, val, base_size=9.5, color=RGBColor(0x44, 0x44, 0x44), italic=True)
        elif kind == "ul":
            for item in val:
                p = doc.add_paragraph(style="List Bullet")
                add_inline_docx(p, item, base_size=11)
        elif kind == "ol":
            for item in val:
                p = doc.add_paragraph(style="List Number")
                add_inline_docx(p, item, base_size=11)
        elif kind == "code":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.4)
            p.paragraph_format.space_after = Pt(8)
            shade_paragraph(p, "F5F5F5")
            lines = val.split("\n")
            for i, line in enumerate(lines):
                run = p.add_run(line)
                run.font.name = "Consolas"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
                run.font.size = Pt(8.5)
                if i < len(lines) - 1:
                    run.add_break()
        elif kind == "table":
            headers = val["headers"]
            rows = val["rows"]
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            hdr = table.rows[0].cells
            for i, h in enumerate(headers):
                hdr[i].text = ""
                p = hdr[i].paragraphs[0]
                run = p.add_run(h)
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(9)
                shade_cell(hdr[i], "EEEEEE")
            for row in rows:
                cells = table.add_row().cells
                for i, c in enumerate(row):
                    cells[i].text = ""
                    p = cells[i].paragraphs[0]
                    run = p.add_run(str(c))
                    run.font.name = "Arial"
                    run.font.size = Pt(9)
            # Espacio después de la tabla
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
        elif kind == "figure":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(os.path.join(BASE, val["png"]), width=Cm(val["width"]))
            p.paragraph_format.space_after = Pt(2)
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = cap.add_run(val["caption"])
            run.font.name = "Arial"
            run.font.size = Pt(8.8)
            run.italic = True
            run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            cap.paragraph_format.space_after = Pt(10)
        elif kind == "placeholder":
            table = doc.add_table(rows=1, cols=1)
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = table.rows[0].cells[0]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = "Arial"
            run.font.size = Pt(9.5)
            run.italic = True
            run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)
            doc.add_paragraph()

    doc.save(path)


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    import generar_diagramas
    generar_diagramas.main()

    md = render_markdown()
    with open(os.path.join(BASE, "Informe_TP_Llenado_Tanque.md"), "w", encoding="utf-8") as f:
        f.write(md)

    html = render_html(use_svg=True)
    with open(os.path.join(BASE, "Informe_TP_Llenado_Tanque.html"), "w", encoding="utf-8") as f:
        f.write(html)

    HTML(string=html, base_url=BASE).write_pdf(os.path.join(BASE, "Informe_TP_Llenado_Tanque.pdf"))

    render_docx(os.path.join(BASE, "Informe_TP_Llenado_Tanque.docx"))

    print("Generado: MD, HTML, PDF y DOCX")


if __name__ == "__main__":
    main()
