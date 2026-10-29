# -*- coding: utf-8 -*-
"""
Generador del Informe Técnico Oficial en PDF (6 Páginas A4 Calibradas)
Trabajo Práctico: Modelado y Simulación de un Sistema Mecatrónico — Suite de Simulación y SCADA Propia
UTN Facultad Regional Paraná — Tecnicatura Superior en Mecatrónica — Mecatrónica II
Alumno: Hugo Ariel Martinez
"""

import os
import subprocess
import fitz

os.makedirs("Resolucion", exist_ok=True)
OUTPUT_HTML = os.path.abspath("Resolucion/informe_tp_mecatronica.html")
OUTPUT_PDF = os.path.abspath("Resolucion/Informe_TP_Modelado_y_Simulacion_Mecatronica.pdf")

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>TP Modelado y Simulación de un Sistema Mecatrónico — Hugo Ariel Martinez</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 12mm 13mm 14mm 13mm;
    }

    *, *::before, *::after {
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
      font-size: 8.5pt;
      line-height: 1.38;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }

    .page {
      page-break-after: always;
      position: relative;
    }

    .page:last-child {
      page-break-after: auto;
    }

    /* Encabezado Principal */
    .header-box {
      border-bottom: 2.5px solid #004b87;
      padding-bottom: 7px;
      margin-bottom: 9px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }

    .inst-title {
      font-size: 10.5pt;
      font-weight: 800;
      color: #004b87;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      margin: 0 0 2px 0;
    }

    .inst-sub {
      font-size: 8pt;
      color: #475569;
      font-weight: 600;
      margin: 0;
    }

    .doc-meta {
      text-align: right;
      font-size: 7.6pt;
      color: #475569;
      line-height: 1.25;
    }

    .doc-meta b {
      color: #0f172a;
    }

    .running-header {
      border-bottom: 1.5px solid #cbd5e1;
      padding-bottom: 4px;
      margin-bottom: 9px;
      display: flex;
      justify-content: space-between;
      font-size: 7.5pt;
      color: #64748b;
      font-weight: 600;
    }

    /* Banner de Título */
    .title-banner {
      background: linear-gradient(135deg, #003366 0%, #004b87 65%, #0284c7 100%);
      color: #ffffff;
      padding: 10px 14px;
      border-radius: 6px;
      margin-bottom: 10px;
    }

    .title-banner h1 {
      font-size: 12.2pt;
      font-weight: 800;
      margin: 0 0 3px 0;
      letter-spacing: 0.2px;
    }

    .title-banner p {
      font-size: 8.2pt;
      margin: 0;
      color: #e0f2fe;
    }

    /* Títulos de Sección */
    h2.sec-title {
      font-size: 9.8pt;
      font-weight: 800;
      color: #004b87;
      text-transform: uppercase;
      border-left: 3.5px solid #0284c7;
      padding-left: 8px;
      margin: 9px 0 6px 0;
      letter-spacing: 0.2px;
    }

    h3.sub-title {
      font-size: 8.8pt;
      font-weight: 700;
      color: #0f172a;
      margin: 7px 0 4px 0;
    }

    p {
      margin: 0 0 6px 0;
      text-align: justify;
    }

    /* Cajas y Grillas */
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9px;
      margin-bottom: 8px;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
      margin-bottom: 8px;
    }

    .info-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-top: 2.5px solid #004b87;
      border-radius: 5px;
      padding: 7px 9px;
    }

    .info-card h4 {
      font-size: 8.3pt;
      font-weight: 800;
      color: #004b87;
      margin: 0 0 4px 0;
      text-transform: uppercase;
    }

    .callout {
      background: #f0f9ff;
      border-left: 3.5px solid #0284c7;
      border: 1px solid #bae6fd;
      border-left-width: 3.5px;
      border-radius: 4px;
      padding: 7px 10px;
      margin-bottom: 8px;
      font-size: 8.2pt;
    }

    .callout-title {
      font-weight: 800;
      color: #0369a1;
      margin-bottom: 2px;
      text-transform: uppercase;
      font-size: 8pt;
    }

    /* Tablas Técnicas */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 6px;
      font-size: 7.45pt;
      line-height: 1.25;
    }

    th {
      background: #004b87;
      color: #ffffff;
      font-weight: 700;
      text-align: left;
      padding: 3.5px 6px;
      border: 1px solid #003b6b;
    }

    td {
      padding: 3px 6px;
      border: 1px solid #cbd5e1;
      vertical-align: top;
    }

    tr:nth-child(even) td {
      background: #f8fafc;
    }

    .mono {
      font-family: 'Consolas', 'Courier New', monospace;
      font-weight: 700;
      color: #0f172a;
    }

    .badge {
      display: inline-block;
      padding: 1px 5px;
      border-radius: 3px;
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
    }

    .b-in { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .b-sensor { background: #e0f2fe; color: #075985; border: 1px solid #7dd3fc; }
    .b-reed { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
    .b-out { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .b-safe { background: #ffe4e6; color: #9f1239; border: 1px solid #fda4af; }

    .svg-box {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      background: #ffffff;
      padding: 6px;
      margin-bottom: 8px;
      text-align: center;
    }

    .svg-caption {
      font-size: 7.4pt;
      color: #475569;
      font-style: italic;
      margin-top: 3px;
      text-align: center;
    }

    ul {
      margin: 0 0 6px 0;
      padding-left: 16px;
    }

    li {
      margin-bottom: 2.5px;
    }
  </style>
</head>
<body>

  <!-- ===================================================================== -->
  <!-- PÁGINA 1: SELECCIÓN Y DESCRIPCIÓN DEL SISTEMA MECATRÓNICO             -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="header-box">
      <div>
        <div class="inst-title">Universidad Tecnológica Nacional — Facultad Regional Paraná</div>
        <div class="inst-sub">Tecnicatura Superior en Mecatrónica · Cátedra: Mecatrónica II</div>
      </div>
      <div class="doc-meta">
        <b>Trabajo Práctico:</b> Modelado y Simulación Mecatrónica<br>
        <b>Alumno:</b> Hugo Ariel Martinez<br>
        <b>Fecha:</b> Octubre 2026 · <b>Pág. 1 de 6</b>
      </div>
    </div>

    <div class="title-banner">
      <h1>MODELADO Y SIMULACIÓN DE UN SISTEMA MECATRÓNICO: ESTACIÓN DE CLASIFICACIÓN ELECTRONEUMÁTICA DE PIEZAS EN CINTA</h1>
      <p>Resolución Integral según Normas ISO 1219-1/2 (Neumática), IEC 60617 (Mando Eléctrico), IEC 60848 (GRAFCET) y Supervisión SCADA ISA-101</p>
    </div>

    <h2 class="sec-title">1. Selección y Descripción del Sistema Mecatrónico (Consigna Punto 1)</h2>
    <p>
      Para el desarrollo del presente Trabajo Práctico se seleccionó un <b>Sistema Automatizado de Clasificación de Piezas en Cinta Transportadora con Expulsores Electroneumáticos</b>. Este sistema constituye un caso arquetípico de la <b>ingeniería mecatrónica industrial</b>, ya que integra de forma sinérgica cuatro dominios tecnológicos fundamentales: <b>mecánica de transporte continuo</b> (cinta motorizada y rampas de desvío), <b>neumática de potencia</b> (cilindros de doble efecto y electroválvulas direccionales 5/2), <b>sensórica industrial heterogénea</b> (detección óptica, inductiva, capacitiva y magnética Reed) y <b>control lógico secuencial</b> (implementado íntegramente en nuestra suite interactiva propia de Simulación Electroneumática y Supervisión SCADA).
    </p>

    <div class="grid-3">
      <div class="info-card">
        <h4>Función Principal</h4>
        Transportar piezas de manufactura sobre una banda motorizada (<b>M1</b>), identificar sin contacto la naturaleza del material (<b>Metálico vs. Plástico/Polímero</b>) y segregar automáticamente cada unidad hacia su tolva de acopio mediante cilindros neumáticos (<b>1A1</b> y <b>2A1</b>).
      </div>
      <div class="info-card">
        <h4>Aplicación Industrial</h4>
        Líneas de empaque y logística (<i>sorters</i>), reciclaje automatizado de envases (aluminio vs. PET), control de calidad en mecanizado metalmecánico y alimentación selectiva de celdas de ensamblaje robotizadas.
      </div>
      <div class="info-card">
        <h4>Justificación Mecatrónica</h4>
        A diferencia de un mecanismo puramente neumático o eléctrico aislado, este sistema requiere sincronizar el movimiento continuo de un motor eléctrico con actuaciones lineales discretas y realimentación de posición en lazo cerrado.
      </div>
    </div>

    <h3 class="sub-title">1.1. Arquitectura Física y Disposición en Planta (Layout Mecatrónico)</h3>
    <div class="svg-box">
      <svg viewBox="0 0 760 256" width="100%" height="auto">
        <rect x="4" y="4" width="752" height="248" rx="6" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2"/>
        <text x="16" y="20" fill="#004b87" font-size="9" font-weight="800" font-family="Segoe UI">ESQUEMA FUNCIONAL DE PLANTA — ESTACIÓN CLASIFICADORA DE 3 VÍAS (VISTA SUPERIOR)</text>

        <!-- Unidad FRL -->
        <rect x="18" y="34" width="142" height="48" rx="4" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5"/>
        <text x="89" y="52" fill="#0369a1" font-size="8.5" font-weight="800" text-anchor="middle">GRUPO FRL (0Z1) + P1</text>
        <text x="89" y="67" fill="#0f172a" font-size="7.8" text-anchor="middle">Red Aire 6.0 bar (Umbral ≥ 5b)</text>

        <!-- Cilindro 1A1 -->
        <g transform="translate(275, 28)">
          <text x="35" y="9" fill="#004b87" font-size="8.5" font-weight="800" text-anchor="middle">CILINDRO 1A1 (METAL)</text>
          <rect x="15" y="15" width="40" height="62" rx="3" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
          <rect x="20" y="23" width="30" height="7" fill="#0284c7"/>
          <rect x="31" y="30" width="8" height="55" fill="#64748b"/>
          <rect x="19" y="84" width="32" height="7" rx="2" fill="#0284c7"/>
          <text x="64" y="29" fill="#6b21a8" font-size="7.8" font-weight="700">1B1 (a0=0mm)</text>
          <text x="64" y="72" fill="#6b21a8" font-size="7.8" font-weight="700">1B2 (a1=100mm)</text>
        </g>

        <!-- Cilindro 2A1 -->
        <g transform="translate(475, 28)">
          <text x="35" y="9" fill="#b45309" font-size="8.5" font-weight="800" text-anchor="middle">CILINDRO 2A1 (PLÁSTICO)</text>
          <rect x="15" y="15" width="40" height="62" rx="3" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
          <rect x="20" y="23" width="30" height="7" fill="#d97706"/>
          <rect x="31" y="30" width="8" height="55" fill="#64748b"/>
          <rect x="19" y="84" width="32" height="7" rx="2" fill="#d97706"/>
          <text x="64" y="29" fill="#6b21a8" font-size="7.8" font-weight="700">2B1 (b0=0mm)</text>
          <text x="64" y="72" fill="#6b21a8" font-size="7.8" font-weight="700">2B2 (b1=100mm)</text>
        </g>

        <!-- Cinta Transportadora -->
        <g transform="translate(95, 122)">
          <rect x="0" y="0" width="535" height="52" rx="8" fill="#334155" stroke="#0f172a" stroke-width="1.8"/>
          <line x1="20" y1="26" x2="515" y2="26" stroke="#475569" stroke-width="34" stroke-dasharray="12 12"/>
          <circle cx="18" cy="26" r="17" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
          <circle cx="517" cy="26" r="17" fill="#1e293b" stroke="#94a3b8" stroke-width="1.5"/>
          <!-- Piezas ejemplo -->
          <circle cx="75" cy="26" r="12" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"/>
          <text x="75" y="29" fill="#fff" font-size="7.5" font-weight="700" text-anchor="middle">FE</text>
          <rect x="320" y="14" width="24" height="24" rx="4" fill="#d97706" stroke="#ffffff" stroke-width="1.5"/>
          <text x="332" y="29" fill="#fff" font-size="7.5" font-weight="700" text-anchor="middle">PL</text>
        </g>

        <!-- Motor M1 -->
        <rect x="18" y="128" width="66" height="40" rx="4" fill="#dcfce7" stroke="#166534" stroke-width="1.5"/>
        <text x="51" y="146" fill="#166534" font-size="8.5" font-weight="800" text-anchor="middle">MOTOR M1</text>
        <text x="51" y="158" fill="#166534" font-size="7.5" text-anchor="middle">Contactor KM1</text>
        <line x1="84" y1="148" x2="95" y2="148" stroke="#166534" stroke-width="3"/>

        <!-- Sensores B1, B2, B3 -->
        <rect x="132" y="94" width="58" height="18" rx="3" fill="#dcfce7" stroke="#166534" stroke-width="1.2"/>
        <text x="161" y="106" fill="#166534" font-size="7.8" font-weight="700" text-anchor="middle">B1 (Óptico)</text>
        <line x1="161" y1="112" x2="161" y2="122" stroke="#166534" stroke-width="1.2" stroke-dasharray="2 2"/>

        <rect x="206" y="94" width="70" height="18" rx="3" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.2"/>
        <text x="241" y="106" fill="#0369a1" font-size="7.8" font-weight="700" text-anchor="middle">B2 (Inductivo)</text>
        <polyline points="241,112 241,117 310,117 310,122" fill="none" stroke="#0369a1" stroke-width="1.2" stroke-dasharray="2 2"/>

        <rect x="404" y="94" width="70" height="18" rx="3" fill="#fef3c7" stroke="#b45309" stroke-width="1.2"/>
        <text x="439" y="106" fill="#b45309" font-size="7.8" font-weight="700" text-anchor="middle">B3 (Capacit.)</text>
        <polyline points="439,112 439,117 510,117 510,122" fill="none" stroke="#b45309" stroke-width="1.2" stroke-dasharray="2 2"/>

        <!-- Rampas de Salida -->
        <rect x="276" y="178" width="68" height="62" rx="4" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
        <text x="310" y="200" fill="#1d4ed8" font-size="8.5" font-weight="800" text-anchor="middle">TOLVA 1</text>
        <text x="310" y="214" fill="#1e293b" font-size="7.5" text-anchor="middle">Piezas Metálicas</text>
        <text x="310" y="228" fill="#2563eb" font-size="7.5" font-weight="700" text-anchor="middle">(Expulsor 1A1)</text>

        <rect x="476" y="178" width="68" height="62" rx="4" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>
        <text x="510" y="200" fill="#b45309" font-size="8.5" font-weight="800" text-anchor="middle">TOLVA 2</text>
        <text x="510" y="214" fill="#1e293b" font-size="7.5" text-anchor="middle">Piezas Plásticas</text>
        <text x="510" y="228" fill="#b45309" font-size="7.5" font-weight="700" text-anchor="middle">(Expulsor 2A1)</text>

        <rect x="642" y="118" width="96" height="62" rx="4" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
        <text x="690" y="142" fill="#334155" font-size="8.5" font-weight="800" text-anchor="middle">TOLVA 3</text>
        <text x="690" y="156" fill="#475569" font-size="7.5" text-anchor="middle">Final de Cinta</text>
        <text x="690" y="169" fill="#475569" font-size="7.5" text-anchor="middle">(Paso Directo)</text>
      </svg>
      <div class="svg-caption">Figura 1.1: Disposición física de actuadores, sensores de campo y estaciones de clasificación en la cinta transportadora.</div>
    </div>

    <h3 class="sub-title">1.2. Descripción Operativa de las Estaciones de Trabajo</h3>
    <ul>
      <li><b>Zona de Alimentación y Validación de Ingreso (Sensor Óptico B1):</b> Las piezas se depositan al comienzo de la banda impulsada por el motor eléctrico <b>M1</b>. Al cortar la barrera fotoeléctrica <b>B1</b>, la lógica incrementa el contador de lote entrante y enclava el relé auxiliar de <b>Pieza en Tránsito (KB1)</b>, habilitando las estaciones de clasificación posteriores (evitando disparos falsos en B2/B3 si un operario acerca una herramienta sin ingreso previo por B1).</li>
      <li><b>Estación Clasificadora 1 — Metales (Sensor Inductivo B2 + Cilindro 1A1):</b> Cuando una pieza validada por <b>B1 (KB1=1)</b> enfrenta al detector inductivo <b>B2</b>, la lógica detiene momentáneamente la cinta y energiza el solenoide <b>1Y1</b> de la electroválvula 5/2 (<b>1V1</b>). El cilindro de doble efecto <b>1A1</b> avanza (<b>A+</b>) empujando la pieza hacia la <b>Tolva 1</b>. Al alcanzar el límite delantero <b>1B2 (a1)</b>, se desenergiza <b>1Y1</b> y el cilindro retorna (<b>A-</b>) hasta accionar <b>1B1 (a0)</b>, reanudando la marcha de la cinta.</li>
      <li><b>Estación Clasificadora 2 — Plásticos (Sensor Capacitivo B3 + Cilindro 2A1):</b> Las piezas poliméricas no excitan al sensor inductivo B2 y continúan avanzando hasta la segunda estación, donde el sensor capacitivo/óptico <b>B3</b> las detecta (con permiso <b>KB1=1</b>) y dispara el ciclo análogo (<b>B+ / B-</b>) sobre el cilindro <b>2A1</b> comandado por la electroválvula <b>2V1 (2Y1)</b> hacia la <b>Tolva 2</b>.</li>
      <li><b>Estación Final — Tolva 3:</b> Cualquier pieza no clasificada en las estaciones previas continúa hasta el extremo de descarga gravitacional.</li>
    </ul>
  </div>

  <!-- ===================================================================== -->
  <!-- PÁGINA 2: IDENTIFICACIÓN DE ENTRADAS, PROCESO Y SALIDAS               -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Facultad Regional Paraná · Mecatrónica II — Modelado y Simulación de Sistemas Mecatrónicos</span>
      <span>Alumno: Hugo Ariel Martinez · Pág. 2 de 6</span>
    </div>

    <h2 class="sec-title">2. Identificación de Entradas, Proceso y Salidas (Consigna Punto 2)</h2>
    <p>
      Siguiendo la estructura exigida en la guía del Trabajo Práctico, se detallan a continuación todas las variables de <b>Entrada</b> (pulsadores de mando, sensores de presencia/material, interruptores de fin de carrera y presostato), la etapa de <b>Proceso</b> y las <b>Salidas</b> hacia actuadores eléctricos, neumáticos e indicadores luminosos, codificadas según la norma <b>ISO 1219-2 / IEC 61131-3</b>.
    </p>

    <h3 class="sub-title">2.1. Tabla Maestra de Entradas del Sistema (Sensores y Elementos de Mando)</h3>
    <table style="font-size: 7.15pt; line-height: 1.18;">
      <thead>
        <tr>
          <th style="width: 11%;">Símbolo</th>
          <th style="width: 14%;">Categoría</th>
          <th style="width: 24%;">Componente / Tecnología</th>
          <th style="width: 14%;">Naturaleza</th>
          <th style="width: 37%;">Función Específica en el Proceso</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="mono">S0 (%I0.0)</td>
          <td><span class="badge b-safe">Seguridad</span></td>
          <td>Pulsador golpe de puño (Seta)</td>
          <td>Contacto NC (24V)</td>
          <td><b>Parada de Emergencia (Fail-Safe):</b> Abre el mando, detiene M1, retrae 1A1/2A1 por resorte y enclava la memoria de bloqueo por falla <b>KF</b>.</td>
        </tr>
        <tr>
          <td class="mono">S1 (%I0.1)</td>
          <td><span class="badge b-in">Pulsador</span></td>
          <td>Pulsador luminoso verde</td>
          <td>Contacto NA (24V)</td>
          <td><b>Marcha de Ciclo:</b> Inicia el funcionamiento automático del sistema enclavando el relé maestro K1 (si <b>/KF=1</b>).</td>
        </tr>
        <tr>
          <td class="mono">S2 (%I0.2)</td>
          <td><span class="badge b-in">Pulsador</span></td>
          <td>Pulsador rasante rojo</td>
          <td>Contacto NC (24V)</td>
          <td><b>Parada Normal:</b> Desenclava la retención de marcha K1 deteniendo la estación de forma controlada.</td>
        </tr>
        <tr>
          <td class="mono">S3 (%I0.7)</td>
          <td><span class="badge b-in">Pulsador</span></td>
          <td>Pulsador azul de tablero</td>
          <td>Contacto NA (24V)</td>
          <td><b>Rearme / Reset de Falla:</b> Desenclava la memoria de bloqueo <b>KF</b> (<span class="mono">KF=(/S0+/P1+ALM+KF)·/S3</span>) tras normalizar fallas, restituyendo el permiso de K1.</td>
        </tr>
        <tr>
          <td class="mono">B1 (%I0.3)</td>
          <td><span class="badge b-sensor">Detector</span></td>
          <td>Sensor Fotoeléctrico de Barrera</td>
          <td>Digital PNP 24V DC</td>
          <td><b>Presencia, Conteo y Atasco:</b> Enclava el permiso de pieza en tránsito <b>KB1</b>, cuenta el lote entrante y detecta atasco si permanece obstruido &gt; 3,0 s.</td>
        </tr>
        <tr>
          <td class="mono">B2 (%I0.4)</td>
          <td><span class="badge b-sensor">Sensor</span></td>
          <td>Sensor de Proximidad Inductivo</td>
          <td>Digital PNP 24V DC</td>
          <td><b>Detector de Metal (Estación 1):</b> Conmuta a "1" lógico únicamente ante piezas metálicas frente al cilindro 1A1.</td>
        </tr>
        <tr>
          <td class="mono">B3 (%I0.5)</td>
          <td><span class="badge b-sensor">Sensor</span></td>
          <td>Sensor Capacitivo / Óptico Difuso</td>
          <td>Digital PNP 24V DC</td>
          <td><b>Detector de Plástico (Estación 2):</b> Detecta la llegada de piezas poliméricas frente al cilindro expulsor 2A1.</td>
        </tr>
        <tr>
          <td class="mono">1B1 (a0)</td>
          <td><span class="badge b-reed">Fin Carrera</span></td>
          <td>Sensor Magnético Reed en 1A1</td>
          <td>Contacto NA (0 mm)</td>
          <td><b>Cilindro 1A1 Retraído:</b> Confirma que el vástago 1A1 está en posición trasera (0 mm), habilitando el giro de la cinta M1.</td>
        </tr>
        <tr>
          <td class="mono">1B2 (a1)</td>
          <td><span class="badge b-reed">Fin Carrera</span></td>
          <td>Sensor Magnético Reed en 1A1</td>
          <td>Contacto NA (100mm)</td>
          <td><b>Cilindro 1A1 Extendido:</b> Detecta fin de carrera delantero (100 mm) y ordena el corte de 1Y1 para el retroceso A-.</td>
        </tr>
        <tr>
          <td class="mono">2B1 (b0)</td>
          <td><span class="badge b-reed">Fin Carrera</span></td>
          <td>Sensor Magnético Reed en 2A1</td>
          <td>Contacto NA (0 mm)</td>
          <td><b>Cilindro 2A1 Retraído:</b> Confirma que el vástago 2A1 está en reposo (0 mm), permitiendo el avance seguro de la cinta.</td>
        </tr>
        <tr>
          <td class="mono">2B2 (b1)</td>
          <td><span class="badge b-reed">Fin Carrera</span></td>
          <td>Sensor Magnético Reed en 2A1</td>
          <td>Contacto NA (100mm)</td>
          <td><b>Cilindro 2A1 Extendido:</b> Detecta carrera completa (100 mm) de expulsión plástica y ordena el retorno B-.</td>
        </tr>
        <tr>
          <td class="mono">P1 (%I0.6)</td>
          <td><span class="badge b-sensor">Sensor Neum.</span></td>
          <td>Presostato Electroneumático FRL</td>
          <td>Contacto NA (≥ 5 bar)</td>
          <td><b>Supervisión de Presión:</b> Valida que la red neumática posea al menos 5,0 bar antes de autorizar la marcha.</td>
        </tr>
      </tbody>
    </table>

    <h3 class="sub-title">2.2. Tabla Maestra de Salidas del Sistema (Pre-actuadores, Actuadores e Indicadores)</h3>
    <table style="font-size: 7.15pt; line-height: 1.18;">
      <thead>
        <tr>
          <th style="width: 13%;">Símbolo</th>
          <th style="width: 16%;">Tipo de Salida</th>
          <th style="width: 26%;">Pre-actuador / Actuador Asociado</th>
          <th style="width: 45%;">Acción Física y Efecto sobre la Planta</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="mono">KM1 ➔ M1</td>
          <td><span class="badge b-out">Motor Eléctrico</span></td>
          <td>Contactor KM1 + Motorreductor de Cinta M1</td>
          <td>Acciona los rodillos de la cinta transportadora a velocidad nominal (120 mm/s) mientras no haya expulsión en curso.</td>
        </tr>
        <tr>
          <td class="mono">1Y1 ➔ 1V1 ➔ 1A1</td>
          <td><span class="badge b-out">Electroválvula + Cilindro</span></td>
          <td>Solenoide 1Y1 (EV 5/2 Monoestable 1V1) + Cilindro Doble Efecto 1A1 (Ø32x100 mm)</td>
          <td>Al energizarse 1Y1, conmuta 1V1 enviando presión de 6 bar a la cámara trasera de 1A1 (<b>Avance A+</b>) para expulsar piezas metálicas. Al desenergizarse, el muelle retorna 1V1 produciendo el <b>Retroceso A-</b>.</td>
        </tr>
        <tr>
          <td class="mono">2Y1 ➔ 2V1 ➔ 2A1</td>
          <td><span class="badge b-out">Electroválvula + Cilindro</span></td>
          <td>Solenoide 2Y1 (EV 5/2 Monoestable 2V1) + Cilindro Doble Efecto 2A1 (Ø32x100 mm)</td>
          <td>Al energizarse 2Y1, conmuta 2V1 provocando el <b>Avance B+</b> del cilindro 2A1 para desviar piezas plásticas hacia la Tolva 2. Al cortar 2Y1, el resorte restituye la posición produciendo el <b>Retroceso B-</b>.</td>
        </tr>
        <tr>
          <td class="mono">H1 / H2 / H3</td>
          <td><span class="badge b-out">Torreta Andon</span></td>
          <td>Pilotos LED Verde (H1), Amarillo (H2) y Rojo + Sirena (H3)</td>
          <td><b>H1:</b> Marcha activa (K1=1) · <b>H2:</b> Clasificación en curso (K2+K3) · <b>H3:</b> Bloqueo por falla (KF=1 por S0, P1&lt;5b, timeout de cilindro o conflicto B2/B3).</td>
        </tr>
      </tbody>
    </table>

    <h3 class="sub-title">2.3. Tabla de Polaridades, Contactos Físicos y Convención Lógica (IEC 61131-3)</h3>
    <table style="font-size: 7.1pt; line-height: 1.15; margin-bottom: 0;">
      <thead>
        <tr>
          <th style="width: 14%;">Señal</th>
          <th style="width: 16%;">Contacto Físico</th>
          <th style="width: 24%;">Estado Normal (Planta en Reposo)</th>
          <th style="width: 46%;">Interpretación Lógica en Ecuaciones de Control</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="mono">S0 / S2</td>
          <td>NC (Fail-Safe)</td>
          <td>Cerrado en reposo (24V presentes)</td>
          <td><span class="mono">1</span> = Sin emergencia / sin parada (<span class="mono">0</span> = Abre circuito al presionar o cortarse el cable)</td>
        </tr>
        <tr>
          <td class="mono">S1 / S3</td>
          <td>NA (Mando)</td>
          <td>Abierto en reposo (0V)</td>
          <td><span class="mono">1</span> = Pulso de marcha (<span class="mono">S1</span>) o pulso manual de rearme de alarma (<span class="mono">S3</span>)</td>
        </tr>
        <tr>
          <td class="mono">P1</td>
          <td>NA (Presostato)</td>
          <td>Cerrado con red presurizada a 6 bar</td>
          <td><span class="mono">1</span> = Presión neumática válida (≥ 5,0 bar) · <span class="mono">0</span> = Caída de presión (&lt; 5,0 bar)</td>
        </tr>
        <tr>
          <td class="mono">B1 / B2 / B3</td>
          <td>PNP NA (3 hilos)</td>
          <td>Abierto sin pieza frente al cabezal (0V)</td>
          <td><span class="mono">1</span> = Pieza detectada en ingreso (<span class="mono">B1</span>), estación metal (<span class="mono">B2</span>) o estación plástico (<span class="mono">B3</span>)</td>
        </tr>
        <tr>
          <td class="mono">1B1 (a0) / 2B1 (b0)</td>
          <td>Reed NA (en 0 mm)</td>
          <td><b>Cerrado en reposo</b> (accionado por émbolo)</td>
          <td><span class="mono">1</span> = Cilindro totalmente retraído en origen (0 mm) · <span class="mono">0</span> = Vástago fuera de origen</td>
        </tr>
        <tr>
          <td class="mono">1B2 (a1) / 2B2 (b1)</td>
          <td>Reed NA (en 100mm)</td>
          <td>Abierto en reposo (0V)</td>
          <td><span class="mono">1</span> = Cilindro totalmente extendido al final de carrera delantero (100 mm)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ===================================================================== -->
  <!-- PÁGINA 3: DIAGRAMA EN BLOQUES DEL SISTEMA MECATRÓNICO                 -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Facultad Regional Paraná · Mecatrónica II — Modelado y Simulación de Sistemas Mecatrónicos</span>
      <span>Alumno: Hugo Ariel Martinez · Pág. 3 de 6</span>
    </div>

    <h2 class="sec-title">3. Diagrama en Bloques del Sistema Mecatrónico Completo (Consigna Punto 3)</h2>
    <p>
      Todo sistema mecatrónico se modela estructuralmente diferenciando tres flujos concurrentes: el <b>Flujo de Información / Señales de Control</b> (líneas continuas), el <b>Flujo de Energía Eléctrica y Neumática</b> (líneas de trazos superiores) y el <b>Flujo de Material</b> sobre la planta física, cerrado mediante el <b>Lazo de Realimentación (Feedback)</b> de los sensores e interruptores de fin de carrera.
    </p>

    <div class="svg-box" style="padding: 10px;">
      <svg viewBox="0 0 760 355" width="100%" height="auto">
        <!-- Marco Exterior del Sistema Mecatrónico -->
        <rect x="6" y="6" width="748" height="343" rx="8" fill="#f8fafc" stroke="#004b87" stroke-width="1.6"/>
        <text x="18" y="24" fill="#004b87" font-size="9.5" font-weight="800">DIAGRAMA EN BLOQUES DE LAZO CERRADO — SISTEMA CLASIFICADOR ELECTRONEUMÁTICO</text>

        <!-- SUBSISTEMA DE ALIMENTACIÓN DE ENERGÍA -->
        <rect x="195" y="34" width="465" height="46" rx="5" fill="#eff6ff" stroke="#0284c7" stroke-width="1.5"/>
        <text x="427" y="50" fill="#004b87" font-size="8.5" font-weight="800" text-anchor="middle">SUBSISTEMA DE SUMINISTRO Y ACONDICIONAMIENTO DE ENERGÍA</text>
        <text x="427" y="64" fill="#1e293b" font-size="7.8" text-anchor="middle">• Fuente 24V DC (Mando y Sensores) · Red Eléctrica (Motor M1) · Compresor + Unidad FRL 0Z1 a 6,0 bar (Potencia Neumática)</text>

        <!-- Flechas de energía hacia bloques -->
        <line x1="275" y1="80" x2="275" y2="115" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4 3"/>
        <polygon points="275,115 271,107 279,107" fill="#0284c7"/>
        <line x1="465" y1="80" x2="465" y2="115" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4 3"/>
        <polygon points="465,115 461,107 469,107" fill="#0284c7"/>
        <line x1="640" y1="80" x2="640" y2="115" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4 3"/>
        <polygon points="640,115 636,107 644,107" fill="#0284c7"/>

        <!-- BLOQUE 1: INTERFAZ HOMBRE-MÁQUINA Y ENTRADAS DE MANDO -->
        <rect x="18" y="115" width="148" height="122" rx="6" fill="#dcfce7" stroke="#166534" stroke-width="1.8"/>
        <text x="92" y="133" fill="#166534" font-size="8.5" font-weight="800" text-anchor="middle">1. ENTRADAS DE MANDO</text>
        <text x="92" y="145" fill="#166534" font-size="7.5" font-weight="700" text-anchor="middle">Y SENSORES DE CAMPO</text>
        <line x1="26" y1="151" x2="158" y2="151" stroke="#86efac" stroke-width="1.2"/>
        <text x="26" y="166" fill="#0f172a" font-size="7.6">• Pulsadores: S1, S2, S3</text>
        <text x="26" y="180" fill="#0f172a" font-size="7.6">• Parada Emergencia: S0</text>
        <text x="26" y="194" fill="#0f172a" font-size="7.6">• Presencia: B1 (Óptico)</text>
        <text x="26" y="208" fill="#0f172a" font-size="7.6">• Material: B2 (Ind), B3 (Cap)</text>
        <text x="26" y="222" fill="#0f172a" font-size="7.6">• Presostato Red: P1 (≥5b)</text>

        <line x1="166" y1="176" x2="198" y2="176" stroke="#0f172a" stroke-width="2"/>
        <polygon points="198,176 190,172 190,180" fill="#0f172a"/>

        <!-- BLOQUE 2: UNIDAD DE PROCESAMIENTO LÓGICO (CONTROL) -->
        <rect x="198" y="115" width="162" height="122" rx="6" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.8"/>
        <text x="279" y="133" fill="#0369a1" font-size="8.5" font-weight="800" text-anchor="middle">2. PROCESO / UNIDAD</text>
        <text x="279" y="145" fill="#0369a1" font-size="7.5" font-weight="700" text-anchor="middle">DE CONTROL SECUENCIAL</text>
        <line x1="206" y1="151" x2="352" y2="151" stroke="#7dd3fc" stroke-width="1.2"/>
        <text x="206" y="166" fill="#0f172a" font-size="7.6">• Rearme Falla KF (S3 / S0 / P1)</text>
        <text x="206" y="180" fill="#0f172a" font-size="7.6">• Validación Ingreso KB1 (B1)</text>
        <text x="206" y="194" fill="#0f172a" font-size="7.6">• Marcha K1 y Cinta KM1 (1B1·2B1)</text>
        <text x="206" y="208" fill="#0f172a" font-size="7.6">• Secuencia Metal K2 (A+ A-)</text>
        <text x="206" y="222" fill="#0f172a" font-size="7.6">• Secuencia Plást. K3 (B+ B-)</text>

        <line x1="360" y1="176" x2="392" y2="176" stroke="#0f172a" stroke-width="2"/>
        <polygon points="392,176 384,172 384,180" fill="#0f172a"/>

        <!-- BLOQUE 3: ETAPA DE PRE-ACTUACIÓN (CONVERSIÓN DE POTENCIA) -->
        <rect x="392" y="115" width="152" height="122" rx="6" fill="#fef3c7" stroke="#b45309" stroke-width="1.8"/>
        <text x="468" y="133" fill="#b45309" font-size="8.5" font-weight="800" text-anchor="middle">3. PRE-ACTUADORES</text>
        <text x="468" y="145" fill="#b45309" font-size="7.5" font-weight="700" text-anchor="middle">(INTERFAZ DE POTENCIA)</text>
        <line x1="400" y1="151" x2="536" y2="151" stroke="#fde68a" stroke-width="1.2"/>
        <text x="400" y="166" fill="#0f172a" font-size="7.6">• Contactor de Fuerza KM1</text>
        <text x="400" y="180" fill="#0f172a" font-size="7.6">• EV 5/2 Monoestable 1V1 (1Y1)</text>
        <text x="400" y="194" fill="#0f172a" font-size="7.6">• EV 5/2 Monoestable 2V1 (2Y1)</text>
        <text x="400" y="208" fill="#0f172a" font-size="7.6">• Estranguladores 1V2/1V3</text>
        <text x="400" y="222" fill="#0f172a" font-size="7.6">• Estranguladores 2V2/2V3</text>

        <line x1="544" y1="176" x2="576" y2="176" stroke="#0f172a" stroke-width="2"/>
        <polygon points="576,176 568,172 568,180" fill="#0f172a"/>

        <!-- BLOQUE 4: SALIDAS / ACTUADORES Y PROCESO FÍSICO -->
        <rect x="576" y="115" width="162" height="122" rx="6" fill="#ffe4e6" stroke="#be123c" stroke-width="1.8"/>
        <text x="657" y="133" fill="#be123c" font-size="8.5" font-weight="800" text-anchor="middle">4. SALIDAS: ACTUADORES</text>
        <text x="657" y="145" fill="#be123c" font-size="7.5" font-weight="700" text-anchor="middle">Y PLANTA MECATRÓNICA</text>
        <line x1="584" y1="151" x2="730" y2="151" stroke="#fda4af" stroke-width="1.2"/>
        <text x="584" y="166" fill="#0f172a" font-size="7.6">• Motor Cinta M1 (Transporte)</text>
        <text x="584" y="180" fill="#0f172a" font-size="7.6">• Cilindro 1A1 (Desvío Metal)</text>
        <text x="584" y="194" fill="#0f172a" font-size="7.6">• Cilindro 2A1 (Desvío Plást.)</text>
        <text x="584" y="208" fill="#0f172a" font-size="7.6">• Baliza Luminosa H1, H2, H3</text>
        <text x="584" y="222" fill="#0f172a" font-size="7.6">• Piezas Clasificadas en Tolvas</text>

        <!-- LAZO DE REALIMENTACIÓN (FEEDBACK) -->
        <path d="M657,237 L657,305 L92,305 L92,237" fill="none" stroke="#6b21a8" stroke-width="2.2"/>
        <polygon points="92,237 87,246 97,246" fill="#6b21a8"/>
        <rect x="175" y="282" width="410" height="44" rx="5" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.6"/>
        <text x="380" y="299" fill="#6b21a8" font-size="8.5" font-weight="800" text-anchor="middle">5. LAZO DE REALIMENTACIÓN (SENSORES DE FIN DE CARRERA Y POSICIÓN)</text>
        <text x="380" y="314" fill="#1e293b" font-size="7.7" text-anchor="middle">Detectores Magnéticos Reed: 1B1 (a0), 1B2 (a1) en Cilindro 1A1 · 2B1 (b0), 2B2 (b1) en Cilindro 2A1</text>
      </svg>
      <div class="svg-caption">Figura 3.1: Diagrama en bloques funcional completo mostrando los 5 subsistemas y los flujos de energía, señal y realimentación.</div>
    </div>

    <h3 class="sub-title">3.1. Análisis Funcional de los Subsistemas del Diagrama en Bloques</h3>
    <div class="grid-2">
      <div class="info-card">
        <h4>1. Adquisición de Señales y Referencias</h4>
        Convierte las magnitudes físicas del entorno (presencia óptica de pieza, permeabilidad magnética del metal en <b>B2</b>, constante dieléctrica del polímero en <b>B3</b> y campo magnético del imán permanente de los émbolos en <b>1B1/1B2</b> y <b>2B1/2B2</b>) en señales eléctricas discretas de <b>0 V / 24 V DC</b> compatibles con la lógica de control.
      </div>
      <div class="info-card">
        <h4>2. Procesamiento Lógico y Enclavamientos</h4>
        Evalúa en tiempo real las ecuaciones booleanas de estado. Su función crítica es evitar colisiones mecánicas: cuando <b>B2</b> o <b>B3</b> detectan una pieza a clasificar, el controlador abre inmediatamente el circuito del contactor <b>KM1</b> (deteniendo la cinta en la posición exacta frente al vástago) antes de comandar el avance del cilindro correspondiente.
      </div>
      <div class="info-card">
        <h4>3. Pre-Actuación y Modulación de Energía</h4>
        Las señales de mando de baja potencia (24V DC, ~100 mA) no pueden mover directamente las cargas mecánicas. El contactor <b>KM1</b> conmuta la potencia eléctrica del motor <b>M1</b>, mientras que las electroválvulas direccionales 5/2 (<b>1V1</b> y <b>2V1</b>) canalizan el aire comprimido a <b>6,0 bar</b> hacia las cámaras de los cilindros, reguladas por las válvulas estranguladoras antirretorno.
      </div>
      <div class="info-card">
        <h4>4 y 5. Actuación Mecánica y Cierre de Lazo</h4>
        Los cilindros neumáticos de doble efecto transforman la energía neumática en trabajo lineal (<i>F = P · A</i>), desplazando las piezas 100 mm hacia las rampas colectoras. Los sensores magnéticos de fin de carrera informan al controlador que el objetivo físico se cumplió, cerrando el lazo de control.
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PÁGINA 4: LÓGICA BÁSICA DE FUNCIONAMIENTO, ECUACIONES Y GRAFCET       -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Facultad Regional Paraná · Mecatrónica II — Modelado y Simulación de Sistemas Mecatrónicos</span>
      <span>Alumno: Hugo Ariel Martinez · Pág. 4 de 6</span>
    </div>

    <h2 class="sec-title">4. Desarrollo de la Lógica de Funcionamiento y GRAFCET (Consigna Punto 4)</h2>
    <p>
      El comportamiento secuencial del sistema se modela formalmente mediante ecuaciones lógicas de conmutación (implementadas con relés auxiliares <b>KF, K1, KB1, K2, K3</b> y lógica de PLC) y mediante el diagrama funcional <b>GRAFCET (Norma IEC 60848)</b> acompañado de su <b>Diagrama Espacio-Fase</b>.
    </p>

    <h3 class="sub-title" style="margin-top: 4px; margin-bottom: 3px;">4.1. Ecuaciones Booleanas del Circuito Electroneumático de Mando y Watchdogs</h3>
    <table style="font-size: 7.2pt; margin: 2px 0 4px 0;">
      <thead>
        <tr>
          <th style="width: 21%; padding: 2.5px 5px;">Variable / Salida</th>
          <th style="width: 35%; padding: 2.5px 5px;">Ecuación Lógica Normalizada</th>
          <th style="width: 44%; padding: 2.5px 5px;">Justificación Técnica, Prioridad y Seguridad Fail-Safe</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="mono" style="padding: 2px 5px;">KF (Bloqueo Falla)</td>
          <td class="mono" style="padding: 2px 5px;">KF = (/S0 + /P1 + ALM_WD + KF) · /S3</td>
          <td style="padding: 2px 5px;">Enclava alarma ante emergencia (<b>S0=0</b>), baja presión (<b>P1=0</b>) o timeout/atasco (<b>ALM_WD=1</b>). Exige pulsar <b>Rearme S3</b> para liberar el sistema (IEC 60204-1).</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">K1 (Memoria Marcha)</td>
          <td class="mono" style="padding: 2px 5px;">K1 = S0 · S2 · P1 · /KF · (S1 + K1)</td>
          <td style="padding: 2px 5px;">Retención de marcha con prioridad a la desconexión, habilitada únicamente sin falla activa (<b>/KF=1</b> tras rearme con <b>S3</b>).</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">KB1 (Validación B1)</td>
          <td class="mono" style="padding: 2px 5px;">KB1 = K1 · (B1 + KB1) · /Fin_Lote | T_B1 &lt; 3,0s</td>
          <td style="padding: 2px 5px;"><b>B1</b> registra ingreso de pieza, suma al contador de lote, habilita expulsores <b>K2/K3</b> y vigila atasco en entrada (si <b>B1=1 &gt; 3,0 s</b> dispara <b>ALM_WD</b>).</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">KM1 (Motor Cinta M1)</td>
          <td class="mono" style="padding: 2px 5px;">KM1 = K1 · 1B1 · 2B1 · /K2 · /K3</td>
          <td style="padding: 2px 5px;">La cinta tracciona solo si <b>K1=1</b>, ambos cilindros están retraídos (<b>1B1·2B1=1</b>) y no hay expulsión activa (<b>/K2·/K3</b>).</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">K2 / 1Y1 (Ciclo Metal)</td>
          <td class="mono" style="padding: 2px 5px;">1Y1 = K2 = K1 · KB1 · (B2·1B1 + K2) · /1B2</td>
          <td style="padding: 2px 5px;">Con pieza validada por <b>B1 (KB1=1)</b> y metal en <b>B2=1</b>, retiene <b>K2</b> y energiza <b>1Y1</b> (Avance A+) hasta confirmar <b>1B2 (a1)</b>. Tiene <b>prioridad</b> sobre B3.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">K3 / 2Y1 (Ciclo Plást.)</td>
          <td class="mono" style="padding: 2px 5px;">2Y1 = K3 = K1 · KB1 · (B3·/B2·/K2·2B1 + K3) · /2B2</td>
          <td style="padding: 2px 5px;">Con pieza validada (<b>KB1=1</b>) y plástico en <b>B3=1</b>, activa <b>2Y1</b> (B+) hasta <b>2B2 (b1)</b>. Incluye bloqueo <b>/B2·/K2</b> que prioriza la rama metálica ante conflicto.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">ALM_WD (Watchdogs)</td>
          <td class="mono" style="padding: 2px 5px;">WD = (Y·/B2 &gt; 1,5s) + (/Y·/B1 &gt; 2,0s) + (B2·B3 &gt; 1s)</td>
          <td style="padding: 2px 5px;">Supervisa timeouts de avance (<b>&gt;1,5 s</b> sin 1B2/2B2), retroceso (<b>&gt;2,0 s</b> sin 1B1/2B1), conflicto simultáneo <b>B2·B3 (&gt;1,0 s)</b> y atasco en <b>B1 (&gt;3,0 s)</b>.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">H1, H2, H3 (Baliza)</td>
          <td class="mono" style="padding: 2px 5px;">H1 = K1 | H2 = K2+K3 | H3 = KF</td>
          <td style="padding: 2px 5px;">Señalización óptica continua de marcha (<b>H1</b>), maniobra de clasificación (<b>H2</b>) y bloqueo por alarma/falla hasta pulsar <b>S3</b> (<b>H3</b>).</td>
        </tr>
      </tbody>
    </table>

    <h3 class="sub-title" style="margin-top: 4px; margin-bottom: 3px;">4.2. Modelado Secuencial GRAFCET (IEC 60848) y Diagrama Espacio-Fase</h3>
    <div class="svg-box" style="padding: 5px; margin: 3px 0;">
      <svg viewBox="0 0 760 254" width="100%" height="auto">
        <!-- MITAD IZQUIERDA: GRAFCET -->
        <rect x="6" y="4" width="370" height="246" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
        <text x="191" y="20" fill="#004b87" font-size="8.6" font-weight="800" text-anchor="middle">DIAGRAMA FUNCIONAL GRAFCET (IEC 60848)</text>

        <!-- Etapa 0 (Inicial) -->
        <rect x="166" y="28" width="46" height="24" fill="#ffffff" stroke="#004b87" stroke-width="2"/>
        <rect x="170" y="32" width="38" height="16" fill="#e0f2fe" stroke="#004b87" stroke-width="1"/>
        <text x="189" y="44" fill="#004b87" font-size="9" font-weight="800" text-anchor="middle">0</text>
        <line x1="189" y1="52" x2="189" y2="70" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="179" y1="61" x2="199" y2="61" stroke="#0f172a" stroke-width="2"/>
        <text x="204" y="64" fill="#166534" font-size="7.2" font-weight="700">S1 · S0 · P1 · /KF(S3) · 1B1 · 2B1</text>

        <!-- Etapa 1: Cinta en Marcha + Validación B1 -->
        <rect x="166" y="70" width="46" height="24" fill="#dcfce7" stroke="#166534" stroke-width="1.8"/>
        <text x="189" y="86" fill="#166534" font-size="9" font-weight="800" text-anchor="middle">1</text>
        <line x1="212" y1="82" x2="224" y2="82" stroke="#166534" stroke-width="1.5"/>
        <rect x="224" y="71" width="144" height="22" fill="#ffffff" stroke="#166534" stroke-width="1.2"/>
        <text x="296" y="85" fill="#0f172a" font-size="7.3" font-weight="700" text-anchor="middle">KM1 (Cinta) + H1 + KB1 (si B1=1)</text>

        <!-- Divergencia en O hacia Rama Metal (Izq) y Rama Plástico (Der) -->
        <line x1="189" y1="94" x2="189" y2="106" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="95" y1="106" x2="285" y2="106" stroke="#0f172a" stroke-width="1.6"/>

        <!-- Rama Izquierda: Metal (Etapa 2 y 3) -->
        <line x1="95" y1="106" x2="95" y2="128" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="85" y1="117" x2="105" y2="117" stroke="#0f172a" stroke-width="2"/>
        <text x="109" y="120" fill="#0369a1" font-size="7.2" font-weight="700">KB1(B1) · B2 · 1B1</text>

        <rect x="75" y="128" width="40" height="22" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.6"/>
        <text x="95" y="143" fill="#0369a1" font-size="8.5" font-weight="800" text-anchor="middle">2</text>
        <rect x="120" y="128" width="62" height="22" fill="#fff" stroke="#0284c7" stroke-width="1.2"/>
        <text x="151" y="142" fill="#0f172a" font-size="7.4" font-weight="700" text-anchor="middle">1Y1 (1A1+)</text>

        <line x1="95" y1="150" x2="95" y2="172" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="85" y1="161" x2="105" y2="161" stroke="#0f172a" stroke-width="2"/>
        <text x="109" y="164" fill="#6b21a8" font-size="7.3" font-weight="700">1B2 (T&lt;1,5s)</text>

        <rect x="75" y="172" width="40" height="22" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.6"/>
        <text x="95" y="187" fill="#6b21a8" font-size="8.5" font-weight="800" text-anchor="middle">3</text>
        <rect x="120" y="172" width="62" height="22" fill="#fff" stroke="#6b21a8" stroke-width="1.2"/>
        <text x="151" y="186" fill="#0f172a" font-size="7.4" font-weight="700" text-anchor="middle">1A1- (Muelle)</text>

        <line x1="95" y1="194" x2="95" y2="218" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="85" y1="206" x2="105" y2="206" stroke="#0f172a" stroke-width="2"/>
        <text x="109" y="209" fill="#6b21a8" font-size="7.3" font-weight="700">1B1 (T&lt;2,0s)</text>

        <!-- Rama Derecha: Plástico (Etapa 4 y 5) -->
        <line x1="285" y1="106" x2="285" y2="128" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="275" y1="117" x2="295" y2="117" stroke="#0f172a" stroke-width="2"/>
        <text x="268" y="120" fill="#b45309" font-size="7.1" font-weight="700" text-anchor="end">KB1 · B3 · /B2 · 2B1</text>

        <rect x="265" y="128" width="40" height="22" fill="#fef3c7" stroke="#d97706" stroke-width="1.6"/>
        <text x="285" y="143" fill="#b45309" font-size="8.5" font-weight="800" text-anchor="middle">4</text>
        <rect x="310" y="128" width="58" height="22" fill="#fff" stroke="#d97706" stroke-width="1.2"/>
        <text x="339" y="142" fill="#0f172a" font-size="7.4" font-weight="700" text-anchor="middle">2Y1 (2A1+)</text>

        <line x1="285" y1="150" x2="285" y2="172" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="275" y1="161" x2="295" y2="161" stroke="#0f172a" stroke-width="2"/>
        <text x="268" y="164" fill="#6b21a8" font-size="7.3" font-weight="700" text-anchor="end">2B2 (T&lt;1,5s)</text>

        <rect x="265" y="172" width="40" height="22" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.6"/>
        <text x="285" y="187" fill="#6b21a8" font-size="8.5" font-weight="800" text-anchor="middle">5</text>
        <rect x="310" y="172" width="58" height="22" fill="#fff" stroke="#6b21a8" stroke-width="1.2"/>
        <text x="339" y="186" fill="#0f172a" font-size="7.4" font-weight="700" text-anchor="middle">2A1- (Muelle)</text>

        <line x1="285" y1="194" x2="285" y2="218" stroke="#0f172a" stroke-width="1.6"/>
        <line x1="275" y1="206" x2="295" y2="206" stroke="#0f172a" stroke-width="2"/>
        <text x="268" y="209" fill="#6b21a8" font-size="7.3" font-weight="700" text-anchor="end">2B1 (T&lt;2,0s)</text>

        <!-- Convergencia y retorno a Etapa 1 -->
        <line x1="95" y1="218" x2="285" y2="218" stroke="#0f172a" stroke-width="1.6"/>
        <path d="M189,218 L189,236 L38,236 L38,82 L166,82" fill="none" stroke="#004b87" stroke-width="1.5" stroke-dasharray="4 2"/>
        <polygon points="166,82 158,78 158,86" fill="#004b87"/>

        <!-- MITAD DERECHA: DIAGRAMA ESPACIO-FASE -->
        <rect x="384" y="4" width="370" height="246" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
        <text x="569" y="20" fill="#004b87" font-size="8.6" font-weight="800" text-anchor="middle">DIAGRAMA ESPACIO-FASE (SECUENCIA OPERATIVA)</text>

        <!-- Grilla de Fases F1..F6 -->
        <g transform="translate(445, 38)">
          <!-- Líneas verticales de fase -->
          <line x1="0" y1="0" x2="0" y2="188" stroke="#94a3b8" stroke-width="1"/>
          <line x1="48" y1="0" x2="48" y2="188" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 2"/>
          <line x1="96" y1="0" x2="96" y2="188" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 2"/>
          <line x1="144" y1="0" x2="144" y2="188" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 2"/>
          <line x1="192" y1="0" x2="192" y2="188" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 2"/>
          <line x1="240" y1="0" x2="240" y2="188" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 2"/>
          <line x1="288" y1="0" x2="288" y2="188" stroke="#94a3b8" stroke-width="1"/>

          <text x="24" y="-5" fill="#475569" font-size="7.4" font-weight="700" text-anchor="middle">Transp.</text>
          <text x="72" y="-5" fill="#0284c7" font-size="7.4" font-weight="700" text-anchor="middle">1A1+ (A+)</text>
          <text x="120" y="-5" fill="#0284c7" font-size="7.4" font-weight="700" text-anchor="middle">1A1- (A-)</text>
          <text x="168" y="-5" fill="#475569" font-size="7.4" font-weight="700" text-anchor="middle">Transp.</text>
          <text x="216" y="-5" fill="#d97706" font-size="7.4" font-weight="700" text-anchor="middle">2A1+ (B+)</text>
          <text x="264" y="-5" fill="#d97706" font-size="7.4" font-weight="700" text-anchor="middle">2A1- (B-)</text>

          <!-- Track 1: Motor Cinta KM1 (1/0) -->
          <text x="-8" y="23" fill="#166534" font-size="8" font-weight="800" text-anchor="end">KM1 (M1)</text>
          <line x1="0" y1="34" x2="288" y2="34" stroke="#cbd5e1" stroke-width="1"/>
          <polyline points="0,10 48,10 48,34 144,34 144,10 192,10 192,34 288,34" fill="none" stroke="#166534" stroke-width="2.5"/>

          <!-- Track 2: Cilindro 1A1 (0..100 mm) -->
          <text x="-8" y="84" fill="#0284c7" font-size="8" font-weight="800" text-anchor="end">1A1 (mm)</text>
          <line x1="0" y1="100" x2="288" y2="100" stroke="#cbd5e1" stroke-width="1"/>
          <line x1="0" y1="60" x2="288" y2="60" stroke="#cbd5e1" stroke-width="1"/>
          <polyline points="0,100 48,100 96,60 144,100 288,100" fill="none" stroke="#0284c7" stroke-width="2.5"/>
          <circle cx="96" cy="60" r="3.5" fill="#6b21a8"/>
          <text x="96" y="55" fill="#6b21a8" font-size="7" font-weight="700" text-anchor="middle">1B2(a1)</text>
          <circle cx="144" cy="100" r="3.5" fill="#166534"/>
          <text x="144" y="112" fill="#166534" font-size="7" font-weight="700" text-anchor="middle">1B1(a0)</text>

          <!-- Track 3: Cilindro 2A1 (0..100 mm) -->
          <text x="-8" y="152" fill="#d97706" font-size="8" font-weight="800" text-anchor="end">2A1 (mm)</text>
          <line x1="0" y1="170" x2="288" y2="170" stroke="#cbd5e1" stroke-width="1"/>
          <line x1="0" y1="132" x2="288" y2="132" stroke="#cbd5e1" stroke-width="1"/>
          <polyline points="0,170 192,170 240,132 288,170" fill="none" stroke="#d97706" stroke-width="2.5"/>
          <circle cx="240" cy="132" r="3.5" fill="#6b21a8"/>
          <text x="240" y="127" fill="#6b21a8" font-size="7" font-weight="700" text-anchor="middle">2B2(b1)</text>
          <circle cx="288" cy="170" r="3.5" fill="#166534"/>
          <text x="278" y="182" fill="#166534" font-size="7" font-weight="700" text-anchor="middle">2B1(b0)</text>
        </g>
      </svg>
      <div class="svg-caption">Figura 4.1: Izquierda: GRAFCET con divergencia selectiva en "O" y prioridad metálica (/B2). Derecha: Diagrama Espacio-Fase sincronizado.</div>
    </div>

    <h3 class="sub-title" style="margin-top: 4px; margin-bottom: 3px;">4.3. Explicación Paso a Paso de la Secuencia Funcional y Protecciones</h3>
    <ol style="margin: 0; padding-left: 16px; font-size: 7.65pt; line-height: 1.28;">
      <li><b>Rearme Manual (S3) y Permiso de Arranque (Etapa 0):</b> Ante cualquier emergencia (<b>S0=0</b>), baja presión (<b>P1=0</b>) o fallo por timeout/atasco (<b>ALM_WD=1</b>), se enclava el relé de falla <b>KF</b>. Normalizada la planta, el operador debe pulsar <b>Rearme S3</b> para desenclavar <b>KF (/KF=1)</b> y habilitar el arranque con ambos cilindros retraídos en <b>1B1 (a0)</b> y <b>2B1 (b0)</b>.</li>
      <li><b>Transporte en Cinta y Validación/Supervisión por B1 (Etapa 1):</b> Al pulsar <b>S1</b>, se enclava <b>K1</b>, enciende <b>H1</b> y tracciona <b>KM1 (M1)</b>. Al cruzar una pieza por <b>B1</b>, se incrementa el contador de lote y se enclava la memoria de tránsito <b>KB1</b> (que habilita <b>K2/K3</b>). Si <b>B1=1</b> persiste más de <b>3,0 s</b> consecutivos, se dispara alarma por <b>Atasco en Entrada B1</b>.</li>
      <li><b>Rama A — Clasificación de Pieza Metálica (Etapas 2 y 3):</b> Con pieza validada (<b>KB1=1</b>), al activarse el inductivo <b>B2</b> entra <b>K2</b>, pausa la cinta (<b>/K2</b> abre <b>KM1</b>) y energiza <b>1Y1</b>. El cilindro <b>1A1</b> avanza (<b>A+</b>) hasta cerrar <b>1B2 (a1=100 mm)</b>, que corta <b>K2/1Y1</b>. El muelle retorna la válvula 5/2 y el cilindro retrocede (<b>A-</b>) hasta <b>1B1 (a0)</b>, reanudando la cinta.</li>
      <li><b>Rama B — Clasificación Plástica y Manejo de Conflicto B2/B3 (Etapas 4 y 5):</b> Si la pieza es polimérica, activa el capacitivo <b>B3</b> y ejecuta el ciclo <b>B+ / B-</b> con <b>2A1</b>. Ante detección simultánea <b>B2=1 y B3=1</b>, el contacto <b>/B2·/K2</b> prioriza la clasificación metálica y bloquea la rama plástica hasta completar el ciclo de <b>1A1</b>; si la simultaneidad persiste <b>&gt; 1,0 s</b>, genera alarma <b>"Conflicto de detección B2/B3"</b>.</li>
      <li><b>Watchdogs de Tiempo de Carrera en Cilindros 1A1 y 2A1:</b> Si se energiza <b>1Y1 (o 2Y1)</b> y el sensor <b>1B2 (o 2B2)</b> no confirma en <b>1,5 s</b>, se genera alarma <b>"Fallo avance 1A1/2A1"</b>. Si se desenergiza <b>1Y1 (o 2Y1)</b> y <b>1B1 (o 2B1)</b> no confirma retorno en <b>2,0 s</b>, se genera alarma <b>"Fallo retroceso 1A1/2A1"</b>, deteniendo la planta en modo seguro.</li>
    </ol>
  </div>

  <!-- ===================================================================== -->
  <!-- PÁGINA 5: PLANOS DE SIMULACIÓN ELECTRONEUMÁTICA (NEUMÁTICO + ELÉCTRICO) -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Facultad Regional Paraná · Mecatrónica II — Modelado y Simulación de Sistemas Mecatrónicos</span>
      <span>Alumno: Hugo Ariel Martinez · Pág. 5 de 6</span>
    </div>

    <h2 class="sec-title">5. Implementación de la Simulación Electroneumática (Consigna Punto 5)</h2>
    <p>
      Se presenta a continuación el plano integral del sistema diseñado y ejecutado en tiempo real dentro de nuestro software propio de simulación (<span class="mono">Simulador_SCADA/</span>). En la parte superior se ubica el <b>Circuito Neumático de Potencia (Norma ISO 1219-1)</b> con sus cilindros de doble efecto y electroválvulas 5/2, y en la parte inferior el <b>Circuito Eléctrico de Mando en 24V DC (Norma IEC 60617)</b>.
    </p>

    <div class="svg-box" style="padding: 8px;">
      <svg viewBox="0 0 760 520" width="100%" height="auto">
        <!-- SECCIÓN SUPERIOR: ESQUEMA NEUMÁTICO ISO 1219 -->
        <rect x="6" y="6" width="748" height="232" rx="5" fill="#ffffff" stroke="#004b87" stroke-width="1.5"/>
        <text x="16" y="22" fill="#004b87" font-size="9" font-weight="800">5.1. ESQUEMA NEUMÁTICO DE POTENCIA (NORMA ISO 1219-1)</text>

        <!-- CILINDRO 1A1 -->
        <g transform="translate(105, 38)">
          <!-- Regla de posición 1B1 / 1B2 -->
          <line x1="35" y1="6" x2="155" y2="6" stroke="#475569" stroke-width="1.5"/>
          <line x1="40" y1="0" x2="40" y2="12" stroke="#166534" stroke-width="2"/>
          <text x="40" y="-3" fill="#166534" font-size="8" font-weight="800" text-anchor="middle">1B1 (a0)</text>
          <line x1="145" y1="0" x2="145" y2="12" stroke="#0284c7" stroke-width="2"/>
          <text x="145" y="-3" fill="#0284c7" font-size="8" font-weight="800" text-anchor="middle">1B2 (a1)</text>

          <text x="-8" y="36" fill="#0f172a" font-size="9.5" font-weight="800">1A1</text>
          <rect x="20" y="16" width="110" height="34" fill="#f8fafc" stroke="#0f172a" stroke-width="1.8"/>
          <rect x="35" y="17" width="7" height="32" fill="#334155"/>
          <rect x="42" y="30" width="105" height="6" fill="#64748b" stroke="#0f172a" stroke-width="1"/>
        </g>

        <!-- CILINDRO 2A1 -->
        <g transform="translate(465, 38)">
          <line x1="35" y1="6" x2="155" y2="6" stroke="#475569" stroke-width="1.5"/>
          <line x1="40" y1="0" x2="40" y2="12" stroke="#166534" stroke-width="2"/>
          <text x="40" y="-3" fill="#166534" font-size="8" font-weight="800" text-anchor="middle">2B1 (b0)</text>
          <line x1="145" y1="0" x2="145" y2="12" stroke="#d97706" stroke-width="2"/>
          <text x="145" y="-3" fill="#d97706" font-size="8" font-weight="800" text-anchor="middle">2B2 (b1)</text>

          <text x="-8" y="36" fill="#0f172a" font-size="9.5" font-weight="800">2A1</text>
          <rect x="20" y="16" width="110" height="34" fill="#f8fafc" stroke="#0f172a" stroke-width="1.8"/>
          <rect x="35" y="17" width="7" height="32" fill="#334155"/>
          <rect x="42" y="30" width="105" height="6" fill="#64748b" stroke="#0f172a" stroke-width="1"/>
        </g>

        <!-- Líneas neumáticas y reguladores de caudal 1V2, 1V3, 2V2, 2V3 -->
        <line x1="132" y1="88" x2="132" y2="142" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 2"/>
        <line x1="225" y1="88" x2="225" y2="142" stroke="#0055cc" stroke-width="2.5"/>
        <rect x="123" y="102" width="18" height="22" fill="#fff" stroke="#0f172a" stroke-width="1.3"/>
        <text x="118" y="116" fill="#0f172a" font-size="7.5" font-weight="700" text-anchor="end">1V2 (80%)</text>
        <rect x="216" y="102" width="18" height="22" fill="#fff" stroke="#0f172a" stroke-width="1.3"/>
        <text x="239" y="116" fill="#0f172a" font-size="7.5" font-weight="700" text-anchor="start">1V3 (80%)</text>

        <line x1="492" y1="88" x2="492" y2="142" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 2"/>
        <line x1="585" y1="88" x2="585" y2="142" stroke="#0055cc" stroke-width="2.5"/>
        <rect x="483" y="102" width="18" height="22" fill="#fff" stroke="#0f172a" stroke-width="1.3"/>
        <text x="478" y="116" fill="#0f172a" font-size="7.5" font-weight="700" text-anchor="end">2V2 (80%)</text>
        <rect x="576" y="102" width="18" height="22" fill="#fff" stroke="#0f172a" stroke-width="1.3"/>
        <text x="599" y="116" fill="#0f172a" font-size="7.5" font-weight="700" text-anchor="start">2V3 (80%)</text>

        <!-- Válvula 5/2 1V1 -->
        <g transform="translate(112, 142)">
          <rect x="-36" y="6" width="36" height="24" fill="#fef3c7" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="-26" y1="6" x2="-8" y2="30" stroke="#0f172a" stroke-width="1.2"/>
          <text x="-18" y="21" fill="#0f172a" font-size="8" font-weight="800" text-anchor="middle">1Y1</text>

          <rect x="0" y="0" width="64" height="36" fill="#fff" stroke="#0f172a" stroke-width="1.6"/>
          <rect x="64" y="0" width="64" height="36" fill="#eff6ff" stroke="#0055cc" stroke-width="1.8"/>
          <line x1="32" y1="36" x2="18" y2="2" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="48" y1="0" x2="48" y2="34" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="96" y1="36" x2="112" y2="2" stroke="#0055cc" stroke-width="1.6"/>
          <line x1="80" y1="0" x2="80" y2="34" stroke="#0f172a" stroke-width="1.4"/>
          <polyline points="128,12 134,6 140,24 146,6 152,24 158,15" fill="none" stroke="#0f172a" stroke-width="1.4"/>
          <text x="-18" y="-2" fill="#004b87" font-size="8" font-weight="800" text-anchor="middle">1V1 (5/2)</text>
        </g>

        <!-- Válvula 5/2 2V1 -->
        <g transform="translate(472, 142)">
          <rect x="-36" y="6" width="36" height="24" fill="#fef3c7" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="-26" y1="6" x2="-8" y2="30" stroke="#0f172a" stroke-width="1.2"/>
          <text x="-18" y="21" fill="#0f172a" font-size="8" font-weight="800" text-anchor="middle">2Y1</text>

          <rect x="0" y="0" width="64" height="36" fill="#fff" stroke="#0f172a" stroke-width="1.6"/>
          <rect x="64" y="0" width="64" height="36" fill="#eff6ff" stroke="#0055cc" stroke-width="1.8"/>
          <line x1="32" y1="36" x2="18" y2="2" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="48" y1="0" x2="48" y2="34" stroke="#0f172a" stroke-width="1.4"/>
          <line x1="96" y1="36" x2="112" y2="2" stroke="#0055cc" stroke-width="1.6"/>
          <line x1="80" y1="0" x2="80" y2="34" stroke="#0f172a" stroke-width="1.4"/>
          <polyline points="128,12 134,6 140,24 146,6 152,24 158,15" fill="none" stroke="#0f172a" stroke-width="1.4"/>
          <text x="-18" y="-2" fill="#004b87" font-size="8" font-weight="800" text-anchor="middle">2V1 (5/2)</text>
        </g>

        <!-- Colector Presión 6 bar y Unidad FRL -->
        <path d="M176,178 L176,212 L536,212 L536,178" fill="none" stroke="#0055cc" stroke-width="2.5"/>
        <rect x="295" y="196" width="125" height="30" rx="3" fill="#e0f2fe" stroke="#0055cc" stroke-width="1.6"/>
        <polygon points="282,211 294,204 294,218" fill="#0055cc"/>
        <text x="357" y="209" fill="#004b87" font-size="8" font-weight="800" text-anchor="middle">UNIDAD FRL 0Z1 (6,0 bar)</text>
        <text x="357" y="221" fill="#166534" font-size="7.5" font-weight="700" text-anchor="middle">+ Presostato P1 (≥ 5,0 bar)</text>

        <!-- SECCIÓN INFERIOR: CIRCUITO ELÉCTRICO DE MANDO (IEC 60617) -->
        <rect x="6" y="246" width="748" height="268" rx="5" fill="#ffffff" stroke="#004b87" stroke-width="1.5"/>
        <text x="16" y="263" fill="#004b87" font-size="9" font-weight="800">5.2. CIRCUITO ELÉCTRICO DE CONTROL SECUENCIAL (24V DC — NORMA IEC 60617)</text>

        <!-- Riel +24V y 0V -->
        <line x1="36" y1="282" x2="730" y2="282" stroke="#dc2626" stroke-width="2.5"/>
        <text x="16" y="285" fill="#dc2626" font-size="8.5" font-weight="800">+24V</text>

        <line x1="36" y1="488" x2="730" y2="488" stroke="#2563eb" stroke-width="2.5"/>
        <text x="18" y="491" fill="#2563eb" font-size="8.5" font-weight="800">0V</text>

        <!-- Numeración de Columnas 1 a 7 -->
        <text x="78" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 1: Marcha K1</text>
        <text x="185" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 2: Cinta + B1</text>
        <text x="305" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 3: Metal 1Y1</text>
        <text x="425" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 4: Plást. 2Y1</text>
        <text x="540" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 5: H1</text>
        <text x="625" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 6: H2</text>
        <text x="705" y="505" fill="#475569" font-size="7.5" font-weight="700" text-anchor="middle">Rama 7: Falla KF/S3</text>

        <!-- Rama 1 (x=78) -->
        <g transform="translate(78, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-24" y="10" width="48" height="19" rx="2" fill="#ffe4e6" stroke="#be123c" stroke-width="1.3"/>
          <text x="0" y="23" fill="#9f1239" font-size="7.6" font-weight="700" text-anchor="middle">S0 (NC)</text>
          <rect x="-24" y="38" width="48" height="19" rx="2" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>
          <text x="0" y="51" fill="#0f172a" font-size="7.6" font-weight="700" text-anchor="middle">S2 (NC)</text>
          <rect x="-28" y="66" width="56" height="20" rx="2" fill="#dcfce7" stroke="#166534" stroke-width="1.3"/>
          <text x="0" y="79" fill="#166534" font-size="7.6" font-weight="700" text-anchor="middle">S1 + K1</text>
          <rect x="-24" y="96" width="48" height="19" rx="2" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.3"/>
          <text x="0" y="109" fill="#0369a1" font-size="7.6" font-weight="700" text-anchor="middle">P1 (≥5b)</text>
          <rect x="-26" y="125" width="52" height="19" rx="2" fill="#ffe4e6" stroke="#be123c" stroke-width="1.3"/>
          <text x="0" y="138" fill="#9f1239" font-size="7.5" font-weight="700" text-anchor="middle">/KF (S3)</text>
          <rect x="-20" y="164" width="40" height="26" fill="#fef3c7" stroke="#b45309" stroke-width="1.5"/>
          <text x="0" y="180" fill="#0f172a" font-size="8.5" font-weight="800" text-anchor="middle">K1</text>
        </g>

        <!-- Rama 2 (x=185) -->
        <g transform="translate(185, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-24" y="14" width="48" height="19" rx="2" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>
          <text x="0" y="27" fill="#0f172a" font-size="7.6" font-weight="700" text-anchor="middle">K1 (NA)</text>
          <rect x="-30" y="44" width="60" height="19" rx="2" fill="#dcfce7" stroke="#166534" stroke-width="1.3"/>
          <text x="0" y="57" fill="#166534" font-size="7.4" font-weight="700" text-anchor="middle">B1 ➔ KB1</text>
          <rect x="-28" y="74" width="56" height="19" rx="2" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.3"/>
          <text x="0" y="87" fill="#6b21a8" font-size="7.6" font-weight="700" text-anchor="middle">1B1 · 2B1</text>
          <rect x="-28" y="104" width="56" height="19" rx="2" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>
          <text x="0" y="117" fill="#0f172a" font-size="7.6" font-weight="700" text-anchor="middle">/K2 · /K3</text>
          <rect x="-22" y="164" width="44" height="26" fill="#dcfce7" stroke="#166534" stroke-width="1.5"/>
          <text x="0" y="180" fill="#166534" font-size="8.5" font-weight="800" text-anchor="middle">KM1</text>
        </g>

        <!-- Rama 3 (x=305) -->
        <g transform="translate(305, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-30" y="18" width="60" height="20" rx="2" fill="#dcfce7" stroke="#166534" stroke-width="1.3"/>
          <text x="0" y="31" fill="#166534" font-size="7.5" font-weight="700" text-anchor="middle">K1 · KB1(B1)</text>
          <rect x="-32" y="56" width="64" height="20" rx="2" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.3"/>
          <text x="0" y="69" fill="#0369a1" font-size="7.5" font-weight="700" text-anchor="middle">B2·1B1 + K2</text>
          <rect x="-26" y="94" width="52" height="20" rx="2" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.3"/>
          <text x="0" y="107" fill="#6b21a8" font-size="7.8" font-weight="700" text-anchor="middle">/1B2 (NC)</text>
          <rect x="-26" y="164" width="52" height="26" fill="#fef3c7" stroke="#b45309" stroke-width="1.5"/>
          <text x="0" y="180" fill="#0f172a" font-size="8" font-weight="800" text-anchor="middle">K2 / 1Y1</text>
        </g>

        <!-- Rama 4 (x=425) -->
        <g transform="translate(425, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-32" y="18" width="64" height="20" rx="2" fill="#dcfce7" stroke="#166534" stroke-width="1.3"/>
          <text x="0" y="31" fill="#166534" font-size="7.3" font-weight="700" text-anchor="middle">K1·KB1·/B2</text>
          <rect x="-32" y="56" width="64" height="20" rx="2" fill="#fef3c7" stroke="#b45309" stroke-width="1.3"/>
          <text x="0" y="69" fill="#b45309" font-size="7.5" font-weight="700" text-anchor="middle">B3·2B1 + K3</text>
          <rect x="-26" y="94" width="52" height="20" rx="2" fill="#f3e8ff" stroke="#6b21a8" stroke-width="1.3"/>
          <text x="0" y="107" fill="#6b21a8" font-size="7.8" font-weight="700" text-anchor="middle">/2B2 (NC)</text>
          <rect x="-26" y="164" width="52" height="26" fill="#fef3c7" stroke="#b45309" stroke-width="1.5"/>
          <text x="0" y="180" fill="#0f172a" font-size="8" font-weight="800" text-anchor="middle">K3 / 2Y1</text>
        </g>

        <!-- Rama 5 (x=540) -->
        <g transform="translate(540, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-22" y="46" width="44" height="20" rx="2" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>
          <text x="0" y="59" fill="#0f172a" font-size="7.8" font-weight="700" text-anchor="middle">K1</text>
          <circle cx="0" cy="177" r="13" fill="#dcfce7" stroke="#166534" stroke-width="1.5"/>
          <text x="0" y="180" fill="#166534" font-size="8" font-weight="800" text-anchor="middle">H1</text>
        </g>

        <!-- Rama 6 (x=625) -->
        <g transform="translate(625, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-26" y="46" width="52" height="20" rx="2" fill="#f8fafc" stroke="#334155" stroke-width="1.3"/>
          <text x="0" y="59" fill="#0f172a" font-size="7.8" font-weight="700" text-anchor="middle">K2 + K3</text>
          <circle cx="0" cy="177" r="13" fill="#fef3c7" stroke="#b45309" stroke-width="1.5"/>
          <text x="0" y="180" fill="#b45309" font-size="8" font-weight="800" text-anchor="middle">H2</text>
        </g>

        <!-- Rama 7 (x=705) -->
        <g transform="translate(705, 282)">
          <line x1="0" y1="0" x2="0" y2="206" stroke="#334155" stroke-width="1.6"/>
          <rect x="-32" y="32" width="64" height="20" rx="2" fill="#ffe4e6" stroke="#be123c" stroke-width="1.3"/>
          <text x="0" y="45" fill="#9f1239" font-size="6.9" font-weight="700" text-anchor="middle">/S0+/P1+WD+KF</text>
          <rect x="-26" y="68" width="52" height="20" rx="2" fill="#e0f2fe" stroke="#0369a1" stroke-width="1.3"/>
          <text x="0" y="81" fill="#0369a1" font-size="7.5" font-weight="700" text-anchor="middle">/S3 (Reset)</text>
          <circle cx="0" cy="177" r="14" fill="#ffe4e6" stroke="#be123c" stroke-width="1.5"/>
          <text x="0" y="180" fill="#9f1239" font-size="7.5" font-weight="800" text-anchor="middle">KF/H3</text>
        </g>
      </svg>
      <div class="svg-caption">Figura 5.1: Esquema completo de simulación electroneumática (Potencia Neumática ISO 1219 + Mando Eléctrico IEC 60617).</div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- PÁGINA 6: DEMOSTRACIÓN DE FUNCIONAMIENTO Y SUITE SCADA PROPIA         -->
  <!-- ===================================================================== -->
  <div class="page">
    <div class="running-header">
      <span>UTN Facultad Regional Paraná · Mecatrónica II — Modelado y Simulación de Sistemas Mecatrónicos</span>
      <span>Alumno: Hugo Ariel Martinez · Pág. 6 de 6</span>
    </div>

    <h2 class="sec-title">6. Simulador Interactivo Propio y Demostración Funcional (Consigna Punto 6)</h2>
    <p style="margin-bottom: 4px;">
      Para la resolución e implementación práctica del sistema se desarrolló una <b>Suite Interactiva Propia de Simulación Electroneumática y SCADA Mecatrónico (bajo norma ISA-101)</b>, ejecutable con doble clic sobre <span class="mono">INICIAR_SIMULADOR.bat</span> (o <span class="mono">Simulador_SCADA/index.html</span>). Esta plataforma integra el <b>Gemelo Digital 2D de la Planta</b>, el <b>Esquema Electroneumático ISO 1219 / IEC 60617 animado en tiempo real</b> y el <b>Diagrama Espacio-Fase en vivo</b>.
    </p>

    <h3 class="sub-title" style="margin-top: 4px; margin-bottom: 3px;">6.1. Protocolo de Ensayos y Resultados Verificados en la Simulación</h3>
    <table style="font-size: 7.15pt; margin: 2px 0 5px 0;">
      <thead>
        <tr>
          <th style="width: 7%; padding: 2.5px 5px;">Ensayo</th>
          <th style="width: 23%; padding: 2.5px 5px;">Escenario de Prueba</th>
          <th style="width: 33%; padding: 2.5px 5px;">Acción Ejecutada en el Simulador</th>
          <th style="width: 37%; padding: 2.5px 5px;">Comportamiento Observado y Verificado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-01</td>
          <td style="padding: 2px 5px;"><b>Puesta en Marcha y Permiso Inicial</b></td>
          <td style="padding: 2px 5px;">Verificar <span class="mono">S0=1</span>, <span class="mono">P1=6.0 bar</span> y presionar <span class="mono">▶ MARCHA (S1)</span>.</td>
          <td style="padding: 2px 5px;">Se enclava <span class="mono">K1=1</span>, enciende piloto verde <span class="mono">H1</span> y el contactor <span class="mono">KM1</span> arranca la cinta <span class="mono">M1</span> a 120 mm/s.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-02</td>
          <td style="padding: 2px 5px;"><b>Clasificación de Pieza Metálica</b></td>
          <td style="padding: 2px 5px;">Pulsar <span class="mono">+ Pieza Metálica</span> y observar paso por <span class="mono">B1</span> y <span class="mono">B2</span>.</td>
          <td style="padding: 2px 5px;"><span class="mono">B1</span> valida ingreso (<span class="mono">KB1=1</span>). En <span class="mono">B2</span> se pausa <span class="mono">KM1</span>, activa <span class="mono">1Y1</span>, <span class="mono">1A1</span> avanza a <span class="mono">1B2 (100 mm)</span> hacia <b>Tolva 1</b>, retorna a <span class="mono">1B1</span> y reanuda cinta.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-03</td>
          <td style="padding: 2px 5px;"><b>Clasificación de Pieza Plástica</b></td>
          <td style="padding: 2px 5px;">Pulsar <span class="mono">+ Pieza Plástica</span> y observar su trayectoria.</td>
          <td style="padding: 2px 5px;">Validada por <span class="mono">B1 (KB1=1)</span>, ignora <span class="mono">B2</span> y en <span class="mono">B3 (Capacitivo)</span> pausa cinta, activa <span class="mono">2Y1</span>, extiende <span class="mono">2A1</span> hasta <span class="mono">2B2</span> hacia <b>Tolva 2</b> y retorna a <span class="mono">2B1</span>.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-04</td>
          <td style="padding: 2px 5px;"><b>Pieza de Descarte / Tercera Vía</b></td>
          <td style="padding: 2px 5px;">Pulsar <span class="mono">+ Pieza Descarte</span> en modo continuo.</td>
          <td style="padding: 2px 5px;">Registra ingreso en <span class="mono">B1</span> y, al no activar <span class="mono">B2</span> ni <span class="mono">B3</span>, los cilindros permanecen en reposo y cae en <b>Tolva 3 (Final de Cinta)</b>.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-05</td>
          <td style="padding: 2px 5px;"><b>Seguridad y Rearme (S0, P1, S3)</b></td>
          <td style="padding: 2px 5px;">Accionar <span class="mono">🛑 EMERGENCIA (S0)</span> o bajar presión a <span class="mono">3.2 bar</span>, luego pulsar <span class="mono">↺ REARME (S3)</span>.</td>
          <td style="padding: 2px 5px;">Enclava <span class="mono">KF=1 (H3)</span>, caen <span class="mono">K1, KM1, 1Y1, 2Y1</span> y retornan vástagos por muelle. Exige presionar <span class="mono">S3</span> para liberar <span class="mono">KF</span> antes de rearrancar.</td>
        </tr>
        <tr>
          <td class="mono" style="padding: 2px 5px;">E-06</td>
          <td style="padding: 2px 5px;"><b>Watchdogs de Cilindros y Conflicto B2/B3</b></td>
          <td style="padding: 2px 5px;">Inyectar <span class="mono">Atasco 1A1/2A1</span> o <span class="mono">Conflicto B2+B3</span> en Pestaña 3.</td>
          <td style="padding: 2px 5px;">Ante falta de <span class="mono">1B2/2B2 (&gt;1,5 s)</span>, falta de <span class="mono">1B1/2B1 (&gt;2,0 s)</span> o simultaneidad <span class="mono">B2·B3 (&gt;1,0 s)</span>, dispara <span class="mono">ALM_WD ➔ KF=1</span> y detiene la planta.</td>
        </tr>
      </tbody>
    </table>

    <h3 class="sub-title" style="margin-top: 4px; margin-bottom: 3px;">6.2. Matriz de Trazabilidad de Requisitos y Verificación Funcional (V&amp;V)</h3>
    <table style="font-size: 7.1pt; margin: 2px 0 6px 0;">
      <thead>
        <tr>
          <th style="width: 28%; padding: 2.5px 5px;">Requisito Funcional / de Seguridad</th>
          <th style="width: 17%; padding: 2.5px 5px;">Elemento Asociado</th>
          <th style="width: 33%; padding: 2.5px 5px;">Ecuación / Condición Lógica</th>
          <th style="width: 11%; padding: 2.5px 5px;">Ensayo</th>
          <th style="width: 11%; padding: 2.5px 5px;">Resultado</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding: 2px 5px;">Validar ingreso, conteo y vigilar atasco</td>
          <td class="mono" style="padding: 2px 5px;">B1 ➔ KB1</td>
          <td class="mono" style="padding: 2px 5px;">KB1 = K1·(B1+KB1)·/Fin | T_B1 &lt; 3,0s</td>
          <td class="mono" style="padding: 2px 5px;">E-01 / E-06</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Detectar y expulsar pieza metálica</td>
          <td class="mono" style="padding: 2px 5px;">B2 ➔ 1Y1 ➔ 1A1</td>
          <td class="mono" style="padding: 2px 5px;">1Y1 = K2 = K1·KB1·(B2·1B1+K2)·/1B2</td>
          <td class="mono" style="padding: 2px 5px;">E-02</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Detectar y expulsar pieza plástica</td>
          <td class="mono" style="padding: 2px 5px;">B3 ➔ 2Y1 ➔ 2A1</td>
          <td class="mono" style="padding: 2px 5px;">2Y1 = K3 = K1·KB1·(B3·/B2·/K2·2B1+K3)·/2B2</td>
          <td class="mono" style="padding: 2px 5px;">E-03</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Detener cinta durante expulsión</td>
          <td class="mono" style="padding: 2px 5px;">KM1 ➔ Motor M1</td>
          <td class="mono" style="padding: 2px 5px;">KM1 = K1 · 1B1 · 2B1 · /K2 · /K3</td>
          <td class="mono" style="padding: 2px 5px;">E-02 / E-03</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Prioridad metal y alarma conflicto B2/B3</td>
          <td class="mono" style="padding: 2px 5px;">B2 + B3 ➔ K2 / WD</td>
          <td class="mono" style="padding: 2px 5px;">Bloqueo /B2·/K2 en K3 | B2·B3 &gt; 1,0s ➔ KF</td>
          <td class="mono" style="padding: 2px 5px;">E-06</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Supervisión timeouts avance / retroceso</td>
          <td class="mono" style="padding: 2px 5px;">1B1/1B2, 2B1/2B2</td>
          <td class="mono" style="padding: 2px 5px;">Avance &gt; 1,5s | Retroceso &gt; 2,0s ➔ KF</td>
          <td class="mono" style="padding: 2px 5px;">E-06</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
        <tr>
          <td style="padding: 2px 5px;">Parada emergencia, baja presión y rearme</td>
          <td class="mono" style="padding: 2px 5px;">S0, P1, S3 ➔ KF</td>
          <td class="mono" style="padding: 2px 5px;">KF = (/S0 + /P1 + ALM_WD + KF) · /S3</td>
          <td class="mono" style="padding: 2px 5px;">E-05</td>
          <td class="mono" style="padding: 2px 5px; color: #166534; font-weight: 800;">PASS</td>
        </tr>
      </tbody>
    </table>

    <div class="callout" style="margin-top: 6px; padding: 6px 10px;">
      <div class="callout-title">Resumen de Entregables Incluidos en la Carpeta del Trabajo Práctico</div>
      <ul>
        <li><b>Informe Técnico Completo (este documento PDF):</b> Descripción del sistema, tablas de Entradas/Proceso/Salidas y Polaridades, Diagrama en Bloques, GRAFCET, planos electroneumáticos ISO 1219 / IEC 60617 y Matriz de Trazabilidad V&amp;V.</li>
        <li><b>Suite Interactiva Propia (<span class="mono">Simulador_SCADA/</span> + <span class="mono">INICIAR_SIMULADOR.bat</span>):</b> Simulador electroneumático y supervisión SCADA ISA-101 a 60 FPS con watchdogs de carrera, manejo de conflicto B2/B3 y gestión de alarmas ISA-18.2.</li>
      </ul>
    </div>

    <table style="margin-top: 10px; border: none;">
      <tr style="background: none;">
        <td style="border: none; width: 100%; text-align: center; padding-top: 12px;">
          <div style="border-top: 1.5px solid #94a3b8; width: 42%; margin: 0 auto; padding-top: 4px;">
            <b>Hugo Ariel Martinez</b><br>
            Alumno — Tecnicatura Superior en Mecatrónica<br>
            UTN Facultad Regional Paraná · Año Académico 2026
          </div>
        </td>
      </tr>
    </table>
  </div>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML generado: {OUTPUT_HTML}")

if os.path.exists(OUTPUT_PDF):
    os.remove(OUTPUT_PDF)

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
temp_profile = os.path.abspath(r"C:\Users\mhugo\.gemini\antigravity\brain\f1ba0874-5a37-4e06-985b-5b93c483e922\scratch\edge_profile")
os.makedirs(temp_profile, exist_ok=True)
cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    f"--user-data-dir={temp_profile}",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    f"file:///{OUTPUT_HTML.replace(os.sep, '/')}"
]

print("Renderizando PDF con Microsoft Edge Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(OUTPUT_PDF):
    doc = fitz.open(OUTPUT_PDF)
    print(f"PDF creado exitosamente: {OUTPUT_PDF} ({len(doc)} páginas, {os.path.getsize(OUTPUT_PDF)/1024:.1f} KB)")
else:
    print("Error:", res.stderr)
