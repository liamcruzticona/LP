/**
 * APP: Punto de entrada del frontend.
 * ABSTRACCIÓN: Inicializa componentes y conecta eventos de UI.
 */

let currentProfile = languageProfiles.c;

/* ── Actualización de perfil de lenguaje ── */

function actualizarPerfil(lenguaje) {
    currentProfile = languageProfiles[lenguaje];
    document.body.className = currentProfile.theme;
    document.getElementById("language-name").textContent = currentProfile.name;
    document.getElementById("language-tagline").textContent = currentProfile.tagline;
    document.getElementById("language-description").textContent = currentProfile.description;
    document.getElementById("language-theme").textContent = `Tema: ${currentProfile.name}`;
    document.getElementById("language-icon").innerHTML = `<i class="${currentProfile.icon}"></i>`;

    const keywordsNode = document.getElementById("language-keywords");
    keywordsNode.innerHTML = currentProfile.keywords.map(word => `<li>${word}</li>`).join("");

    document.getElementById("language-detect").textContent =
        `El sistema está configurado para ${currentProfile.name}.`;

    destacarColumnaComparador(lenguaje);
}

function cambiarLenguaje() {
    const lenguaje = document.getElementById("lenguaje-select").value;
    const profile = languageProfiles[lenguaje];
    if (!profile) return;

    editor.setOption("mode", obtenerModoPorLenguaje(lenguaje));
    editor.setValue(profile.examples[0]);
    actualizarPerfil(lenguaje);
}

/* ── Carga de ejemplos ── */

function cargarEjemploPorPerfil() {
    editor.setValue(currentProfile.examples[0]);
    editor.focus();
}

function cargarEjemploDeComparador() {
    const lenguaje = document.getElementById("lenguaje-select").value;
    editor.setValue(syntaxComparison.function[lenguaje]);
    editor.focus();
}

/* ── Comparador dinámico ── */

function destacarColumnaComparador(lenguaje) {
    document.querySelectorAll('.comparison-highlight').forEach(el => {
        el.classList.remove('comparison-highlight');
    });
    document.querySelectorAll(`[data-lang="${lenguaje}"]`).forEach(el => {
        el.classList.add('comparison-highlight');
    });
}

/* ── Inicialización ── */

document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btn-analizar');
    if (btn) btn.onclick = ejecutarAnalisis;
});

window.addEventListener('load', function () {
    actualizarPerfil('c');
});
