import { audioEngine } from './audio-engine.js';
import { Fretboard } from './fretboard.js'; // Importa a classe Fretboard

/**
 * Utilitários Globais da Aplicação Guitar Study.
 */
document.addEventListener("DOMContentLoaded", () => {
    // 1. Inicializa controle global de volume se houver slider de volume na página
    const volumeSlider = document.getElementById("globalVolume");
    if (volumeSlider) {
        // Restaura volume salvo
        const savedVol = localStorage.getItem("guitarVolume");
        if (savedVol !== null) {
            volumeSlider.value = savedVol;
            audioEngine.setVolume(parseFloat(savedVol));
        }

        volumeSlider.addEventListener("input", (e) => {
            const val = parseFloat(e.target.value);
            audioEngine.setVolume(val);
            localStorage.setItem("guitarVolume", val);
        });
    }

    // Inicializa botões de parar som globais
    const stopAudioBtn = document.getElementById("globalStopAudio");
    if (stopAudioBtn) {
        stopAudioBtn.addEventListener("click", () => {
            audioEngine.stop();
        });
    }

    // 2. Lógica específica para a página do Braço Livre (Fretboard)
    const fretboardContainer = document.getElementById("fretboard-container");
    if (fretboardContainer) {
        // Assumindo que a instância do Fretboard é criada e atribuída a window.fretboard na página
        const fretboard = window.fretboard;

        const toggleLinkingMode = document.getElementById('toggleLinkingMode');
        const colorPalette = document.getElementById('color-palette');

        if (fretboard && toggleLinkingMode && colorPalette) {
            // Ativa/desativa o modo de ligação de notas
            toggleLinkingMode.addEventListener('change', (e) => {
                const isLinking = e.target.checked;
                fretboard.linkingState.isLinking = isLinking;

                // Mostra ou esconde a paleta de cores
                colorPalette.style.display = isLinking ? 'flex' : 'none';
                colorPalette.style.display = isLinking ? 'flex' : 'none !important;';


                if (!isLinking && fretboard.linkingState.startCell) {
                    // Limpa a seleção visual se o modo for desativado no meio de uma ligação
                    const badge = fretboard.linkingState.startCell.querySelector('.fret-note');
                    if (badge) badge.style.boxShadow = '';
                    fretboard.linkingState.startCell = null;
                }
            });

            // Cria os botões de cores dinamicamente
            fretboard.blockLinkColors.forEach((color, index) => {
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm rounded-circle';
                btn.style.backgroundColor = color;
                btn.style.width = '25px';
                btn.style.height = '25px';
                btn.dataset.color = color;
                if (index === 0) {
                    btn.style.border = '2px solid white'; // Destaque inicial
                }
                colorPalette.appendChild(btn);
            });

            // Lógica para selecionar a cor na paleta
            colorPalette.addEventListener('click', (e) => {
                if (e.target.dataset.color) {
                    fretboard.linkingState.color = e.target.dataset.color;
                    // Atualiza o destaque visual para o botão de cor selecionado
                    Array.from(colorPalette.children).forEach(child => child.style.border = 'none');
                    e.target.style.border = '2px solid white';
                }
            });

            // Ouve o evento para salvar a conexão (exemplo)
            fretboard.container.addEventListener('connection-added', (e) => {
                console.log('Nova conexão de bloco para salvar:', e.detail);
                // Aqui você faria uma chamada fetch para sua API para salvar e.detail no banco.
            });
        }
    }
});

/**
 * Função global para gerenciar favoritos (adicionar/remover).
 * Altera a cor do ícone no Frontend e sincroniza com a tabela 'favorites' no PostgreSQL.
 * @param {HTMLElement} buttonEl - O elemento do botão clicado.
 * @param {string} category - 'scale', 'mode', 'chord'
 * @param {string} itemKey - Identificador (Ex: "C_major")
 */
export async function toggleFavorite(buttonEl, category, itemKey) {
    if (!buttonEl) return;

    const isFavorited = buttonEl.classList.contains("favorited");
    const icon = buttonEl.querySelector("i");

    try {
        if (isFavorited) {
            // Remove dos favoritos
            const response = await fetch(`${window.APP_PREFIX || ""}/guitar-study/api/v1/favorites`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category, item_key: itemKey })
            });
            const res = await response.json();
            if (res.success) {
                buttonEl.classList.remove("favorited");
                if (icon) {
                    icon.classList.remove("bi-heart-fill");
                    icon.classList.add("bi-heart");
                }
                showToast("Removido dos favoritos!", "info");
            }
        } else {
            // Adiciona aos favoritos
            const response = await fetch(`${window.APP_PREFIX || ""}/guitar-study/api/v1/favorites`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category, item_key: itemKey })
            });
            const res = await response.json();
            if (res.success) {
                buttonEl.classList.add("favorited");
                if (icon) {
                    icon.classList.remove("bi-heart");
                    icon.classList.add("bi-heart-fill");
                }
                showToast("Adicionado aos favoritos!", "success");
            }
        }
    } catch (e) {
        console.error("Erro ao favoritar item:", e);
        showToast("Ocorreu um erro de rede ao gerenciar favoritos.", "danger");
    }
}

/**
 * Registra uma nova sessão de estudos.
 * @param {string} category - 'fretboard', 'scale', 'mode', 'chord', 'exercise'
 * @param {string} itemKey - O item estudado
 * @param {number} durationMinutes - Tempo estudado
 * @param {string} notes - Notas pessoais
 */
export async function registerStudySession(category, itemKey, durationMinutes, notes = "") {
    try {
        const response = await fetch(`${window.APP_PREFIX || ""}/guitar-study/api/v1/study-sessions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                category,
                item_key: itemKey,
                duration_minutes: durationMinutes,
                notes
            })
        });
        const res = await response.json();
        return res.success;
    } catch (e) {
        console.error("Erro ao registrar sessão:", e);
        return false;
    }
}

/**
 * Mostra uma mensagem flutuante (Toast) elegante usando Bootstrap.
 */
export function showToast(message, type = "success") {
    // Procura por container de toast ou cria um dinamicamente
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container position-fixed bottom-0 end-0 p-3";
        container.style.zIndex = "1055";
        document.body.appendChild(container);
    }

    const toastId = "toast_" + Date.now();
    const bgClass = type === "danger" ? "bg-danger" : (type === "info" ? "bg-info" : (type === "warning" ? "bg-warning" : "bg-success"));

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3000">
            <div class="d-flex">
                <div class="toast-body fw-medium">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML("beforeend", toastHtml);
    const toastEl = document.getElementById(toastId);

    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();

    // Remove do DOM após sumir
    toastEl.addEventListener("hidden.bs.toast", () => {
        toastEl.remove();
    });
}

// Vincula ao escopo global (window) para facilitar o acesso nos templates HTML legado do Jinja2
window.toggleFavorite = toggleFavorite;
window.registerStudySession = registerStudySession;
window.showToast = showToast;
