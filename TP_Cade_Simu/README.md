# Universidad Tecnológica Nacional — Facultad Regional Paraná
## Tecnicatura Superior en Mecatrónica · Cátedra: Mecatrónica II
### Trabajo Práctico: Modelado y Simulación de un Sistema Mecatrónico en Cade simu
**Etapa 1: Puntos 1 al 4 (Especificación, Entradas/Salidas, Diagrama en Bloques y Lógica Secuencial / GRAFCET)**  
**Alumno:** Hugo Ariel Martinez · **Año Académico:** 2026

---

## 1. Selección y Descripción del Sistema Mecatrónico (Consigna Punto 1)

### 1.1. Sistema Seleccionado
Se ha seleccionado un **Sistema Automatizado de Clasificación de Piezas en Cinta Transportadora con Expulsores Electroneumáticos**.

### 1.2. Función que Cumple
El sistema cumple la función de:
1. Recibir y transportar de manera continua piezas sólidas heterogéneas depositadas en cabecera de línea mediante una banda accionada por motorreductor eléctrico ($M1$).
2. Identificar en tiempo real y sin contacto el material de cada pieza en tránsito mediante sensores industriales específicos:
   - Detección de presencia física e ingreso en cabecera ($B1$).
   - Discriminación de piezas metálicas / ferromagnéticas mediante sensor inductivo ($B2$).
   - Discriminación de piezas plásticas / poliméricas mediante sensor capacitivo ($B3$).
3. Clasificar y desviar automáticamente cada pieza hacia su respectiva estación de acopio:
   - **Tolva 1 (Metálica):** Desviada mediante el cilindro neumático de doble efecto $1A1$, comandado por la electroválvula $5/2$ monoestable $1V1$ (solenoide $1Y1$).
   - **Tolva 2 (Plástica):** Desviada mediante el cilindro neumático de doble efecto $2A1$, comandado por la electroválvula $5/2$ monoestable $2V1$ (solenoide $2Y1$).
   - **Tolva 3 (Descarte / Paso Directo):** Piezas no metálicas ni plásticas (o que no cumplan criterios) continúan por la cinta hasta el final de línea por descarga gravitacional.

### 1.3. Aplicación Industrial
Este sistema es un pilar fundamental en la automatización moderna:
- **Líneas de empaque y logística:** Separación automatizada de bultos y envases según material o código.
- **Plantas de reciclaje:** Clasificación automática de latas de aluminio / hojalata frente a botellas de PET y polímeros.
- **Control de calidad metalmecánico:** Expulsión de piezas no conformes o no maquinadas antes de ingresar a celdas robotizadas.
- **Distribución de flujo en celdas de manufactura:** Alimentación selectiva hacia máquinas herramientas CNC.

### 1.4. Justificación Mecatrónica
A diferencia de un mecanismo puramente eléctrico o puramente neumático, este sistema constituye un sistema mecatrónico integral debido a la sinergia de cuatro tecnologías:
1. **Mecánica de transporte:** Bastidor, rodillos, cinta transportadora, guías laterales y rampas colectoras.
2. **Neumática de potencia:** Vástagos actuadores, cámaras de cilindros de doble efecto, distribución por electroválvulas direccionales y acondicionamiento por unidad FRL a $6{,}0\text{ bar}$.
3. **Sensórica heterogénea:** Transductores fotoeléctricos, electromagnéticos inductivos, dieléctricos capacitivos y de contacto magnético Reed de fin de carrera.
4. **Control secuencial en lazo cerrado:** Sincronización lógica de paradas de la cinta transportadora antes de la expulsión lineal para evitar esfuerzos de cizallamiento transversal sobre los vástagos neumáticos, supervisión de alarmas y rearme manual seguro.

```
       [Red Neumática FRL (0Z1) 6 bar + Presostato P1 (>=5 bar)]
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     │                                                       │
 ┌───▼─────────────┐                                   ┌─────▼───────────┐
 │ Cilindro 1A1    │ (Metal)                           │ Cilindro 2A1    │ (Plástico)
 │ [1B1]     [1B2] │                                   │ [2B1]     [2B2] │
 └───┬─────────────┘                                   └─────┬───────────┘
     │                                                       │
═════╪═══════════════════════════════════════════════════════╪═══════════════════╗
[M1] │   (B1 Óptico)       (B2 Inductivo)      (B3 Capacit.) │                   ║ TOLVA 3
(KM1)│ ───►  [Pieza]  ───►       │       ───►       │        │   ───► [Descarte] ║ Descarte
═════╪═══════════════════════════╪═══════════════════════════╪═══════════════════╝ Final
     │                           │                           │
     ▼                           ▼                           ▼
  [TOLVA 1]                   [TOLVA 1]                   [TOLVA 2]
 (Metálicas)                 (Expulsión)                 (Expulsión)
```

---

## 2. Identificación de Entradas, Proceso y Salidas (Consigna Punto 2)

Siguiendo las pautas de diseño industrial y normativas **IEC 61131-3** e **ISO 1219-2**, se clasifican las variables del sistema:

### 2.1. Entradas (Sensores, Interruptores y Pulsadores de Mando)

| Símbolo | Categoría | Componente Físico | Tipo de Contacto | Función en el Sistema |
| :---: | :---: | :---: | :---: | :--- |
| **$S0$** | Seguridad | Pulsador de Parada de Emergencia (Seta con retención) | NC ($24\text{V}$) *Fail-Safe* | Abre instantáneamente el mando, desenergiza actuadores y enclava bloqueo por falla $KF$. |
| **$S1$** | Mando | Pulsador de Marcha de Ciclo (Color Verde) | NA ($24\text{V}$) | Da inicio a la operación continua enclavando el relé maestro de marcha $K1$. |
| **$S2$** | Mando | Pulsador de Parada Normal (Color Rojo) | NC ($24\text{V}$) | Detiene la marcha de forma ordenada al finalizar la orden de tracción. |
| **$S3$** | Seguridad | Pulsador de Rearme / Reset de Fallas (Color Azul) | NA ($24\text{V}$) | Desenclava la memoria de bloqueo $KF$ una vez normalizada la emergencia o presión. |
| **$B1$** | Sensor | Sensor Fotoeléctrico de Barrera en Ingreso | PNP NA ($24\text{V}$ DC) | Valida el ingreso físico de pieza ($KB1$), cuenta unidades y vigila atascos en entrada. |
| **$B2$** | Sensor | Sensor de Proximidad Inductivo (Estación 1) | PNP NA ($24\text{V}$ DC) | Detecta la presencia de material metálico frente al cilindro expulsor $1A1$. |
| **$B3$** | Sensor | Sensor de Proximidad Capacitivo (Estación 2) | PNP NA ($24\text{V}$ DC) | Detecta la presencia de material plástico/polimérico frente al expulsor $2A1$. |
| **$1B1$ ($a_0$)** | Fin de Carrera | Sensor Magnético Reed en Cilindro $1A1$ ($0\text{ mm}$) | NA magnético | Confirma que el cilindro $1A1$ se encuentra totalmente retraído (reposo). |
| **$1B2$ ($a_1$)** | Fin de Carrera | Sensor Magnético Reed en Cilindro $1A1$ ($100\text{ mm}$) | NA magnético | Confirma avance completo de $1A1$ y ordena el corte de $1Y1$ para el retroceso. |
| **$2B1$ ($b_0$)** | Fin de Carrera | Sensor Magnético Reed en Cilindro $2A1$ ($0\text{ mm}$) | NA magnético | Confirma que el cilindro $2A1$ se encuentra totalmente retraído (reposo). |
| **$2B2$ ($b_1$)** | Fin de Carrera | Sensor Magnético Reed en Cilindro $2A1$ ($100\text{ mm}$) | NA magnético | Confirma avance completo de $2A1$ y ordena el corte de $2Y1$ para el retroceso. |
| **$P1$** | Sensor | Presostato Electroneumático en Unidad FRL | NA neumático ($\ge 5{,}0\text{ bar}$) | Habilita el funcionamiento sólo si la presión de red es segura ($\ge 5{,}0\text{ bar}$). |

### 2.2. Proceso (Control Secuencial y Lógica de Enclavamiento)
La etapa de proceso procesa las señales de entrada mediante lógica cableada de relés auxiliares o autómata programable (PLC):
- **Supervisión de Condiciones Iniciales:** No permite el arranque si la parada de emergencia está activada ($S0=0$), si la presión neumática es insuficiente ($P1=0$), o si los cilindros no están retraídos en sus orígenes ($1B1=1$, $2B1=1$).
- **Interbloqueo Cinemático:** Desconecta el contactor de cinta $KM1$ durante la excursión de cualquiera de los dos cilindros ($/K2 \cdot /K3$), asegurando que la pieza esté quieta al ser empujada y protegiendo el vástago de flexiones mecánicas.
- **Prioridad y Arbitraje:** Ante la activación simultánea de $B2$ y $B3$, prioriza la rama metálica y bloquea la plástica.
- **Watchdogs:** Monitorea tiempos máximos de avance ($1{,}5\text{ s}$), retroceso ($2{,}0\text{ s}$) y presencia en entrada ($3{,}0\text{ s}$).

### 2.3. Salidas (Pre-actuadores, Actuadores e Indicadores)

| Símbolo | Tipo | Pre-actuador / Actuador Asociado | Acción Física sobre la Planta |
| :---: | :---: | :---: | :--- |
| **$KM1 \rightarrow M1$** | Motor Eléctrico | Contactor trifásico $KM1$ + Motorreductor $M1$ | Tracciona los rodillos de la cinta a velocidad constante de transporte ($120\text{ mm/s}$). |
| **$1Y1 \rightarrow 1A1$** | Electroneumático | Solenoide $1Y1$ (Válvula $5/2$ monoestable $1V1$) + Cilindro $1A1$ | Al energizarse $1Y1$, avanza el vástago ($A+$) expulsando la pieza de metal a Tolva 1. Al desenergizarse, el resorte retorna el vástago ($A-$). |
| **$2Y1 \rightarrow 2A1$** | Electroneumático | Solenoide $2Y1$ (Válvula $5/2$ monoestable $2V1$) + Cilindro $2A1$ | Al energizarse $2Y1$, avanza el vástago ($B+$) desviando la pieza plástica a Tolva 2. Al desenergizarse, el resorte retorna el vástago ($B-$). |
| **$H1$** | Señalización | Piloto Luminoso Verde en Baliza | Indica máquina energizada y en régimen de marcha automática ($K1 = 1$). |
| **$H2$** | Señalización | Piloto Luminoso Amarillo en Baliza | Señala ciclo de clasificación y movimiento de cilindros en curso ($K2 + K3 = 1$). |
| **$H3$** | Señalización / Alarma | Piloto Luminoso Rojo + Zumbador Acústico | Alarma de emergencia, baja presión o falla bloqueante ($KF = 1$). |

### 2.4. Tabla de Polaridades, Contactos Físicos y Convención Lógica (IEC 61131-3)

| Señal | Contacto Físico | Estado en Reposo (24V DC) | Interpretación Lógica de Control |
| :---: | :---: | :---: | :--- |
| **$S0$ / $S2$** | NC (*Fail-Safe*) | Cerrado ($24\text{V}$ presentes) | $1 =$ Sin parada / Sin emergencia ($0 =$ Pulsado o cable cortado). |
| **$S1$ / $S3$** | NA (*Mando*) | Abierto ($0\text{V}$) | $1 =$ Pulso de activación / rearme manual. |
| **$P1$** | NA (*Presostato*) | Cerrado con red a $6\text{ bar}$ | $1 =$ Presión neumática de trabajo correcta ($\ge 5{,}0\text{ bar}$). |
| **$B1 / B2 / B3$** | PNP NA | Abierto ($0\text{V}$) | $1 =$ Detección positiva de objeto frente al sensor. |
| **$1B1 / 2B1$** | Reed NA | Cerrado en $0\text{ mm}$ | $1 =$ Vástago en posición de reposo retraído. |
| **$1B2 / 2B2$** | Reed NA | Abierto en reposo | $1 =$ Vástago en posición de máxima extensión ($100\text{ mm}$). |

---

## 3. Diagrama en Bloques del Sistema Mecatrónico (Consigna Punto 3)

De acuerdo con la teoría clásica de sistemas mecatrónicos en lazo cerrado, se estructuran cinco subsistemas funcionales con tres flujos concurrentes: **Flujo de Información/Control**, **Flujo de Energía** (Eléctrica y Neumática) y **Flujo de Materia** (piezas).

```
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                 DIAGRAMA EN BLOQUES DE LAZO CERRADO                                        ║
║                                                                                                            ║
║  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                           SUBSISTEMA DE ALIMENTACIÓN Y ACONDICIONAMIENTO ENERGÉTICO                  │  ║
║  │   • Fuente Conmutada 24V DC (Control y Sensórica)                                                     │  ║
║  │   • Línea de Fuerza 380V/220V AC (Potencia Motor M1)                                                 │  ║
║  │   • Compresor de Aire + Filtro-Regulador-Lubricador FRL (0Z1) a 6,0 bar (Potencia Neumática)        │  ║
║  └──────────────────────────────────┬───────────────────────────────────────────────────────────────────┘  ║
║                                     │                                                                      ║
║      Flujo de Información           │ Flujos de Potencia                                                   ║
║   ┌────────────────────────┐        │                                                                      ║
║   │ 1. SUBSISTEMA DE       │        │                                                                      ║
║   │    ENTRADAS Y MANDOS   │        │                                                                      ║
║   │ • Pulsadores S0,S1,S2,S3        │                                                                      ║
║   │ • Sensores B1, B2, B3  │        │                                                                      ║
║   │ • Presostato FRL P1    │        │                                                                      ║
║   └───────────┬────────────┘        │                                                                      ║
║               │ (Señales 24V)       │                                                                      ║
║   ┌───────────▼────────────┐        │                                                                      ║
║   │ 2. SUBSISTEMA DE       │        │                                                                      ║
║   │    PROCESO Y CONTROL   │        │                                                                      ║
║   │ • Memoria Marcha K1    │        │                                                                      ║
║   │ • Validación KB1       │        │                                                                      ║
║   │ • Relé Bloqueo KF      │        │                                                                      ║
║   │ • Enclavamientos K2,K3 │        │                                                                      ║
║   └───────────┬────────────┘        │                                                                      ║
║               │ (Órdenes de mando)  │                                                                      ║
║   ┌───────────▼────────────┐        │                                                                      ║
║   │ 3. SUBSISTEMA DE       │◄───────┤                                                                      ║
║   │    PRE-ACTUACIÓN       │        │ (Modulación de Potencia)                                             ║
║   │ • Contactor KM1        │        │                                                                      ║
║   │ • Solenoides 1Y1 y 2Y1 │        │                                                                      ║
║   │ • Estranguladoras 1V2..│        │                                                                      ║
║   └───────────┬────────────┘        │                                                                      ║
║               │ (Energía modulada)  │                                                                      ║
║   ┌───────────▼─────────────────────▼────────────────────────┐                                             ║
║   │ 4. SUBSISTEMA DE ACTUACIÓN Y PLANTA MECATRÓNICA          │◄─────────── [Flujo de Material: Piezas]     ║
║   │ • Motorreductor de Tracción de Banda M1                  │                                             ║
║   │ • Cilindro 1A1 (Expulsor de Metal a Tolva 1)             │───────────► [Tolva 1: Metálicas]            ║
║   │ • Cilindro 2A1 (Expulsor de Plástico a Tolva 2)          │───────────► [Tolva 2: Plásticas]            ║
║   │ • Baliza Andon H1 (Verde), H2 (Amarillo), H3 (Rojo/Sirena│───────────► [Tolva 3: Descarte / Directo]   ║
║   └───────────────────────────┬──────────────────────────────┘                                             ║
║                               │                                                                            ║
║                               │ (Posición mecánica de vástagos)                                            ║
║   ┌───────────────────────────▼──────────────────────────────┐                                             ║
║   │ 5. LAZO DE REALIMENTACIÓN (FEEDBACK SENSORIAL)           │                                             ║
║   │ • Sensores Reed de fin de carrera 1B1 (a0) y 1B2 (a1)    │                                             ║
║   │ • Sensores Reed de fin de carrera 2B1 (b0) y 2B2 (b1)    │                                             ║
║   └───────────────────────────┬──────────────────────────────┘                                             ║
║                               │                                                                            ║
║                               └──────────────────► (Retorna al Subsistema 2: Cierre de Lazo)               ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### 3.1. Análisis Detallado de los Subsistemas
1. **Subsistema 1 (Adquisición de Señales):** Transforma variables del medio físico (presión de contacto, índice de permeabilidad magnética, constante dieléctrica, posición del campo magnético del émbolo y presión barométrica) en niveles binarios estandarizados de $0\text{V} / 24\text{V}$ DC.
2. **Subsistema 2 (Proceso y Lógica Secuencial):** Procesa la secuencia de estados booleanos. Evita colisiones cinemáticas: si $B2=1$ o $B3=1$, interrumpe la excitación de $KM1$ antes de energizar los solenoides de empuje.
3. **Subsistema 3 (Pre-actuación):** Conmuta las altas potencias a partir de señales de comando de baja corriente ($\sim 100\text{ mA}$). Incluye contactos de potencia de $KM1$, bobinas de las electroválvulas direccionales y estranguladoras de caudal unidireccionales que regulan la velocidad de carrera.
4. **Subsistema 4 (Actuación Mecánica y Planta):** Convierte energía eléctrica en par motor rotacional ($M1$) y energía neumática en fuerza lineal ($F = P \cdot A$) a través de los cilindros $1A1$ y $2A1$.
5. **Subsistema 5 (Lazo de Realimentación):** Proporciona la confirmación positiva de cumplimiento de carrera ($1B2, 2B2$) y regreso seguro a reposo ($1B1, 2B1$), garantizando el funcionamiento en lazo cerrado indispensable en mecatrónica.

---

## 4. Desarrollo de una Lógica Básica de Funcionamiento (Consigna Punto 4)

### 4.1. Ecuaciones Lógicas Booleanas de Mando

Las ecuaciones normalizadas que gobiernan el mando del sistema son:

1. **Bloqueo de Seguridad y Memoria de Fallo ($KF$):**
   $$KF = (\overline{S0} + \overline{P1} + ALM\_WD + KF) \cdot \overline{S3}$$
   *Justificación:* Si se acciona la parada de emergencia ($S0=0$), cae la presión de red ($P1=0$) o se detecta un watchdog de tiempo de carrera ($ALM\_WD=1$), el relé $KF$ se enclava cortando todo movimiento. Únicamente se desbloquea tras normalizar el defecto y accionar intencionalmente el pulsador de Rearme $S3$.

2. **Memoria Maestra de Marcha ($K1$):**
   $$K1 = S0 \cdot S2 \cdot P1 \cdot \overline{KF} \cdot (S1 + K1)$$
   *Justificación:* Circuito marcha/parada con autorretención y prioridad absoluta a la desconexión. Exige condiciones seguras ($S0=1$, $S2=1$, $P1=1$ y $\overline{KF}=1$).

3. **Validación de Pieza en Tránsito ($KB1$):**
   $$KB1 = K1 \cdot (B1 + KB1) \cdot \overline{Fin\_Lote}$$
   *Justificación:* El sensor óptico $B1$ detecta el ingreso, suma al contador y enclava $KB1$. Impide disparos falsos de los expulsores ante perturbaciones externas si no hubo ingreso previo por cabecera.

4. **Comando del Motor de Cinta ($KM1$):**
   $$KM1 = K1 \cdot 1B1 \cdot 2B1 \cdot \overline{K2} \cdot \overline{K3}$$
   *Justificación:* El motor de la cinta tracciona únicamente si el sistema está en marcha ($K1=1$), ambos cilindros están en su posición de reposo ($1B1=1$ y $2B1=1$) y no existe ninguna maniobra de expulsión activa ($\overline{K2} \cdot \overline{K3}$).

5. **Expulsión Metálica - Cilindro $1A1$ ($K2 / 1Y1$):**
   $$1Y1 = K2 = K1 \cdot KB1 \cdot (B2 \cdot 1B1 + K2) \cdot \overline{1B2}$$
   *Justificación:* Al activarse el detector inductivo $B2$ con $1A1$ en reposo, se activa $K2$, energizando el solenoide $1Y1$ (avance $A+$) y pausando la cinta. Al alcanzar el fin de carrera delantero $1B2$, $K2$ cae, desenergizando $1Y1$ y permitiendo el retroceso por muelle mecánico ($A-$).

6. **Expulsión Plástica - Cilindro $2A1$ ($K3 / 2Y1$ con Arbitraje de Conflicto):**
   $$2Y1 = K3 = K1 \cdot KB1 \cdot (B3 \cdot \overline{B2} \cdot \overline{K2} \cdot 2B1 + K3) \cdot \overline{2B2}$$
   *Justificación:* Al activarse $B3$, se energiza $2Y1$ provocando el avance $B+$ hasta $2B2$. Incluye el enclavamiento $\overline{B2} \cdot \overline{K2}$ para dar prioridad estricta al metal si una pieza llegara a activar ambos sensores simultáneamente.

7. **Ecuación de Watchdog de Carrera y Atasco ($ALM\_WD$):**
   $$ALM\_WD = (1Y1 \cdot \overline{1B2} > 1{,}5\text{ s}) + (\overline{1Y1} \cdot \overline{1B1} > 2{,}0\text{ s}) + (2Y1 \cdot \overline{2B2} > 1{,}5\text{ s}) + (\overline{2Y1} \cdot \overline{2B1} > 2{,}0\text{ s}) + (B2 \cdot B3 > 1{,}0\text{ s}) + (B1 > 3{,}0\text{ s})$$

---

### 4.2. Modelado Funcional Mediante GRAFCET (Norma IEC 60848)

```
        ┌─────────┐
        │ ══ 0 ══ │  Etapa Inicial: Reposo general (Cilindros retraídos 1B1·2B1)
        └────┬────┘
             │ Transición: S1 · S0 · S2 · P1 · /KF · 1B1 · 2B1 (Orden de Marcha)
        ┌────┴────┐
        │    1    │  Acción: KM1 (Cinta ON) + H1 (Luz Verde) + Habilitación B1
        └────┬────┘
             │
      ┌──────┴─────────────────────────────────┐ Divergencia en "O"
      │ Transición: KB1 · B2 · 1B1             │ Transición: KB1 · B3 · /B2 · 2B1
┌─────┴─────┐                            ┌─────┴─────┐
│     2     │ Acción: 1Y1 (Avance 1A1+)  │     4     │ Acción: 2Y1 (Avance 2A1+)
└─────┬─────┘                            └─────┬─────┘
      │ Transición: 1B2 (a1 = 100mm)           │ Transición: 2B2 (b1 = 100mm)
┌─────┴─────┐                            ┌─────┴─────┐
│     3     │ Acción: 1A1- (Retorno)     │     5     │ Acción: 2A1- (Retorno)
└─────┬─────┘                            └─────┬─────┘
      │ Transición: 1B1 (a0 = 0mm)             │ Transición: 2B1 (b0 = 0mm)
      └──────┬─────────────────────────────────┘ Convergencia en "O"
             │
             └─────────────────────────────────► Retorno a Etapa 1 (Cinta ON)
```

---

### 4.3. Diagrama Espacio-Fase Sincronizado

El comportamiento dinámico coordinado entre el motor $M1$ y los cilindros $1A1$ y $2A1$ se representa a continuación:

| Elemento / Fase | Fase 1 (Transp.) | Fase 2 ($A+$) | Fase 3 ($A-$) | Fase 4 (Transp.) | Fase 5 ($B+$) | Fase 6 ($B-$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Motor Cinta $KM1$** | **ON (1)** | **OFF (0)** | **OFF (0)** | **ON (1)** | **OFF (0)** | **OFF (0)** |
| **Cilindro $1A1$ ($mm$)** | $0\text{ mm}$ ($1B1$) | $0 \rightarrow 100\text{ mm}$ | $100 \rightarrow 0\text{ mm}$ | $0\text{ mm}$ ($1B1$) | $0\text{ mm}$ ($1B1$) | $0\text{ mm}$ ($1B1$) |
| **Cilindro $2A1$ ($mm$)** | $0\text{ mm}$ ($2B1$) | $0\text{ mm}$ ($2B1$) | $0\text{ mm}$ ($2B1$) | $0\text{ mm}$ ($2B1$) | $0 \rightarrow 100\text{ mm}$ | $100 \rightarrow 0\text{ mm}$ |
| **Fin de Carrera Activo** | $1B1 \cdot 2B1$ | $1B2$ ($a_1$) | $1B1$ ($a_0$) | $1B1 \cdot 2B1$ | $2B2$ ($b_1$) | $2B1$ ($b_0$) |

---

## 5. Proyección y Arquitectura para las Próximas Etapas (Puntos 5 y 6: CADe SIMU)

Para la siguiente etapa de entrega, este desarrollo se implementará directamente en **CADe SIMU**:
1. **Punto 5 (Implementación en CADe SIMU):**
   - **Esquema de Fuerza Tridimensional / Multifilar:** Alimentación $3\sim 380\text{V} + N + PE$, guardamotor magnetotérmico $QM1$, contactor de potencia $KM1$ y motorreductor trifásico $M1$.
   - **Esquema de Mando Electroneumático:** Fuente de alimentación conmutada $230\text{V AC} / 24\text{V DC}$, circuito de parada de emergencia con relé de seguridad $KF$, pulsadores de mando $S1/S2/S3$, bobinas de contactores y electroválvulas $1Y1$ y $2Y1$.
   - **Esquema Neumático de Potencia:** Alimentación de aire comprimido, unidad de mantenimiento $0Z1$, electroválvulas $5/2$ monoestables accionadas por solenoide y retorno por resorte, reguladores de flujo unidireccionales y actuadores lineales de doble efecto con detectores magnéticos reed.
2. **Punto 6 (Demostración y Validación):**
   - Protocolo de pruebas de laboratorio simulado en CADe SIMU: verificación de arranque, ciclo metálico $A+/A-$, ciclo plástico $B+/B-$, descarte en tolva 3, disparo de parada de emergencia $S0$ y rearme manual con $S3$.

