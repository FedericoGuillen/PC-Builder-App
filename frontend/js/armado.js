/**
 * armado.js
 * Punto de entrada del flujo de armado.
 *
 * Detecta la pantalla actual y reutiliza los módulos storage.js y ui.js.
 * De esta forma todas las páginas comparten la misma lógica de arrastre,
 * guardado y actualización visual.
 */

import {
    agregarComponenteSeleccionado,
    guardarComponente,
    guardarComponentes,
    guardarCpuId,
    guardarPlataforma,
    limpiarSeleccion,
    obtenerComponentes,
    obtenerCpuId,
    obtenerIdsSeleccionados,
    obtenerPerfil,
    obtenerPlataforma
} from './storage.js';

import {
    actualizarCapacidad,
    actualizarConsumo,
    actualizarEstadoBoton,
    escaparHTML,
    habilitarBotonSiguiente,
    marcarTarjetaInstalada,
    marcarZonaDisponible,
    marcarZonaInstalada,
    mostrarAlerta,
    mostrarDiagnostico,
    mostrarErrorConexion,
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

function htmlCpuInstalado(nombre) {
    return `
        <div style="font-size: 2rem; margin-bottom: 5px;">🔳</div>
        <div style="font-weight: bold; color: white; font-size: 0.85rem;">${escaparHTML(nombre)}</div>
        <div style="font-size:0.65rem; color:#3fb950; font-weight: 600; margin-top:4px;">✔ INSTALADO</div>
    `;
}

const PASOS = Object.freeze({
    cpu: {
        cardSelector: '.component-card[draggable="true"]',
        dropzoneSelector: '.dropzone',
        pieza: 'procesador-amd',
        tipo: 'cpu',
        watts: 65,
        capacidad: 650,
        installedHTML: () => htmlCpuInstalado(nombreCpuActual),
        estilosZona: { borde: '1px solid #30363d', fondo: '#161b22' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    ram: {
        cardSelector: '#ram-card',
        dropzoneSelector: '.dropzone-ram',
        pieza: 'memoria-ram',
        tipo: 'ram',
        watts: 75,
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
        cardSelector: '#cooler-card',
        dropzoneSelector: '.dropzone-cooler',
        pieza: 'cooler-cpu',
        tipo: 'cooler',
        watts: 80,
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 2.5rem; color: #8b949e;">❄</div>
            <div style="font-size: 0.65rem; color: #3fb950; font-weight: bold; margin-top: 5px;">✔ CONECTADO</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#1f2937' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    almacenamiento: {
        cardSelector: '#m2-card',
        dropzoneSelector: '.dropzone-m2',
        pieza: 'almacenamiento-m2',
        tipo: 'almacenamiento',
        watts: 85,
        capacidad: 650,
        installedHTML: `
            <div style="font-size: 0.55rem; color: #3fb950; font-weight: bold; pointer-events: none;">✔ INSTALADO</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#30363d' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    psu: {
        cardSelector: '#psu-card',
        dropzoneSelector: '.dropzone-psu',
        pieza: 'fuente-poder',
        tipo: 'psu',
        capacidad: 650,
        soloCapacidad: true,
        installedHTML: `
            <div style="font-size: 2rem; color: #8b949e; margin-bottom: 5px;">🔌</div>
            <div style="font-size: 0.75rem; color: #3fb950; font-weight: bold; pointer-events: none;">✔ ATORNILLADA</div>
        `,
        estilosZona: { borde: '1px solid #161b22', fondo: '#1f2937' },
        colorBoton: 'rgba(88, 166, 255, 0.6)'
    },
    gpu: {
        cardSelector: '#gpu-card',
        dropzoneSelector: '.dropzone-gpu',
        pieza: 'tarjeta-grafica',
        tipo: 'gpu',
        watts: 200,
        capacidad: 650,
        resaltarCapacidad: true,
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

function contenidoInstalado(paso) {
    return typeof paso.installedHTML === 'function'
        ? paso.installedHTML()
        : paso.installedHTML;
}

function obtenerDatosTarjeta(tarjeta, tipo) {
    const datos = {
        tipo,
        nombre: tarjeta.querySelector('.comp-name')?.textContent.trim() || '',
        descripcion: tarjeta.querySelector('.comp-desc')?.textContent.trim() || '',
        watts: tarjeta.querySelector('.comp-watts')?.textContent.trim() || ''
    };

    const id = Number(tarjeta.dataset.id);
    if (Number.isFinite(id)) {
        datos.id_componente = id;
    }

    return datos;
}

function guardarPaso(paso, tarjeta) {
    const datos = obtenerDatosTarjeta(tarjeta, paso.tipo);

    if (paso.tipo === 'cpu') {
        let cpuId = obtenerCpuId();
        const config = PLATAFORMAS[plataformaActual] || PLATAFORMAS.AMD;

        if (cpuId == null) {
            cpuId = config.ids[0];
            guardarCpuId(cpuId);
        }

        datos.id_componente = cpuId;

        // Si el ID por defecto de la plataforma estaba en la lista, se sustituye
        // por el CPU real de la API sin dejar dos procesadores seleccionados.
        const seleccionados = obtenerComponentes();
        const indiceCpuPorDefecto = seleccionados.indexOf(config.ids[0]);

        if (indiceCpuPorDefecto >= 0) {
            seleccionados[indiceCpuPorDefecto] = cpuId;
            guardarComponentes(seleccionados);
        } else {
            agregarComponenteSeleccionado(cpuId);
        }
    }

    guardarComponente(paso.tipo, datos);
}

function configurarPaso(paso) {
    const tarjeta = document.querySelector(paso.cardSelector);
    const dropzone = document.querySelector(paso.dropzoneSelector);

    if (!tarjeta || !dropzone) return;

    tarjeta.addEventListener('dragstart', (evento) => {
        evento.dataTransfer.setData('text/plain', paso.pieza);
        marcarZonaDisponible(dropzone);
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

        const piezaArrastrada = evento.dataTransfer.getData('text/plain');
        if (piezaArrastrada !== paso.pieza) return;

        marcarZonaInstalada(dropzone, contenidoInstalado(paso), paso.estilosZona);

        if (paso.soloCapacidad) {
            actualizarCapacidad(paso.capacidad);
        } else {
            actualizarConsumo(paso.watts, paso.capacidad, {
                resaltarCapacidad: paso.resaltarCapacidad
            });
        }

        marcarTarjetaInstalada(tarjeta);
        habilitarBotonSiguiente(document.querySelector('.btn-next'), paso.colorBoton);
        guardarPaso(paso, tarjeta);
    });
}

async function cargarCpuDesdeApi(plataforma) {
    try {
        const response = await fetch(`${API_BASE}/componentes`);
        if (!response.ok) return;

        const componentes = await response.json();

        const cpuProcesador = componentes.find((componente) => {
            const categoria = String(
                componente.categoria
                || (typeof componente.tipo === 'object' ? componente.tipo.nombre : componente.tipo)
                || ''
            ).toUpperCase();
            const esCPU = categoria === 'CPU';

            if (!esCPU) return false;

            const plataformaTexto = plataforma.toLowerCase();
            const marca = String(componente.marca || '').toLowerCase();
            const nombre = String(componente.nombre || '').toLowerCase();
            const socket = String(componente.especificaciones?.socket || '').toLowerCase();

            const coincidePorMarcaONombre = marca.includes(plataformaTexto) || nombre.includes(plataformaTexto);
            const coincidePorSocket = plataforma === 'AMD'
                ? socket.includes('am5')
                : (socket.includes('lga1700') || socket.includes('lga 1700'));

            return coincidePorMarcaONombre || coincidePorSocket;
        });

        if (!cpuProcesador) return;

        nombreCpuActual = cpuProcesador.nombre || nombreCpuActual;

        const nameElem = document.querySelector('.comp-name');
        const wattsElem = document.querySelector('.comp-watts');

        if (nameElem) nameElem.textContent = nombreCpuActual;
        if (wattsElem) wattsElem.textContent = `${cpuProcesador.consumo_watts || 65} W`;

        if (cpuProcesador.id_componente != null) {
            guardarCpuId(cpuProcesador.id_componente);
        }
    } catch (error) {
        console.warn('No se pudieron cargar los datos dinámicos del servidor, usando vista estática:', error);
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
    const config = PLATAFORMAS[plataforma] || PLATAFORMAS.AMD;

    plataformaActual = PLATAFORMAS[plataforma] ? plataforma : 'AMD';
    aplicarPlataforma(config);
    configurarPaso(PASOS.cpu);
    await cargarCpuDesdeApi(plataforma);
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
            if (wattsNumber) wattsNumber.innerHTML = '200';
            if (wattsMax) wattsMax.style.color = 'var(--accent-green)';
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
        if (wattsNumber) wattsNumber.innerHTML = '0';
        if (wattsMax) wattsMax.style.color = 'var(--text-muted)';
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
