# Checklist para la demostración

Duración estimada: 3 minutos.

---

## Antes de la clase

- [ ] Abrir el `.cad` y probar toda la secuencia una vez.
- [ ] Dejar la simulación detenida y QM1 abierto antes de empezar.
- [ ] Tener el PDF impreso o abierto en el celular.
- [ ] Tener las capturas guardadas por si falla la notebook.
- [ ] Saber de memoria los tags: S0, S1, S2, SA1, N1, N2, KM1, YV1, H1, H2.
- [ ] Revisar que el zoom de CADe SIMU deje ver todo el circuito.

---

## Guion de 3 minutos

**0:00 a 0:25 — Presentación**

"Elegí la estación de llenado y vaciado de tanque. Tiene dos flotantes, una bomba y una electroválvula. La lógica es cableada, con un contactor y un selector. Lo simulé en CADe SIMU porque no tengo FluidSIM y este sistema es eléctrico."

Señalar en el esquema:
- Entradas: S0, S1, S2, SA1, N1, N2.
- Proceso: contactos y relay.
- Salidas: KM1, M1, YV1, H1, H2.
- Realimentación: N1 y N2.

**0:25 a 1:00 — Llenado**

"Con SA1 en LLENADO aprieto S1. KM1 se energiza, arranca la bomba y se prende H1. Suelto S1 y la bomba sigue porque KM1 se enclava con su contacto auxiliar."

Acciones:
1. Cerrar QM1.
2. Apretar S1 y soltar.
3. Señalar KM1 y H1.

**1:00 a 1:20 — Tanque lleno**

"Cuando el agua llega al flotante de arriba, N2 se abre. Eso corta el enclavamiento, se apaga KM1 y se detiene la bomba."

Acción:
1. Hacer clic en N2 para abrirlo.
2. Mostrar que KM1 y H1 se apagan.

**1:20 a 1:50 — Vaciado**

"Giro el selector a VACIADO. Ahora se energiza YV1 y se abre la válvula. Se prende H2. Cuando el nivel baja hasta N1, el flotante abre y cierra la válvula."

Acciones:
1. Girar SA1 a VACIADO.
2. Mostrar YV1 y H2.
3. Hacer clic en N1 para abrirlo.
4. Mostrar que YV1 y H2 se apagan.

**1:50 a 2:10 — Seguridad**

"Aprieto la emergencia y se apaga todo. La válvula es normalmente cerrada, así que sin tensión queda cerrada. Si se va la luz, pasa lo mismo: no arranca solo cuando vuelve."

Acción:
1. Apretar S0.
2. Mostrar que todo queda apagado.
3. Soltar S0 y recordar que hay que volver a apretar S1.

**2:10 a 2:30 — Interlock**

"El selector tiene un contacto NA y uno NC. Por eso la bomba y la válvula no pueden funcionar juntas."

Acción:
1. Poner SA1 en VACIADO.
2. Apretar S1.
3. Mostrar que la bomba no arranca.

**2:30 a 3:00 — Cierre**

"El sistema quedó simple: mantiene el nivel entre un mínimo y un máximo, con protecciones y enclavamiento. Como mejora se podría automatizar el vaciado o usar mando a 24 V."

---

## Preguntas posibles y respuestas cortas

**¿Por qué no usaste FluidSIM?**
Porque no tengo licencia. La guía pedía FluidSIM, pero elegí un sistema eléctrico para poder simularlo completo en CADe SIMU. Si la cátedra lo exige, se puede hacer una variante neumática, pero este sistema no necesita aire.

**¿Por qué usaste contactor y no un PLC?**
Porque la lógica es muy simple. Un contactor con un contacto auxiliar y un selector alcanzan. Un PLC sería más caro y más complicado para esta función.

**¿Por qué los flotantes son NC?**
Para que el sistema falle hacia el lado seguro. Si se corta un cable o se afloja un borne, el contacto se abre y se detiene el sistema. Con NA, un cable cortado podría dejar la bomba andando.

**¿Qué pasa si el tanque está lleno y el operador deja el selector en LLENADO?**
La bomba queda detenida porque N2 está abierto. No vuelve a arrancar hasta que el nivel baje y se apriete S1 de nuevo.

**¿Qué pasa si se aprieta S1 en VACIADO?**
No arranca la bomba porque la rama de LLENADO está abierta por SA1. Es el interlock.

**¿Qué pasa si se va la luz?**
Se apaga todo. La válvula es NC y queda cerrada. Cuando vuelve la luz, KM1 no se enclava solo: hay que apretar S1.

**¿Qué pasa si falla N2?**
Si falla abierto, la bomba no arranca o se detiene antes. Si falla cerrado, podría llenar de más. En una instalación real conviene agregar una segunda protección de nivel alto o una alarma.

**¿Qué pasa si falla N1?**
Si queda cerrado, la válvula sigue abierta después del mínimo. No rompe nada porque la bomba está detenida, pero es una mejora a tener en cuenta.

**¿Por qué hay dos lámparas?**
Para mostrar desde el tablero si está andando la bomba o si está abierta la válvula. También sirve para la demostración.

**¿Cuál es la parte mecatrónica?**
El tanque, la bomba y la válvula son la parte mecánica; los flotantes son los sensores; el contactor y el motor son la parte eléctrica; y la lógica de contactos es el control.

**¿Se puede automatizar el ciclo completo?**
Sí. Se podría agregar un relé de memoria que abra la válvula cuando N2 se active y la cierre cuando N1 se active. Así no habría que girar el selector.

**¿Por qué el mando es a 220 V?**
Para no agregar una fuente de 24 V en la simulación. En una instalación real convendría mando a 24 V por seguridad.

**¿Qué protege cada cosa?**
QM1 protege la instalación y el motor; F2 protege el circuito de mando; F1 protege el motor contra sobrecarga; S0 corta el mando completo.

---

## Si algo falla durante la demo

- **No arranca la bomba:** revisar QM1 cerrado, S0 y S2 sin apretar, F1 sin disparar, SA1 en LLENADO.
- **Arranca pero no se mantiene:** falta el contacto auxiliar de KM1 en paralelo con S1.
- **No se apaga con N2:** revisar que N2 esté en la rama de LLENADO y que sea NC.
- **La válvula no abre:** revisar SA1 en VACIADO, N1 cerrado y bobina de YV1 con neutro.
- **Se trabó CADe SIMU:** detener la simulación, revisar cortocircuitos y volver a iniciar.

No entrar en pánico. Explicar lo que debería pasar y seguir. Si no se puede simular, usar las capturas del Anexo B.
