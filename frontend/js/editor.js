/**
 * EDITOR: Configuración de CodeMirror.
 * ENCAPSULAMIENTO: Toda la inicialización y eventos del editor aquí.
 */

const editor = CodeMirror(document.getElementById("editor"), {
    value: languageProfiles.c.examples[0],
    mode: obtenerModoPorLenguaje("c"),
    theme: "material-darker",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autoCloseBrackets: true,
    matchBrackets: true,
    extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-Enter": function () { ejecutarAnalisis(); }
    },
    hintOptions: {
        completeSingle: false
    }
});

editor.on("keyup", (cm, event) => {
    if (!cm.state.completionActive && /[\w.]/.test(event.key)) {
        CodeMirror.commands.autocomplete(cm, null, { completeSingle: false });
    }
    actualizarDeteccion();
});

function actualizarDeteccion() {
    document.getElementById("language-detect").textContent =
        detectarLenguaje() || `El sistema está configurado para ${currentProfile.name}.`;
}

function limpiar() {
    editor.setValue("");
    document.getElementById("tokens-content").textContent = "";
    document.getElementById("ast-tree").textContent = "";
    document.getElementById("ast-content").textContent = "";
    document.getElementById("semantica-content").textContent = "";
    document.getElementById("stats-content").textContent = "";
    document.getElementById("hint-status").textContent = "";
    document.getElementById("entropy-bar-fill").style.width = "0%";
    document.getElementById("entropy-value").textContent = "--";
    document.getElementById("entropy-max").textContent = "--";
    document.getElementById("entropy-unique").textContent = "--";
}
