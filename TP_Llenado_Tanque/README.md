# TP Mecatrónica II — Estación de llenado y vaciado de tanque

Trabajo práctico para la cátedra Mecatrónica II, UTN Facultad Regional Paraná, año 2026.

Alumno: Hugo Ariel Martinez.

## Qué hay en esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `Informe_TP_Llenado_Tanque.pdf` | Versión para leer o imprimir. Es la que conviene entregar. |
| `Informe_TP_Llenado_Tanque.docx` | Versión editable en Word. Acá se completan los datos y las capturas. |
| `Informe_TP_Llenado_Tanque.md` | Texto plano, por si hay que copiar o modificar algo rápido. |
| `Informe_TP_Llenado_Tanque.html` | Versión para abrir en el navegador o imprimir desde ahí. |
| `Guia_CADe_SIMU_paso_a_paso.md` | Guía personal para dibujar el circuito en CADe SIMU. No hace falta entregarla. |
| `Checklist_Demostracion.md` | Guion corto y preguntas posibles para la defensa. No hace falta entregarlo. |
| `generar_diagramas.py` | Genera las figuras de la carpeta `img/`. |
| `generar_informe.py` | Genera el informe en Markdown, HTML, PDF y DOCX. |
| `img/` | Diagramas en SVG y PNG. `diagrama_proceso.png` es un esquema extra de la planta, por si se quiere agregar al informe. |

## Sistema elegido

Estación de llenado y vaciado de un tanque de agua.

- La bomba llena el tanque.
- Una electroválvula lo vacía.
- Dos flotantes NC marcan el nivel mínimo y el máximo.
- El control es lógica cableada: contactor KM1 con enclavamiento y selector SA1.
- No usa PLC ni neumática.

Está elegido de la lista de la guía ("Sistema de llenado de tanque"). Se puede simular completo en CADe SIMU, que es la herramienta que tengo disponible.

## Por qué CADe SIMU y no FluidSIM

La guía pide FluidSIM, pero no tengo licencia. Para que la simulación sea completa elegí un sistema eléctrico, no neumático. La lógica de contactos, el contactor, el motor, los flotantes y las lámparas se pueden probar en CADe SIMU. El informe explica esto en la introducción y en la conclusión.

## Qué falta completar antes de entregar

1. Poner el nombre del profesor y la fecha en la portada (`[completar]`).
2. Dibujar el circuito en CADe SIMU y guardarlo como `TP_Llenado_Tanque.cad`.
3. Reemplazar los dos recuadros del Anexo B por capturas reales de CADe SIMU.
4. Hacer las 10 pruebas de la tabla 5.5 y completar la columna "Resultado".
5. Revisar que las fechas, la cátedra y el nombre estén bien.
6. Leer el informe completo y cambiar las frases que no suenen propias.

## Cómo generar el PDF y el DOCX de nuevo

Si se edita el texto en `generar_informe.py`:

```bash
cd TP_Llenado_Tanque
python3 generar_diagramas.py
python3 generar_informe.py
```

Si se edita el Word directamente, no hace falta generar nada: se guarda desde Word y se exporta a PDF con "Guardar como".

Dependencias usadas: `pymupdf`, `weasyprint`, `python-docx`, `cairosvg`, `htmldocx`, `pillow`. No son necesarias para entregar, solo para regenerar.

## Aclaraciones

- Los diagramas son esquemas de referencia, no capturas de CADe SIMU. Las capturas reales van en el Anexo B.
- El archivo `.cad` no se puede generar desde acá: hay que dibujarlo en el programa. La guía paso a paso explica cómo.
- La tabla de pruebas está vacía a propósito. Se completa después de simular, con lo que realmente pasó.
- Si la cátedra insiste con FluidSIM, el informe ya aclara que este sistema no necesita neumática y que se podría hacer una variante, pero no es lo que se entrega.

## Consejo para la entrega

El informe está escrito en primera persona y con lenguaje simple, pero conviene personalizarlo. Leerlo, corregir lo que no coincida con mi forma de hablar y, si se puede, rehacer el ladder a mano o con CADe SIMU. Eso vale más que un texto perfecto.
