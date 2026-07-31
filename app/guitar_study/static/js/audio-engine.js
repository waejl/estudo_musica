/**
 * AudioEngine — Síntese híbrida de guitarra elétrica + acústica.
 *
 * Timbres acústicos (violao_classico, default):
 *   Karplus-Strong puro — corda vibrante que decai naturalmente.
 *
 * Timbres elétricos (les_paul_clean, crunch, drive):
 *   Fonte HÍBRIDA:
 *     1. KS curto → ataque realista do pick (primeiros ~60 ms)
 *     2. Sawtooth filtrado → sustain de guitarra com gain alto (humbucker simulado)
 *   Cadeia de efeitos:
 *     HPF → Preamp (clipagem assimétrica 12AX7) → Tone Stack → Power amp → Cabinet IR
 *
 * O cabinet IR é gerado sinteticamente via OfflineAudioContext na inicialização.
 * É ele que transforma "sawtooth distorcido" em "guitarra saindo de um Marshall 4x12".
 */
class AudioEngine {
    constructor() {
        this.ctx         = null;
        this.activeNodes = [];
        this.volume      = 0.5;

        this.samplesCache  = {};
        this.isPreloading  = false;
        this._cabinetIRs   = {};
        this._cabinetReady = {};

        this.sampleUrls = {
            1: "/guitar-study/static/audio/E4.mp3",
            2: "/guitar-study/static/audio/B3.mp3",
            3: "/guitar-study/static/audio/G3.mp3",
            4: "/guitar-study/static/audio/D3.mp3",
            5: "/guitar-study/static/audio/A2.mp3",
            6: "/guitar-study/static/audio/E2.mp3"
        };

        this.stringBaseFreqs = [
            { id: 1, freq: 329.63 },
            { id: 2, freq: 246.94 },
            { id: 3, freq: 196.00 },
            { id: 4, freq: 146.83 },
            { id: 5, freq: 110.00 },
            { id: 6, freq:  82.41 }
        ];
    }

    // -----------------------------------------------------------------------
    // Contexto de áudio
    // -----------------------------------------------------------------------
    initContext() {
        if (!this.ctx) {
            const AC = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AC();
            this.preloadSamples();
            this._warmCabinet('crunch');
            this._warmCabinet('drive');
        }
        if (this.ctx.state === 'suspended') this.ctx.resume();
    }

    async preloadSamples() {
        if (this.isPreloading) return;
        this.isPreloading = true;
        for (let n = 1; n <= 6; n++) {
            try {
                const r = await fetch(this.sampleUrls[n]);
                if (!r.ok) continue;
                const ab = await r.arrayBuffer();
                this.ctx.decodeAudioData(ab, buf => { this.samplesCache[n] = buf; });
            } catch (_) {}
        }
    }

    // -----------------------------------------------------------------------
    // Cabinet Impulse Response sintético via OfflineAudioContext
    //
    // Aproxima a resposta de frequência de um alto-falante de guitarra:
    //   - Ressonância do cone (~130-150 Hz)
    //   - Corpo de médios (700-900 Hz)
    //   - Roll-off acima de 5 kHz (limite físico do falante)
    //   - Decaimento de caixa (~50 ms)
    // -----------------------------------------------------------------------
    _warmCabinet(profile) {
        if (this._cabinetReady[profile]) return this._cabinetReady[profile];
        this._cabinetReady[profile] = this._buildCabinetIR(profile)
            .then(ir => { this._cabinetIRs[profile] = ir; });
        return this._cabinetReady[profile];
    }

    async _buildCabinetIR(profile) {
        const sr      = this.ctx.sampleRate;
        const irLen   = Math.round(0.05 * sr);
        const offline = new OfflineAudioContext(2, irLen, sr);

        const nBuf = offline.createBuffer(2, irLen, sr);
        for (let c = 0; c < 2; c++) {
            const d = nBuf.getChannelData(c);
            for (let i = 0; i < irLen; i++) {
                d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (sr * 0.006));
            }
        }
        const src = offline.createBufferSource();
        src.buffer = nBuf;

        const isDrive = profile === 'drive';

        const hpf = offline.createBiquadFilter();
        hpf.type = 'highpass';
        hpf.frequency.value = isDrive ? 100 : 80;
        hpf.Q.value = 0.9;

        const cone = offline.createBiquadFilter();
        cone.type = 'peaking';
        cone.frequency.value = isDrive ? 140 : 120;
        cone.Q.value = isDrive ? 4.5 : 3.5;
        cone.gain.value = isDrive ? 10 : 7;

        const body = offline.createBiquadFilter();
        body.type = 'peaking';
        body.frequency.value = isDrive ? 650 : 900;
        body.Q.value = 0.7;
        body.gain.value = isDrive ? 4 : 3;

        const presence = offline.createBiquadFilter();
        presence.type = 'peaking';
        presence.frequency.value = 2500;
        presence.Q.value = 1.5;
        presence.gain.value = isDrive ? -5 : 1;

        const lpf = offline.createBiquadFilter();
        lpf.type = 'lowpass';
        lpf.frequency.value = isDrive ? 4500 : 5500;
        lpf.Q.value = 0.6;

        src.connect(hpf);
        hpf.connect(cone);
        cone.connect(body);
        body.connect(presence);
        presence.connect(lpf);
        lpf.connect(offline.destination);
        src.start(0);
        return offline.startRendering();
    }

    // -----------------------------------------------------------------------
    // Curvas de distorção
    // -----------------------------------------------------------------------

    // Clipagem assimétrica de triodo 12AX7 (tanh diferente em + e −)
    _tubeClipCurve(amount) {
        const N = 16384;
        const curve = new Float32Array(N);
        for (let i = 0; i < N; i++) {
            const x = (i * 2) / (N - 1) - 1;
            if (x >= 0) {
                curve[i] =  Math.tanh(x * amount)      / Math.tanh(amount);
            } else {
                curve[i] = -Math.tanh(-x * amount * 1.2) / Math.tanh(amount * 1.2);
            }
        }
        return curve;
    }

    // Saturação suave simétrica (power amp)
    _softClipCurve(amount) {
        const N = 16384;
        const curve = new Float32Array(N);
        for (let i = 0; i < N; i++) {
            const x = (i * 2) / (N - 1) - 1;
            curve[i] = Math.tanh(x * amount) / Math.tanh(amount);
        }
        return curve;
    }

    // -----------------------------------------------------------------------
    // Karplus-Strong — corda vibrante física (usada para acústicos e ataque)
    // -----------------------------------------------------------------------
    _ksBuffer(freq, timbre) {
        const sr = this.ctx.sampleRate;
        const CFG = {
            'violao_classico':  [2.8, 0.9968, 0.85, 0.54],
            'les_paul_clean':   [1.0, 0.9985, 0.90, 0.50],
            'les_paul_crunch':  [0.5, 0.9988, 0.92, 0.48],
            'les_paul_drive':   [0.4, 0.9990, 0.95, 0.46],
            'default':          [3.5, 0.9980, 0.87, 0.50],
        };
        const [dur, damp, noiseR, alpha] = CFG[timbre] || CFG['default'];
        const N     = Math.max(2, Math.round(sr / freq));
        const total = Math.min(Math.round(dur * sr), 8 * sr);
        const buf   = this.ctx.createBuffer(1, total, sr);
        const out   = buf.getChannelData(0);
        const delay = new Float32Array(N);
        for (let i = 0; i < N; i++) {
            delay[i] = (Math.random() * 2 - 1) * noiseR
                     + Math.sin(2 * Math.PI * i / N) * (1 - noiseR);
        }
        let ptr = 0;
        for (let i = 0; i < total; i++) {
            const curr = delay[ptr];
            const prev = delay[(ptr + N - 1) % N];
            out[i]     = curr;
            delay[ptr] = damp * ((1 - alpha) * curr + alpha * prev);
            ptr        = (ptr + 1) % N;
        }
        return buf;
    }

    // -----------------------------------------------------------------------
    // Fonte HÍBRIDA para guitarra elétrica
    //
    // O que a torna realista:
    //   1. KS curto:  fornece o transiente de pick — os primeiros 30-80 ms onde
    //      o som "nasce" com o caráter percussivo real de uma corda.
    //   2. Sawtooth filtrado: simula a saída de um humbucker (pickup) sob ganho
    //      alto — sinal periódico, sustain contínuo, rico em harmônicos para distorção.
    //      O LP antes da distorção replica o roll-off do próprio pickup (~1-2 kHz).
    //   3. Crossfade: KS decai enquanto o sawtooth cresce → transição imperceptível.
    //
    // Retorna { outputNode, stopNodes }
    // -----------------------------------------------------------------------
    _hybridSource(freq, timbre, now) {
        const ctx     = this.ctx;
        const isDrive = timbre === 'les_paul_drive';

        const output = ctx.createGain();
        output.gain.value = 1.0;

        // --- 1. KS: ataque do pick ---
        const ksNode = ctx.createBufferSource();
        ksNode.buffer = this._ksBuffer(freq, timbre);

        const ksEnv = ctx.createGain();
        ksEnv.gain.setValueAtTime(1.0, now);
        // KS faz crossfade para zero em ~60-100ms
        ksEnv.gain.setTargetAtTime(0, now + 0.01, isDrive ? 0.025 : 0.04);

        ksNode.connect(ksEnv);
        ksEnv.connect(output);
        ksNode.start(now);

        // --- 2. Sawtooth: sustain (humbucker simulado) ---

        // Oscilador principal
        const saw1 = ctx.createOscillator();
        saw1.type           = 'sawtooth';
        saw1.frequency.value = freq;

        // Segundo oscilador levemente desafinado (+4 cents) — natural de cordas duplas
        const saw2 = ctx.createOscillator();
        saw2.type           = 'sawtooth';
        saw2.frequency.value = freq * 1.0023;

        // Mistura 50/50 dos dois saws
        const mixGain1 = ctx.createGain();
        mixGain1.gain.value = 0.5;
        const mixGain2 = ctx.createGain();
        mixGain2.gain.value = 0.5;

        // Filtro passa-baixa simulando o roll-off do humbucker
        // Humbuckers têm pico de ressonância em ~3-5 kHz mas caem abaixo do single coil
        const pickupLP = ctx.createBiquadFilter();
        pickupLP.type            = 'lowpass';
        pickupLP.frequency.value = isDrive ? 1200 : 1800;
        pickupLP.Q.value         = 1.5;

        // Pico de ressonância do humbucker (~700-900 Hz)
        const pickupRes = ctx.createBiquadFilter();
        pickupRes.type            = 'peaking';
        pickupRes.frequency.value = isDrive ? 700 : 950;
        pickupRes.Q.value         = 2.5;
        pickupRes.gain.value      = 5;

        // Envelope do sustain: entra enquanto KS sai
        const sawEnv = ctx.createGain();
        sawEnv.gain.setValueAtTime(0, now);
        sawEnv.gain.linearRampToValueAtTime(isDrive ? 0.75 : 0.6, now + 0.07);

        saw1.connect(mixGain1);
        saw2.connect(mixGain2);
        mixGain1.connect(pickupRes);
        mixGain2.connect(pickupRes);
        pickupRes.connect(pickupLP);
        pickupLP.connect(sawEnv);
        sawEnv.connect(output);

        saw1.start(now);
        saw2.start(now);

        return { outputNode: output, stopNodes: [ksNode, saw1, saw2] };
    }

    // -----------------------------------------------------------------------
    // Seleção de amostra MP3
    // -----------------------------------------------------------------------
    _bestSample(freq) {
        let best = null, bestFreq = 0;
        for (const item of this.stringBaseFreqs) {
            if (this.samplesCache[item.id] && freq >= item.freq * 0.88 && item.freq > bestFreq) {
                best = { buffer: this.samplesCache[item.id], baseFreq: item.freq };
                bestFreq = item.freq;
            }
        }
        if (!best) {
            for (let n = 6; n >= 1; n--) {
                if (this.samplesCache[n]) {
                    best = { buffer: this.samplesCache[n], baseFreq: this.stringBaseFreqs[n - 1].freq };
                    break;
                }
            }
        }
        return best;
    }

    // -----------------------------------------------------------------------
    // playFreq — reproduz uma frequência com a cadeia correta por timbre
    // -----------------------------------------------------------------------
    playFreq(freq, duration = 1.8, delay = 0) {
        if (!freq || freq <= 0) return;
        this.initContext();

        const now    = this.ctx.currentTime + delay;
        const timbre = localStorage.getItem("guitarTimbre") || "default";
        const ctx    = this.ctx;

        // Envelope de amplitude master
        const gainNode = ctx.createGain();
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(this.volume * 0.85, now + 0.005);
        gainNode.gain.setTargetAtTime(0, now + duration * 0.6, duration * 0.28);

        let stopNodes = [];

        if (timbre === 'les_paul_crunch' || timbre === 'les_paul_drive') {
            // Fonte híbrida KS + sawtooth para elétrica com ganho
            const hybrid = this._hybridSource(freq, timbre, now);
            stopNodes = hybrid.stopNodes;
            this._buildElectricChain(timbre, hybrid.outputNode, gainNode, now);

        } else {
            // Fonte única: amostra MP3 ou KS puro
            const sample = this._bestSample(freq);
            let srcNode;
            if (sample) {
                srcNode = ctx.createBufferSource();
                srcNode.buffer = sample.buffer;
                srcNode.playbackRate.setValueAtTime(freq / sample.baseFreq, now);
            } else {
                srcNode = ctx.createBufferSource();
                srcNode.buffer = this._ksBuffer(freq, timbre);
            }
            srcNode.start(now);
            stopNodes = [srcNode];
            this._buildAcousticChain(timbre, srcNode, gainNode, now);
        }

        gainNode.connect(ctx.destination);

        const nodeRef = { gainNode, stopNodes };
        this.activeNodes.push(nodeRef);
        setTimeout(() => {
            const i = this.activeNodes.indexOf(nodeRef);
            if (i > -1) this.activeNodes.splice(i, 1);
        }, (delay + duration + 2) * 1000);
    }

    // -----------------------------------------------------------------------
    // Cadeia de sinal para elétrica com distorção
    // Fonte → HPF → Pre-gain → Preamp clip → Tone Stack → Power clip → Cabinet IR → Gain
    // -----------------------------------------------------------------------
    _buildElectricChain(timbre, inputNode, gainNode, now) {
        const ctx     = this.ctx;
        const isDrive = timbre === 'les_paul_drive';

        // 1. HPF — corta sub-graves abaixo da faixa do pickup
        const hpf = ctx.createBiquadFilter();
        hpf.type            = 'highpass';
        hpf.frequency.value = isDrive ? 100 : 80;
        hpf.Q.value         = 0.7;

        // 2. Pre-gain — sobe o nível antes da clipagem (gain knob do amp)
        const preGain = ctx.createGain();
        preGain.gain.value  = isDrive ? 5.0 : 3.0;

        // 3. Preamp (12AX7) — clipagem assimétrica, estágio 1
        const preamp = ctx.createWaveShaper();
        preamp.curve        = this._tubeClipCurve(isDrive ? 10 : 6);
        preamp.oversample   = '4x';

        // 4. Tone stack (Bass / Mid / Treble estilo Marshall)
        const bass = ctx.createBiquadFilter();
        bass.type            = 'lowshelf';
        bass.frequency.value = 250;
        bass.gain.value      = isDrive ? -4 : -2;   // corte de graves evita mud

        const mid = ctx.createBiquadFilter();
        mid.type             = 'peaking';
        mid.frequency.value  = isDrive ? 750 : 1000;
        mid.Q.value          = 0.9;
        mid.gain.value       = isDrive ? 4 : 5;

        const treble = ctx.createBiquadFilter();
        treble.type           = 'highshelf';
        treble.frequency.value = 3500;
        treble.gain.value     = isDrive ? -5 : 0;

        // 5. Power amp — saturação suave simétrica (válvulas de potência)
        const powerAmp = ctx.createWaveShaper();
        powerAmp.curve      = this._softClipCurve(isDrive ? 4 : 2.5);
        powerAmp.oversample = '4x';

        // 6. Cabinet IR — o que faz soar como uma caixa de guitarra de verdade
        const convolver = ctx.createConvolver();
        const ir = this._cabinetIRs[isDrive ? 'drive' : 'crunch'];
        if (ir) convolver.buffer = ir;

        // 7. Make-up gain (convolver reduz volume)
        const makeup = ctx.createGain();
        makeup.gain.value = isDrive ? 4.0 : 3.0;

        inputNode.connect(hpf);
        hpf.connect(preGain);
        preGain.connect(preamp);
        preamp.connect(bass);
        bass.connect(mid);
        mid.connect(treble);
        treble.connect(powerAmp);
        powerAmp.connect(convolver);
        convolver.connect(makeup);
        makeup.connect(gainNode);
    }

    // -----------------------------------------------------------------------
    // Cadeia de sinal para acústico e clean
    // -----------------------------------------------------------------------
    _buildAcousticChain(timbre, inputNode, gainNode, now) {
        const ctx = this.ctx;

        if (timbre === 'violao_classico') {
            const body = ctx.createBiquadFilter();
            body.type            = 'peaking';
            body.frequency.value = 250;
            body.Q.value         = 1.2;
            body.gain.value      = 5;

            const warmLP = ctx.createBiquadFilter();
            warmLP.type            = 'lowpass';
            warmLP.frequency.value = 1000;
            warmLP.frequency.exponentialRampToValueAtTime(300, now + 2.5);
            warmLP.Q.value         = 0.7;

            inputNode.connect(body);
            body.connect(warmLP);
            warmLP.connect(gainNode);

        } else if (timbre === 'les_paul_clean') {
            const presence = ctx.createBiquadFilter();
            presence.type            = 'peaking';
            presence.frequency.value = 2000;
            presence.Q.value         = 0.9;
            presence.gain.value      = 3;

            const lpf = ctx.createBiquadFilter();
            lpf.type            = 'lowpass';
            lpf.frequency.value = 7000;

            inputNode.connect(presence);
            presence.connect(lpf);
            lpf.connect(gainNode);

        } else {
            inputNode.connect(gainNode);
        }
    }

    // -----------------------------------------------------------------------
    // API pública
    // -----------------------------------------------------------------------
    playNote(freq) { this.playFreq(freq, 1.8, 0); }

    playChord(freqs) {
        if (!freqs?.length) return;
        this.stop();
        freqs.forEach((freq, idx) => {
            if (freq > 0) this.playFreq(freq, 2.2, idx * 0.05);
        });
    }

    playScale(freqs, speedMs = 500, ascending = true) {
        if (!freqs?.length) return;
        this.stop();
        const list = ascending ? [...freqs] : [...freqs].reverse();
        list.forEach((freq, idx) => {
            if (freq > 0) this.playFreq(freq, 1.2, (idx * speedMs) / 1000);
        });
    }

    stop() {
        const now = this.ctx?.currentTime || 0;
        this.activeNodes.forEach(node => {
            try { node.gainNode?.gain.setTargetAtTime(0, now, 0.01); } catch (_) {}
            (node.stopNodes || []).forEach(n => {
                try { n.stop(now + 0.05); } catch (_) {}
            });
        });
        this.activeNodes = [];
    }

    setVolume(val) { this.volume = Math.max(0, Math.min(1, val)); }

    // -----------------------------------------------------------------------
    // SINTETIZADORES DE BATERIA E BAIXO EM TEMPO REAL (BACKING BAND)
    // -----------------------------------------------------------------------

    _synthesizeKick(time) {
        const ctx = this.ctx;
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(150, time);
        osc.frequency.exponentialRampToValueAtTime(0.01, time + 0.1);
        
        gain.gain.setValueAtTime(0.8 * this.volume, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.12);
        
        osc.start(time);
        osc.stop(time + 0.15);
    }

    _synthesizeSnare(time) {
        const ctx = this.ctx;
        if (!ctx) return;
        
        const bufferSize = ctx.sampleRate * 0.12; // 120ms
        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const noise = ctx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = ctx.createBiquadFilter();
        filter.type = "bandpass";
        filter.frequency.value = 1000;
        
        const gain = ctx.createGain();
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(ctx.destination);
        
        gain.gain.setValueAtTime(0.4 * this.volume, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.12);
        
        noise.start(time);
        noise.stop(time + 0.15);
    }

    _synthesizeHiHat(time) {
        const ctx = this.ctx;
        if (!ctx) return;
        
        const bufferSize = ctx.sampleRate * 0.03; // 30ms
        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const noise = ctx.createBufferSource();
        noise.buffer = buffer;
        
        const filter = ctx.createBiquadFilter();
        filter.type = "highpass";
        filter.frequency.value = 8000;
        
        const gain = ctx.createGain();
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(ctx.destination);
        
        gain.gain.setValueAtTime(0.2 * this.volume, time);
        gain.gain.exponentialRampToValueAtTime(0.01, time + 0.03);
        
        noise.start(time);
        noise.stop(time + 0.04);
    }

    _synthesizeBass(freq, time, duration) {
        const ctx = this.ctx;
        if (!ctx) return;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const filter = ctx.createBiquadFilter();
        
        osc.type = "triangle";
        
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(ctx.destination);
        
        filter.type = "lowpass";
        filter.frequency.setValueAtTime(250, time);
        
        osc.frequency.setValueAtTime(freq, time);
        
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(0.6 * this.volume, time + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.01, time + duration - 0.02);
        
        osc.start(time);
        osc.stop(time + duration);
    }

    startBackingBand(style, bpm, getActiveChordFn) {
        this.initContext();
        this.stopBackingBand();
        
        this.backingBandActive = true;
        
        // Frequências para o Baixo (Oitava grave)
        const BASS_FREQS = {
            "C": 65.41, "C#": 69.30, "Db": 69.30, "D": 73.42, "D#": 77.78, "Eb": 77.78,
            "E": 82.41, "F": 87.31, "F#": 92.50, "Gb": 92.50, "G": 98.00, "G#": 103.83,
            "Ab": 103.83, "A": 55.00, "A#": 58.27, "Bb": 58.27, "B": 61.74
        };

        const beatDuration = 60 / bpm; // Duração de uma batida em segundos
        let step = 0; // Passo atual (em colcheias, loop de 8 passos)
        const stepDuration = beatDuration / 2; // Colcheia

        this.backingBandInterval = setInterval(() => {
            const now = this.ctx.currentTime;
            
            // Obtém o acorde ativo via callback dinâmico
            const activeChord = getActiveChordFn ? getActiveChordFn() : { note: "C", type: "Major" };
            const bassFreq = BASS_FREQS[activeChord.note] || 65.41;
            
            // Agenda as notas com 50ms de antecipação (para evitar jitter)
            const schedTime = now + 0.05;

            if (style === "rock") {
                // Estilo Rock 4/4 (8 passos de colcheia por compasso)
                if (step === 0 || step === 4) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 2 || step === 6) {
                    this._synthesizeSnare(schedTime);
                }
                this._synthesizeHiHat(schedTime);
                
                if (step % 2 === 0) {
                    this._synthesizeBass(bassFreq, schedTime, beatDuration - 0.05);
                }
            } 
            else if (style === "hard_rock") {
                // Estilo Hard Rock de Arena (Guns N' Roses / AC/DC)
                if (step === 0 || step === 4 || step === 5) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 2 || step === 6) {
                    this._synthesizeSnare(schedTime);
                }
                this._synthesizeHiHat(schedTime);
                
                // Baixo pulsante e firme na tônica
                this._synthesizeBass(bassFreq, schedTime, stepDuration - 0.02);
            }
            else if (style === "ballad") {
                // Estilo Balada Lenta Romântica (Bed of Roses)
                if (step === 0 || step === 3) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 4) {
                    this._synthesizeSnare(schedTime);
                }
                if (step % 2 === 0) {
                    this._synthesizeHiHat(schedTime);
                }
                // Baixo mais espaçado com notas longas
                if (step % 4 === 0) {
                    this._synthesizeBass(bassFreq, schedTime, beatDuration * 2 - 0.1);
                }
            }
            else if (style === "rock_n_roll") {
                // Estilo Rock 'n' Roll Clássico dos Anos 50 (Boogie Woogie / Chuck Berry)
                const thirdFactor = activeChord.type === "Major" ? 1.2599 : 1.1892;
                const fifthFactor = 1.4983;
                const sixthFactor = 1.6818; // Sexta maior clássica do Boogie Woogie
                
                const boogieBassPattern = [
                    bassFreq,
                    bassFreq * thirdFactor,
                    bassFreq * fifthFactor,
                    bassFreq * sixthFactor
                ];
                
                if (step % 2 === 0) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 2 || step === 6) {
                    this._synthesizeSnare(schedTime);
                }
                this._synthesizeHiHat(schedTime);
                
                if (step % 2 === 0) {
                    const walkIdx = Math.floor(step / 2) % 4;
                    this._synthesizeBass(boogieBassPattern[walkIdx], schedTime, beatDuration - 0.05);
                }
            }
            else if (style === "reggae") {
                // Estilo Reggae
                this._synthesizeHiHat(schedTime);
                
                if (step === 4) {
                    this._synthesizeKick(schedTime);
                    this._synthesizeSnare(schedTime);
                }
                if (step === 0 || step === 2 || step === 5) {
                    this._synthesizeBass(bassFreq, schedTime, stepDuration - 0.02);
                }
            }
            else if (style === "blues") {
                // Estilo Blues Shuffle (Walking Bass dinâmico sem erros de sintaxe)
                const thirdFactor = activeChord.type === "Major" ? 1.2599 : 1.1892;
                const fifthFactor = 1.4983;
                const sixthFactor = 1.6818; // Sexta maior para caminhada clássica
                
                const walkingBassPattern = [
                    bassFreq,
                    bassFreq * thirdFactor,
                    bassFreq * fifthFactor,
                    bassFreq * sixthFactor
                ];
                
                if (step % 2 === 0) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 2 || step === 6) {
                    this._synthesizeSnare(schedTime);
                }
                if (step % 2 === 0 || step % 4 === 1) {
                    this._synthesizeHiHat(schedTime);
                }
                if (step % 2 === 0) {
                    const walkIdx = Math.floor(step / 2) % 4;
                    this._synthesizeBass(walkingBassPattern[walkIdx], schedTime, beatDuration - 0.05);
                }
            }
            else if (style === "baiao") {
                // Estilo Baião 2/4 (4 colcheias por compasso)
                if (step === 0 || step === 2 || step === 3) {
                    this._synthesizeKick(schedTime);
                }
                if (step === 1 || step === 3) {
                    this._synthesizeHiHat(schedTime);
                }
                if (step === 0 || step === 2) {
                    this._synthesizeBass(bassFreq, schedTime, stepDuration - 0.02);
                }
            }
            
            // Avança o passo (loop de 8 passos)
            step = (step + 1) % 8;
            
        }, stepDuration * 1000);
    }

    stopBackingBand() {
        if (this.backingBandInterval) {
            clearInterval(this.backingBandInterval);
            this.backingBandInterval = null;
        }
        this.backingBandActive = false;
    }
}

export const audioEngine = new AudioEngine();
