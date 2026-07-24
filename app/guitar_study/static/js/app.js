import { audioEngine } from './audio-engine.js';

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
            const response = await fetch("/guitar-study/api/v1/favorites", {
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
            const response = await fetch("/guitar-study/api/v1/favorites", {
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
        const response = await fetch("/guitar-study/api/v1/study-sessions", {
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
