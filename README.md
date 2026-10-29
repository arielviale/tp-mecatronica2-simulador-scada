# Mecatrónica II — Modelado y Simulación de un Sistema Mecatrónico
### Estación Automatizada de Clasificación Electroneumática de Piezas en Cinta Transportadora

---

<p align="center">
  <img src="https://img.shields.io/badge/Institución-UTN%20Facultad%20Regional%20Paraná-004b87?style=for-the-badge&logo=mortarboard" alt="UTN FRP"/>
  <img src="https://img.shields.io/badge/Carrera-Tecnicatura%20Superior%20en%20Mecatrónica-0284c7?style=for-the-badge" alt="Mecatrónica"/>
  <img src="https://img.shields.io/badge/Cátedra-Mecatrónica%20II-00e599?style=for-the-badge" alt="Mecatrónica II"/>
  <img src="https://img.shields.io/badge/Estándares-ISO%201219%20%7C%20IEC%2060617%20%7C%20ISA--101-ffb703?style=for-the-badge" alt="Normas"/>
</p>

---

## 📌 Datos Académicos e Institucionales

* **Universidad:** Universidad Tecnológica Nacional (UTN) — Facultad Regional Paraná.
* **Carrera:** Tecnicatura Superior en Mecatrónica.
* **Cátedra:** Mecatrónica II.
* **Alumno:** Hugo Ariel Martinez.
* **Trabajo Práctico:** Modelado y Simulación de un Sistema Mecatrónico mediante Simulador Electroneumático y SCADA Propio.
* **Sistema Seleccionado:** Estación de Clasificación de Piezas en Cinta Transportadora con Expulsores Electroneumáticos (3 Vías: Metal, Plástico y Descarte).

---

## 🚀 Puesta en Marcha Instantánea (Simulador Electroneumático + SCADA)

1. Hacer doble clic sobre el lanzador **`INICIAR_SIMULADOR.bat`** (o abrir directamente [`Simulador_SCADA/index.html`](Simulador_SCADA/index.html) en cualquier navegador moderno).
2. En la barra de control superior del simulador:
   * Presionar **`▶ MARCHA (S1)`** para enclavar el sistema (`K1 = 1`) y poner en marcha el motor de la cinta (`M1`).
   * Presionar **`⚙️ + Pieza Metálica`**, **`🟧 + Pieza Plástica`** o **`📦 + Pieza Descarte`**, o activar **`🔄 Alimentación Auto: ON`** para observar la secuencia completa automática.
3. También se puede hacer clic directamente sobre los contactos **`S0`**, **`S1`** y **`S2`** dentro del plano eléctrico de mando (**IEC 60617**) a la derecha de la pantalla, o regular en vivo la presión de la unidad FRL (`2.0` a `8.0 bar`) y los estranguladores de caudal (`1V2 / 2V2`).

---

## 📂 Estructura de Entregables del Proyecto

| Archivo / Carpeta | Descripción |
|---|---|
| 📄 [**Resolucion/Informe_TP_Modelado_y_Simulacion_Mecatronica.pdf**](Resolucion/Informe_TP_Modelado_y_Simulacion_Mecatronica.pdf) | **Informe Técnico Oficial (6 Páginas A4):** Cumplimiento íntegro de los 6 puntos de la consigna (Descripción del sistema, Entradas/Proceso/Salidas, Diagrama en Bloques, Lógica Booleana/GRAFCET, Planos Electroneumáticos ISO 1219 / IEC 60617 y Protocolo de Demostración). |
| 🖥️ [**Simulador_SCADA/**](Simulador_SCADA/) | **Suite Propia de Simulación Electroneumática y SCADA ISA-101:** Simulador web a 60 FPS con Gemelo Digital 2D de la planta, Circuito Neumático y Eléctrico animado en vivo, Diagrama Espacio-Fase en tiempo real, Audio Neumático sintetizado (Web Audio API) y Gestión de Alarmas ISA-18.2. |
| ▶️ [**INICIAR_SIMULADOR.bat**](INICIAR_SIMULADOR.bat) | Lanzador automático de un clic para la demostración en clase. |
