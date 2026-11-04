/**
 * storage.js
 * Acceso centralizado a localStorage para el flujo de armado de EnsamblaPC.
 *
 * Mantiene las claves históricas que ya usaba la aplicación
 * (plataforma_seleccionada, componentes_seleccionados, cpu_seleccionado_id, id_perfil)
 * y agrega una clave por cada tipo de componente del armado.
 */

export const STORAGE_KEYS = Object.freeze({
    plataforma: 'plataforma_seleccionada',
    componentes: 'componentes_seleccionados',
    cpuId: 'cpu_seleccionado_id',
    perfil: 'id_perfil',
    gabinete: 'gabinete_seleccionado',
    motherboard: 'motherboard_seleccionada',
    gpu: 'gpu_seleccionada',
    ram: 'ram_seleccionada',
    cpu: 'cpu_seleccionado',
    cooler: 'cooler_seleccionado',
    psu: 'fuente_seleccionada',
    almacenamiento: 'almacenamiento_seleccionado',
    sesionToken: 'auth_access_token',
    sesionUsuario: 'auth_usuario'
});

const SLOT_KEYS = Object.freeze({
    gabinete: STORAGE_KEYS.gabinete,
    motherboard: STORAGE_KEYS.motherboard,
    gpu: STORAGE_KEYS.gpu,
    ram: STORAGE_KEYS.ram,
    cpu: STORAGE_KEYS.cpu,
    cooler: STORAGE_KEYS.cooler,
    psu: STORAGE_KEYS.psu,
    almacenamiento: STORAGE_KEYS.almacenamiento
});

function almacenamientoDisponible() {
    return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function leer(clave) {
    if (!almacenamientoDisponible()) return null;
    try {
        return window.localStorage.getItem(clave);
    } catch (error) {
        console.warn(`No se pudo leer "${clave}" de localStorage:`, error);
        return null;
    }
}

function escribir(clave, valor) {
    if (!almacenamientoDisponible()) return false;
    try {
        window.localStorage.setItem(clave, String(valor));
        return true;
    } catch (error) {
        console.warn(`No se pudo guardar "${clave}" en localStorage:`, error);
        return false;
    }
}

function eliminar(clave) {
    if (!almacenamientoDisponible()) return false;
    try {
        window.localStorage.removeItem(clave);
        return true;
    } catch (error) {
        console.warn(`No se pudo eliminar "${clave}" de localStorage:`, error);
        return false;
    }
}

function leerJSON(clave, valorPredeterminado = null) {
    const valor = leer(clave);
    if (!valor) return valorPredeterminado;

    try {
        return JSON.parse(valor);
    } catch (error) {
        console.warn(`El contenido de "${clave}" no es JSON válido:`, error);
        return valorPredeterminado;
    }
}

function escribirJSON(clave, valor) {
    return escribir(clave, JSON.stringify(valor));
}

function normalizarIds(ids) {
    const lista = Array.isArray(ids) ? ids : (ids == null ? [] : [ids]);
    const normalizados = lista
        .map((id) => Number(id))
        .filter((id) => Number.isFinite(id));

    return [...new Set(normalizados)];
}

function obtenerId(componente) {
    if (componente == null) return null;
    if (typeof componente === 'number' || typeof componente === 'string') {
        const id = Number(componente);
        return Number.isFinite(id) ? id : null;
    }

    const id = Number(
        componente.id_componente
        ?? componente.id
        ?? componente.componente_id
        ?? NaN
    );

    return Number.isFinite(id) ? id : null;
}

/* -------------------------------------------------------------------------- */
/* Plataforma                                                                  */
/* -------------------------------------------------------------------------- */

export function guardarPlataforma(plataforma) {
    return escribir(STORAGE_KEYS.plataforma, plataforma);
}

export function obtenerPlataforma() {
    return leer(STORAGE_KEYS.plataforma);
}

export function limpiarPlataforma() {
    return eliminar(STORAGE_KEYS.plataforma);
}

/* -------------------------------------------------------------------------- */
/* Lista de IDs seleccionados                                                  */
/* -------------------------------------------------------------------------- */

export function guardarComponentes(ids) {
    return escribirJSON(STORAGE_KEYS.componentes, normalizarIds(ids));
}

export function obtenerComponentes() {
    return normalizarIds(leerJSON(STORAGE_KEYS.componentes, []));
}

export function agregarComponenteSeleccionado(id) {
    const idNormalizado = obtenerId(id);
    if (idNormalizado == null) return null;

    const seleccionados = obtenerComponentes();
    if (!seleccionados.includes(idNormalizado)) {
        seleccionados.push(idNormalizado);
        guardarComponentes(seleccionados);
    }

    return seleccionados;
}

/**
 * Quita un ID de la lista de componentes seleccionados.
 * Se usa al reemplazar el componente de un slot para no enviar IDs obsoletos
 * al endpoint de compatibilidad.
 */
export function quitarComponenteSeleccionado(id) {
    const idNormalizado = obtenerId(id);
    if (idNormalizado == null) return null;

    const seleccionados = obtenerComponentes().filter(
        (actual) => actual !== idNormalizado
    );

    guardarComponentes(seleccionados);

    return seleccionados;
}

export function limpiarComponentesSeleccionados() {
    return eliminar(STORAGE_KEYS.componentes);
}

/* -------------------------------------------------------------------------- */
/* Componentes por tipo (gabinete, motherboard, GPU, RAM, etc.)                */
/* -------------------------------------------------------------------------- */

export function guardarComponente(tipo, componente) {
    const clave = SLOT_KEYS[tipo];
    if (!clave) {
        console.warn(`Tipo de componente no soportado: "${tipo}"`);
        return null;
    }

    // Se lee el componente anterior antes de sobrescribir el slot para poder
    // sacar su ID de la lista que se envía a compatibilidad.
    const idAnterior = obtenerId(obtenerComponente(tipo));

    escribirJSON(clave, componente);

    const id = obtenerId(componente);

    if (idAnterior != null && idAnterior !== id) {
        quitarComponenteSeleccionado(idAnterior);
    }

    if (id != null) {
        agregarComponenteSeleccionado(id);
    }

    return componente;
}

export function obtenerComponente(tipo) {
    const clave = SLOT_KEYS[tipo];
    if (!clave) return null;

    return leerJSON(clave, null);
}

export function limpiarComponente(tipo) {
    const clave = SLOT_KEYS[tipo];
    if (!clave) return false;

    return eliminar(clave);
}

export const guardarGabinete = (componente) => guardarComponente('gabinete', componente);
export const obtenerGabinete = () => obtenerComponente('gabinete');
export const limpiarGabinete = () => limpiarComponente('gabinete');

export const guardarMotherboard = (componente) => guardarComponente('motherboard', componente);
export const obtenerMotherboard = () => obtenerComponente('motherboard');
export const limpiarMotherboard = () => limpiarComponente('motherboard');

export const guardarGpu = (componente) => guardarComponente('gpu', componente);
export const obtenerGpu = () => obtenerComponente('gpu');
export const limpiarGpu = () => limpiarComponente('gpu');

export const guardarRam = (componente) => guardarComponente('ram', componente);
export const obtenerRam = () => obtenerComponente('ram');
export const limpiarRam = () => limpiarComponente('ram');

export const guardarCooler = (componente) => guardarComponente('cooler', componente);
export const obtenerCooler = () => obtenerComponente('cooler');
export const limpiarCooler = () => limpiarComponente('cooler');

export const guardarPsu = (componente) => guardarComponente('psu', componente);
export const obtenerPsu = () => obtenerComponente('psu');
export const limpiarPsu = () => limpiarComponente('psu');

export const guardarAlmacenamiento = (componente) => guardarComponente('almacenamiento', componente);
export const obtenerAlmacenamiento = () => obtenerComponente('almacenamiento');
export const limpiarAlmacenamiento = () => limpiarComponente('almacenamiento');

/* -------------------------------------------------------------------------- */
/* CPU y perfil                                                                */
/* -------------------------------------------------------------------------- */

export function guardarCpuId(id) {
    const idNormalizado = obtenerId(id);
    if (idNormalizado == null) return false;

    return escribir(STORAGE_KEYS.cpuId, idNormalizado);
}

export function obtenerCpuId() {
    const valor = leer(STORAGE_KEYS.cpuId);
    if (valor == null || valor === '') return null;

    const id = Number(valor);
    return Number.isFinite(id) ? id : null;
}

export function limpiarCpuId() {
    return eliminar(STORAGE_KEYS.cpuId);
}

export function guardarPerfil(idPerfil) {
    const id = Number(idPerfil);
    if (!Number.isFinite(id)) return false;

    return escribir(STORAGE_KEYS.perfil, id);
}

export function obtenerPerfil() {
    const valor = leer(STORAGE_KEYS.perfil);
    if (valor == null || valor === '') return null;

    const id = Number(valor);
    return Number.isFinite(id) ? id : null;
}

/* -------------------------------------------------------------------------- */
/* Armado completo                                                             */
/* -------------------------------------------------------------------------- */

/**
 * Reúne los IDs de todos los componentes del armado actual.
 *
 * Combina la lista histórica `componentes_seleccionados` con cada slot
 * individual (motherboard, RAM, GPU, fuente, etc.) y con el CPU, de modo
 * que la validación no dependa de una sola de las dos representaciones.
 */
export function obtenerIdsSeleccionados() {
    const ids = [...obtenerComponentes()];

    const cpuId = obtenerCpuId();
    if (cpuId != null) ids.push(cpuId);

    Object.keys(SLOT_KEYS).forEach((tipo) => {
        const id = obtenerId(obtenerComponente(tipo));
        if (id != null) ids.push(id);
    });

    return normalizarIds(ids);
}

/* -------------------------------------------------------------------------- */
/* Sesión de usuario                                                           */
/* -------------------------------------------------------------------------- */

/**
 * Guarda el token y los datos públicos del usuario autenticado.
 */
export function guardarSesion(accessToken, usuario) {
    const tokenGuardado = escribir(STORAGE_KEYS.sesionToken, accessToken);
    const usuarioGuardado = escribirJSON(STORAGE_KEYS.sesionUsuario, usuario);

    return tokenGuardado && usuarioGuardado;
}

export function obtenerTokenSesion() {
    return leer(STORAGE_KEYS.sesionToken);
}

export function obtenerUsuarioSesion() {
    return leerJSON(STORAGE_KEYS.sesionUsuario, null);
}

export function limpiarSesion() {
    eliminar(STORAGE_KEYS.sesionToken);
    eliminar(STORAGE_KEYS.sesionUsuario);
}

/* -------------------------------------------------------------------------- */
/* Limpieza                                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Limpia todos los componentes del armado actual.
 * Conserva la plataforma, el perfil y cualquier preferencia general.
 */
export function limpiarSeleccion() {
    Object.values(SLOT_KEYS).forEach((clave) => eliminar(clave));
    limpiarComponentesSeleccionados();
    limpiarCpuId();
}

/**
 * Limpia por completo el estado del armado, incluida la plataforma.
 */
export function limpiarTodo() {
    limpiarSeleccion();
    limpiarPlataforma();
    eliminar(STORAGE_KEYS.perfil);
}
