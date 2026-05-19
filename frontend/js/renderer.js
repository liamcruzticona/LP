/**
 * RENDERER: Visualización de AST, estadísticas y resultados.
 * ABSTRACCIÓN: Funciones puras que transforman datos en HTML.
 */

function renderAST(ast) {
    if (!ast || !Array.isArray(ast) || ast.length === 0) {
        if (ast && ast.tipo === 'error') return `<p class="text-danger">Error: ${ast.mensaje || 'desconocido'}</p>`;
        return '<p class="code-meta">AST vacio o codigo invalido.</p>';
    }
    return `<ul>${ast.map(nodo => renderNodo(nodo)).join("")}</ul>`;
}

function renderNodo(nodo) {
    if (typeof nodo !== 'object' || nodo === null) {
        return `<li>${String(nodo)}</li>`;
    }
    const tipo = nodo.tipo || 'nodo';
    const props = Object.entries(nodo).filter(([key]) => key !== 'tipo');
    return `<li><strong>${tipo}</strong>${props.length ? `: ${props.map(([key, value]) => `<div class="ps-3"><em>${key}</em> ${renderValor(value)}</div>`).join('')}` : ''}</li>`;
}

function renderValor(value) {
    if (Array.isArray(value)) {
        return `<ul>${value.map(item => renderNodo(item)).join('')}</ul>`;
    }
    if (typeof value === 'object' && value !== null) {
        return `<ul>${renderNodo(value)}</ul>`;
    }
    return `<span>${String(value)}</span>`;
}

function renderStats(data) {
    if (!data.estadisticas) {
        document.getElementById('stats-content').textContent = 'No hay estadisticas.';
        return;
    }
    const s = data.estadisticas;
    let h = 'ENTROPIA DE SHANNON\n===================\n\n';
    h += 'Entropia: ' + s.entropia_shannon + '\n';
    h += 'Entropia maxima: ' + s.entropia_maxima + '\n';
    h += 'Normalizacion (0-1): ' + s.normalizacion + '\n';
    h += 'Total tokens: ' + s.total_tokens + '\n';
    h += 'Tipos unicos: ' + s.tipos_unicos + '\n';
    h += 'Densidad: ' + s.densidad + '\n\nDISTRIBUCION:\n-------------\n';
    for (const t in s.distribucion) {
        if (s.distribucion.hasOwnProperty(t)) {
            const inf = s.distribucion[t];
            h += t + ': ' + inf.frecuencia + ' (' + inf.porcentaje + '%)\n';
        }
    }
    document.getElementById('stats-content').textContent = h;

    actualizarPanelEntropia(data);
}

function actualizarPanelEntropia(data) {
    const barEl = document.getElementById('entropy-bar-fill');
    if (!barEl || !data.estadisticas) return;
    const norm = data.estadisticas.normalizacion || 0;
    barEl.style.width = (norm * 100) + '%';
    const porcentaje = (norm * 100).toFixed(1);
    barEl.textContent = porcentaje > 15 ? porcentaje + '%' : '';

    const valorEl = document.getElementById('entropy-value');
    if (valorEl) valorEl.textContent = data.estadisticas.entropia_shannon;

    const maxEl = document.getElementById('entropy-max');
    if (maxEl) maxEl.textContent = data.estadisticas.entropia_maxima;

    const uniqueEl = document.getElementById('entropy-unique');
    if (uniqueEl) uniqueEl.textContent = data.estadisticas.tipos_unicos;
}

/* ── Copiar al portapapeles ── */

function copiarTab(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const texto = el.textContent || el.innerText || '';
    navigator.clipboard.writeText(texto).then(function () {
        const btn = document.querySelector(`[onclick="copiarTab('${elementId}')"]`);
        if (btn) {
            btn.innerHTML = '<i class="fas fa-check"></i>';
            btn.classList.add('copied');
            setTimeout(function () {
                btn.innerHTML = '<i class="fas fa-copy"></i>';
                btn.classList.remove('copied');
            }, 1500);
        }
    }).catch(function () {
        alert('No se pudo copiar al portapapeles');
    });
}
