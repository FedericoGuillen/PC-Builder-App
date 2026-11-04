const API_BASE = 'http://127.0.0.1:8000/api/v1';

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Obtener los IDs guardados en el flujo o usar los por defecto para pruebas
    const componentesIds = JSON.parse(localStorage.getItem('componentes_seleccionados')) || [1, 9, 5, 13, 17, 21, 25, 29];
    const idPerfil = Number(localStorage.getItem('id_perfil')) || 1;

    const summaryBox = document.querySelector('.summary-box');
    const inventoryBox = document.querySelector('.inventory-box');

    try {
        // 2. Consulta al backend de validación
        const response = await fetch(`${API_BASE}/compatibilidad/validar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                id_perfil: idPerfil,
                componentes_ids: componentesIds
            })
        });

        if (!response.ok) {
            throw new Error(`Error en el servidor (${response.status})`);
        }

        const resultado = await response.json();

        // 3. Actualizar la caja de diagnóstico con la respuesta de FastAPI
        if (summaryBox) {
            if (resultado.es_compatible) {
                summaryBox.style.borderColor = 'var(--accent-green)';
                summaryBox.style.backgroundColor = 'rgba(63, 185, 80, 0.08)';
                
                let advertenciasHTML = '';
                if (resultado.advertencias && resultado.advertencias.length > 0) {
                    advertenciasHTML = `
                        <h4 style="color: #e3b341; margin-top: 10px;">Advertencias:</h4>
                        <ul>${resultado.advertencias.map(adv => `<li><span>${adv}</span></li>`).join('')}</ul>
                    `;
                }

                summaryBox.innerHTML = `
                    <h4 style="color: var(--accent-green);">Diagnóstico: ¡Configuración Compatible!</h4>
                    <p>La validación de reglas de dominio confirmó que la fuente, sockets y requerimientos eléctricos son correctos.</p>
                    ${advertenciasHTML}
                `;
            } else {
                summaryBox.style.borderColor = 'var(--accent-red)';
                summaryBox.style.backgroundColor = 'rgba(218, 54, 51, 0.08)';
                
                const listaErrores = resultado.errores.map(err => `<li><span>${err}</span></li>`).join('');
                summaryBox.innerHTML = `
                    <h4 style="color: var(--accent-red);">Diagnóstico: Incompatibilidad Detectada</h4>
                    <p>Se detectaron problemas de compatibilidad en la configuración seleccionada:</p>
                    <ul style="color: #f85149;">${listaErrores}</ul>
                `;
            }
        }

        // 4. Traer la lista real de componentes desde PostgreSQL y renderizar en el inventario
        cargarInventarioReal(componentesIds, inventoryBox);

    } catch (error) {
        console.error("Error al validar con el servidor:", error);
        if (summaryBox) {
            summaryBox.style.borderColor = 'var(--accent-red)';
            summaryBox.innerHTML = `
                <h4 style="color: var(--accent-red);">Error de Conexión</h4>
                <p>No se pudo conectar con el servidor de validación (${error.message}). Revisa que Uvicorn esté en ejecución.</p>
            `;
        }
    }
});

/**
 * Consulta los datos de los componentes a PostgreSQL para renderizarlos en la Columna 3
 */
async function cargarInventarioReal(ids, contenedor) {
    if (!contenedor) return;

    try {
        const res = await fetch(`${API_BASE}/componentes`);
        if (!res.ok) return;
        
        const todosLosComponentes = await res.json();
        
        // Filtrar solo los componentes elegidos
        const seleccionados = todosLosComponentes.filter(c => ids.includes(c.id_componente));

        if (seleccionados.length === 0) return;

        let html = `
            <div class="inventory-header">
                <h3>Componentes Instalados (${seleccionados.length})</h3>
            </div>
        `;

        seleccionados.forEach(c => {
            const nombreTipo = typeof c.tipo === 'object' ? c.tipo.nombre : (c.tipo || 'Componente');
            html += `
                <div class="final-item">
                    <div class="final-icon">⚙️</div>
                    <div class="final-info">
                        <div class="final-name">${c.nombre}</div>
                        <div class="final-type">${nombreTipo}</div>
                    </div>
                    <div class="final-check">✔</div>
                </div>
            `;
        });

        contenedor.innerHTML = html;

    } catch (e) {
        console.error("Error al cargar detalles de inventario:", e);
    }
}