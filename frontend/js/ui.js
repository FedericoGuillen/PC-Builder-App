/**
 * ui.js
 * Utilidades de interfaz compartidas por las pantallas de armado.
 *
 * No crea ni modifica la estructura base del HTML: solamente actualiza
 * los elementos existentes (tarjetas, dropzones, botones y alertas).
 */

const ICONOS_POR_TIPO = Object.freeze({
    CPU: '🔳',
    PROCESADOR: '🔳',
    COOLER: '❄',
    DISIPADOR: '❄',
    RAM: '▤',
    MEMORIA: '▤',
    GPU: '🎮',
    'TARJETA GRAFICA': '🎮',
    'TARJETA GRÁFICA': '🎮',
    ALMACENAMIENTO: '💽',
    'M.2': '💽',
    SSD: '💽',
    STORAGE: '💽',
    PSU: '🔌',
    FUENTE: '🔌',
    'FUENTE DE PODER': '🔌',
    GABINETE: '🖥',
    CASE: '🖥',
    MOTHERBOARD: '▦',
    'PLACA MADRE': '▦'
});

const NOMBRES_POR_CATEGORIA = Object.freeze({
    CPU: 'CPU',
    CPU_COOLER: 'Disipador',
    MOTHERBOARD: 'Motherboard',
    RAM: 'RAM',
    GPU: 'Tarjeta Gráfica',
    PSU: 'Fuente de Poder',
    STORAGE: 'Almacenamiento',
    CASE: 'Gabinete'
});

export function escaparHTML(valor = '') {
    return String(valor).replace(/[&<>"']/g, (caracter) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[caracter]));
}

export function obtenerNombreTipo(componente) {
    const tipo = componente?.tipo;
    if (tipo && typeof tipo === 'object') {
        return tipo.nombre || tipo.nombre_tipo || 'Componente';
    }

    if (tipo) return tipo;

    const categoria = componente?.categoria;
    if (categoria) {
        return NOMBRES_POR_CATEGORIA[categoria] || categoria;
    }

    return componente?.tipo_componente || 'Componente';
}

export function obtenerIcono(componente) {
    const tipo = obtenerNombreTipo(componente).toUpperCase();
    return ICONOS_POR_TIPO[tipo] || '⚙️';
}

function obtenerEspecificaciones(componente) {
    const especificaciones = componente?.especificaciones;

    if (!especificaciones) return {};

    if (typeof especificaciones === 'string') {
        try {
            return JSON.parse(especificaciones);
        } catch (error) {
            return {};
        }
    }

    return especificaciones;
}

/**
 * Devuelve los watts que conviene mostrar en la tarjeta.
 *
 * Para las fuentes se muestra la potencia entregada (`potencia_w` / `watts`),
 * no su consumo. Para el resto se usa el consumo del componente.
 */
function obtenerWattsComponente(componente) {
    const tipo = obtenerNombreTipo(componente).toUpperCase();
    const especificaciones = obtenerEspecificaciones(componente);

    if (['PSU', 'FUENTE', 'FUENTE DE PODER'].includes(tipo)) {
        return especificaciones.potencia_w
            ?? especificaciones.watts
            ?? componente?.consumo_watts
            ?? '';
    }

    return componente?.consumo_watts
        ?? especificaciones.consumo_w
        ?? componente?.watts
        ?? '';
}

/**
 * Devuelve el HTML de una tarjeta con las mismas clases que usa el maquetado.
 * Se expone para poder reutilizar el renderizado en cualquier pantalla.
 */
export function renderizarTarjetaComponente(componente, opciones = {}) {
    const {
        id = '',
        draggable = false,
        inactiva = false,
        descripcion = componente?.descripcion || '',
        pista = ''
    } = opciones;

    const nombre = componente?.nombre || componente?.name || 'Componente';
    const tipo = obtenerNombreTipo(componente);
    const icono = obtenerIcono(componente);
    const watts = obtenerWattsComponente(componente);
    const idComponente = componente?.id_componente ?? componente?.id ?? '';
    const wattsTexto = watts === '' || watts == null
        ? ''
        : (/w$/i.test(String(watts).trim()) ? String(watts).trim() : `${watts} W`);

    return `
        <div class="component-card${inactiva ? ' component-card-inactive' : ''}"
             ${draggable ? 'draggable="true"' : ''}
             ${id ? `id="${escaparHTML(id)}"` : ''}
             ${idComponente !== '' ? `data-id="${escaparHTML(idComponente)}"` : ''}>
            <div class="comp-top">
                <div class="comp-icon">${icono}</div>
                <div class="comp-info">
                    <div class="comp-type">${escaparHTML(tipo)}</div>
                    <div class="comp-name">${escaparHTML(nombre)}</div>
                </div>
                ${wattsTexto !== '' ? `<div class="comp-watts">${escaparHTML(wattsTexto)}</div>` : ''}
            </div>
            ${descripcion ? `<div class="comp-desc">${escaparHTML(descripcion)}</div>` : ''}
            ${pista ? `<div class="drag-hint">${escaparHTML(pista)}</div>` : ''}
        </div>
    `;
}

export function renderizarTarjetasComponentes(contenedor, componentes = [], opciones = {}) {
    if (!contenedor) return [];

    contenedor.innerHTML = componentes
        .map((componente) => renderizarTarjetaComponente(componente, opciones))
        .join('');

    return Array.from(contenedor.querySelectorAll('.component-card'));
}

/**
 * Renderiza todas las tarjetas dentro de un inventario existente.
 *
 * Conserva el encabezado y cualquier contenido extra del maquetado (por
 * ejemplo, el enlace al video) y reemplaza únicamente las tarjetas viejas.
 * No aplica ningún límite de cantidad: pinta todos los componentes recibidos.
 */
export function renderizarInventario(contenedor, componentes = [], opciones = {}) {
    if (!contenedor) return [];

    const {
        draggable = true,
        pista = '',
        descripcion = null
    } = opciones;

    contenedor.querySelectorAll('.component-card').forEach((tarjeta) => {
        tarjeta.remove();
    });

    const encabezado = contenedor.querySelector('.inventory-header');
    const fragmento = document.createDocumentFragment();

    componentes.forEach((componente) => {
        const descripcionComponente = typeof descripcion === 'function'
            ? descripcion(componente)
            : (descripcion || componente?.descripcion || '');

        const plantilla = document.createElement('div');
        plantilla.innerHTML = renderizarTarjetaComponente(componente, {
            draggable,
            pista,
            descripcion: descripcionComponente
        }).trim();

        const tarjeta = plantilla.firstElementChild;
        if (!tarjeta) return;

        // Guardamos la referencia completa para no depender de parsear el DOM.
        tarjeta.__componente = componente;
        fragmento.appendChild(tarjeta);
    });

    if (encabezado) {
        encabezado.after(fragmento);
    } else {
        contenedor.prepend(fragmento);
    }

    if (encabezado) {
        const contador = encabezado.querySelector('span');
        if (contador) {
            contador.textContent = `${componentes.length} disponible${componentes.length === 1 ? '' : 's'}`;
        }
    }

    return Array.from(contenedor.querySelectorAll('.component-card'));
}

/**
 * Actualiza el número de watts y la capacidad mostrada en el panel derecho.
 */
export function actualizarConsumo(watts, capacidad = 650, opciones = {}) {
    const stats = document.querySelector('.stats-value');
    if (!stats) return null;

    const conservarId = Boolean(stats.querySelector('#capacity-text'));
    const spanInicio = conservarId ? '<span id="capacity-text">' : '<span>';
    stats.innerHTML = `${watts} ${spanInicio}Watts en uso / ${capacidad} W</span>`;

    const etiquetaCapacidad = stats.querySelector('#capacity-text');
    if (etiquetaCapacidad && opciones.resaltarCapacidad) {
        etiquetaCapacidad.style.color = '#3fb950';
    }

    return stats;
}

/**
 * Actualiza solamente la capacidad de la fuente, conservando el consumo actual.
 */
export function actualizarCapacidad(capacidad = 650) {
    const stats = document.querySelector('.stats-value');
    if (!stats) return null;

    const consumoActual = Number.parseInt(stats.textContent, 10) || 0;
    stats.innerHTML = `${consumoActual} <span id="capacity-text">Watts en uso / ${capacidad} W</span>`;

    const etiquetaCapacidad = stats.querySelector('#capacity-text');
    if (etiquetaCapacidad) {
        etiquetaCapacidad.style.color = '#3fb950';
    }

    return stats;
}

/* -------------------------------------------------------------------------- */
/* Estados de arrastre                                                         */
/* -------------------------------------------------------------------------- */

export function marcarZonaDisponible(dropzone) {
    if (dropzone) dropzone.style.borderColor = '#58a6ff';
}

export function resaltarZona(dropzone) {
    if (dropzone) dropzone.style.backgroundColor = 'rgba(88, 166, 255, 0.2)';
}

export function restablecerZona(dropzone) {
    if (dropzone) dropzone.style.backgroundColor = 'rgba(63, 185, 80, 0.1)';
}

export function marcarZonaInstalada(dropzone, contenido, estilos = {}) {
    if (!dropzone) return;

    dropzone.style.border = estilos.borde || '1px solid #161b22';
    dropzone.style.backgroundColor = estilos.fondo || '#1f2937';
    dropzone.style.animation = 'none';
    dropzone.innerHTML = contenido || '';
}

export function marcarTarjetaInstalada(tarjeta) {
    if (!tarjeta) return;

    tarjeta.setAttribute('draggable', 'false');
    tarjeta.classList.add('component-card-inactive');
    tarjeta.style.cursor = 'default';
}

export function habilitarBotonSiguiente(boton, colorSombra = 'rgba(88, 166, 255, 0.6)') {
    if (!boton) return;

    boton.style.boxShadow = `0 0 20px ${colorSombra}`;
    boton.style.transform = 'scale(1.02)';
}

export function actualizarEstadoBoton(boton, habilitado = true) {
    if (!boton) return;

    boton.disabled = !habilitado;
    boton.style.opacity = habilitado ? '1' : '0.6';
    boton.style.cursor = habilitado ? '' : 'not-allowed';
}

/* -------------------------------------------------------------------------- */
/* Alertas y diagnóstico                                                       */
/* -------------------------------------------------------------------------- */

const ESTILOS_ALERTA = Object.freeze({
    exito: {
        color: 'var(--accent-green, #3fb950)',
        fondo: 'rgba(63, 185, 80, 0.08)'
    },
    error: {
        color: 'var(--accent-red, #da3633)',
        fondo: 'rgba(218, 54, 51, 0.08)'
    },
    advertencia: {
        color: '#e3b341',
        fondo: 'rgba(227, 179, 65, 0.08)'
    },
    info: {
        color: 'var(--accent-blue, #58a6ff)',
        fondo: 'rgba(88, 166, 255, 0.08)'
    }
});

export function mostrarAlerta(contenedor, opciones = {}) {
    if (!contenedor) return;

    const {
        tipo = 'info',
        titulo = '',
        mensaje = '',
        items = [],
        htmlExtra = ''
    } = opciones;

    const estilo = ESTILOS_ALERTA[tipo] || ESTILOS_ALERTA.info;
    contenedor.style.borderColor = estilo.color;
    contenedor.style.backgroundColor = estilo.fondo;

    const lista = Array.isArray(items) && items.length > 0
        ? `<ul style="color: ${estilo.color};">${items
            .map((item) => `<li><span>${escaparHTML(item)}</span></li>`)
            .join('')}</ul>`
        : '';

    contenedor.innerHTML = `
        ${titulo ? `<h4 style="color: ${estilo.color};">${escaparHTML(titulo)}</h4>` : ''}
        ${mensaje ? `<p>${escaparHTML(mensaje)}</p>` : ''}
        ${lista}
        ${htmlExtra}
    `;
}

function listaConTitulo(mensajes, titulo, color) {
    if (!Array.isArray(mensajes) || mensajes.length === 0) return '';

    return `
        <h4 style="color: ${color}; margin-top: 10px;">${escaparHTML(titulo)}</h4>
        <ul>${mensajes
            .map((mensaje) => `<li><span>${escaparHTML(mensaje)}</span></li>`)
            .join('')}</ul>
    `;
}

export function mostrarDiagnostico(contenedor, resultado = {}) {
    if (!contenedor) return;

    const advertencias = Array.isArray(resultado.advertencias) ? resultado.advertencias : [];
    const errores = Array.isArray(resultado.errores) ? resultado.errores : [];
    const compatible = Boolean(resultado.es_compatible) && errores.length === 0;

    if (compatible) {
        mostrarAlerta(contenedor, {
            tipo: 'exito',
            titulo: '✅ Compatibilidad Verificada',
            mensaje: advertencias.length > 0
                ? 'La configuración es compatible. Revisá las advertencias antes de encender la PC.'
                : 'Todos los componentes seleccionados son compatibles entre sí.',
            htmlExtra: listaConTitulo(advertencias, 'Advertencias', '#e3b341')
        });
        return;
    }

    const problemas = errores.length > 0
        ? errores
        : (advertencias.length > 0
            ? advertencias
            : ['La configuración no superó la validación de compatibilidad.']);

    mostrarAlerta(contenedor, {
        tipo: 'error',
        titulo: '❌ Incompatibilidad Detectada',
        mensaje: 'La configuración no es compatible. Corregí los siguientes problemas:',
        items: problemas,
        htmlExtra: errores.length > 0
            ? listaConTitulo(advertencias, 'Advertencias', '#e3b341')
            : ''
    });
}

export function mostrarErrorConexion(contenedor, mensaje = '') {
    mostrarAlerta(contenedor, {
        tipo: 'error',
        titulo: 'Error de Conexión',
        mensaje: `No se pudo conectar con el servidor de validación (${mensaje}). Revisa que Uvicorn esté en ejecución.`
    });
}

/* -------------------------------------------------------------------------- */
/* Inventario final                                                            */
/* -------------------------------------------------------------------------- */

export function renderizarInventarioFinal(contenedor, componentes = []) {
    if (!contenedor) return;

    const items = componentes.map((componente) => {
        const nombre = componente?.nombre || 'Componente';
        const tipo = obtenerNombreTipo(componente);

        return `
            <div class="final-item">
                <div class="final-icon">${obtenerIcono(componente)}</div>
                <div class="final-info">
                    <div class="final-name">${escaparHTML(nombre)}</div>
                    <div class="final-type">${escaparHTML(tipo)}</div>
                </div>
                <div class="final-check">✔</div>
            </div>
        `;
    }).join('');

    contenedor.innerHTML = `
        <div class="inventory-header">
            <h3>Componentes Instalados (${componentes.length})</h3>
        </div>
        ${items}
    `;
}
