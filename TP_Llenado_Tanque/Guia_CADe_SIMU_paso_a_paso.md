# Guía para armar el TP en CADe SIMU

Esta guía es para mí, para no perderme cuando abra el programa. No hace falta entregarla.

Circuito de referencia: `img/circuito_mando.png` y `img/circuito_potencia.png`.

Esquema de la planta (extra): `img/diagrama_proceso.png`.

---

## 1. Antes de empezar

- Abrir CADe SIMU.
- Crear un archivo nuevo.
- Configurar hoja **A4 horizontal**.
- Completar el cajetín con nombre, materia, año y título.
- Guardar como `TP_Llenado_Tanque.cad` desde el primer momento.

Consejo: dejar la potencia a la izquierda y el mando a la derecha. Así se ve ordenado y no se cruzan los cables.

---

## 2. Componentes que voy a usar

Los nombres pueden cambiar un poco según la versión de CADe SIMU. Buscar por el nombre parecido.

| Componente | Tag | Para qué |
|---|---|---|
| Alimentación F + N | — | 220 V AC |
| Interruptor automático 2 polos | QM1 | Protección general |
| Fusible | F2 | Protección del mando |
| Contactor 2 polos con contacto auxiliar NA | KM1 | Bomba |
| Relé térmico | F1 | Protección del motor |
| Motor monofásico | M1 | Bomba |
| Pulsador NC | S0 | Emergencia |
| Pulsador NA | S1 | Marcha |
| Pulsador NC | S2 | Paro |
| Selector de 2 posiciones, con un contacto NA y uno NC | SA1 | LLENADO / VACIADO |
| Final de carrera NC | N1 | Flotante de nivel mínimo |
| Final de carrera NC | N2 | Flotante de nivel máximo |
| Bobina de electroválvula | YV1 | Vaciado |
| Lámpara verde | H1 | Bomba en marcha |
| Lámpara roja | H2 | Válvula abierta |

Si el selector de la biblioteca tiene un solo contacto, buscar uno de dos contactos o usar dos contactos mecánicamente unidos. Lo importante es que en LLENADO cierre el NA y en VACIADO cierre el NC.

---

## 3. Circuito de potencia

Orden de conexión:

1. Colocar la alimentación F + N.
2. L1 → QM1 (los dos polos) → contacto principal de KM1 → F1 → M1 → N.
3. Conectar PE a la carcasa del motor.
4. Verificar que el motor esté configurado en 220 V monofásico.

Antes de seguir, probar solo la potencia: cerrar QM1 y ver que el motor pueda girar. Si no gira, el problema está en esta parte y no en el mando.

---

## 4. Circuito de mando

### 4.1. Cadena común

Desde L1, después de QM1:

**L1 → F2 → S0 NC → S2 NC → F1 NC → punto A**

El punto A es el que alimenta las dos ramas. Si S0, S2 o F1 se abren, se apaga todo.

### 4.2. Rama de LLENADO

Desde el punto A:

**SA1 NA → N2 NC → punto B**

Desde el punto B salen dos caminos que se unen en la bobina KM1:

- **B → S1 NA → bobina KM1 → N**
- **B → contacto auxiliar NA de KM1 → bobina KM1 → N**

Ese segundo camino es el enclavamiento. Sin él, la bomba se apaga al soltar S1.

La lámpara H1 va en paralelo con la bobina de KM1.

### 4.3. Rama de VACIADO

Desde el punto A:

**SA1 NC → N1 NC → bobina YV1 → N**

La lámpara H2 va en paralelo con la bobina de YV1.

### 4.4. Orden recomendado para dibujar

1. Primero la cadena común: F2, S0, S2, F1.
2. Después la rama de LLENADO completa, incluyendo el paralelo S1/KM1.
3. Probar que KM1 se enclava.
4. Recién después agregar la rama de VACIADO.
5. Al final agregar H1 y H2.

Así, si algo falla, sé en qué parte está el error.

---

## 5. Etiquetas y detalles

- Poner el nombre de cada componente igual que en el informe: QM1, F2, KM1, F1, M1, S0, S1, S2, SA1, N1, N2, YV1, H1, H2.
- No puede haber dos componentes con el mismo nombre. Si hay dos KM1, la simulación no funciona bien.
- Revisar que las bobinas y las lámparas sean de 220 V AC.
- Los flotantes se representan con finales de carrera **NC**.
- La electroválvula es **normalmente cerrada**: sin tensión, queda cerrada.

---

## 6. Simulación

1. Poner el programa en modo simulación.
2. Cerrar QM1.
3. Apretar S1 y soltar: KM1 tiene que quedar energizado y el motor andando. H1 encendida.
4. Hacer clic en N2 para abrirlo (simula el tanque lleno): KM1 se apaga, el motor se detiene y H1 se apaga.
5. Girar SA1 a VACIADO: YV1 se energiza y H2 se enciende.
6. Hacer clic en N1 para abrirlo (simula el nivel mínimo): YV1 se apaga y H2 se apaga.
7. Apretar S0: todo se apaga.
8. Volver a probar el enclavamiento: apretar S1, soltar y ver que KM1 sigue encendido.
9. Probar el interlock: con SA1 en VACIADO, apretar S1. La bomba no debe arrancar.
10. Repetir el ciclo: abrir N1, poner SA1 en LLENADO, apretar S1. La bomba debe arrancar de nuevo.

Los pulsadores vuelven solos. Para mantenerlos apretados hay que hacer clic y arrastrar un poco.

---

## 7. Capturas para el Anexo B

Captura 1:
- Circuito en modo simulación.
- Bomba en marcha (KM1 y H1 activos, motor girando).
- Que se lean los tags.

Captura 2:
- Selector en VACIADO.
- YV1 y H2 activos.
- Que se vea la rama de vaciado.

Usar Win + Shift + S o la herramienta de recortes. Guardar como PNG y pegar en el Anexo B del Word. Poner un epígrafe corto debajo de cada una.

---

## 8. Errores comunes y cómo los resolví

| Problema | Causa probable | Solución |
|---|---|---|
| La bomba arranca solo mientras aprieto S1 | Falta el contacto auxiliar de KM1 | Agregar KM1 NA en paralelo con S1 |
| La válvula se abre también en LLENADO | Usé un solo contacto NA del selector | Usar NA para LLENADO y NC para VACIADO |
| N1 o N2 actúan al revés | Olvidé que son NC | En simulación, hacer clic para abrirlos cuando el flotante actúa |
| KM1 no se energiza | Falta el neutro en la bobina o la bobina no es de 220 V | Revisar A2/N y la tensión de la bobina |
| La simulación marca cortocircuito | Hay un camino directo de L1 a N | Revisar que cada rama termine en una bobina o lámpara |
| Dos componentes con el mismo tag | Copié y pegué sin renombrar | Renombrar uno por uno |
| El motor no gira | F1 disparado o motor mal configurado | Resetear F1 y revisar la configuración del motor |
| La lámpara no enciende | Está en serie con la bobina | Ponerla en paralelo |

---

## 9. Antes de guardar la versión final

- [ ] Todos los tags coinciden con el informe.
- [ ] La potencia y el mando están separados y se entienden.
- [ ] KM1 se enclava al soltar S1.
- [ ] N2 detiene la bomba.
- [ ] SA1 cambia de LLENADO a VACIADO.
- [ ] N1 cierra la válvula.
- [ ] S0 apaga todo.
- [ ] H1 y H2 funcionan.
- [ ] Las dos capturas están guardadas.
- [ ] El archivo `.cad` está guardado con el nombre `TP_Llenado_Tanque.cad`.

---

## 10. Para la defensa

No hace falta explicar CADe SIMU, alcanza con explicar el sistema. Pero si preguntan:

- **¿Por qué CADe SIMU?** Porque no tengo licencia de FluidSIM y este sistema es eléctrico, así que se puede simular completo.
- **¿Por qué contactor y no PLC?** Porque la lógica es simple y no necesita PLC. Con contactos alcanza y es más barato.
- **¿Por qué los flotantes son NC?** Para que un cable cortado o un borne flojo detenga el sistema. Es más seguro.
- **¿Qué pasa si se va la luz?** Se apaga todo. La válvula es NC, así que queda cerrada. Al volver la luz no arranca solo: hay que apretar S1.
- **¿Qué mejorarías?** Poner el mando a 24 V, agregar un piloto de tanque lleno y, si se quiere, automatizar el ciclo con un relé de memoria o un PLC.
