/**
 * armado.js
 * Punto de entrada del flujo de armado.
 *
 * Detecta la pantalla actual y reutiliza los módulos storage.js y ui.js.
 * De esta forma todas las páginas comparten la misma lógica de arrastre,
 * guardado y actualización visual.
 */

import {
    guardarComponente,
    guardarComponentes,
    guardarCpuId,
    guardarPlataforma,
    limpiarSeleccion,
    obtenerComponente,
    obtenerIdsSeleccionados,
    obtenerPerfil,
    obtenerPlataforma,
    quitarComponenteSeleccionado
} from './storage.js';

import {
    actualizarConsumo,
    actualizarEstadoBoton,
    calcularConsumoTotal,
    escaparHTML,
    habilitarBotonSiguiente,
    marcarTarjetaInstalada,
    marcarZonaDisponible,
    marcarZonaInstalada,
    mostrarAlerta,
    mostrarDiagnostico,
    mostrarErrorConexion,
    renderizarInventario,
    renderizarInventarioFinal,
    resaltarZona,
    restablecerZona
} from './ui.js';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

const PLATAFORMAS = Object.freeze({
    AMD: {
        ids: [1, 9, 5, 13, 17, 21, 25, 29],
        chipset: 'B650',
        socket: 'AM5',
        imagen: 'mother-amd.jpg',
        encabezado: 'Placa madre B650 • AM5 • Micro-ATX'
    },
    Intel: {
        ids: [3, 11, 6, 14, 18, 22, 26, 30],
        chipset: 'B760',
        socket: 'LGA 1700',
        imagen: 'mother-intel.jpg',
        encabezado: 'Placa madre B760 • LGA 1700 • Micro-ATX'
    }
});

let nombreCpuActual = 'Ryzen 5 7600';
let plataformaActual = 'AMD';
let compatibilidadVerificada = false;
let arrastreActual = null;
let componentesCache = null;

/**
 * Orden histórico de los IDs por defecto de cada plataforma.
 * Se usa para quitar los IDs "placeholder" cuando el usuario elige un
 * componente real desde el backend.
 */
const INDICE_PLACEHOLDER_POR_TIPO = Object.freeze({
    cpu: 0,
    motherboard: 1,
    cooler: 2,
    ram: 3,
    almacenamiento: 4,
    gpu: 5,
    psu: 6,
    gabinete: 7
});

/**
 * Componentes que deben estar guardados para habilitar "Finalizar Armado".
 * El gabinete no se elige en el flujo: se usa el modelo predeterminado de la
 * plataforma, por eso no se exige como slot.
 */
const SLOTS_REQUERIDOS_ARMADO = Object.freeze([
    { tipo: 'cpu', etiqueta: 'CPU', articulo: 'el' },
    { tipo: 'motherboard', etiqueta: 'Motherboard', articulo: 'la' },
    { tipo: 'ram', etiqueta: 'RAM', articulo: 'la' },
    { tipo: 'cooler', etiqueta: 'Disipador', articulo: 'el' },
    { tipo: 'almacenamiento', etiqueta: 'Almacenamiento', articulo: 'el' },
    { tipo: 'psu', etiqueta: 'Fuente de Poder', articulo: 'la' },
    { tipo: 'gpu', etiqueta: 'Tarjeta Gráfica', articulo: 'la' }
]);

function htmlCpuInstalado(nombre) {
    return `
        <div style="font-size: 2rem; margin-bottom: 5px;">🔳</div>
        <div style="font-weight: bold; color: white; font-size: 0.85rem;">${escaparHTML(nombre)}</div>
        <div style="font-size:0.65rem; color:#3fb950; font-weight: 600; margin-top:4px;">✔ INSTALADO</div>
    `;
}

const PASOS = Object.freeze({
    cpu: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone',
        tipo: 'cpu',
        categoria: 'CPU',
        pista: '⇱ Arrastra al socket de CPU resaltado',
        capacidad: 650,
        installedHTML: (componente) => htmlCpuInstalado(
            componente?.nombre || nombreCpuActual
        ),
        estilosZona: { borde: '1px solid #30363d', fondo: '#161b22' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    ram: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone-ram',
        tipo: 'ram',
        categoria: 'RAM',
        pista: '⇱ Arrastra a las ranuras DIMM',
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 1.2rem; color: #4b5563; display: flex; gap: 4px; height: 100%;">
                <div style="width: 10px; background: #30363d; height: 100%; border-radius: 2px;"></div>
                <div style="width: 10px; background: #30363d; height: 100%; border-radius: 2px;"></div>
            </div>
        `,
        estilosZona: { borde: '1px solid #30363d', fondo: '#161b22' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    cooler: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone-cooler',
        tipo: 'cooler',
        categoria: 'CPU_COOLER',
        pista: '⇱ Arrastra el disipador sobre el CPU',
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 2.5rem; color: #8b949e;">❄</div>
            <div style="font-size: 0.65rem; color: #3fb950; font-weight: bold; margin-top: 5px;">✔ CONECTADO</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#1f2937' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    almacenamiento: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone-m2',
        tipo: 'almacenamiento',
        categoria: 'STORAGE',
        pista: '⇱ Arrastra el M.2 a la ranura',
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 0.55rem; color: #3fb950; font-weight: bold; pointer-events: none;">✔ INSTALADO</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#30363d' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    psu: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone-psu',
        tipo: 'psu',
        categoria: 'PSU',
        pista: '⇱ Arrastra la fuente a su bahía',
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 2rem; color: #8b949e; margin-bottom: 5px;">🔌</div>
            <div style="font-size: 0.75rem; color: #3fb950; font-weight: bold; pointer-events: none;">✔ ATORNILLADA</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#1f2937' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    gpu: {
        contenedorSelector: '.inventory-box',
        dropzoneSelector: '.dropzone-gpu',
        tipo: 'gpu',
        categoria: 'GPU',
        pista: '⇱ Arrastra la GPU al slot PCIe',
        capacidad: 650,
        resaltarCapacidad: true,
        finalizaArmado: true,
        installedHTML: `
            <div style="font-size: 1.5rem; color: #8b949e; margin-bottom: 2px;">🎮</div>
            <div style="font-size: 0.75rem; color: #3fb950; font-weight: bold; pointer-events: none;">✔ CONECTADA</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#1f2937' },
        colorBoton: 'rgba(63, 185, 80, 0.6)'
    }
});

function paginaActual() {
    const archivo = window.location.pathname.split('/').pop() || '';
    return archivo.replace(/\.html$/i, '').toLowerCase();
}

function plataformaDePagina() {
    const pagina = paginaActual();
    if (pagina.includes('intel')) return 'Intel';
    if (pagina.includes('-amd')) return 'AMD';
    return null;
}

function alCargarDocumento(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
        callback();
    }
}

function contenidoInstalado(paso, componente) {
    return typeof paso.installedHTML === 'function'
        ? paso.installedHTML(componente)
        : paso.installedHTML;
}

function plataformaVigente() {
    const plataformaDeLaPagina = plataformaDePagina();

    if (plataformaDeLaPagina) {
        plataformaActual = plataformaDeLaPagina;
        return plataformaDeLaPagina;
    }

    const plataformaGuardada = obtenerPlataforma();

    if (plataformaGuardada && PLATAFORMAS[plataformaGuardada]) {
        plataformaActual = plataformaGuardada;
        return plataformaGuardada;
    }

    return plataformaActual;
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

function obtenerCategoria(componente) {
    const categoria = componente?.categoria
        || (typeof componente?.tipo === 'object' ? componente.tipo.nombre : componente?.tipo)
        || '';

    return String(categoria).toUpperCase();
}

function obtenerConsumoComponente(componente) {
    const especificaciones = obtenerEspecificaciones(componente);
    const consumo = componente?.consumo_watts
        ?? especificaciones.consumo_w
        ?? especificaciones.tdp_w
        ?? 0;
    const numero = Number(consumo);

    return Number.isFinite(numero) ? numero : 0;
}

function obtenerPotenciaPsu(componente) {
    const especificaciones = obtenerEspecificaciones(componente);
    const potencia = especificaciones.potencia_w
        ?? especificaciones.watts
        ?? componente?.consumo_watts
        ?? 0;
    const numero = Number(potencia);

    return Number.isFinite(numero) ? numero : 0;
}

function botonSiguiente() {
    return document.querySelector('.btn-next, #btn-siguiente');
}

function quitarPlaceholder(tipo) {
    const indice = INDICE_PLACEHOLDER_POR_TIPO[tipo];
    if (indice == null) return;

    const config = PLATAFORMAS[plataformaVigente()] || PLATAFORMAS.AMD;
    const idPlaceholder = Number(config.ids[indice]);

    if (Number.isFinite(idPlaceholder)) {
        quitarComponenteSeleccionado(idPlaceholder);
    }
}

function guardarPaso(paso, componente) {
    const id = Number(componente?.id_componente ?? componente?.id);
    const datos = {
        tipo: paso.tipo,
        categoria: obtenerCategoria(componente),
        id_componente: Number.isFinite(id) ? id : null,
        nombre: componente?.nombre || '',
        descripcion: componente?.descripcion || '',
        watts: obtenerConsumoComponente(componente),
        potencia_w: obtenerPotenciaPsu(componente),
        especificaciones: componente?.especificaciones ?? null
    };

    // El armado arranca con IDs por defecto de la plataforma elegida.
    // Al elegir un componente real, se quita el placeholder de ese slot.
    quitarPlaceholder(paso.tipo);

    if (paso.tipo === 'cpu') {
        if (datos.id_componente != null) {
            guardarCpuId(datos.id_componente);
        }

        nombreCpuActual = datos.nombre || nombreCpuActual;
    }

    guardarComponente(paso.tipo, datos);
}

async function cargarComponentes() {
    if (componentesCache) return componentesCache;

    const response = await fetch(`${API_BASE}/componentes`);

    if (!response.ok) {
        throw new Error(`La API respondió con HTTP ${response.status}.`);
    }

    const datos = await response.json();
    componentesCache = Array.isArray(datos) ? datos : [];

    return componentesCache;
}

/**
 * Devuelve todas las opciones del backend para el paso actual.
 * No se aplica ningún límite de cantidad: se muestran todos los componentes.
 * Los CPUs se filtran por socket de la plataforma (AM5 o LGA1700).
 */
function filtrarComponentesPaso(paso, componentes) {
    const categoriaBuscada = paso.categoria.toUpperCase();
    const deLaCategoria = componentes.filter(
        (componente) => obtenerCategoria(componente) === categoriaBuscada
    );

    if (paso.tipo !== 'cpu') return deLaCategoria;

    const plataforma = plataformaVigente();
    const socketBuscado = plataforma === 'Intel' ? 'lga1700' : 'am5';

    const porSocket = deLaCategoria.filter((componente) => {
        const socket = String(obtenerEspecificaciones(componente).socket || '')
            .toLowerCase()
            .replace(/\s+/g, '');

        if (socket) {
            return socket.includes(socketBuscado);
        }

        const marca = String(componente.marca || '').toLowerCase();
        const nombre = String(componente.nombre || '').toLowerCase();

        return plataforma === 'Intel'
            ? (marca.includes('intel') || nombre.includes('intel'))
            : (marca.includes('amd') || nombre.includes('amd'));
    });

    return porSocket.length > 0 ? porSocket : deLaCategoria;
}

/**
 * Clona el dropzone para descartar los listeners inline del HTML.
 * Así el arrastre y el guardado quedan centralizados en este módulo.
 */
function prepararDropzone(dropzone) {
    if (!dropzone) return null;

    const clon = dropzone.cloneNode(true);

    clon.style.borderColor = '';
    clon.style.backgroundColor = '';
    clon.style.border = '';
    clon.style.animation = '';

    dropzone.replaceWith(clon);

    return clon;
}

function capacidadFuenteGuardada(paso = {}) {
    const psu = obtenerComponente('psu');
    const potencia = psu ? obtenerPotenciaPsu(psu) : 0;

    if (potencia > 0) return potencia;

    const capacidadPaso = Number(paso.capacidad);
    return Number.isFinite(capacidadPaso) && capacidadPaso > 0
        ? capacidadPaso
        : 650;
}

/**
 * Recalcula y pinta el consumo acumulado de todos los slots guardados.
 * Se invoca al cargar cada paso y después de guardar un componente.
 */
function actualizarPanelConsumo(paso = {}) {
    const total = calcularConsumoTotal();
    const capacidad = capacidadFuenteGuardada(paso);

    actualizarConsumo(total, capacidad, {
        resaltarCapacidad: Boolean(paso.resaltarCapacidad)
    });

    return total;
}

function slotArmadoCargado(tipo) {
    const componente = obtenerComponente(tipo);

    if (!componente || typeof componente !== 'object') return false;

    const id = Number(componente.id_componente ?? componente.id);
    return Number.isFinite(id) || Boolean(componente.nombre);
}

/**
 * Valida que todos los slots necesarios para finalizar el armado estén
 * guardados en localStorage. Deja en consola el detalle de cada slot.
 */
function validarArmadoCompleto() {
    const faltantes = SLOTS_REQUERIDOS_ARMADO.filter(
        ({ tipo }) => !slotArmadoCargado(tipo)
    );
    const completo = faltantes.length === 0;

    console.log('[Armado] Validación del botón Finalizar Armado:');
    SLOTS_REQUERIDOS_ARMADO.forEach(({ tipo, etiqueta }) => {
        const estado = slotArmadoCargado(tipo) ? 'cargado' : 'FALTA';
        console.log(`[Armado]   - Slot "${tipo}" (${etiqueta}): ${estado}`);
    });

    if (completo) {
        console.log('[Armado] Resultado: OK. Todos los slots requeridos están cargados.');
    } else {
        const detalle = faltantes
            .map(({ tipo, etiqueta }) => `${tipo} (${etiqueta})`)
            .join(', ');
        console.log(`[Armado] Resultado: FALLA. Falta(n): ${detalle}.`);
    }

    return { completo, faltantes };
}

function mensajeArmadoIncompleto(faltantes) {
    if (!Array.isArray(faltantes) || faltantes.length === 0) return '';

    if (faltantes.length === 1) {
        const { articulo, etiqueta } = faltantes[0];
        return `Te falta seleccionar ${articulo} ${etiqueta} para completar tu armado.`;
    }

    return `Te faltan seleccionar: ${faltantes
        .map(({ etiqueta }) => etiqueta)
        .join(', ')}.`;
}

/**
 * Crea (si hace falta) el contenedor de avisos junto a la navegación del paso.
 */
function obtenerContenedorAviso() {
    let aviso = document.getElementById('armado-aviso');
    if (aviso) return aviso;

    const navegacion = document.querySelector('.step-nav');
    if (!navegacion) return null;

    aviso = document.createElement('div');
    aviso.id = 'armado-aviso';
    aviso.setAttribute('role', 'status');
    aviso.setAttribute('aria-live', 'polite');
    aviso.style.display = 'none';
    aviso.style.marginTop = '20px';
    aviso.style.padding = '12px 15px';
    aviso.style.borderRadius = '8px';
    aviso.style.border = '1px solid transparent';
    aviso.style.fontSize = '0.85rem';
    aviso.style.lineHeight = '1.45';

    navegacion.parentNode.insertBefore(aviso, navegacion);

    return aviso;
}

function mostrarAvisoArmado(tipo, opciones = {}) {
    const aviso = obtenerContenedorAviso();
    if (!aviso) return null;

    if (!tipo) {
        aviso.style.display = 'none';
        aviso.innerHTML = '';
        return aviso;
    }

    aviso.style.display = 'block';
    mostrarAlerta(aviso, { tipo, ...opciones });

    return aviso;
}

function paginaFinalArmado() {
    return paginaActual().includes('intel')
        ? 'armado-final-intel.html'
        : 'armado-final.html';
}

/**
 * Habilita o deshabilita "Finalizar Armado" según los slots guardados.
 * Cuando falta algo, además de dejarlo en consola, muestra el motivo en la UI.
 */
function actualizarBotonFinalizar() {
    const boton = document.getElementById('btn-finalizar');
    if (!boton) return false;

    const { completo, faltantes } = validarArmadoCompleto();

    if (completo) {
        boton.disabled = false;
        boton.removeAttribute('disabled');
        boton.title = 'Finalizar armado y validar compatibilidad';
        mostrarAvisoArmado(null);
        return true;
    }

    const mensaje = mensajeArmadoIncompleto(faltantes);
    boton.disabled = true;
    boton.setAttribute('disabled', '');
    boton.title = mensaje;
    mostrarAvisoArmado('advertencia', {
        titulo: 'Armado incompleto',
        mensaje
    });

    return false;
}

async function consultarCompatibilidad(componentesIds) {
    const idPerfil = obtenerPerfil() || 1;

    const respuesta = await fetch(`${API_BASE}/compatibilidad/validar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
        },
        body: JSON.stringify({
            id_perfil: idPerfil,
            componentes_ids: componentesIds
        })
    });

    const resultado = await respuesta.json().catch(() => null);

    return { respuesta, resultado };
}

async function manejarFinalizarArmado(evento) {
    evento?.preventDefault();

    const boton = document.getElementById('btn-finalizar');
    const { completo } = validarArmadoCompleto();

    if (!completo) {
        actualizarBotonFinalizar();
        return;
    }

    const ids = obtenerIdsSeleccionados();
    console.log('[Armado] POST /api/v1/compatibilidad/validar con IDs:', ids);

    const aviso = mostrarAvisoArmado('info', {
        titulo: 'Validando compatibilidad...',
        mensaje: 'Consultando las reglas de compatibilidad en el servidor.'
    });

    const textoOriginal = boton?.textContent;
    if (boton) {
        boton.disabled = true;
        boton.textContent = 'Validando...';
    }

    try {
        const { respuesta, resultado } = await consultarCompatibilidad(ids);

        if (!respuesta.ok) {
            const detalle = typeof resultado?.detail === 'string'
                ? resultado.detail
                : `El servidor respondió con HTTP ${respuesta.status}.`;

            mostrarAlerta(aviso, {
                tipo: 'error',
                titulo: 'No se pudo validar la compatibilidad',
                mensaje: detalle
            });
            return;
        }

        if (!resultado || typeof resultado.es_compatible !== 'boolean') {
            mostrarAlerta(aviso, {
                tipo: 'error',
                titulo: 'Respuesta inesperada del servidor',
                mensaje: 'La API no devolvió el resultado de compatibilidad esperado.'
            });
            return;
        }

        console.log(
            `[Armado] Resultado de compatibilidad: es_compatible = ${resultado.es_compatible}`,
            resultado
        );

        const errores = Array.isArray(resultado.errores) ? resultado.errores : [];
        const compatible = resultado.es_compatible && errores.length === 0;

        if (compatible) {
            // La pantalla final vuelve a validar y muestra el diagnóstico completo.
            window.location.href = paginaFinalArmado();
            return;
        }

        mostrarDiagnostico(aviso, resultado);
    } catch (error) {
        console.error('No se pudo conectar con la API de compatibilidad:', error);
        mostrarErrorConexion(aviso, error.message);
    } finally {
        if (boton) {
            boton.textContent = textoOriginal || 'Finalizar Armado ✔';
            boton.disabled = false;
            boton.removeAttribute('disabled');
        }
    }
}

function configurarBotonFinalizar() {
    const boton = document.getElementById('btn-finalizar');
    if (!boton) return;

    // La navegación ahora depende de la validación de compatibilidad.
    boton.removeAttribute('onclick');

    if (boton.dataset.finalizarConfigurado !== 'true') {
        boton.addEventListener('click', manejarFinalizarArmado);
        boton.dataset.finalizarConfigurado = 'true';
    }

    actualizarBotonFinalizar();
}

function instalarComponente(paso, dropzone, componente, tarjeta, contenedor) {
    marcarZonaInstalada(
        dropzone,
        contenidoInstalado(paso, componente),
        paso.estilosZona
    );

    // Primero persiste el slot y después recalcula el acumulado global.
    guardarPaso(paso, componente);
    actualizarPanelConsumo(paso);

    // Se permite cambiar de componente: todas las tarjetas vuelven a estar
    // disponibles y solamente queda marcada la elegida.
    contenedor.querySelectorAll('.component-card').forEach((otraTarjeta) => {
        otraTarjeta.setAttribute('draggable', 'true');
        otraTarjeta.classList.remove('component-card-inactive');
        otraTarjeta.style.cursor = '';
    });

    marcarTarjetaInstalada(tarjeta);

    const boton = botonSiguiente();
    habilitarBotonSiguiente(boton, paso.colorBoton);
    if (boton) {
        boton.disabled = false;
    }

    if (paso.finalizaArmado) {
        actualizarBotonFinalizar();
    }
}

function configurarArrastre(contenedor, dropzone, paso) {
    contenedor.addEventListener('dragstart', (evento) => {
        const tarjeta = evento.target.closest?.('.component-card');

        if (!tarjeta || !contenedor.contains(tarjeta)) return;
        if (tarjeta.getAttribute('draggable') === 'false') return;

        const componente = tarjeta.__componente;
        if (!componente) return;

        arrastreActual = { paso, componente, tarjeta };

        const referencia = componente.id_componente
            ?? componente.id
            ?? componente.nombre
            ?? 'componente';

        evento.dataTransfer.setData('text/plain', String(referencia));
        evento.dataTransfer.effectAllowed = 'move';
        marcarZonaDisponible(dropzone);
    });

    contenedor.addEventListener('dragend', () => {
        restablecerZona(dropzone);
    });

    dropzone.addEventListener('dragover', (evento) => {
        evento.preventDefault();
        resaltarZona(dropzone);
    });

    dropzone.addEventListener('dragleave', () => {
        restablecerZona(dropzone);
    });

    dropzone.addEventListener('drop', (evento) => {
        evento.preventDefault();

        const arrastre = arrastreActual;
        restablecerZona(dropzone);

        if (!arrastre || arrastre.paso !== paso) return;

        instalarComponente(
            paso,
            dropzone,
            arrastre.componente,
            arrastre.tarjeta,
            contenedor
        );

        arrastreActual = null;
    });
}

async function configurarPaso(paso) {
    const contenedor = document.querySelector(paso.contenedorSelector);
    if (!contenedor) return;

    // Refleja de inmediato lo elegido en pasos anteriores.
    actualizarPanelConsumo(paso);

    if (paso.finalizaArmado) {
        configurarBotonFinalizar();
    }

    try {
        const componentes = await cargarComponentes();
        const opciones = filtrarComponentesPaso(paso, componentes);

        if (opciones.length === 0) {
            console.warn(`No hay componentes disponibles para la categoría ${paso.categoria}.`);
            return;
        }

        renderizarInventario(contenedor, opciones, {
            draggable: true,
            pista: paso.pista
        });

        // Marca para que otros scripts de la página no vuelvan a pisar las
        // tarjetas con datos estáticos o con un único componente.
        contenedor.dataset.dinamico = 'true';

        const dropzone = prepararDropzone(
            document.querySelector(paso.dropzoneSelector)
        );

        if (!dropzone) return;

        configurarArrastre(contenedor, dropzone, paso);
    } catch (error) {
        console.warn(
            'No se pudo cargar el inventario desde la API; se conserva la vista estática:',
            error
        );
    }
}

function aplicarPlataforma(config) {
    const imagen = document.querySelector('.motherboard-img');
    const encabezado = document.querySelector('.center-header p');
    const socket = document.querySelector('.dropzone-sub');

    if (imagen) imagen.src = config.imagen;
    if (encabezado) encabezado.textContent = config.encabezado;
    if (socket) socket.textContent = `SOCKET ${config.socket}`;
}

async function inicializarPasoCPU() {
    const plataforma = plataformaDePagina() || obtenerPlataforma() || 'AMD';

    plataformaActual = PLATAFORMAS[plataforma] ? plataforma : 'AMD';
    aplicarPlataforma(PLATAFORMAS[plataformaActual]);
    await configurarPaso(PASOS.cpu);
}

function inicializarEleccionMother() {
    const opciones = [
        { plataforma: 'AMD', selector: '.card-amd .btn-select' },
        { plataforma: 'Intel', selector: '.card-intel .btn-select' }
    ];

    opciones.forEach(({ plataforma, selector }) => {
        const boton = document.querySelector(selector);
        if (!boton) return;

        boton.addEventListener('click', () => {
            const config = PLATAFORMAS[plataforma];

            limpiarSeleccion();
            guardarPlataforma(plataforma);
            guardarComponentes(config.ids);
            guardarComponente('motherboard', {
                id_componente: config.ids[1],
                plataforma,
                chipset: config.chipset,
                socket: config.socket,
                imagen: config.imagen,
                componentes: config.ids
            });
        });
    });
}

function actualizarEstadoEncendido(habilitado, motivo = '') {
    compatibilidadVerificada = habilitado;

    const btnEncender = document.getElementById('btn-encender');
    if (!btnEncender) return;

    actualizarEstadoBoton(btnEncender, habilitado);
    btnEncender.title = habilitado
        ? 'Encender la PC'
        : (motivo || 'Validá la compatibilidad antes de encender la PC.');
}

function configurarBotonEncendido() {
    const btnEncender = document.getElementById('btn-encender');
    if (!btnEncender) return;

    const canvasChasis = document.getElementById('canvas-chasis');
    const statsBox = document.getElementById('stats-box');
    const statusText = document.getElementById('status-text');
    const wattsNumber = document.getElementById('watts-number');
    const wattsMax = document.getElementById('watts-max');

    let isPowerOn = false;

    const capacidad = capacidadFuenteGuardada(PASOS.psu);

    // La pantalla final arranca apagada: 0 W de consumo y la capacidad real
    // de la fuente ya guardada. Al encender se muestra el total acumulado.
    actualizarConsumo(0, capacidad);
    actualizarEstadoEncendido(false, 'Validando compatibilidad...');

    btnEncender.addEventListener('click', () => {
        if (!compatibilidadVerificada) return;

        isPowerOn = !isPowerOn;

        if (isPowerOn) {
            if (canvasChasis) canvasChasis.classList.add('powered-on');
            btnEncender.classList.add('on');
            btnEncender.innerHTML = '⏻ Apagar PC';

            if (statsBox) statsBox.style.borderColor = 'var(--accent-blue)';
            if (statusText) {
                statusText.innerHTML = '● ENCENDIDO';
                statusText.style.color = 'var(--accent-green)';
            }
            if (wattsNumber) {
                wattsNumber.textContent = String(calcularConsumoTotal());
            }
            if (wattsMax) {
                wattsMax.textContent = `Watts en uso / ${capacidad} W`;
                wattsMax.style.color = 'var(--accent-green)';
            }
            return;
        }

        if (canvasChasis) canvasChasis.classList.remove('powered-on');
        btnEncender.classList.remove('on');
        btnEncender.innerHTML = '⚡ Encender PC';

        if (statsBox) statsBox.style.borderColor = 'var(--border-color)';
        if (statusText) {
            statusText.innerHTML = '● APAGADO';
            statusText.style.color = 'var(--text-muted)';
        }
        if (wattsNumber) wattsNumber.textContent = '0';
        if (wattsMax) {
            wattsMax.textContent = `Watts en uso / ${capacidad} W`;
            wattsMax.style.color = 'var(--text-muted)';
        }
    });
}

async function cargarInventarioReal(ids, contenedor) {
    if (!contenedor) return;

    try {
        const response = await fetch(`${API_BASE}/componentes`);
        if (!response.ok) return;

        const todosLosComponentes = await response.json();
        const idsNumericos = ids.map((id) => Number(id));

        const seleccionados = todosLosComponentes.filter((componente) => (
            idsNumericos.includes(Number(componente.id_componente))
        ));

        if (seleccionados.length === 0) return;

        renderizarInventarioFinal(contenedor, seleccionados);
    } catch (error) {
        console.error('Error al cargar detalles de inventario:', error);
    }
}

/**
 * Recolecta los IDs guardados en localStorage mediante storage.js y consulta
 * la API de compatibilidad del backend.
 *
 * Devuelve la respuesta validada o null si la petición no pudo completarse.
 */
export async function validarCompatibilidadAPI() {
    const summaryBox = document.querySelector('.summary-box');
    const inventoryBox = document.querySelector('.inventory-box');
    const componentesIds = obtenerIdsSeleccionados();
    const idPerfil = obtenerPerfil() || 1;

    console.log('[Armado] Validando compatibilidad de la pantalla final con IDs:', componentesIds);

    if (summaryBox) {
        summaryBox.setAttribute('role', 'status');
        summaryBox.setAttribute('aria-live', 'polite');

        mostrarAlerta(summaryBox, {
            tipo: 'info',
            titulo: 'Validando compatibilidad...',
            mensaje: 'Consultando las reglas de compatibilidad en el servidor.'
        });
    }

    actualizarEstadoEncendido(false, 'Validando compatibilidad...');

    let respuesta;

    try {
        respuesta = await fetch(`${API_BASE}/compatibilidad/validar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json'
            },
            body: JSON.stringify({
                id_perfil: idPerfil,
                componentes_ids: componentesIds
            })
        });
    } catch (error) {
        console.error('No se pudo conectar con la API de compatibilidad:', error);
        mostrarErrorConexion(summaryBox, error.message);
        actualizarEstadoEncendido(false, 'Sin conexión con el servidor de validación.');
        return null;
    }

    const resultado = await respuesta.json().catch(() => null);

    if (!respuesta.ok) {
        const detalle = typeof resultado?.detail === 'string'
            ? resultado.detail
            : `El servidor respondió con HTTP ${respuesta.status}.`;

        mostrarAlerta(summaryBox, {
            tipo: 'error',
            titulo: 'No se pudo validar la compatibilidad',
            mensaje: detalle
        });
        actualizarEstadoEncendido(false, 'No se pudo validar la compatibilidad.');
        return null;
    }

    if (!resultado || typeof resultado.es_compatible !== 'boolean') {
        mostrarAlerta(summaryBox, {
            tipo: 'error',
            titulo: 'Respuesta inesperada del servidor',
            mensaje: 'La API no devolvió el resultado de compatibilidad esperado.'
        });
        actualizarEstadoEncendido(false, 'Respuesta inválida del servidor.');
        return null;
    }

    console.log(
        `[Armado] Resultado de compatibilidad (pantalla final): es_compatible = ${resultado.es_compatible}`,
        resultado
    );

    mostrarDiagnostico(summaryBox, resultado);

    const errores = Array.isArray(resultado.errores) ? resultado.errores : [];
    const compatible = resultado.es_compatible && errores.length === 0;

    actualizarEstadoEncendido(
        compatible,
        compatible ? '' : 'La configuración no es compatible. Corregí los componentes para encender la PC.'
    );

    await cargarInventarioReal(componentesIds, inventoryBox);

    return resultado;
}

function inicializarFinal() {
    configurarBotonEncendido();
    validarCompatibilidadAPI();
}

const PAGINAS = {
    'eleccion-mother': inicializarEleccionMother,
    'armado-guiado': inicializarPasoCPU,
    'armado-guiado-amd': inicializarPasoCPU,
    'armado-guiado-intel': inicializarPasoCPU,
    'armado-ram': () => configurarPaso(PASOS.ram),
    'armado-ram-intel': () => configurarPaso(PASOS.ram),
    'armado-disipador': () => configurarPaso(PASOS.cooler),
    'armado-disipador-intel': () => configurarPaso(PASOS.cooler),
    'armado-almacenamiento': () => configurarPaso(PASOS.almacenamiento),
    'armado-almacenamiento-intel': () => configurarPaso(PASOS.almacenamiento),
    'armado-fuente': () => configurarPaso(PASOS.psu),
    'armado-fuente-intel': () => configurarPaso(PASOS.psu),
    'armado-gpu': () => configurarPaso(PASOS.gpu),
    'armado-gpu-intel': () => configurarPaso(PASOS.gpu),
    'armado-final': inicializarFinal,
    'armado-final-intel': inicializarFinal
};

const inicializador = PAGINAS[paginaActual()];

if (inicializador) {
    alCargarDocumento(inicializador);
}
