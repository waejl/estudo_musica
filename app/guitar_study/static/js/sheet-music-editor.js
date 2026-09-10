import { Fretboard } from './fretboard.js';
import { audioEngine } from './audio-engine.js'; // Importação explícita e direta do motor de áudio

document.addEventListener('DOMContentLoaded', () => {
    console.log('[DEBUG] DOMContentLoaded - Editor HTML5 Polifônico de Precisão Estrita Iniciado.');

    // --- DOM Elements ---
    const scoreContainer = document.getElementById('sheet-music-container');
    const gridContainer = document.getElementById('pauta-html-grid');
    const timeSignatureSelect = document.getElementById('time-signature-select');
    const noteButtons = document.querySelectorAll('#add-note-buttons button');
    const restButtons = document.querySelectorAll('#add-rest-buttons button');
    const accidentalButtons = document.querySelectorAll('#accidental-buttons button');
    const clearScoreBtn = document.getElementById('clear-score-btn');
    const saveScoreBtn = document.getElementById('save-score-btn');
    const savedScoresList = document.getElementById('saved-scores-list');
    const currentScoreIdInput = document.getElementById('current-score-id');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const bpmInput = document.getElementById('bpm-input');
    const metronomeIndicator = document.getElementById('metronome-indicator');
    const hoverNoteDisplay = document.getElementById('hover-note-display');

    // --- State ---
    let scoreElements = []; // Armazena { treble: { noteName, octave, vexflowNote, freq, isRest }, bass: { noteName, octave, vexflowNote, freq, isRest }, duration, beats }
    let selectedDuration = 'q';
    let selectedType = 'note';
    let selectedAccidental = 'none'; // 'none', 'sharp', 'flat'
    let isPlaying = false;
    let playbackTimeoutId = null;

    // Muda o cursor do mouse para "crosshair" (uma cruz fina +) para dar precisão de mira
    scoreContainer.style.cursor = 'crosshair';

    // --- Célula de Guia Visual Flutuante do Mouse (Hover Guide) ---
    const hoverGuide = document.createElement('div');
    hoverGuide.id = 'score-hover-guide';
    hoverGuide.style.position = 'absolute';
    hoverGuide.style.height = '2px';
    hoverGuide.style.backgroundColor = 'rgba(220, 53, 69, 0.5)'; // Linha guia vermelha
    hoverGuide.style.pointerEvents = 'none';
    hoverGuide.style.display = 'none';
    hoverGuide.style.left = '40px';
    hoverGuide.style.right = '20px';
    scoreContainer.appendChild(hoverGuide);

    const hoverBadge = document.createElement('span');
    hoverBadge.className = 'badge bg-danger fs-9 font-monospace shadow-sm';
    hoverBadge.style.position = 'absolute';
    hoverBadge.style.pointerEvents = 'none';
    hoverBadge.style.display = 'none';
    hoverBadge.style.zIndex = '100';
    scoreContainer.appendChild(hoverBadge);

    // Mapeamento de durações para tempos (em compasso de 4/4)
    const durationBeatsMap = { 'w': 4, 'h': 2, 'q': 1, '8': 0.5, '16': 0.25 };

    // --- Escala Diatônica de Degraus de Sol e Fá (De Cima para Baixo) ---
    const trebleDiatonicScale = [
        { note: 'G', octave: 5, isLine: false, isLedger: false }, 
        { note: 'F', octave: 5, isLine: true, isLedger: false },  // Linha 1 (topo)
        { note: 'E', octave: 5, isLine: false, isLedger: false }, 
        { note: 'D', octave: 5, isLine: true, isLedger: false },  // Linha 2
        { note: 'C', octave: 5, isLine: false, isLedger: false }, 
        { note: 'B', octave: 4, isLine: true, isLedger: false },  // Linha 3 (meio)
        { note: 'A', octave: 4, isLine: false, isLedger: false }, 
        { note: 'G', octave: 4, isLine: true, isLedger: false },  // Linha 4
        { note: 'F', octave: 4, isLine: false, isLedger: false }, 
        { note: 'E', octave: 4, isLine: true, isLedger: false },  // Linha 5 (base)
        { note: 'D', octave: 4, isLine: false, isLedger: false }, 
        { note: 'C', octave: 4, isLine: false, isLedger: true },  // Dó Central (LINHA SUPLEMENTAR)
        { note: 'B', octave: 3, isLine: false, isLedger: false }  
    ];

    const bassDiatonicScale = [
        { note: 'B', octave: 3, isLine: false, isLedger: false }, 
        { note: 'A', octave: 3, isLine: true, isLedger: false },  // Linha 1 (topo)
        { note: 'G', octave: 3, isLine: false, isLedger: false }, 
        { note: 'F', octave: 3, isLine: true, isLedger: false },  // Linha 2
        { note: 'E', octave: 3, isLine: false, isLedger: false }, 
        { note: 'D', octave: 3, isLine: true, isLedger: false },  // Linha 3 (meio)
        { note: 'C', octave: 3, isLine: false, isLedger: false }, 
        { note: 'B', octave: 2, isLine: true, isLedger: false },  // Linha 4
        { note: 'A', octave: 2, isLine: false, isLedger: false }, 
        { note: 'G', octave: 2, isLine: true, isLedger: false },  // Linha 5 (base)
        { note: 'F', octave: 2, isLine: false, isLedger: false }, 
        { note: 'E', octave: 2, isLine: false, isLedger: true },  // Mi Grave (LINHA SUPLEMENTAR)
        { note: 'D', octave: 2, isLine: false, isLedger: false }, 
        { note: 'C', octave: 2, isLine: false, isLedger: true }   // Dó grave (LINHA SUPLEMENTAR)
    ];

    // --- Mapeamento Didático de Digitação Recomendada na Guitarra (Primeira Posição Aberta) ---
    const guitarOpenPositionMap = {
        // Clave de Fá (Notas Graves / Médias graves)
        'e/2': { string: 6, fret: 0 },  // 6ª corda solta (Mi grave)
        'f/2': { string: 6, fret: 1 },  // 6ª corda casa 1
        'g/2': { string: 6, fret: 3 },  // 6ª corda casa 3
        'a/2': { string: 5, fret: 0 },  // 5ª corda solta
        'b/2': { string: 5, fret: 2 },  // 5ª corda casa 2
        'c/3': { string: 5, fret: 3 },  // 5ª corda casa 3 (Dó grave)
        'd/3': { string: 4, fret: 0 },  // 4ª corda solta
        'e/3': { string: 4, fret: 2 },  // 4ª corda casa 2
        'f/3': { string: 4, fret: 3 },  // 4ª corda casa 3
        'g/3': { string: 3, fret: 0 },  // 3ª corda solta
        'a/3': { string: 3, fret: 2 },  // 3ª corda casa 2
        'b/3': { string: 2, fret: 0 },  // 2ª corda solta

        // Clave de Sol (Notas Médias / Agudas)
        'c/4': { string: 2, fret: 1 },  // 2ª corda casa 1 (Dó Central!)
        'd/4': { string: 2, fret: 3 },  // 2ª corda casa 3 (Ré 4)
        'e/4': { string: 1, fret: 0 },  // 1ª corda solta (Mi agudo)
        'f/4': { string: 1, fret: 1 },  // 1ª corda casa 1
        'g/4': { string: 1, fret: 3 },  // 1ª corda casa 3
        'a/4': { string: 1, fret: 5 },  // 1ª corda casa 5
        'b/4': { string: 1, fret: 7 },  // 1ª corda casa 7
        'c/5': { string: 1, fret: 8 },  // 1ª corda casa 8
        'd/5': { string: 1, fret: 10 }, // 1ª corda casa 10
        'e/5': { string: 1, fret: 12 }, // 1ª corda casa 12
        'f/5': { string: 1, fret: 13 }, // 1ª corda casa 13
        'g/5': { string: 1, fret: 15 }  // 1ª corda casa 15
    };

    // --- Inicialização da Grade de Escrita (4 compassos de 4/4 = 16 tempos de pausas) ---
    function initializeGrid(numMeasures = 4) {
        scoreElements = [];
        const beatsPerMeasure = parseInt(timeSignatureSelect.value.split('/')[0]) || 4;
        const totalBeats = numMeasures * beatsPerMeasure;
        
        for (let i = 0; i < totalBeats; i++) {
            scoreElements.push({
                treble: { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true },
                bass: { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true },
                duration: 'q',
                beats: 1
            });
        }
    }

    // Adiciona um compasso de pausas no final para expandir a música de forma dinâmica
    function addMeasureToGrid() {
        const beatsPerMeasure = parseInt(timeSignatureSelect.value.split('/')[0]) || 4;
        for (let i = 0; i < beatsPerMeasure; i++) {
            scoreElements.push({
                treble: { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true },
                bass: { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true },
                duration: 'q',
                beats: 1
            });
        }
    }

    // --- Renderizador Dinâmico da Pauta HTML5 ---
    function renderPautaDOM(highlightNoteIndex = -1) {
        gridContainer.innerHTML = '';
        const beatsPerMeasure = parseInt(timeSignatureSelect.value.split('/')[0]) || 4;

        scoreElements.forEach((el, colIdx) => {
            // Cria a coluna do tempo/batida
            const colDiv = document.createElement('div');
            colDiv.className = 'pauta-coluna';
            colDiv.dataset.col = colIdx;

            // Se for o final de um compasso, adiciona a linha de compasso vertical '|'
            if ((colIdx + 1) % beatsPerMeasure === 0) {
                colDiv.classList.add('fim-compasso');
            }

            // Destaca a coluna inteira durante o playback
            if (colIdx === highlightNoteIndex) {
                colDiv.style.backgroundColor = 'rgba(25, 135, 84, 0.08)';
            }

            // --- Pauta Superior (Clave de Sol) ---
            const solDiv = document.createElement('div');
            solDiv.className = 'pauta-sistema-sol';
            trebleDiatonicScale.forEach((note, degIdx) => {
                const degDiv = document.createElement('div');
                degDiv.className = 'pauta-degrau';
                
                if (note.isLine) degDiv.classList.add('pauta-linha');
                if (note.isLedger) degDiv.classList.add('suplementar'); 
                
                degDiv.dataset.col = colIdx;
                degDiv.dataset.deg = degIdx;
                degDiv.dataset.clef = 'treble';
                degDiv.dataset.note = note.note;
                degDiv.dataset.octave = note.octave;

                // Desenha a nota real elíptica se estiver ativa neste degrau
                if (!el.treble.isRest && el.treble.noteName && el.treble.noteName.startsWith(note.note) && el.treble.octave === note.octave) {
                    const notaReal = document.createElement('div');
                    notaReal.className = 'nota-musica-real';
                    notaReal.setAttribute('data-duration', el.duration);
                    
                    // Se a nota tiver alteração (sustenido/bemol)
                    if (el.treble.noteName.includes('#') || el.treble.noteName.includes('b')) {
                        const acidenteSpan = document.createElement('span');
                        acidenteSpan.className = 'acidente-visual-pauta';
                        acidenteSpan.textContent = el.treble.noteName.includes('#') ? '♯' : '♭';
                        notaReal.appendChild(acidenteSpan);
                    }
                    degDiv.appendChild(notaReal);
                }

                registerDegrauEvents(degDiv);
                solDiv.appendChild(degDiv);
            });

            // --- Espaço Divisor do Meio (Só mostra pausa se ambas as claves forem silêncio naquele tempo) ---
            const divisorDiv = document.createElement('div');
            divisorDiv.className = 'pauta-divisor-espaco d-flex align-items-center justify-content-center';
            
            const isColumnRest = el.treble.isRest && el.bass.isRest;
            if (isColumnRest) {
                const restSpan = document.createElement('span');
                restSpan.className = 'text-muted fs-4 fw-bold';
                restSpan.style.userSelect = 'none';
                restSpan.textContent = '𝄾'; 
                divisorDiv.appendChild(restSpan);
            }
            colDiv.appendChild(solDiv);
            colDiv.appendChild(divisorDiv);

            // --- Pauta Inferior (Clave de Fá) ---
            const faDiv = document.createElement('div');
            faDiv.className = 'pauta-sistema-fa';
            bassDiatonicScale.forEach((note, degIdx) => {
                const degDiv = document.createElement('div');
                degDiv.className = 'pauta-degrau';
                
                if (note.isLine) degDiv.classList.add('pauta-linha');
                if (note.isLedger) degDiv.classList.add('suplementar'); 
                
                degDiv.dataset.col = colIdx;
                degDiv.dataset.deg = degIdx;
                degDiv.dataset.clef = 'bass';
                degDiv.dataset.note = note.note;
                degDiv.dataset.octave = note.octave;

                // Desenha a nota real elíptica com o atributo data-duration
                if (!el.bass.isRest && el.bass.noteName && el.bass.noteName.startsWith(note.note) && el.bass.octave === note.octave) {
                    const notaReal = document.createElement('div');
                    notaReal.className = 'nota-musica-real';
                    notaReal.setAttribute('data-duration', el.duration);
                    
                    // Desenha acidente
                    if (el.bass.noteName.includes('#') || el.bass.noteName.includes('b')) {
                        const acidenteSpan = document.createElement('span');
                        acidenteSpan.className = 'acidente-visual-pauta';
                        acidenteSpan.textContent = el.bass.noteName.includes('#') ? '♯' : '♭';
                        notaReal.appendChild(acidenteSpan);
                    }
                    degDiv.appendChild(notaReal);
                }

                registerDegrauEvents(degDiv);
                faDiv.appendChild(degDiv);
            });

            colDiv.appendChild(faDiv);
            gridContainer.appendChild(colDiv);
        });
    }

    // --- Eventos de Hover e Clique nos Degraus HTML5 ---
    function registerDegrauEvents(degDiv) {
        degDiv.addEventListener('mousemove', (e) => {
            if (isPlaying) return;
            const note = degDiv.dataset.note;
            const octave = degDiv.dataset.octave;
            const clef = degDiv.dataset.clef === 'treble' ? 'Sol' : 'Fá';
            
            // Exibe alteração na mira
            let finalNote = note;
            if (selectedAccidental === 'sharp') finalNote += '♯';
            if (selectedAccidental === 'flat') finalNote += '♭';
            
            hoverNoteDisplay.textContent = `Mira: ${finalNote}${octave} (${clef})`;
        });

        degDiv.addEventListener('mouseleave', () => {
            hoverNoteDisplay.textContent = `Mira: --`;
        });

        degDiv.addEventListener('click', () => {
            if (isPlaying) return;

            const colIdx = parseInt(degDiv.dataset.col);
            const baseNote = degDiv.dataset.note;
            const octave = parseInt(degDiv.dataset.octave);
            const clef = degDiv.dataset.clef;

            const beats = durationBeatsMap[selectedDuration] || 1;

            if (selectedType === 'rest') {
                // Remove a nota de Sol ou Fá dependendo de qual pauta clicou
                if (clef === 'treble') {
                    scoreElements[colIdx].treble = { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true };
                } else {
                    scoreElements[colIdx].bass = { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true };
                }
                scoreElements[colIdx].duration = selectedDuration;
                scoreElements[colIdx].beats = beats;
                
                highlightActiveMelody(null);
            } else {
                // Aplica acidentes (Sustenido ou Bemol) ao nome da nota
                let noteName = baseNote;
                if (selectedAccidental === 'sharp') noteName += '#';
                if (selectedAccidental === 'flat') noteName += 'b';

                const vexflowNote = `${noteName.toLowerCase()}/${octave}`;
                const freq = getFrequencyOfNote(noteName, octave);

                if (clef === 'treble') {
                    scoreElements[colIdx].treble = {
                        noteName: noteName,
                        octave: octave,
                        vexflowNote: vexflowNote,
                        freq: freq,
                        isRest: false
                    };
                } else {
                    scoreElements[colIdx].bass = {
                        noteName: noteName,
                        octave: octave,
                        vexflowNote: vexflowNote,
                        freq: freq,
                        isRest: false
                    };
                }

                scoreElements[colIdx].duration = selectedDuration;
                scoreElements[colIdx].beats = beats;

                // Toca a nota instantaneamente através da importação explícita de áudio!
                if (audioEngine) {
                    audioEngine.playNote(freq);
                }
                
                // Destaca no braço com foco verde para a nota clicada
                highlightActiveMelody(vexflowNote);

                // Avanço de Compasso Automático: Se clicar na última coluna, gera mais um compasso
                if (colIdx === scoreElements.length - 1) {
                    addMeasureToGrid();
                }
            }

            renderPautaDOM();
        });
    }

    function getFrequencyOfNote(noteName, octave) {
        const baseMidi = { 
            'C': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3, 'E': 4, 'F': 5, 
            'F#': 6, 'GB': 6, 'G': 7, 'G#': 8, 'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11 
        };
        const normalized = noteName.toUpperCase().trim();
        const midiNumber = 12 * (octave + 1) + baseMidi[normalized];
        return 440 * Math.pow(2, (midiNumber - 69) / 12);
    }

    // --- Feedback Pedagógico Avançado Realista: Caminho Transversal Real no Braço da Guitarra ---
    function highlightActiveMelody(activeVexflowNote = null) {
        // 1. Limpa todos os destaques do braço (incluindo fundos e sombras de notas soltas)
        const badges = document.querySelectorAll('#guitarFretboard .fret-note');
        badges.forEach(badge => {
            badge.classList.remove('visible');
            badge.classList.remove('visible-ativa'); // Remove a classe de foco ativa também!
            badge.style.opacity = '0';
            badge.style.transform = 'scale(0.6)';
            badge.style.backgroundColor = ''; 
            badge.style.boxShadow = '';
        });

        const cellOpens = document.querySelectorAll('#guitarFretboard .fretboard-cell.cell-open');
        cellOpens.forEach(cell => {
            cell.style.backgroundColor = '';
            cell.style.borderLeft = '';
            cell.style.boxShadow = '';
            
            // Força a remoção das classes de visibilidade dos badges das notas soltas também!
            const badge = cell.querySelector('.fret-note');
            if (badge) {
                badge.classList.remove('visible');
                badge.classList.remove('visible-ativa');
            }
        });

        // 2. Destaca as notas anteriores da música na Posição Recomendada (Trilha em Azul Royal)
        const cells = document.querySelectorAll('#guitarFretboard .fretboard-cell');
        
        scoreElements.forEach((el) => {
            // Destaca de forma polifônica: se o Treble for nota, destaca. Se o Bass for nota, destaca também!
            if (!el.treble.isRest && el.treble.vexflowNote) {
                const posTreble = guitarOpenPositionMap[el.treble.vexflowNote];
                if (posTreble) {
                    if (posTreble.fret === 0) {
                        // Se for nota solta anterior, brilha a pestana correspondente em azul de trilha
                        const cellOpen = document.querySelector(`#guitarFretboard .fretboard-cell.cell-open[data-string="${posTreble.string}"]`);
                        if (cellOpen) {
                            cellOpen.style.backgroundColor = 'rgba(13, 110, 253, 0.25)'; // Azul translúcido de trilha
                            cellOpen.style.borderLeft = '4px solid #0d6efd';
                            
                            // CRÍTICO: Busca o badge e torna visível para exibir a letra "E" ou "A" no Nut!
                            const b = cellOpen.querySelector('.fret-note');
                            if (b) {
                                b.classList.add('visible');
                            }
                        }
                    } else {
                        // Se for nota normal com traste, brilha o balão
                        const cell = document.querySelector(`#guitarFretboard .fretboard-cell[data-string="${posTreble.string}"][data-fret="${posTreble.fret}"]`);
                        if (cell) {
                            const b = cell.querySelector('.fret-note');
                            if (b) {
                                b.classList.add('visible');
                                b.style.opacity = '0.85';
                                b.style.transform = 'scale(1.05)'; 
                                b.style.backgroundColor = '#0d6efd'; // Azul representa a Trilha de digitação
                            }
                        }
                    }
                }
            }

            if (!el.bass.isRest && el.bass.vexflowNote) {
                const posBass = guitarOpenPositionMap[el.bass.vexflowNote];
                if (posBass) {
                    if (posBass.fret === 0) {
                        // Se for nota solta anterior, brilha a pestana em azul de trilha
                        const cellOpen = document.querySelector(`#guitarFretboard .fretboard-cell.cell-open[data-string="${posBass.string}"]`);
                        if (cellOpen) {
                            cellOpen.style.backgroundColor = 'rgba(13, 110, 253, 0.25)';
                            cellOpen.style.borderLeft = '4px solid #0d6efd';
                            
                            const b = cellOpen.querySelector('.fret-note');
                            if (b) {
                                b.classList.add('visible');
                            }
                        }
                    } else {
                        const cell = document.querySelector(`#guitarFretboard .fretboard-cell[data-string="${posBass.string}"][data-fret="${posBass.fret}"]`);
                        if (cell) {
                            const b = cell.querySelector('.fret-note');
                            if (b) {
                                b.classList.add('visible');
                                b.style.opacity = '0.85';
                                b.style.transform = 'scale(1.05)'; 
                                b.style.backgroundColor = '#0d6efd';
                            }
                        }
                    }
                }
            }
        });

        // 3. Destaca a última nota clicada na Posição Transversal (Foco atual em Verde Brilhante com sombra)
        if (activeVexflowNote) {
            const position = guitarOpenPositionMap[activeVexflowNote];
            if (position) {
                if (position.fret === 0) {
                    // Se a nota ativa for solta (Casa 0), brilha a pestana inteira de forma maravilhosa e proeminente!
                    const cellOpen = document.querySelector(`#guitarFretboard .fretboard-cell.cell-open[data-string="${position.string}"]`);
                    if (cellOpen) {
                        cellOpen.style.backgroundColor = 'rgba(25, 135, 84, 0.4)'; // Fundo verde translúcido
                        cellOpen.style.borderLeft = '6px solid #198754'; // Borda grossa verde de tônica solta
                        cellOpen.style.boxShadow = '0 0 10px #198754'; // Efeito neon brilhante
                        
                        // CRÍTICO: Busca o badge interno e força a visibilidade ativa para exibir a letra "E" ou "A" em verde no Nut!
                        const badge = cellOpen.querySelector('.fret-note');
                        if (badge) {
                            badge.classList.add('visible');
                            badge.classList.add('visible-ativa'); // Ativa o estilo CSS de alta visibilidade!
                        }
                    }
                } else {
                    // Se for nota normal em traste, brilha o balão redondo
                    const cell = document.querySelector(`#guitarFretboard .fretboard-cell[data-string="${position.string}"][data-fret="${position.fret}"]`);
                    if (cell) {
                        const badge = cell.querySelector('.fret-note');
                        if (badge) {
                            badge.classList.add('visible');
                            badge.style.opacity = '1';
                            badge.style.transform = 'scale(1.3)'; // Tamanho aumentado
                            badge.style.backgroundColor = '#198754'; // Verde indica Foco Ativo
                            badge.style.boxShadow = '0 0 10px #198754';
                        }
                    }
                }
            }
        }
    }

    // --- Playback & Metrônomo Polifônico Síncrono do Editor ---
    function playNextNote(index) {
        if (index >= scoreElements.length || !isPlaying) {
            stopPlayback();
            return;
        }

        const item = scoreElements[index];
        const bpm = parseInt(bpmInput.value) || 94;
        const beatDuration = 60000 / bpm;

        const multiplier = durationBeatsMap[item.duration] || 1;
        const noteDurationMs = beatDuration * multiplier;
        
        renderPautaDOM(index); 
        metronomeIndicator.style.backgroundColor = '#0d6efd';

        // Reproduz polifonia: toca os sons de Sol e Fá ao mesmo tempo se ambos existirem!
        let hasActiveNotes = false;
        
        if (!item.treble.isRest && item.treble.freq > 0) {
            if (audioEngine) {
                audioEngine.playNote(item.treble.freq);
            }
            hasActiveNotes = true;
        }

        if (!item.bass.isRest && item.bass.freq > 0) {
            if (audioEngine) {
                audioEngine.playNote(item.bass.freq);
            }
            hasActiveNotes = true;
        }

        // Destaca no braço a última tocada com foco
        if (hasActiveNotes) {
            const lastNote = !item.treble.isRest ? item.treble.vexflowNote : item.bass.vexflowNote;
            highlightActiveMelody(lastNote);
        } else {
            highlightActiveMelody(null); 
        }

        playbackTimeoutId = setTimeout(() => {
            metronomeIndicator.style.backgroundColor = '#6c757d';
            playNextNote(index + 1);
        }, noteDurationMs);
    }

    function startPlayback() {
        if (scoreElements.length === 0) return;
        isPlaying = true;
        playPauseBtn.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
        playPauseBtn.classList.replace('btn-success', 'btn-warning');
        renderPautaDOM();
        playNextNote(0);
    }

    function stopPlayback() {
        isPlaying = false;
        clearTimeout(playbackTimeoutId);
        playbackTimeoutId = null;
        playPauseBtn.innerHTML = '<i class="bi bi-play-fill"></i> Play';
        playPauseBtn.classList.replace('btn-warning', 'btn-success');
        metronomeIndicator.style.backgroundColor = '#6c757d';
        highlightActiveMelody(null); // Limpa destaques do braço
        renderPautaDOM();
    }

    playPauseBtn.addEventListener('click', () => {
        if (isPlaying) {
            stopPlayback();
        } else {
            startPlayback();
        }
    });

    // --- Serialização e Salvamento ---
    function serializeScore() {
        return scoreElements.map(el => ({
            treble: {
                pitch: el.treble.noteName,
                vexflowNote: el.treble.vexflowNote,
                freq: el.treble.freq,
                isRest: el.treble.isRest
            },
            bass: {
                pitch: el.bass.noteName,
                vexflowNote: el.bass.vexflowNote,
                freq: el.bass.freq,
                isRest: el.bass.isRest
            },
            duration: el.duration,
            beats: el.beats
        }));
    }

    function loadScoreFromData(data) {
        scoreElements = [];
        try {
            data.forEach(item => {
                // Retrocompatibilidade robusta com partituras de formatos antigos
                if (item.treble !== undefined && item.bass !== undefined) {
                    scoreElements.push({
                        treble: item.treble,
                        bass: item.bass,
                        duration: item.duration || 'q',
                        beats: item.beats || 1
                    });
                } else {
                    // Se era do formato antigo do VexFlow, converte para polifonia limpa
                    const isRest = item.isRest !== undefined ? item.isRest : (item.keys ? false : true);
                    const duration = item.duration || 'q';
                    const clef = item.clef || 'treble';
                    const freq = item.freq || 0;
                    const noteName = item.pitch || null;
                    const vexflowNote = item.vexflowNote || null;

                    const newNote = { noteName, octave: vexflowNote ? parseInt(vexflowNote.split('/')[1]) : null, vexflowNote, freq, isRest };
                    const emptyNote = { noteName: null, octave: null, vexflowNote: null, freq: 0, isRest: true };

                    scoreElements.push({
                        treble: clef === 'treble' ? newNote : emptyNote,
                        bass: clef === 'bass' ? newNote : emptyNote,
                        duration: duration,
                        beats: durationBeatsMap[duration] || 1
                    });
                }
            });
            renderPautaDOM();
            highlightActiveMelody(null);
        } catch (e) {
            console.error("Erro ao carregar partituras:", e);
        }
    }

    async function saveScore() {
        // Filtra para ver se há pelo menos uma nota real adicionada em qualquer das claves
        const hasRealNotes = scoreElements.some(el => !el.treble.isRest || !el.bass.isRest);
        if (!hasRealNotes) {
            alert("Adicione pelo menos uma nota antes de salvar.");
            return;
        }
        const title = prompt("Digite um título para a partitura:", "Minha Composição");
        if (!title) return;

        const url = currentScoreIdInput.value ? `/guitar-study/api/v1/sheet-music/${currentScoreIdInput.value}` : '/guitar-study/api/v1/sheet-music';
        const method = currentScoreIdInput.value ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title, data: serializeScore() }),
            });
            const result = await response.json();
            if (result.success) {
                alert('Partitura salva!');
                currentScoreIdInput.value = result.data.id;
                await loadSavedScores();
            } else {
                alert(`Erro: ${result.error.message}`);
            }
        } catch (e) {
            alert('Erro de conexão ao salvar.');
        }
    }

    async function loadSavedScores() {
        try {
            const response = await fetch('/guitar-study/api/v1/sheet-music');
            const result = await response.json();
            savedScoresList.innerHTML = '';
            if (result.success && result.data.scores.length > 0) {
                result.data.scores.forEach(score => {
                    const item = document.createElement('a');
                    item.href = '#';
                    item.className = 'list-group-item list-group-item-action fs-8 py-2';
                    item.innerHTML = `<i class="bi bi-file-music text-primary me-2"></i>${score.title}`;
                    item.addEventListener('click', async (e) => {
                        e.preventDefault();
                        const res = await fetch(`/guitar-study/api/v1/sheet-music/${score.id}`);
                        const scoreData = await res.json();
                        if (scoreData.success) {
                            currentScoreIdInput.value = scoreData.data.id; 
                            loadScoreFromData(scoreData.data.data);
                        }
                    });
                    savedScoresList.appendChild(item);
                });
            } else {
                savedScoresList.innerHTML = '<div class="p-3 text-center text-muted fs-8">Nenhuma partitura salva.</div>';
            }
        } catch (e) {
            savedScoresList.innerHTML = '<div class="p-3 text-center text-danger">Erro ao carregar as partituras.</div>';
        }
    }

    // --- Inicialização do Braço de Guitarra Coadjuvante de Edição Puro ---
    const fretboard = new Fretboard('guitarFretboard', {
        viewMode: "modo_editor",
        highlightedNotes: [], 
        tonic: null
    });
    fretboard.init().catch(err => console.error("Erro ao inicializar o braço da guitarra:", err));

    // --- Toolbar Event Listeners ---
    function updateSelectedButton(button) {
        document.querySelectorAll('#sheet-music-toolbar button').forEach(btn => btn.classList.remove('active'));
        button.className = "btn btn-outline-primary py-0 active";
        selectedDuration = button.dataset.duration;
        selectedType = button.dataset.type === 'rest' ? 'rest' : 'note';
    }

    noteButtons.forEach(button => button.addEventListener('click', (e) => updateSelectedButton(e.currentTarget)));
    restButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            updateSelectedButton(e.currentTarget);
        });
    });

    accidentalButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            accidentalButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            selectedAccidental = button.dataset.accidental;
        });
    });
    
    clearScoreBtn.addEventListener('click', () => {
        initializeGrid(); // Reseta para o grid padrão de pausas vazias
        currentScoreIdInput.value = '';
        highlightActiveMelody(null); 
        renderPautaDOM();
    });

    saveScoreBtn.addEventListener('click', saveScore);
    timeSignatureSelect.addEventListener('change', renderPautaDOM);

    // --- Inicialização ---
    document.querySelector('#add-note-buttons button[data-duration="q"]').classList.add('active');
    initializeGrid(); // Inicializa o grid de compassos síncronos com 16 tempos
    renderPautaDOM(); // Renderiza a pauta HTML5
    loadSavedScores().catch(err => console.error("Erro ao carregar partituras:", err));
});
