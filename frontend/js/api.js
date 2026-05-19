/**
 * API: Comunicación con el backend.
 * ENCAPSULAMIENTO: Toda la lógica de fetch y manejo de errores aquí.
 */

async function ejecutarAnalisis() {
    const codigo = editor.getValue().trim();
    if (!codigo) {
        alert('Escribe código para analizar');
        return;
    }

    const spinner = document.getElementById('spinner');
    const hint = document.getElementById('hint-status');
    hint.innerHTML = '<span class="spinner"></span> Analizando...';

    try {
        const res = await fetch(CONFIG.API_URL + '/analizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                codigo: codigo,
                lenguaje: document.getElementById('lenguaje-select').value
            })
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);

        document.getElementById('tokens-content').textContent = JSON.stringify(data.tokens, null, 2);
        document.getElementById('ast-tree').innerHTML = renderAST(data.ast);
        document.getElementById('ast-content').textContent = JSON.stringify(data.ast, null, 2);
        document.getElementById('semantica-content').textContent =
            data.validacion && data.validacion.exito
                ? 'Validacion semantica correcta'
                : (data.validacion ? 'Errores semanticos:\n' + (data.validacion.errores || []).map(function (e) {
                    return 'Linea ' + (e.linea || '?') + ': ' + e.mensaje;
                }).join('\n') : 'Sin info');

        renderStats(data);
        hint.textContent = 'Analisis completado.';
    } catch (err) {
        hint.textContent = 'Error: ' + (err.message || err);
        document.getElementById('semantica-content').textContent = 'Error de conexion.';
        document.getElementById('stats-content').textContent = '';
        console.error(err);
        alert('ERROR: No se pudo conectar a ' + CONFIG.API_URL + '\n\nDetalle: ' + (err.message || err) + '\n\nVerifica que el backend este corriendo.');
    }
}
