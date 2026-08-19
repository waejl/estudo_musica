import { audioEngine } from './audio-engine.js';

/**
 * Fretboard - Componente dinâmico que renderiza e gerencia a interatividade do braço de guitarra.
 */
export class Fretboard {
    /**
     * @param {string} containerId - ID do elemento HTML onde o braço será gerado.
     * @param {Object} options - Opções iniciais.
     */
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container #${containerId} não encontrado.`);
            return;
        }

        // Opções padrão
        this.options = {
            tuningId: options.tuningId || "standard",
            fretCount: options.fretCount || 22,
            preference: options.preference || "sharps",
            handOrientation: options.handOrientation || "right_handed", // right_handed ou left_handed
            viewMode: options.viewMode || "show_all", // show_all, hide_all, natural, tonic_only, highlight_set
            displayType: options.displayType || "notes", // notes, intervals, degrees
            tonic: options.tonic || "C", // Tônica padrão de referência
            highlightedNotes: options.highlightedNotes || [], // Array de strings de notas a destacar (ex: ["C", "E", "G"])
            onNoteClick: options.onNoteClick || null, // Callback ao clicar em uma nota
            ...options
        };

        this.stringsData = []; // Armazenará os dados vindos da API
        this.fretboardEl = null;
        this.pathOverlay = null; // SVG para desenhar caminhos
    }

    /**
     * Busca dados do braço na API e inicializa a renderização.
     */
    async init() {
        this.container.innerHTML = `<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2 text-muted">Afinando guitarra e montando o braço...</p></div>`;
        
        try {
            const url = `${window.APP_PREFIX || ""}/guitar-study/api/v1/fretboard?tuning_id=${this.options.tuningId}&fret_count=${this.options.fretCount}&preference=${this.options.preference}`;
            const response = await fetch(url);
            const resData = await response.json();
            
            if (resData.success) {
                this.stringsData = resData.data.strings;
                this.render();
            } else {
                this.container.innerHTML = `<div class="alert alert-danger">Erro ao carregar o braço: ${resData.error.message}</div>`;
            }
        } catch (e) {
            this.container.innerHTML = `<div class="alert alert-danger">Erro de rede ao carregar o braço da guitarra.</div>`;
            console.error(e);
        }
    }

    /**
     * Desenha o caminho de execução entre as notas.
     * @param {Array<Object>} notes - Array de objetos de nota, cada um com `string`, `fret` e `sequence`.
     * @param {Array<Object>} connections - Array de objetos de conexão manual.
     * @param {string} mode - Modo de conexão ("auto" ou "manual").
     */
    renderExecutionPath(notes, connections = [], mode = "auto") {
        if (!this.pathOverlay) return;

        // Mantém as definições de defs que são limpas no innerHTML = ''
        const defs = this.pathOverlay.querySelector('defs');
        this.pathOverlay.innerHTML = '';
        if (defs) {
            this.pathOverlay.appendChild(defs);
        } else {
            const newDefs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
            marker.setAttribute('id', 'arrowhead');
            marker.setAttribute('viewBox', '0 0 10 10');
            marker.setAttribute('refX', '8');
            marker.setAttribute('refY', '5');
            marker.setAttribute('markerWidth', '6');
            marker.setAttribute('markerHeight', '6');
            marker.setAttribute('orient', 'auto-start-reverse');
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
            path.setAttribute('fill', '#ffc107');
            marker.appendChild(path);
            newDefs.appendChild(marker);
            this.pathOverlay.appendChild(newDefs);
        }

        // DESENHO AUTOMÁTICO DE PESTANAS (BARRE CHORDS)
        // Agrupa as notas visíveis que estão na mesma casa (fret > 0)
        const notesByFret = {};
        notes.forEach(note => {
            const f = parseInt(note.fret);
            if (f > 0) {
                if (!notesByFret[f]) notesByFret[f] = [];
                notesByFret[f].push(note);
            }
        });

        // Para cada casa com 3 ou mais notas visíveis, desenhamos uma barra vertical grossa de pestana
        for (const [fret, fretNotes] of Object.entries(notesByFret)) {
            if (fretNotes.length >= 3) {
                // Ordena por corda para encontrar o intervalo (da corda menor à maior)
                fretNotes.sort((a, b) => a.string - b.string);
                const minStr = fretNotes[0].string;
                const maxStr = fretNotes[fretNotes.length - 1].string;

                const cellMin = this.fretboardEl.querySelector(`.fretboard-cell[data-string="${minStr}"][data-fret="${fret}"]`);
                const cellMax = this.fretboardEl.querySelector(`.fretboard-cell[data-string="${maxStr}"][data-fret="${fret}"]`);

                if (cellMin && cellMax) {
                    const rectMin = cellMin.getBoundingClientRect();
                    const rectMax = cellMax.getBoundingClientRect();
                    const containerRect = this.container.getBoundingClientRect();

                    const x = rectMin.left - containerRect.left + rectMin.width / 2;
                    const y1 = rectMin.top - containerRect.top + rectMin.height / 2;
                    const y2 = rectMax.top - containerRect.top + rectMax.height / 2;

                    const barreLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    barreLine.setAttribute('x1', x);
                    barreLine.setAttribute('y1', y1);
                    barreLine.setAttribute('x2', x);
                    barreLine.setAttribute('y2', y2);
                    barreLine.setAttribute('stroke', 'rgba(255, 193, 7, 0.45)'); // Amarelo translúcido didático
                    barreLine.setAttribute('stroke-width', '18'); // Espessura de 18px cobrindo a casa como um dedo
                    barreLine.setAttribute('stroke-linecap', 'round');
                    barreLine.style.pointerEvents = 'none';

                    this.pathOverlay.appendChild(barreLine);
                }
            }
        }

        const linkNotesSwitch = document.getElementById('linkNotesSwitch');
        if (!linkNotesSwitch || !linkNotesSwitch.checked) {
            return;
        }

        if (mode === "auto") {
            const sortedNotes = notes
                .filter(n => n.sequence > 0)
                .sort((a, b) => a.sequence - b.sequence);

            if (sortedNotes.length < 2) return;

            for (let i = 0; i < sortedNotes.length - 1; i++) {
                const noteA = sortedNotes[i];
                const noteB = sortedNotes[i+1];
                this.drawArrow(noteA.string, noteA.fret, noteB.string, noteB.fret);
            }
        } else {
            connections.forEach(conn => {
                this.drawArrow(
                    conn.from_string || conn.fromStr,
                    conn.from_fret || conn.fromFret,
                    conn.to_string || conn.toStr,
                    conn.to_fret || conn.toFret
                );
            });
        }
    }

    /**
     * Desenha uma seta de ligação entre duas células do braço de guitarra.
     */
    drawArrow(fromStr, fromFret, toStr, toFret, color = '#ffc107') {
        const cellA = this.fretboardEl.querySelector(`.fretboard-cell[data-string="${fromStr}"][data-fret="${fromFret}"]`);
        const cellB = this.fretboardEl.querySelector(`.fretboard-cell[data-string="${toStr}"][data-fret="${toFret}"]`);

        if (cellA && cellB) {
            const rectA = cellA.getBoundingClientRect();
            const rectB = cellB.getBoundingClientRect();
            const containerRect = this.container.getBoundingClientRect();

            const x1 = rectA.left - containerRect.left + rectA.width / 2;
            const y1 = rectA.top - containerRect.top + rectA.height / 2;
            const x2 = rectB.left - containerRect.left + rectB.width / 2;
            const y2 = rectB.top - containerRect.top + rectB.height / 2;

            const dx = x2 - x1;
            const dy = y2 - y1;
            const dist = Math.sqrt(dx * dx + dy * dy);

            let finalX2 = x2;
            let finalY2 = y2;
            const shrinkOffset = 18; // Deslocamento de 18px para que a seta termine na borda do badge da nota

            if (dist > shrinkOffset) {
                finalX2 = x2 - (shrinkOffset * dx) / dist;
                finalY2 = y2 - (shrinkOffset * dy) / dist;
            }

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', x1);
            line.setAttribute('y1', y1);
            line.setAttribute('x2', finalX2);
            line.setAttribute('y2', finalY2);

            line.setAttribute('stroke', color);
            line.setAttribute('stroke-width', '3');
            line.setAttribute('marker-end', 'url(#arrowhead)');

            // Estilização e suporte a clique duplo para exclusão de ligação individual
            line.setAttribute('class', 'fretboard-connection-line');
            line.style.cursor = 'pointer';
            line.style.pointerEvents = 'auto'; // Habilita detecção de mousedown/dblclick na própria linha

            line.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                const event = new CustomEvent('connection-dblclick', {
                    detail: {
                        from_string: parseInt(fromStr),
                        from_fret: parseInt(fromFret),
                        to_string: parseInt(toStr),
                        to_fret: parseInt(toFret)
                    }
                });
                this.container.dispatchEvent(event);
            });

            this.pathOverlay.appendChild(line);
        }
    }

    /**
     * Define o modo de exibição das notas e redesenha.
     * @param {string} mode - show_all, hide_all, natural, tonic_only, highlight_set, modo_editor
     */
    setViewMode(mode) {
        this.options.viewMode = mode;
        if (mode === "modo_editor") {
            // Limpa o braço de guitarra ao entrar no Modo Editor para o usuário "pintar" o braço livremente do zero
            if (this.fretboardEl) {
                const badges = this.fretboardEl.querySelectorAll(".fret-note");
                badges.forEach(b => {
                    b.classList.remove("visible");
                    b.style.opacity = "0";
                    b.style.transform = "scale(0.6)";
                });
            }
        } else {
            this.updateNoteVisibilities();
        }
    }

    /**
     * Define o tipo de caractere exibido dentro da nota.
     * @param {string} type - notes, intervals, degrees
     */
    setDisplayType(type) {
        this.options.displayType = type;
        this.renderNotesContent();
    }

    /**
     * Define qual é a tônica de referência e a lista de notas destacadas (para escalas, acordes, etc.).
     * @param {string} tonic - Nota (Ex: "A", "C#")
     * @param {Array<string>} notesToHighlight - Lista de notas que compõem a escala/acorde
     */
    setHighlightedSet(tonic, notesToHighlight = []) {
        this.options.tonic = tonic;
        this.options.highlightedNotes = notesToHighlight.map(n => this.normalizeNoteName(n));
        this.updateNoteVisibilities();
        this.renderNotesContent();
    }

    /**
     * Normaliza enarmônicos para comparação.
     */
    normalizeNoteName(note) {
        return note.trim();
    }

    /**
     * Renderiza a estrutura completa do braço de guitarra no DOM.
     */
    render() {
        this.container.innerHTML = "";
        
        // 1. Container de scroll horizontal
        const outerWrapper = document.createElement("div");
        outerWrapper.className = "fretboard-container";
        outerWrapper.style.position = 'relative'; // Para o overlay SVG
        
        // Overlay SVG para desenhar caminhos
        this.pathOverlay = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.pathOverlay.setAttribute('class', 'fretboard-path-overlay');
        this.pathOverlay.style.position = 'absolute';
        this.pathOverlay.style.top = '0';
        this.pathOverlay.style.left = '0';
        this.pathOverlay.style.width = '100%';
        this.pathOverlay.style.height = '100%';
        this.pathOverlay.style.pointerEvents = 'none';
        this.pathOverlay.style.zIndex = '10';

        // Definir a ponta da seta para as linhas
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('viewBox', '0 0 10 10');
        marker.setAttribute('refX', '8');
        marker.setAttribute('refY', '5');
        marker.setAttribute('markerWidth', '6');
        marker.setAttribute('markerHeight', '6');
        marker.setAttribute('orient', 'auto-start-reverse');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
        path.setAttribute('fill', '#ffc107');
        marker.appendChild(path);
        defs.appendChild(marker);
        this.pathOverlay.appendChild(defs);

        outerWrapper.appendChild(this.pathOverlay);
        
        // 2. O braço em si
        this.fretboardEl = document.createElement("div");
        this.fretboardEl.className = "fretboard";
        if (this.options.handOrientation === "right_handed") {
            this.fretboardEl.classList.add("right-handed");
        }
        
        // 3. Renderizar Trastes (Linhas verticais metálicas)
        const fretsRow = document.createElement("div");
        fretsRow.className = "fretboard-frets-row";
        fretsRow.style.position = "absolute";
        if (this.options.handOrientation === "right_handed") {
            fretsRow.style.right = "85px";
            fretsRow.style.left = "auto";
            fretsRow.style.flexDirection = "row-reverse";
        } else {
            fretsRow.style.left = "85px";
            fretsRow.style.right = "auto";
        }
        fretsRow.style.width = "calc(100% - 85px)";
        fretsRow.style.height = "100%";
        fretsRow.style.display = "flex";
        fretsRow.style.pointerEvents = "none";
        fretsRow.style.zIndex = "1";
        
        // Adiciona Nut (Linha inicial)
        const nut = document.createElement("div");
        nut.className = "fretboard-nut";
        nut.style.position = "absolute";
        if (this.options.handOrientation === "right_handed") {
            nut.style.right = "60px";
            nut.style.left = "auto";
        } else {
            nut.style.left = "60px";
            nut.style.right = "auto";
        }
        nut.style.width = "25px";
        nut.style.height = "100%";
        nut.style.zIndex = "2";
        this.fretboardEl.appendChild(nut);
        
        // Casas
        for (let f = 1; f <= this.options.fretCount; f++) {
            const fretEl = document.createElement("div");
            fretEl.className = "fretboard-fret";
            fretEl.style.flex = "1";
            fretEl.style.height = "100%";
            fretEl.style.position = "relative";
            
            // Adiciona marcações (Inlays) nas casas 3, 5, 7, 9, 12 (duplo), 15, 17, 19, 21
            if ([3, 5, 7, 9, 15, 17, 19, 21].includes(f)) {
                const inlay = document.createElement("div");
                inlay.className = "fret-inlay center-inlay";
                fretEl.appendChild(inlay);
            } else if (f === 12) {
                // Marcação dupla na casa 12
                const inlayTop = document.createElement("div");
                inlayTop.className = "fret-inlay top-inlay";
                const inlayBottom = document.createElement("div");
                inlayBottom.className = "fret-inlay bottom-inlay";
                fretEl.appendChild(inlayTop);
                fretEl.appendChild(inlayBottom);
            }
            
            fretsRow.appendChild(fretEl);
        }
        this.fretboardEl.appendChild(fretsRow);
        
        // 4. Renderizar Cordas de Guitarras (Linhas horizontais - Desabilitado o método de render antigo)
        const stringsEl = document.createElement("div");
        stringsEl.className = "fretboard-strings";
        this.fretboardEl.appendChild(stringsEl);
        
        // 5. Renderizar Grade de Células clicáveis (Notas sobre as cordas e casas com indicadores embutidos)
        const gridEl = document.createElement("div");
        gridEl.className = "fretboard-grid";
        
        const renderedStrings = this.options.handOrientation === "right_handed" ? [...this.stringsData].reverse() : this.stringsData;
        
        renderedStrings.forEach((strData, loopIdx) => {
            const strIdx = this.options.handOrientation === "right_handed" ? (this.stringsData.length - 1 - loopIdx) : loopIdx;
            
            const stringRow = document.createElement("div");
            stringRow.className = "fretboard-string-row";
            
            // Cria o indicador lateral esquerdo da corda (Ex: 1 - MI, 2 - SI, 3 - SOL, etc.)
            const stringLabel = document.createElement("div");
            stringLabel.className = "string-label-indicator";
            
            // Nomes de cordas em português do Brasil conforme solicitado
            const stringNamesMap = {
                0: "MI",  // 1ª corda (E aguda)
                1: "SI",  // 2ª corda (B)
                2: "SOL", // 3ª corda (G)
                3: "RÉ",  // 4ª corda (D)
                4: "LÁ",  // 5ª corda (A)
                5: "MI"   // 6ª corda (E grave)
            };
            const labelName = stringNamesMap[strIdx] || strData.open_note;
            stringLabel.textContent = `${strIdx + 1} - ${labelName}`;
            stringRow.appendChild(stringLabel);
            
            strData.frets.forEach((fretData) => {
                const cell = document.createElement("div");
                cell.className = "fretboard-cell";
                if (fretData.fret === 0) {
                    cell.classList.add("cell-open");
                }
                
                cell.setAttribute("data-string", strIdx + 1);
                cell.setAttribute("data-fret", fretData.fret);
                cell.setAttribute("data-note", fretData.note);
                cell.setAttribute("data-freq", fretData.frequency);
                
                // Cria o balãozinho da nota que fica oculto ou visível
                const noteBadge = document.createElement("div");
                noteBadge.className = "fret-note";
                
                // Define se é natural ou sustenido/bemol para cor diferente
                const isAccidental = fretData.note.includes("#") || fretData.note.includes("b");
                noteBadge.classList.add(isAccidental ? "accidental" : "natural");
                
                cell.appendChild(noteBadge);
                
                // Evento de clique na casa/nota
                cell.addEventListener("click", () => {
                    // Toca som
                    audioEngine.playNote(fretData.frequency);
                    
                    // Callback externo de clique
                    if (this.options.onNoteClick) {
                        this.options.onNoteClick({
                            string: strIdx + 1,
                            fret: fretData.fret,
                            note: fretData.note,
                            frequency: fretData.frequency,
                            openString: strData.open_note,
                            cell: cell,
                            noteBadge: noteBadge
                        });
                    } else if (this.options.viewMode === "modo_editor") {
                        // Comportamento padrão do modo editor se nenhum callback for fornecido
                        noteBadge.classList.toggle("visible");
                        if (noteBadge.classList.contains("visible")) {
                            noteBadge.style.opacity = "1";
                            noteBadge.style.transform = "scale(1)";
                        } else {
                            noteBadge.style.opacity = "0";
                            noteBadge.style.transform = "scale(0.6)";
                        }
                        this.updateTabAndSheet();
                    }
                    
                    // Pequeno efeito temporário de pulsação na nota clicada
                    const currentScale = this.options.viewMode === "modo_editor" && !noteBadge.classList.contains("visible") ? "0" : "1";
                    noteBadge.classList.add("active-pulse");
                    noteBadge.style.transform = "scale(1.3)";
                    setTimeout(() => {
                        noteBadge.style.transform = "";
                        noteBadge.classList.remove("active-pulse");
                    }, 200);
                });
                
                stringRow.appendChild(cell);
            });
            gridEl.appendChild(stringRow);
        });
        
        this.fretboardEl.appendChild(gridEl);
        outerWrapper.appendChild(this.fretboardEl);
        
        // 6. Renderizar números das casas abaixo do braço
        const numbersRow = document.createElement("div");
        numbersRow.className = "fretboard-numbers";
        if (this.options.handOrientation === "right_handed") {
            numbersRow.classList.add("right-handed");
        }
        
        // Compensação horizontal de 60px para alinhar com os rótulos laterais esquerdos de cordas
        const spacer = document.createElement("div");
        spacer.style.flex = "0 0 60px";
        numbersRow.appendChild(spacer);
        
        // Casa 0 (Open) - Sem número ou espaço alinhado
        const numberOpen = document.createElement("div");
        numberOpen.className = "fret-number cell-open";
        numberOpen.style.flex = "0 0 25px";
        numbersRow.appendChild(numberOpen);
        
        for (let f = 1; f <= this.options.fretCount; f++) {
            const numberEl = document.createElement("div");
            numberEl.className = "fret-number";
            // Mostra o número somente nas casas principais para não poluir
            if ([0, 1, 3, 5, 7, 9, 12, 15, 17, 19, 21, 24].includes(f)) {
                numberEl.textContent = f;
            }
            numbersRow.appendChild(numberEl);
        }
        outerWrapper.appendChild(numbersRow);
        
        this.container.appendChild(outerWrapper);
        
        // Garante a criação dinâmica dos contêineres de Tablatura e Partitura se não existirem no HTML
        this.renderTablatureAndSheetMusicContainers();
        
        // Renderiza o conteúdo e a visibilidade das notas
        this.renderNotesContent();
        this.updateNoteVisibilities();
        
        // Atualiza a Tablatura e Partitura inicialmente
        this.updateTabAndSheet();
    }

    /**
     * Renderiza o conteúdo textual correto para cada bolinha de nota no braço.
     */
    renderNotesContent() {
        if (!this.fretboardEl) return;
        
        const cells = this.fretboardEl.querySelectorAll(".fretboard-cell");
        cells.forEach(cell => {
            const noteName = cell.getAttribute("data-note");
            const noteBadge = cell.querySelector(".fret-note");
            if (!noteBadge) return;
            
            noteBadge.classList.remove("tonica");
            
            const isTonic = this.isNotesEqual(noteName, this.options.tonic);
            
            if (isTonic) {
                noteBadge.classList.add("tonica");
            }
            
            const noteType = noteBadge.getAttribute("data-note-type");
            if (noteType === "open") {
                noteBadge.textContent = "O";
            } else if (noteType === "muted") {
                noteBadge.textContent = "X";
            } else if (this.options.displayType === "intervals" || this.options.displayType === "degrees") {
                const intervalSymbol = this.calculateIntervalSymbol(this.options.tonic, noteName);
                noteBadge.textContent = intervalSymbol;
            } else {
                // Se a célula for a tônica, force o texto a ser o da seleção original.
                // Caso contrário, use o nome da nota que respeita a preferência de #/b.
                if (isTonic && this.options.tonic) {
                    noteBadge.textContent = this.options.tonic;
                } else {
                    noteBadge.textContent = noteName;
                }
            }
        });
    }

    /**
     * Atualiza quais notas devem ficar visíveis no braço com base no viewMode.
     */
    updateNoteVisibilities() {
        if (!this.fretboardEl) return;
        
        // Se estiver no Modo Editor, preservamos a seleção manual e individual das notas pelo usuário
        if (this.options.viewMode === "modo_editor") {
            return;
        }
        
        const cells = this.fretboardEl.querySelectorAll(".fretboard-cell");
        cells.forEach(cell => {
            const noteName = cell.getAttribute("data-note");
            const noteBadge = cell.querySelector(".fret-note");
            if (!noteBadge) return;
            
            let isVisible = false;
            
            switch (this.options.viewMode) {
                case "show_all":
                    isVisible = true;
                    break;
                case "hide_all":
                    isVisible = false;
                    break;
                case "natural":
                    // Notas naturais não possuem # ou b
                    isVisible = !noteName.includes("#") && !noteName.includes("b");
                    break;
                case "tonic_only":
                    // Somente a tônica de referência
                    isVisible = this.isNotesEqual(noteName, this.options.tonic);
                    break;
                case "highlight_set":
                    // Mostra somente se a nota pertencer ao conjunto destacado (escala ou acorde)
                    isVisible = this.options.highlightedNotes.some(hn => this.isNotesEqual(noteName, hn));
                    break;
            }
            
            if (isVisible) {
                noteBadge.classList.add("visible");
            } else {
                noteBadge.classList.remove("visible");
            }
        });
        
        // Atualiza a Tablatura e Partitura com as notas que ficaram visíveis
        this.updateTabAndSheet();
    }

    /**
     * Compara se duas notas são equivalentes enarmônicas simples.
     */
    isNotesEqual(n1, n2) {
        if (!n1 || !n2) return false;
        n1 = n1.trim();
        n2 = n2.trim();
        if (n1 === n2) return true;
        
        // Equivalências simples
        const map = {
            "C#": "Db", "Db": "C#",
            "D#": "Eb", "Eb": "D#",
            "F#": "Gb", "Gb": "F#",
            "G#": "Ab", "Ab": "G#",
            "A#": "Bb", "Bb": "A#",
            "C": "B#", "B#": "C",
            "F": "E#", "E#": "F",
            "B": "Cb", "Cb": "B",
            "E": "Fb", "Fb": "E"
        };
        return map[n1] === n2 || map[n2] === n1;
    }

    /**
     * Calcula o símbolo do intervalo em relação à tônica.
     */
    calculateIntervalSymbol(root, target) {
        const sharps = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
        const flats = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
        
        let rIdx = sharps.indexOf(root);
        if (rIdx === -1) rIdx = flats.indexOf(root);
        
        let tIdx = sharps.indexOf(target);
        if (tIdx === -1) tIdx = flats.indexOf(target);
        
        if (rIdx === -1 || tIdx === -1) return "1";
        
        const diff = (tIdx - rIdx + 12) % 12;
        const symbols = {
            0: "1", 1: "b2", 2: "2", 3: "b3", 4: "3", 5: "4", 6: "b5",
            7: "5", 8: "b6", 9: "6", 10: "b7", 11: "7"
        };
        return symbols[diff] || "1";
    }

    /**
     * Garante a criação dinâmica dos contêineres HTML para a Tablatura e Partitura se não existirem no HTML.
     */
    renderTablatureAndSheetMusicContainers() {
        if (!this.container) return;
        
        let tabContainer = document.getElementById("guitarTablature");
        let sheetContainer = document.getElementById("guitarSheetMusic");
        
        if (!tabContainer) {
            const tabCard = document.createElement("div");
            tabCard.className = "card mb-4 bg-body-tertiary border-0 shadow-sm overflow-hidden mt-4";
            tabCard.innerHTML = `
                <div class="card-header bg-transparent border-bottom-0 pt-3 pb-1 d-flex align-items-center gap-2">
                    <i class="bi bi-music-player text-success fs-5"></i>
                    <h5 class="fw-bold mb-0">Tablatura correspondente (Linhas de cordas 1 a 6)</h5>
                </div>
                <div class="card-body p-3">
                    <div id="guitarTablature"></div>
                </div>
            `;
            this.container.appendChild(tabCard);
        }
        
        if (!sheetContainer) {
            const sheetCard = document.createElement("div");
            sheetCard.className = "card mb-4 bg-body-tertiary border-0 shadow-sm overflow-hidden mt-4";
            sheetCard.innerHTML = `
                <div class="card-header bg-transparent border-bottom-0 pt-3 pb-1 d-flex align-items-center gap-2">
                    <i class="bi bi-music-note text-primary fs-5"></i>
                    <h5 class="fw-bold mb-0">Partitura tradicional (Clave de Sol)</h5>
                </div>
                <div class="card-body p-3 overflow-x-auto">
                    <div id="guitarSheetMusic" class="abcjs-container"></div>
                </div>
            `;
            this.container.appendChild(sheetCard);
        }
    }

    /**
     * Analisa as notas visíveis e atualiza de forma dinâmica e síncrona a Tablatura e a Partitura tradicional.
     */
    updateTabAndSheet() {
        const tabContainer = document.getElementById("guitarTablature");
        const sheetContainer = document.getElementById("guitarSheetMusic");
        
        if (!tabContainer && !sheetContainer) return;
        
        // 1. Coleta todas as células visíveis ativas do braço
        const activeCells = [];
        if (this.fretboardEl) {
            const cells = this.fretboardEl.querySelectorAll(".fretboard-cell");
            cells.forEach(cell => {
                const badge = cell.querySelector(".fret-note");
                if (badge && badge.classList.contains("visible")) {
                    activeCells.push({
                        string: parseInt(cell.getAttribute("data-string")), // 1 a 6
                        fret: parseInt(cell.getAttribute("data-fret")), // 0 a 22
                        note: cell.getAttribute("data-note"), // Ex: "C"
                        freq: parseFloat(cell.getAttribute("data-freq"))
                    });
                }
            });
        }
        
        // Ordena as notas em ordem crescente de frequência (do grave para o agudo) para que a partitura
        // e tablatura sequenciais fiquem de leitura didática perfeita!
        activeCells.sort((a, b) => a.freq - b.freq);
        
        // -------------------------------------------------------------
        // RENDER 1: TABLATURA DINÂMICA
        // -------------------------------------------------------------
        if (tabContainer) {
            tabContainer.innerHTML = "";
            const tabView = document.createElement("div");
            tabView.className = "guitar-tab-view";
            
            const stringNamesMap = {
                1: "MI", 2: "SI", 3: "SOL", 4: "RÉ", 5: "LÁ", 6: "MI"
            };
            
            // Desenha as 6 linhas da tablatura (Corda 1 aguda no topo, Corda 6 grave embaixo)
            for (let s = 1; s <= 6; s++) {
                const row = document.createElement("div");
                row.className = "guitar-tab-row";
                
                const label = document.createElement("div");
                label.className = "guitar-tab-label";
                label.textContent = `${s} - ${stringNamesMap[s]}`;
                row.appendChild(label);
                
                const notesContainer = document.createElement("div");
                notesContainer.className = "guitar-tab-notes-container";
                
                // Filtra as notas ativas que pertencem a esta corda s
                const stringNotes = activeCells.filter(c => c.string === s);
                if (stringNotes.length > 0) {
                    stringNotes.forEach(c => {
                        // Cria o container do número da casa
                        const wrapper = document.createElement("div");
                        wrapper.className = "guitar-tab-number-wrapper";
                        
                        const num = document.createElement("div");
                        num.className = "guitar-tab-number";
                        const isTonic = this.isNotesEqual(c.note, this.options.tonic);
                        if (isTonic) {
                            num.classList.add("tonica");
                        }
                        num.textContent = c.fret === 0 ? "0" : c.fret;
                        wrapper.appendChild(num);
                        
                        notesContainer.appendChild(wrapper);
                    });
                }
                
                row.appendChild(notesContainer);
                tabView.appendChild(row);
            }
            tabContainer.appendChild(tabView);
        }
        
        // -------------------------------------------------------------
        // RENDER 2: PARTITURA DINÂMICA (ABCJS)
        // -------------------------------------------------------------
        if (sheetContainer && typeof abcjs !== "undefined" || typeof ABCJS !== "undefined") {
            // Inicializa o cabeçalho ABC (Clave de sol, Compasso livre, Tom de C neutro)
            let abcString = "X:1\nT:Partitura do Estudo\nM:4/4\nL:1/4\nK:C clef=treble\n";
            
            if (activeCells.length > 0) {
                const notesAbcList = [];
                activeCells.forEach(cell => {
                    // Calcula a oitava científica real com base no número da corda e casa
                    // Mapeamento de oitava base das 6 cordas padrão (1=aguda, 6=grave)
                    const indexToOctave = { 1:4, 2:3, 3:3, 4:3, 5:2, 6:2 };
                    const baseOctave = indexToOctave[cell.string] || 3;
                    
                    // Descobre o índice cromático da nota da corda solta
                    const sharps = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
                    const flats = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
                    
                    // Busca a nota de afinação da corda real base
                    const stringNotesMap = { 1:"E", 2:"B", 3:"G", 4:"D", 5:"A", 6:"E" };
                    const openNote = stringNotesMap[cell.string] || "E";
                    
                    let startIdx = sharps.indexOf(openNote);
                    if (startIdx === -1) startIdx = flats.indexOf(openNote);
                    if (startIdx === -1) startIdx = 4;
                    
                    // O violão é um instrumento transpositor de uma oitava inteira para cima na pauta
                    // clássica de clave de sol. Transpomos oitava + 1 para que a pauta fique perfeitamente
                    // limpa e idêntica às partituras tradicionais de conservatório de violão e guitarra!
                    const actualOctave = baseOctave + Math.floor((startIdx + cell.fret) / 12) + 1;
                    
                    // Transcreve para formato ABC
                    let abcNote = cell.note.trim();
                    if (abcNote.includes("#")) {
                        abcNote = "^" + abcNote.replace("#", "");
                    } else if (abcNote.includes("b")) {
                        abcNote = "_" + abcNote.replace("b", "");
                    }
                    
                    // Aplica as oitavas do ABC
                    let finalAbcNote = abcNote;
                    if (actualOctave === 2) {
                        finalAbcNote = abcNote + ",,";
                    } else if (actualOctave === 3) {
                        finalAbcNote = abcNote + ",";
                    } else if (actualOctave === 4) {
                        finalAbcNote = abcNote;
                    } else if (actualOctave === 5) {
                        finalAbcNote = abcNote.toLowerCase();
                    } else if (actualOctave === 6) {
                        finalAbcNote = abcNote.toLowerCase() + "'";
                    }
                    notesAbcList.push(finalAbcNote);
                });
                
                // Concatena as notas com compassos a cada 4 notas
                let groupedNotes = "";
                notesAbcList.forEach((n, idx) => {
                    groupedNotes += n + " ";
                    if ((idx + 1) % 4 === 0 && idx < notesAbcList.length - 1) {
                        groupedNotes += "| ";
                    }
                });
                abcString += groupedNotes;
            } else {
                // Pauta vazia se não houver notas
                abcString += "z4";
            }
            
            // Renderiza o SVG dinâmico responsivo
            const engine = typeof abcjs !== "undefined" ? abcjs : ABCJS;
            engine.renderAbc("guitarSheetMusic", abcString, { 
                responsive: "resize",
                scale: 1.1,
                add_classes: true,
                paddingtop: 15,
                paddingbottom: 15
            });
        }
    }
}
