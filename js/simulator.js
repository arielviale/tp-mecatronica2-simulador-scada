/**
 * ============================================================================
 * SUITE INTERACTIVA: SIMULADOR ELECTRONEUMÁTICO + SCADA MECATRÓNICO (ISA-101 / ISO 1219)
 * UTN Facultad Regional Paraná — Tecnicatura Superior en Mecatrónica
 * Cátedra: Mecatrónica II · Alumno: Hugo Ariel Martinez
 * ============================================================================
 */

(function () {
  'use strict';

  // ==================== ESTADO FÍSICO Y LÓGICO DEL SISTEMA ====================
  const state = {
    // Entradas de mando
    S0_ESTOP_OK: true,     // NC: true = normal (cerrado), false = seta presionada
    S1_START: false,       // NA: pulso de marcha
    S2_STOP_OK: true,      // NC: true = reposo, false = pulsado
    S3_RESET: false,

    // Parámetros neumáticos y mecánicos
    pressureBar: 6.0,      // bar en unidad FRL (P1 >= 5.0 bar)
    P1_OK: true,
    flowPercent: 80,       // % apertura reguladores 1V2 / 2V2
    beltSpeedPercent: 100, // % velocidad cinta M1
    cylAJammed: false,     // Simulación de atasco mecánico FMEA

    // Memorias / Relés internos (Lógica cableada / PLC)
    K1_RUN: false,         // Memoria de sistema en marcha
    KB1_VALID: false,      // Memoria de pieza en tránsito validada por sensor óptico B1
    K2_CYCLE_A: false,     // Memoria secuencia A+ (expulsión metal)
    K3_CYCLE_B: false,     // Memoria secuencia B+ (expulsión plástico)
    FAULT_ACTIVE: false,   // Memoria de bloqueo por falla KF (requiere rearme S3)

    // Sensores de presencia en cinta
    B1_OPT: false,         // Ingreso de pieza (x ~ 166)
    B2_IND: false,         // Sensor inductivo estación 1 Metal (x ~ 305)
    B3_CAP: false,         // Sensor capacitivo estación 2 Plástico (x ~ 500)

    // Cilindros neumáticos (posición de 0 a 100 mm)
    cylA_mm: 0,
    cylB_mm: 0,
    // Fines de carrera magnéticos Reed
    S_1B1: true,           // a0 (0 mm)
    S_1B2: false,          // a1 (100 mm)
    S_2B1: true,           // b0 (0 mm)
    S_2B2: false,          // b1 (100 mm)

    // Salidas de potencia / Actuadores
    KM1_MOTOR: false,
    SOL_1Y1: false,
    SOL_2Y1: false,
    H1_GREEN: false,
    H2_YELLOW: false,
    H3_RED: false,

    // Contadores de producción
    cntMetal: 0,
    cntPlastic: 0,
    cntReject: 0,
    grafcetStage: 'E0: Reposo',

    // Animación, temporizadores Watchdog y piezas en la cinta
    beltOffset: 0,
    rollerAngle: 0,
    pieces: [],
    nextPieceId: 1,
    autoFeed: false,
    autoFeedTimer: 0,
    timerAvA: 0,           // Watchdog avance 1A1 (límite 1.5 s)
    timerRetA: 0,          // Watchdog retroceso 1A1 (límite 2.0 s)
    timerAvB: 0,           // Watchdog avance 2A1 (límite 1.5 s)
    timerRetB: 0,          // Watchdog retroceso 2A1 (límite 2.0 s)
    timerJamB1: 0,         // Watchdog atasco en sensor B1 (límite 3.0 s)
    timerConflictB2B3: 0,  // Watchdog conflicto simultáneo B2·B3 (límite 1.0 s)
    simConflictB2B3: false,

    // Audio y Alarmas
    audioEnabled: true,
    alarms: [],
    historySamples: []     // Buffer circular para el Diagrama Espacio-Fase
  };

  // ==================== MOTOR DE AUDIO SINTETIZADO (WEB AUDIO API) ====================
  let audioCtx = null;

  function ensureAudio() {
    if (!state.audioEnabled) return null;
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) audioCtx = new AudioContextClass();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  // Sonido de escape neumático ("pssshh!") al conmutar electroválvula 5/2
  function playPneumaticExhaust(duration = 0.16) {
    const ctx = ensureAudio();
    if (!ctx) return;
    try {
      const bufferSize = ctx.sampleRate * duration;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (ctx.sampleRate * 0.06));
      }
      const noise = ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = 2400;
      filter.Q.value = 1.2;

      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.18, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);
      noise.start();
    } catch (_) {}
  }

  // Sonido de click de relé / solenoide o alarma
  function playTone(freq = 520, duration = 0.08, type = 'sine', vol = 0.08) {
    const ctx = ensureAudio();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(vol, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.005, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (_) {}
  }

  // ==================== GESTIÓN DE ALARMAS ISA-18.2 ====================
  function logEvent(priority, tag, message) {
    const now = new Date();
    const ts = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');
    state.alarms.unshift({
      id: Date.now() + Math.random(),
      ts,
      priority,
      tag,
      message,
      acked: priority === 'INFO'
    });
    if (state.alarms.length > 60) state.alarms.pop();
    renderAlarmsTable();
  }

  function renderAlarmsTable() {
    const tbody = document.getElementById('alarms-tbody');
    const badge = document.getElementById('badge-alarmas');
    if (!tbody) return;

    const unacked = state.alarms.filter(a => !a.acked && (a.priority === 'ALTA' || a.priority === 'MEDIA')).length;
    if (badge) {
      badge.hidden = unacked === 0;
      badge.textContent = String(unacked);
    }

    tbody.innerHTML = state.alarms.map(a => {
      let pillStyle = 'background:rgba(0,180,216,0.15);color:#38bdf8;';
      if (a.priority === 'ALTA') pillStyle = 'background:rgba(255,56,92,0.2);color:#ff385c;';
      else if (a.priority === 'MEDIA') pillStyle = 'background:rgba(255,183,3,0.18);color:#ffb703;';

      const stText = a.acked ? '<span style="color:#00e599;">RECONOCIDA (ACK)</span>' : '<span style="color:#ff385c;font-weight:700;">ACTIVA SIN ACK</span>';
      return `<tr>
        <td class="mono">${a.ts}</td>
        <td><span class="state-pill" style="${pillStyle}">${a.priority}</span></td>
        <td class="mono"><b>${a.tag}</b></td>
        <td>${a.message}</td>
        <td class="mono">${stText}</td>
      </tr>`;
    }).join('');
  }

  // ==================== INYECCIÓN DE PIEZAS EN LA CINTA ====================
  function spawnPiece(type) {
    // Evitar encimar piezas en la zona de carga (x < 165)
    const tooClose = state.pieces.some(p => p.state === 'BELT' && p.x < 170);
    if (tooClose) return false;

    const piece = {
      id: state.nextPieceId++,
      type, // 'METAL' | 'PLASTIC' | 'REJECT'
      x: 112,
      y: 185,
      state: 'BELT', // 'BELT' | 'PUSHED_A' | 'PUSHED_B' | 'CHUTE_1' | 'CHUTE_2' | 'CHUTE_3'
      validatedByB1: false,
      chuteProgress: 0
    };
    state.pieces.push(piece);
    playTone(660, 0.05, 'triangle', 0.05);
    return true;
  }

  // ==================== MOTOR DE SIMULACIÓN FÍSICA Y LÓGICA (60 FPS) ====================
  let prev1Y1 = false;
  let prev2Y1 = false;

  function stepSimulation(dt) {
    // 1. Evaluar Presostato P1 (Umbral 5.0 bar)
    state.P1_OK = state.pressureBar >= 5.0;
    if (!state.P1_OK && state.K1_RUN) {
      state.K1_RUN = false;
      state.FAULT_ACTIVE = true;
      logEvent('ALTA', 'P1_LOW_BAR', `Caída de presión neumática en FRL (${state.pressureBar.toFixed(1)} bar < 5.0 bar). Parada segura.`);
      playTone(240, 0.35, 'sawtooth', 0.14);
    }

    // 2. Evaluar Fines de Carrera Magnéticos Reed (1B1/1B2 y 2B1/2B2)
    state.S_1B1 = state.cylA_mm <= 3;
    state.S_1B2 = state.cylA_mm >= 97;
    state.S_2B1 = state.cylB_mm <= 3;
    state.S_2B2 = state.cylB_mm >= 97;

    // 3. Evaluar Sensores sobre la Cinta (B1, B2, B3)
    state.B1_OPT = false;
    state.B2_IND = false;
    state.B3_CAP = false;

    for (const p of state.pieces) {
      if (p.state === 'BELT') {
        if (Math.abs(p.x - 166) < 16) {
          state.B1_OPT = true;
          p.validatedByB1 = true;
        } else if (p.x >= 166) {
          p.validatedByB1 = true;
        }
        // B2 es Inductivo: solo detecta piezas METÁLICAS frente a Cilindro 1A1 (x ~ 305)
        if (p.type === 'METAL' && Math.abs(p.x - 305) < 15) {
          state.B2_IND = true;
        }
        // B3 es Capacitivo/Óptico en Estación 2: detecta piezas PLÁSTICAS frente a Cilindro 2A1 (x ~ 500)
        if (p.type === 'PLASTIC' && Math.abs(p.x - 500) < 15) {
          state.B3_CAP = true;
        }
      }
    }

    if (state.simConflictB2B3) {
      state.B2_IND = true;
      state.B3_CAP = true;
      state.KB1_VALID = true;
    }

    // 4. Lógica Secuencial Electroneumática / PLC (Ecuaciones de Mando)
    // Rung 7 (Seguridad): KF = (/S0 + /P1 + ALM_WD + KF) · /S3
    if (!state.S0_ESTOP_OK || !state.P1_OK) {
      state.FAULT_ACTIVE = true;
    }

    // Rung 1: Enclavamiento general K1 = S0 · S2 · P1 · /KF · (S1 + K1)
    if (!state.S0_ESTOP_OK || !state.S2_STOP_OK || !state.P1_OK || state.FAULT_ACTIVE) {
      state.K1_RUN = false;
      state.KB1_VALID = false;
      state.K2_CYCLE_A = false;
      state.K3_CYCLE_B = false;
      state.timerJamB1 = 0;
      state.timerConflictB2B3 = 0;
      state.timerAvA = 0;
      state.timerRetA = 0;
      state.timerAvB = 0;
      state.timerRetB = 0;
    } else if (state.S1_START) {
      state.K1_RUN = true;
    }

    // Validación de Pieza en Tránsito (KB1) y Detección de Atasco en B1 (T_B1 > 3.0 s)
    // Si una pieza ya cruzó B1 antes de una Parada (S2), conserva su validación en tránsito al reanudar Marcha (S1)
    const hasValidatedPieceOnBelt = state.pieces.some(
      p => (p.state === 'BELT' || p.state === 'PUSHED_A' || p.state === 'PUSHED_B') && p.validatedByB1
    );
    if (state.K1_RUN) {
      if (state.B1_OPT || hasValidatedPieceOnBelt || state.simConflictB2B3) {
        state.KB1_VALID = true;
      } else if (state.S_1B1 && state.S_2B1) {
        state.KB1_VALID = false;
      }

      if (state.B1_OPT && state.KM1_MOTOR) {
        state.timerJamB1 += dt;
        if (state.timerJamB1 > 3.0 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          logEvent('ALTA', 'ALM_JAM_B1', 'Atasco de pieza en ingreso B1 (obstrucción continua > 3.0 s). Requiere Rearme S3.');
          playTone(210, 0.4, 'sawtooth', 0.15);
        }
      } else if (!state.B1_OPT) {
        state.timerJamB1 = 0;
      }

      // Arbitraje de Conflicto Simultáneo B2 y B3 (Prioridad Metal K2 + Watchdog > 1.0 s)
      if (state.B2_IND && state.B3_CAP) {
        state.timerConflictB2B3 += dt;
        if (state.timerConflictB2B3 > 1.0 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          state.simConflictB2B3 = false;
          logEvent('ALTA', 'ALM_CONF_B2B3', 'Conflicto de detección simultánea B2 y B3 persistente (> 1.0 s). Parada segura KF=1.');
          playTone(200, 0.45, 'sawtooth', 0.16);
        }
      } else {
        state.timerConflictB2B3 = 0;
      }

      // Rung 3: Disparo Ciclo Metal (Prioridad Alta): K2 = K1 · KB1 · (B2 · 1B1 + K2) · /1B2
      if (state.KB1_VALID && state.B2_IND && state.S_1B1 && !state.K2_CYCLE_A) {
        state.K2_CYCLE_A = true;
      }
      if (state.S_1B2) {
        state.K2_CYCLE_A = false; // Al tocar fin de carrera 1B2 (a1), corta 1Y1 y retorna por muelle
      }

      // Rung 4: Disparo Ciclo Plástico (Bloqueado si B2=1 o K2=1): K3 = K1 · KB1 · (B3 · /B2 · /K2 · 2B1 + K3) · /2B2
      if (state.KB1_VALID && state.B3_CAP && !state.B2_IND && !state.K2_CYCLE_A && state.S_2B1 && !state.K3_CYCLE_B) {
        state.K3_CYCLE_B = true;
      }
      if (state.S_2B2) {
        state.K3_CYCLE_B = false; // Al tocar 2B2 (b1), corta 2Y1 y retorna por muelle
      }
    }

    // Salidas a Solenoides 1Y1 y 2Y1
    state.SOL_1Y1 = state.K1_RUN && state.K2_CYCLE_A;
    state.SOL_2Y1 = state.K1_RUN && state.K3_CYCLE_B;

    if (state.SOL_1Y1 !== prev1Y1) {
      playPneumaticExhaust(0.14);
      prev1Y1 = state.SOL_1Y1;
    }
    if (state.SOL_2Y1 !== prev2Y1) {
      playPneumaticExhaust(0.14);
      prev2Y1 = state.SOL_2Y1;
    }

    // Rung 2: Contactor Motor Cinta KM1 (Funciona si K1=1 y ambos cilindros están retraídos en 1B1 y 2B1 y sin ciclo de expulsión activo)
    state.KM1_MOTOR = state.K1_RUN && state.S_1B1 && state.S_2B1 && !state.K2_CYCLE_A && !state.K3_CYCLE_B;

    // Indicadores Luminosos H1, H2, H3
    state.H1_GREEN = state.K1_RUN;
    state.H2_YELLOW = state.K2_CYCLE_A || state.K3_CYCLE_B || !state.S_1B1 || !state.S_2B1;
    state.H3_RED = !state.S0_ESTOP_OK || !state.P1_OK || state.FAULT_ACTIVE;

    // Determinar Etapa GRAFCET para visualización pedagógica
    if (state.H3_RED) {
      state.grafcetStage = 'FALLA / EMERG.';
    } else if (!state.K1_RUN) {
      state.grafcetStage = 'E0: Reposo';
    } else if (state.SOL_1Y1) {
      state.grafcetStage = 'E2: Avance 1A1+';
    } else if (!state.S_1B1) {
      state.grafcetStage = 'E3: Retorno 1A1-';
    } else if (state.SOL_2Y1) {
      state.grafcetStage = 'E4: Avance 2A1+';
    } else if (!state.S_2B1) {
      state.grafcetStage = 'E5: Retorno 2A1-';
    } else {
      state.grafcetStage = 'E1: Cinta M1 ON';
    }

    // 5. Dinámica de Cilindros 1A1 y 2A1 (0..100 mm) y Watchdogs de Avance (1.5 s) / Retroceso (2.0 s)
    const pressureFactor = Math.max(0, (state.pressureBar - 1.5) / 4.5);
    const strokeSpeed = 240 * (state.flowPercent / 100) * pressureFactor; // mm/s

    if (state.SOL_1Y1 && state.P1_OK) {
      state.timerRetA = 0;
      if (state.cylAJammed && state.cylA_mm >= 48) {
        state.cylA_mm = 48;
      } else {
        state.cylA_mm = Math.min(100, state.cylA_mm + strokeSpeed * dt);
      }
      if (!state.S_1B2) {
        state.timerAvA += dt;
        if (state.timerAvA > 1.5 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          logEvent('ALTA', 'ALM_AV_1A1', 'Fallo avance 1A1: 1Y1 energizado y 1B2 (a1) no confirmó en 1.5 s. Bloqueo KF=1.');
          playTone(210, 0.45, 'sawtooth', 0.16);
        }
      } else {
        state.timerAvA = 0;
      }
    } else {
      state.timerAvA = 0;
      state.cylA_mm = Math.max(0, state.cylA_mm - strokeSpeed * 1.15 * dt);
      if (!state.S_1B1 && state.K1_RUN) {
        state.timerRetA += dt;
        if (state.timerRetA > 2.0 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          logEvent('ALTA', 'ALM_RET_1A1', 'Fallo retroceso 1A1: 1Y1 desenergizado y 1B1 (a0) no confirmó en 2.0 s. Bloqueo KF=1.');
          playTone(210, 0.45, 'sawtooth', 0.16);
        }
      } else {
        state.timerRetA = 0;
      }
    }

    if (state.SOL_2Y1 && state.P1_OK) {
      state.timerRetB = 0;
      state.cylB_mm = Math.min(100, state.cylB_mm + strokeSpeed * dt);
      if (!state.S_2B2) {
        state.timerAvB += dt;
        if (state.timerAvB > 1.5 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          logEvent('ALTA', 'ALM_AV_2A1', 'Fallo avance 2A1: 2Y1 energizado y 2B2 (b1) no confirmó en 1.5 s. Bloqueo KF=1.');
          playTone(210, 0.45, 'sawtooth', 0.16);
        }
      } else {
        state.timerAvB = 0;
      }
    } else {
      state.timerAvB = 0;
      state.cylB_mm = Math.max(0, state.cylB_mm - strokeSpeed * 1.15 * dt);
      if (!state.S_2B1 && state.K1_RUN) {
        state.timerRetB += dt;
        if (state.timerRetB > 2.0 && !state.FAULT_ACTIVE) {
          state.FAULT_ACTIVE = true;
          state.K1_RUN = false;
          logEvent('ALTA', 'ALM_RET_2A1', 'Fallo retroceso 2A1: 2Y1 desenergizado y 2B1 (b0) no confirmó en 2.0 s. Bloqueo KF=1.');
          playTone(210, 0.45, 'sawtooth', 0.16);
        }
      } else {
        state.timerRetB = 0;
      }
    }

    // 6. Dinámica de la Cinta Transportadora y Movimiento de Piezas
    const beltSpeedPx = 115 * (state.beltSpeedPercent / 100);
    if (state.KM1_MOTOR) {
      state.beltOffset = (state.beltOffset - beltSpeedPx * dt) % 28;
      state.rollerAngle = (state.rollerAngle + 220 * dt) % 360;
    }

    // Alimentación automática de piezas si está activa
    if (state.autoFeed && state.K1_RUN) {
      state.autoFeedTimer += dt;
      if (state.autoFeedTimer >= 3.4) {
        state.autoFeedTimer = 0;
        const r = Math.random();
        const type = r < 0.45 ? 'METAL' : (r < 0.88 ? 'PLASTIC' : 'REJECT');
        spawnPiece(type);
      }
    }

    // Actualizar posición de cada pieza
    for (let i = state.pieces.length - 1; i >= 0; i--) {
      const p = state.pieces[i];
      if (p.state === 'BELT') {
        if (state.KM1_MOTOR) {
          p.x += beltSpeedPx * dt;
        }
        // ¿Empujada por Cilindro 1A1 (Metal)?
        if (Math.abs(p.x - 305) < 18 && state.cylA_mm > 22) {
          p.state = 'PUSHED_A';
        }
        // ¿Empujada por Cilindro 2A1 (Plástico)?
        if (Math.abs(p.x - 500) < 18 && state.cylB_mm > 22) {
          p.state = 'PUSHED_B';
        }
        // ¿Llegó al final de la cinta hacia Tolva 3 (x >= 638)?
        if (p.x >= 638) {
          p.state = 'CHUTE_3';
          state.cntReject++;
          logEvent('INFO', 'SORT_TOLVA3', `Pieza #${p.id} (${p.type}) derivada a Tolva 3 (Final de línea).`);
        }
      } else if (p.state === 'PUSHED_A') {
        // El vástago de 1A1 empuja la pieza verticalmente hacia la Rampa 1 (y: 185 -> 255)
        const targetY = 148 + (state.cylA_mm / 100) * 95;
        p.y = Math.max(p.y, targetY);
        if (state.cylA_mm >= 92 || p.y >= 232) {
          p.state = 'CHUTE_1';
          state.cntMetal++;
          logEvent('INFO', 'SORT_METAL_1A1', `Pieza Metálica #${p.id} clasificada exitosamente en Tolva 1 por Cilindro 1A1.`);
        } else if (!state.SOL_1Y1 && state.cylA_mm < 20) {
          // Si se presionó Parada/Emergencia a mitad de carrera antes de entrar en la rampa, vuelve al centro de la cinta para ser sensada al reanudar
          p.state = 'BELT';
          p.y = 185;
        }
      } else if (p.state === 'PUSHED_B') {
        const targetY = 148 + (state.cylB_mm / 100) * 95;
        p.y = Math.max(p.y, targetY);
        if (state.cylB_mm >= 92 || p.y >= 232) {
          p.state = 'CHUTE_2';
          state.cntPlastic++;
          logEvent('INFO', 'SORT_PLAST_2A1', `Pieza Plástica #${p.id} clasificada exitosamente en Tolva 2 por Cilindro 2A1.`);
        } else if (!state.SOL_2Y1 && state.cylB_mm < 20) {
          p.state = 'BELT';
          p.y = 185;
        }
      } else if (p.state === 'CHUTE_1' || p.state === 'CHUTE_2') {
        p.y += 140 * dt;
        if (p.y >= 305) {
          state.pieces.splice(i, 1);
        }
      } else if (p.state === 'CHUTE_3') {
        p.x += 90 * dt;
        p.y += 80 * dt;
        if (p.x >= 685) {
          state.pieces.splice(i, 1);
        }
      }
    }

    // 7. Guardar muestra para el Diagrama Espacio-Fase (State Diagram)
    state.historySamples.push({
      m1: state.KM1_MOTOR ? 1 : 0,
      cylA: state.cylA_mm,
      cylB: state.cylB_mm,
      y1: state.SOL_1Y1 ? 1 : 0,
      y2: state.SOL_2Y1 ? 1 : 0
    });
    if (state.historySamples.length > 340) {
      state.historySamples.shift();
    }
  }

  // ==================== RENDERIZADO VISUAL DEL DOM Y SVGs ====================
  function renderUI() {
    // 1. KPIs superiores
    const kpiPlant = document.getElementById('kpi-plant-state');
    const pillPlant = document.getElementById('pill-plant-state');
    const dotSim = document.getElementById('dot-sim-state');

    if (state.H3_RED) {
      kpiPlant.textContent = !state.S0_ESTOP_OK ? 'EMERGENCIA S0' : 'ALARMA ACTIVA';
      pillPlant.textContent = 'FALLA';
      pillPlant.className = 'kpi-indicator alarm';
      dotSim.className = 'dot alarm';
    } else if (state.K1_RUN) {
      kpiPlant.textContent = (state.K2_CYCLE_A || state.K3_CYCLE_B) ? 'CLASIFICANDO' : 'EN MARCHA';
      pillPlant.textContent = 'RUN';
      pillPlant.className = 'kpi-indicator on';
      dotSim.className = 'dot';
    } else {
      kpiPlant.textContent = 'DETENIDO';
      pillPlant.textContent = 'STOP';
      pillPlant.className = 'kpi-indicator';
      dotSim.className = 'dot warn';
    }

    const beltMmS = state.KM1_MOTOR ? Math.round(120 * (state.beltSpeedPercent / 100)) : 0;
    document.getElementById('kpi-motor-m1').textContent = `${beltMmS} mm/s`;
    const pillM1 = document.getElementById('pill-motor-m1');
    pillM1.textContent = state.KM1_MOTOR ? 'KM1: ON' : 'KM1: OFF';
    pillM1.className = state.KM1_MOTOR ? 'kpi-indicator on' : 'kpi-indicator';

    document.getElementById('kpi-pressure').textContent = `${state.pressureBar.toFixed(1)} bar`;
    const pillPress = document.getElementById('pill-pressure');
    pillPress.textContent = state.P1_OK ? 'P1: OK' : 'P1: BAJA';
    pillPress.className = state.P1_OK ? 'kpi-indicator on' : 'kpi-indicator alarm';

    document.getElementById('kpi-cyl-a').textContent = `${Math.round(state.cylA_mm)} mm`;
    const pillCylA = document.getElementById('pill-cyl-a');
    pillCylA.textContent = state.S_1B2 ? '1B2=1 (a1)' : (state.S_1B1 ? '1B1=1 (a0)' : 'EN CARRERA');
    pillCylA.className = state.S_1B2 ? 'kpi-indicator warn' : (state.S_1B1 ? 'kpi-indicator on' : 'kpi-indicator');

    document.getElementById('kpi-cyl-b').textContent = `${Math.round(state.cylB_mm)} mm`;
    const pillCylB = document.getElementById('pill-cyl-b');
    pillCylB.textContent = state.S_2B2 ? '2B2=1 (b1)' : (state.S_2B1 ? '2B1=1 (b0)' : 'EN CARRERA');
    pillCylB.className = state.S_2B2 ? 'kpi-indicator warn' : (state.S_2B1 ? 'kpi-indicator on' : 'kpi-indicator');

    document.getElementById('kpi-grafcet').textContent = state.grafcetStage;
    document.getElementById('kpi-counters').textContent = `${state.cntMetal} / ${state.cntPlastic} / ${state.cntReject}`;
    document.getElementById('pill-total-prod').textContent = `TOT: ${state.cntMetal + state.cntPlastic + state.cntReject}`;

    // Banner descriptivo del proceso
    const banner = document.getElementById('txt-process-banner');
    if (state.H3_RED) {
      banner.textContent = !state.S0_ESTOP_OK
        ? '🛑 PARADA DE EMERGENCIA S0 ACCIONADA — Circuito desenergizado'
        : '⚠️ ALARMA DE SISTEMA — Verifique presión neumática FRL o atasco mecánico y pulse RESET (S3)';
      banner.style.color = '#ff385c';
    } else if (!state.K1_RUN) {
      banner.textContent = 'Sistema listo en espera. Presione ▶ MARCHA (S1) para iniciar la cinta.';
      banner.style.color = '#98abc0';
    } else if (state.SOL_1Y1 || !state.S_1B1) {
      banner.textContent = '⚡ B2 detectó METAL ➔ Pausa cinta M1 ➔ Electroválvula 1Y1 activa secuencia 1A1+ / 1A1-';
      banner.style.color = '#38bdf8';
    } else if (state.SOL_2Y1 || !state.S_2B1) {
      banner.textContent = '⚡ B3 detectó PLÁSTICO ➔ Pausa cinta M1 ➔ Electroválvula 2Y1 activa secuencia 2A1+ / 2A1-';
      banner.style.color = '#fbbf24';
    } else {
      banner.textContent = '✅ Cinta transportadora M1 en marcha continua — Esperando ingreso de piezas en B1...';
      banner.style.color = '#00e599';
    }

    // 2. Gemelo Digital SVG (Planta)
    document.getElementById('belt-stripes').setAttribute('stroke-dashoffset', String(state.beltOffset));
    document.getElementById('roller-left').setAttribute('transform', `translate(18, 37) rotate(${state.rollerAngle})`);
    document.getElementById('roller-right').setAttribute('transform', `translate(542, 37) rotate(${state.rollerAngle})`);
    document.getElementById('motor-m1-body').setAttribute('stroke', state.KM1_MOTOR ? '#00e599' : '#64748b');

    // Posición de vástagos en la planta (desplazamiento vertical 0..56 px)
    const plantTravelA = (state.cylA_mm / 100) * 56;
    const plantTravelB = (state.cylB_mm / 100) * 56;
    document.getElementById('plant-piston-a').setAttribute('transform', `translate(0, ${plantTravelA.toFixed(1)})`);
    document.getElementById('plant-piston-b').setAttribute('transform', `translate(0, ${plantTravelB.toFixed(1)})`);

    // Colores de cámaras neumáticas en planta
    document.getElementById('plant-cylA-cap').setAttribute('fill', state.SOL_1Y1 ? '#0077ff' : '#1e293b');
    document.getElementById('plant-cylA-rod-cam').setAttribute('fill', state.SOL_1Y1 ? '#1e293b' : '#0284c7');
    document.getElementById('plant-cylB-cap').setAttribute('fill', state.SOL_2Y1 ? '#0077ff' : '#1e293b');
    document.getElementById('plant-cylB-rod-cam').setAttribute('fill', state.SOL_2Y1 ? '#1e293b' : '#0284c7');

    // Sensores en planta
    toggleClass('plant-sens-1b1', 'active', state.S_1B1);
    toggleClass('plant-sens-1b2', 'active', state.S_1B2);
    toggleClass('plant-sens-2b1', 'active', state.S_2B1);
    toggleClass('plant-sens-2b2', 'active', state.S_2B2);
    toggleClass('plant-sens-b1', 'active', state.B1_OPT);
    toggleClass('plant-sens-b2', 'active', state.B2_IND);
    toggleClass('plant-sens-b3', 'active', state.B3_CAP);

    document.getElementById('beam-b1').setAttribute('opacity', state.B1_OPT ? '1' : '0.35');
    document.getElementById('beam-b2').setAttribute('opacity', state.B2_IND ? '1' : '0.35');
    document.getElementById('beam-b3').setAttribute('opacity', state.B3_CAP ? '1' : '0.35');

    // Torreta Andon H1, H2, H3
    document.getElementById('lamp-h1').setAttribute('fill', state.H1_GREEN ? '#00e599' : '#1b2a22');
    document.getElementById('lamp-h2').setAttribute('fill', state.H2_YELLOW ? '#ffb703' : '#2c2517');
    document.getElementById('lamp-h3').setAttribute('fill', state.H3_RED ? '#ff385c' : '#2d161e');

    // Contadores en las tolvas SVG
    document.getElementById('svg-cnt-metal').textContent = `${state.cntMetal} pzs`;
    document.getElementById('svg-cnt-plastic').textContent = `${state.cntPlastic} pzs`;
    document.getElementById('svg-cnt-reject').textContent = `${state.cntReject} pzs`;

    // Renderizar piezas móviles sobre la cinta
    const piecesLayer = document.getElementById('pieces-layer');
    piecesLayer.innerHTML = state.pieces.map(p => {
      if (p.type === 'METAL') {
        return `<g transform="translate(${p.x.toFixed(1)}, ${p.y.toFixed(1)})">
          <circle cx="0" cy="0" r="16" fill="url(#metalPieceGrad)" stroke="#93c5fd" stroke-width="2"/>
          <circle cx="0" cy="0" r="6" fill="#1e3a8a" stroke="#bfdbfe" stroke-width="1.2"/>
          <text x="0" y="26" fill="#93c5fd" font-size="8" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">FE #${p.id}</text>
        </g>`;
      } else if (p.type === 'PLASTIC') {
        return `<g transform="translate(${p.x.toFixed(1)}, ${p.y.toFixed(1)})">
          <rect x="-15" y="-15" width="30" height="30" rx="5" fill="url(#plasticPieceGrad)" stroke="#fde68a" stroke-width="2"/>
          <circle cx="0" cy="0" r="4" fill="#78350f"/>
          <text x="0" y="26" fill="#fde68a" font-size="8" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">PL #${p.id}</text>
        </g>`;
      } else {
        return `<g transform="translate(${p.x.toFixed(1)}, ${p.y.toFixed(1)})">
          <polygon points="0,-16 15,12 -15,12" fill="#4b5563" stroke="#d1d5db" stroke-width="1.8"/>
          <text x="0" y="25" fill="#cbd5e1" font-size="8" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">DESC #${p.id}</text>
        </g>`;
      }
    }).join('');

    // 3. Simulador Electroneumático en Vivo (Esquema Neumático ISO 1219 + Eléctrico IEC 60617)
    const fsimTravelA = (state.cylA_mm / 100) * 86;
    const fsimTravelB = (state.cylB_mm / 100) * 86;
    document.getElementById('fsim-piston-a').setAttribute('transform', `translate(${fsimTravelA.toFixed(1)}, 0)`);
    document.getElementById('fsim-piston-b').setAttribute('transform', `translate(${fsimTravelB.toFixed(1)}, 0)`);

    // Cámaras de cilindros en el esquema neumático
    const cylALeftW = Math.max(6, 16 + fsimTravelA);
    const cylARightX = 44 + fsimTravelA;
    const cylARightW = Math.max(4, 94 - fsimTravelA);
    const elCylAL = document.getElementById('fsim-cylA-left');
    const elCylAR = document.getElementById('fsim-cylA-right');
    elCylAL.setAttribute('width', cylALeftW.toFixed(1));
    elCylAL.setAttribute('fill', state.SOL_1Y1 && state.P1_OK ? '#0077ff' : '#1e293b');
    elCylAL.setAttribute('opacity', state.SOL_1Y1 && state.P1_OK ? '0.65' : '0.4');
    elCylAR.setAttribute('x', cylARightX.toFixed(1));
    elCylAR.setAttribute('width', cylARightW.toFixed(1));
    elCylAR.setAttribute('fill', !state.SOL_1Y1 && state.P1_OK ? '#0077ff' : '#1e293b');

    const cylBLeftW = Math.max(6, 16 + fsimTravelB);
    const cylBRightX = 44 + fsimTravelB;
    const cylBRightW = Math.max(4, 94 - fsimTravelB);
    const elCylBL = document.getElementById('fsim-cylB-left');
    const elCylBR = document.getElementById('fsim-cylB-right');
    elCylBL.setAttribute('width', cylBLeftW.toFixed(1));
    elCylBL.setAttribute('fill', state.SOL_2Y1 && state.P1_OK ? '#0077ff' : '#1e293b');
    elCylBL.setAttribute('opacity', state.SOL_2Y1 && state.P1_OK ? '0.65' : '0.4');
    elCylBR.setAttribute('x', cylBRightX.toFixed(1));
    elCylBR.setAttribute('width', cylBRightW.toFixed(1));
    elCylBR.setAttribute('fill', !state.SOL_2Y1 && state.P1_OK ? '#0077ff' : '#1e293b');

    // Tuberías neumáticas 1A1 y 2A1
    document.getElementById('pipe-1A-4').setAttribute('class', state.SOL_1Y1 && state.P1_OK ? 'pneu-line pressurized' : 'pneu-line exhaust');
    document.getElementById('pipe-1A-2').setAttribute('class', !state.SOL_1Y1 && state.P1_OK ? 'pneu-line pressurized' : 'pneu-line exhaust');
    document.getElementById('pipe-2A-4').setAttribute('class', state.SOL_2Y1 && state.P1_OK ? 'pneu-line pressurized' : 'pneu-line exhaust');
    document.getElementById('pipe-2A-2').setAttribute('class', !state.SOL_2Y1 && state.P1_OK ? 'pneu-line pressurized' : 'pneu-line exhaust');
    document.getElementById('pipe-main-manifold').setAttribute('class', state.P1_OK ? 'pneu-line pressurized' : 'pneu-line exhaust');

    // Conmutación visual de las Válvulas 5/2 (1V1 y 2V1)
    toggleClass('fsim-sol-1y1', 'energized', state.SOL_1Y1);
    toggleClass('fsim-sol-2y1', 'energized', state.SOL_2Y1);
    document.getElementById('fsim-1v1-boxL').setAttribute('stroke', state.SOL_1Y1 ? '#00e599' : '#94a3b8');
    document.getElementById('fsim-1v1-boxL').setAttribute('fill', state.SOL_1Y1 ? '#173836' : '#162231');
    document.getElementById('fsim-1v1-boxR').setAttribute('stroke', !state.SOL_1Y1 ? '#38bdf8' : '#94a3b8');
    document.getElementById('fsim-1v1-boxR').setAttribute('fill', !state.SOL_1Y1 ? '#1e3a5f' : '#162231');

    document.getElementById('fsim-2v1-boxL').setAttribute('stroke', state.SOL_2Y1 ? '#00e599' : '#94a3b8');
    document.getElementById('fsim-2v1-boxL').setAttribute('fill', state.SOL_2Y1 ? '#173836' : '#162231');
    document.getElementById('fsim-2v1-boxR').setAttribute('stroke', !state.SOL_2Y1 ? '#38bdf8' : '#94a3b8');
    document.getElementById('fsim-2v1-boxR').setAttribute('fill', !state.SOL_2Y1 ? '#1e3a5f' : '#162231');

    const fsimBarTxt = document.getElementById('fsim-txt-bar');
    fsimBarTxt.textContent = `P1 = ${state.pressureBar.toFixed(1)} bar (${state.P1_OK ? 'OK' : 'BAJA'})`;
    fsimBarTxt.setAttribute('fill', state.P1_OK ? '#00e599' : '#ff385c');

    // Circuito Eléctrico de Mando 24V DC (Ramas 1 a 7)
    toggleClass('wire-r1', 'live', state.K1_RUN);
    toggleClass('wire-r2', 'live', state.KM1_MOTOR);
    toggleClass('wire-r3', 'live', state.SOL_1Y1);
    toggleClass('wire-r4', 'live', state.SOL_2Y1);
    toggleClass('wire-r5', 'live', state.H1_GREEN);
    toggleClass('wire-r6', 'live', state.H2_YELLOW);
    toggleClass('wire-r7', 'live', state.H3_RED);

    toggleClass('fsim-sw-s0', 'active', state.S0_ESTOP_OK);
    toggleClass('fsim-sw-s2', 'active', state.S2_STOP_OK);
    toggleClass('fsim-sw-s1', 'active', state.K1_RUN || state.S1_START);
    toggleClass('fsim-sw-p1', 'active', state.P1_OK);
    toggleClass('fsim-ct-kf-nc', 'active', !state.FAULT_ACTIVE);

    toggleClass('fsim-ct-k1-2', 'active', state.K1_RUN);
    toggleClass('fsim-ct-b1-2', 'active', state.B1_OPT || state.KB1_VALID);
    toggleClass('fsim-ct-1b1-2', 'active', state.S_1B1 && state.S_2B1);
    toggleClass('fsim-ct-k2k3-nc', 'active', !state.K2_CYCLE_A && !state.K3_CYCLE_B);

    toggleClass('fsim-ct-kb1-a', 'active', state.KB1_VALID);
    toggleClass('fsim-ct-b2', 'active', state.B2_IND || state.K2_CYCLE_A);
    toggleClass('fsim-ct-1b1', 'active', state.S_1B1);
    toggleClass('fsim-ct-1b2-nc', 'active', !state.S_1B2);

    toggleClass('fsim-ct-kb1-b', 'active', state.KB1_VALID);
    toggleClass('fsim-ct-b3', 'active', state.B3_CAP || state.K3_CYCLE_B);
    toggleClass('fsim-ct-2b1', 'active', state.S_2B1);
    toggleClass('fsim-ct-2b2-nc', 'active', !state.S_2B2);

    toggleClass('fsim-ct-h1', 'active', state.H1_GREEN);
    toggleClass('fsim-ct-h2', 'active', state.H2_YELLOW);
    toggleClass('fsim-ct-h3', 'active', state.H3_RED);
    toggleClass('fsim-sw-s3', 'active', !state.S3_RESET);

    toggleClass('fsim-coil-k1', 'energized', state.K1_RUN);
    toggleClass('fsim-coil-km1', 'energized', state.KM1_MOTOR);
    toggleClass('fsim-coil-1y1', 'energized', state.SOL_1Y1);
    toggleClass('fsim-coil-2y1', 'energized', state.SOL_2Y1);
    toggleClass('fsim-coil-h1', 'energized', state.H1_GREEN);
    toggleClass('fsim-coil-h2', 'energized', state.H2_YELLOW);
    toggleClass('fsim-coil-h3', 'energized', state.H3_RED);

    // 4. Panel de LEDs de E/S
    toggleClass('led-s0', 'on', state.S0_ESTOP_OK);
    toggleClass('led-s1', 'on', state.S1_START || state.K1_RUN);
    toggleClass('led-b1', 'on', state.B1_OPT);
    toggleClass('led-b2', 'on', state.B2_IND);
    toggleClass('led-b3', 'on', state.B3_CAP);
    toggleClass('led-p1', 'on', state.P1_OK);
    document.getElementById('txt-io-1b').textContent = `a0=${state.S_1B1 ? 1 : 0} a1=${state.S_1B2 ? 1 : 0}`;
    document.getElementById('txt-io-2b').textContent = `b0=${state.S_2B1 ? 1 : 0} b1=${state.S_2B2 ? 1 : 0}`;

    toggleClass('led-km1', 'coil-on', state.KM1_MOTOR);
    toggleClass('led-1y1', 'coil-on', state.SOL_1Y1);
    toggleClass('led-2y1', 'coil-on', state.SOL_2Y1);
    toggleClass('led-k1', 'on', state.K1_RUN);
    toggleClass('led-h1', 'on', state.H1_GREEN);
    toggleClass('led-h2', 'coil-on', state.H2_YELLOW);
    toggleClass('led-h3', 'coil-on', state.H3_RED);

    const estCycleTime = (200 / (240 * (state.flowPercent / 100) * Math.max(0.2, (state.pressureBar - 1.5) / 4.5))).toFixed(2);
    document.getElementById('txt-cycle-ms').textContent = `${estCycleTime} s`;

    // 5. Renderizar Diagrama Espacio-Fase (Canvas)
    renderStateDiagramCanvas();
  }

  function toggleClass(id, cls, cond) {
    const el = document.getElementById(id);
    if (!el) return;
    if (cond) el.classList.add(cls);
    else el.classList.remove(cls);
  }

  // ==================== DIAGRAMA ESPACIO-FASE (CRONOGRAMA EN VIVO) ====================
  function renderStateDiagramCanvas() {
    const canvas = document.getElementById('canvas-state-diagram');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;

    ctx.clearRect(0, 0, W, H);

    // Grilla de fondo estilo osciloscopio industrial
    ctx.strokeStyle = '#192636';
    ctx.lineWidth = 1;
    for (let x = 95; x < W; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 6);
      ctx.lineTo(x, H - 6);
      ctx.stroke();
    }

    const tracks = [
      { label: 'M1 Cinta (0/1)', yBase: 34, h: 18, color: '#00e599', prop: 'm1', scale: 1 },
      { label: '1A1 Metal (mm)', yBase: 86, h: 34, color: '#38bdf8', prop: 'cylA', scale: 100 },
      { label: '2A1 Plást (mm)', yBase: 142, h: 34, color: '#fbbf24', prop: 'cylB', scale: 100 }
    ];

    ctx.font = '700 10px "JetBrains Mono", monospace';
    for (const t of tracks) {
      // Línea base 0 y tope 100%
      ctx.strokeStyle = '#243548';
      ctx.beginPath();
      ctx.moveTo(95, t.yBase);
      ctx.lineTo(W - 8, t.yBase);
      ctx.moveTo(95, t.yBase - t.h);
      ctx.lineTo(W - 8, t.yBase - t.h);
      ctx.stroke();

      ctx.fillStyle = t.color;
      ctx.fillText(t.label, 8, t.yBase - t.h / 2 + 4);

      // Curva en tiempo real
      if (state.historySamples.length > 1) {
        ctx.strokeStyle = t.color;
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        const stepX = (W - 105) / 340;
        for (let i = 0; i < state.historySamples.length; i++) {
          const val = state.historySamples[i][t.prop] / t.scale;
          const x = 95 + i * stepX;
          const y = t.yBase - val * t.h;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
    }
  }

  // ==================== EVENT LISTENERS E INTERACCIÓN ====================
  function bindEvents() {
    // Pestañas de navegación
    document.querySelectorAll('.tab').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        btn.classList.add('active');
        const viewId = 'view-' + btn.getAttribute('data-view');
        const target = document.getElementById(viewId);
        if (target) target.classList.add('active');
      });
    });

    // Pulsador MARCHA (S1)
    const triggerStart = () => {
      state.S1_START = true;
      setTimeout(() => { state.S1_START = false; }, 220);
      if (state.S0_ESTOP_OK && state.P1_OK && !state.FAULT_ACTIVE) {
        state.K1_RUN = true;
        playTone(740, 0.09, 'sine', 0.08);
        logEvent('INFO', 'CMD_S1_MARCHA', 'Orden de Marcha (S1) activada. Cinta M1 habilitada y memoria K1 enclavada.');
        // Si no hay piezas en la cinta, inyectar una pieza automáticamente para demostración inmediata
        if (state.pieces.length === 0) {
          setTimeout(() => spawnPiece('METAL'), 350);
        }
      }
    };

    // Pulsador PARADA (S2)
    const triggerStop = () => {
      state.S2_STOP_OK = false;
      state.K1_RUN = false;
      state.autoFeed = false;
      document.getElementById('txt-auto-feed').textContent = 'OFF';
      setTimeout(() => { state.S2_STOP_OK = true; }, 250);
      playTone(420, 0.1, 'sine', 0.08);
      logEvent('INFO', 'CMD_S2_PARADA', 'Parada normal de proceso (S2) accionada por el operador.');
    };

    // Seta PARADA DE EMERGENCIA (S0)
    const triggerEstop = () => {
      state.S0_ESTOP_OK = !state.S0_ESTOP_OK;
      const btnEstop = document.getElementById('btn-estop');
      if (!state.S0_ESTOP_OK) {
        state.K1_RUN = false;
        state.FAULT_ACTIVE = true;
        state.autoFeed = false;
        document.getElementById('txt-auto-feed').textContent = 'OFF';
        btnEstop.classList.add('active');
        playTone(220, 0.35, 'sawtooth', 0.15);
        logEvent('ALTA', 'ALM_ESTOP_S0', 'Parada de Emergencia (S0) accionada. Corte total de energía de mando.');
      } else {
        btnEstop.classList.remove('active');
        logEvent('MEDIA', 'INFO_ESTOP_REL', 'Seta de Emergencia S0 destrabada mecánicamente. Requiere REARME (S3).');
      }
    };

    // Pulsador REARME / RESET (S3)
    const triggerReset = () => {
      state.S3_RESET = true;
      setTimeout(() => { state.S3_RESET = false; }, 220);
      state.S0_ESTOP_OK = true;
      state.cylAJammed = false;
      state.simConflictB2B3 = false;
      state.timerAvA = 0;
      state.timerRetA = 0;
      state.timerAvB = 0;
      state.timerRetB = 0;
      state.timerJamB1 = 0;
      state.timerConflictB2B3 = 0;
      if (state.pressureBar < 5.0) {
        state.pressureBar = 6.0;
        document.getElementById('slider-pressure').value = '6.0';
        document.getElementById('lbl-slider-bar').textContent = '6.0 bar';
      }
      state.P1_OK = true;
      state.FAULT_ACTIVE = false;
      document.getElementById('btn-estop').classList.remove('active');
      state.alarms.forEach(a => { a.acked = true; });
      renderAlarmsTable();
      playTone(880, 0.1, 'triangle', 0.08);
      logEvent('INFO', 'CMD_S3_RESET', 'Rearme de seguridad (S3) completado: Relé de bloqueo KF y watchdogs reseteados.');
    };

    document.getElementById('btn-start').addEventListener('click', triggerStart);
    document.getElementById('btn-stop').addEventListener('click', triggerStop);
    document.getElementById('btn-estop').addEventListener('click', triggerEstop);
    document.getElementById('btn-reset').addEventListener('click', triggerReset);

    // Click directo sobre los símbolos del plano eléctrico (S0, S1, S2, S3)
    document.getElementById('fsim-sw-s1').addEventListener('click', triggerStart);
    document.getElementById('fsim-sw-s2').addEventListener('click', triggerStop);
    document.getElementById('fsim-sw-s0').addEventListener('click', triggerEstop);
    const elS3 = document.getElementById('fsim-sw-s3');
    if (elS3) elS3.addEventListener('click', triggerReset);
    const elKf = document.getElementById('fsim-ct-kf-nc');
    if (elKf) elKf.addEventListener('click', triggerReset);

    // Inyección manual y automática de piezas
    document.getElementById('btn-spawn-metal').addEventListener('click', () => {
      if (!state.K1_RUN) triggerStart();
      spawnPiece('METAL');
    });
    document.getElementById('btn-spawn-plastic').addEventListener('click', () => {
      if (!state.K1_RUN) triggerStart();
      spawnPiece('PLASTIC');
    });
    document.getElementById('btn-spawn-reject').addEventListener('click', () => {
      if (!state.K1_RUN) triggerStart();
      spawnPiece('REJECT');
    });

    document.getElementById('btn-auto-feed').addEventListener('click', () => {
      state.autoFeed = !state.autoFeed;
      document.getElementById('txt-auto-feed').textContent = state.autoFeed ? 'ON (3.4s)' : 'OFF';
      if (state.autoFeed && !state.K1_RUN) triggerStart();
    });

    // Sliders físicos
    document.getElementById('slider-pressure').addEventListener('input', e => {
      state.pressureBar = parseFloat(e.target.value);
      document.getElementById('lbl-slider-bar').textContent = `${state.pressureBar.toFixed(1)} bar`;
    });
    document.getElementById('slider-flow').addEventListener('input', e => {
      state.flowPercent = parseInt(e.target.value, 10);
      document.getElementById('lbl-slider-flow').textContent = `${state.flowPercent} %`;
    });
    document.getElementById('slider-belt').addEventListener('input', e => {
      state.beltSpeedPercent = parseInt(e.target.value, 10);
      document.getElementById('lbl-slider-belt').textContent = `${state.beltSpeedPercent} %`;
    });

    // Audio toggle
    document.getElementById('btn-toggle-audio').addEventListener('click', () => {
      state.audioEnabled = !state.audioEnabled;
      document.getElementById('ico-audio').textContent = state.audioEnabled ? '🔊' : '🔇';
      document.getElementById('txt-audio').textContent = `Audio Neumático: ${state.audioEnabled ? 'ON' : 'OFF'}`;
    });

    // Botones de simulación de fallas en Pestaña 3
    document.getElementById('btn-fault-pressure').addEventListener('click', () => {
      state.pressureBar = 3.2;
      document.getElementById('slider-pressure').value = '3.2';
      document.getElementById('lbl-slider-bar').textContent = '3.2 bar';
      logEvent('ALTA', 'SIM_DROP_BAR', 'Simulación de rotura de manguera: Presión FRL cayó a 3.2 bar (< 5.0 bar).');
    });

    document.getElementById('btn-fault-jam').addEventListener('click', () => {
      state.cylAJammed = true;
      if (!state.K1_RUN) triggerStart();
      spawnPiece('METAL');
      logEvent('MEDIA', 'SIM_JAM_1A1', 'Falla inyectada: Obstrucción mecánica en Cilindro 1A1 al 48% (dispara Watchdog > 1.5 s).');
    });

    const btnConflict = document.getElementById('btn-fault-conflict');
    if (btnConflict) {
      btnConflict.addEventListener('click', () => {
        if (!state.K1_RUN) triggerStart();
        state.simConflictB2B3 = true;
        logEvent('MEDIA', 'SIM_CONF_B2B3', 'Simulación de conflicto simultáneo B2=1 y B3=1: Prioriza 1A1 y dispara alarma si persiste > 1.0 s.');
      });
    }

    document.getElementById('btn-fault-clear').addEventListener('click', triggerReset);

    document.getElementById('btn-ack-all').addEventListener('click', () => {
      state.alarms.forEach(a => { a.acked = true; });
      renderAlarmsTable();
    });

    document.getElementById('btn-export-csv').addEventListener('click', () => {
      const header = 'Timestamp,Prioridad,Tag,Mensaje,Estado\n';
      const rows = state.alarms.map(a => `"${a.ts}","${a.priority}","${a.tag}","${a.message}","${a.acked ? 'ACK' : 'UNACK'}"`).join('\n');
      const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'Historial_Alarmas_Clasificador_Mecatronico.csv';
      link.click();
    });
  }

  // ==================== RELOJ Y BUCLE PRINCIPAL 60 FPS ====================
  function updateClock() {
    const el = document.getElementById('clock-display');
    if (el) el.textContent = new Date().toTimeString().split(' ')[0];
  }

  let lastTime = performance.now();
  function mainLoop(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;
    stepSimulation(dt);
    renderUI();
    requestAnimationFrame(mainLoop);
  }

  window.addEventListener('DOMContentLoaded', () => {
    bindEvents();
    updateClock();
    setInterval(updateClock, 1000);
    logEvent('INFO', 'SYS_BOOT', 'Suite de Simulación Electroneumática y SCADA Mecatrónico inicializada. Presión FRL: 6.0 bar.');
    requestAnimationFrame(mainLoop);
  });
})();

