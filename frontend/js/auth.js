/**
 * auth.js
 * Módulo de autenticación del frontend de EnsamblaPC.
 *
 * Abstrae las peticiones a la API de login/registro, guarda la sesión
 * en localStorage y actualiza los formularios y la barra de navegación.
 */

import {
    guardarSesion,
    limpiarSesion,
    obtenerTokenSesion,
    obtenerUsuarioSesion
} from './storage.js';

import { mostrarAlerta } from './ui.js';


const API_AUTH = 'http://127.0.0.1:8000/api/v1/auth';
const PAGINA_LOGIN = 'login.html';
const PAGINA_REGISTRO = 'registro.html';
const PAGINA_PERFIL = 'perfil.html';
const EVENTO_SESION = 'auth:cambio';


export class AuthError extends Error {
    constructor(mensaje, status = 0, data = null) {
        super(mensaje);
        this.name = 'AuthError';
        this.status = status;
        this.data = data;
    }
}


/* -------------------------------------------------------------------------- */
/* API                                                                        */
/* -------------------------------------------------------------------------- */

function extraerMensaje(data, status) {
    const detalle = data?.detail;

    if (typeof detalle === 'string' && detalle.trim()) {
        return detalle;
    }

    if (Array.isArray(detalle) && detalle.length > 0) {
        return detalle
            .map((error) => error?.msg || String(error))
            .join(' ');
    }

    if (status === 409) {
        return 'Ya existe un usuario registrado con ese email.';
    }

    if (status === 401) {
        return 'Email o contraseña incorrectos.';
    }

    return `No se pudo completar la operación (HTTP ${status}).`;
}

async function solicitarAuth(ruta, payload) {
    let respuesta;

    try {
        respuesta = await fetch(`${API_AUTH}${ruta}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json'
            },
            body: JSON.stringify(payload)
        });
    } catch (error) {
        throw new AuthError(
            'No se pudo conectar con el servidor. Verificá que el backend esté en ejecución.',
            0,
            error
        );
    }

    const data = await respuesta.json().catch(() => null);

    if (!respuesta.ok) {
        throw new AuthError(
            extraerMensaje(data, respuesta.status),
            respuesta.status,
            data
        );
    }

    return data;
}


/* -------------------------------------------------------------------------- */
/* Sesión                                                                     */
/* -------------------------------------------------------------------------- */

function notificarCambioSesion() {
    if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent(EVENTO_SESION));
    }
}

/**
 * Inicia sesión contra la API y persiste el token y el usuario.
 */
export async function iniciarSesion(email, password) {
    const data = await solicitarAuth('/login', {
        email: String(email || '').trim(),
        password: String(password || '')
    });

    if (!data?.access_token || !data?.usuario) {
        throw new AuthError(
            'La respuesta del servidor no contiene la sesión esperada.',
            500,
            data
        );
    }

    guardarSesion(data.access_token, data.usuario);
    notificarCambioSesion();

    return data;
}

/**
 * Registra un usuario nuevo. El backend devuelve la confirmación y el usuario.
 */
export async function registrarUsuario({ nombre, apellido, email, password }) {
    return solicitarAuth('/register', {
        nombre: String(nombre || '').trim(),
        apellido: apellido ? String(apellido).trim() : null,
        email: String(email || '').trim(),
        password: String(password || '')
    });
}

/**
 * Elimina la sesión local y avisa a la interfaz para que se actualice.
 */
export function cerrarSesion() {
    limpiarSesion();
    notificarCambioSesion();
}

/**
 * Devuelve el usuario autenticado o null si no hay una sesión válida.
 */
export function obtenerUsuarioActual() {
    const token = obtenerTokenSesion();
    const usuario = obtenerUsuarioSesion();

    return token && usuario ? usuario : null;
}

export function obtenerTokenActual() {
    return obtenerTokenSesion();
}


/* -------------------------------------------------------------------------- */
/* Alertas de los formularios                                                  */
/* -------------------------------------------------------------------------- */

function crearContenedorAlerta(form) {
    let contenedor = form.querySelector('.auth-alert');

    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.className = 'auth-alert';
        contenedor.setAttribute('role', 'alert');
        contenedor.style.cssText = [
            'display: none',
            'border: 1px solid transparent',
            'border-radius: 8px',
            'padding: 12px 14px',
            'margin-bottom: 16px',
            'font-size: 0.85rem',
            'line-height: 1.45'
        ].join(';');

        form.insertBefore(contenedor, form.firstChild);
    }

    return contenedor;
}

function ocultarAlerta(contenedor) {
    if (!contenedor) return;

    contenedor.style.display = 'none';
    contenedor.innerHTML = '';
}

function mostrarErrorAuth(contenedor, error) {
    const mensaje = error instanceof AuthError
        ? error.message
        : 'Ocurrió un error inesperado. Intentá nuevamente.';

    mostrarAlerta(contenedor, {
        tipo: 'error',
        titulo: 'No se pudo completar la operación',
        mensaje
    });

    contenedor.style.display = 'block';
    contenedor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function alternarBotonEnviando(boton, enviando, texto) {
    if (!boton) return;

    if (enviando) {
        boton.dataset.htmlOriginal = boton.innerHTML;
        boton.disabled = true;
        boton.style.opacity = '0.7';
        boton.textContent = texto;
        return;
    }

    boton.disabled = false;
    boton.style.opacity = '';

    if (boton.dataset.htmlOriginal) {
        boton.innerHTML = boton.dataset.htmlOriginal;
        delete boton.dataset.htmlOriginal;
    }
}

function obtenerDestinoLogin() {
    const params = new URLSearchParams(window.location.search);
    const destino = params.get('redirect');

    // Solo se aceptan rutas internas para evitar redirecciones externas.
    if (destino && !/^(?:[a-z]+:)?\/\//i.test(destino)) {
        return destino;
    }

    return PAGINA_PERFIL;
}


/* -------------------------------------------------------------------------- */
/* Formularios                                                                */
/* -------------------------------------------------------------------------- */

function inicializarFormularioLogin() {
    const form = document.getElementById('loginForm');

    if (!form || form.dataset.authBound === 'true') return;

    form.dataset.authBound = 'true';

    const alerta = crearContenedorAlerta(form);
    const boton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        ocultarAlerta(alerta);

        const email = form.querySelector('#loginEmail')?.value.trim() || '';
        const password = form.querySelector('#loginPassword')?.value || '';

        if (!email || !password) {
            mostrarErrorAuth(
                alerta,
                new AuthError('Ingresá tu correo y contraseña.')
            );
            return;
        }

        alternarBotonEnviando(boton, true, 'Ingresando...');

        try {
            await iniciarSesion(email, password);

            mostrarAlerta(alerta, {
                tipo: 'exito',
                titulo: 'Sesión iniciada',
                mensaje: 'Redirigiendo...'
            });
            alerta.style.display = 'block';

            window.setTimeout(() => {
                window.location.href = obtenerDestinoLogin();
            }, 700);
        } catch (error) {
            mostrarErrorAuth(alerta, error);
        } finally {
            alternarBotonEnviando(boton, false);
        }
    });
}

function inicializarFormularioRegistro() {
    const form = document.getElementById('registerForm');

    if (!form || form.dataset.authBound === 'true') return;

    form.dataset.authBound = 'true';

    const alerta = crearContenedorAlerta(form);
    const boton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        ocultarAlerta(alerta);

        const nombreCompleto = form.querySelector('#fullName')?.value.trim() || '';
        const email = form.querySelector('#registerEmail')?.value.trim() || '';
        const password = form.querySelector('#registerPassword')?.value || '';
        const confirmPassword = form.querySelector('#confirmPassword')?.value;

        const [nombre, ...resto] = nombreCompleto.split(/\s+/);
        const apellido = resto.join(' ') || null;

        if (!nombre || !email || !password) {
            mostrarErrorAuth(
                alerta,
                new AuthError('Completá tu nombre, correo y contraseña.')
            );
            return;
        }

        if (confirmPassword !== undefined && password !== confirmPassword) {
            mostrarErrorAuth(
                alerta,
                new AuthError('Las contraseñas no coinciden.')
            );
            return;
        }

        alternarBotonEnviando(boton, true, 'Registrando...');

        try {
            const respuesta = await registrarUsuario({
                nombre,
                apellido,
                email,
                password
            });

            mostrarAlerta(alerta, {
                tipo: 'exito',
                titulo: 'Registro exitoso',
                mensaje: respuesta?.mensaje || 'Ya podés iniciar sesión con tu cuenta.'
            });
            alerta.style.display = 'block';

            form.reset();

            // Si la vista es independiente (registro.html), vuelve al login.
            const loginForm = document.getElementById('loginForm');

            if (!loginForm) {
                window.setTimeout(() => {
                    window.location.href = PAGINA_LOGIN;
                }, 1200);
                return;
            }

            // Deja el email cargado en el formulario de login.
            const loginEmail = document.getElementById('loginEmail');
            const loginPassword = document.getElementById('loginPassword');

            // Quita errores previos del formulario de login.
            const alertaLogin = loginForm.querySelector('.auth-alert');
            if (alertaLogin) ocultarAlerta(alertaLogin);

            if (loginEmail) loginEmail.value = email;
            if (loginPassword) {
                loginPassword.focus();
                loginPassword.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } catch (error) {
            mostrarErrorAuth(alerta, error);
        } finally {
            alternarBotonEnviando(boton, false);
        }
    });
}


/* -------------------------------------------------------------------------- */
/* Barra de navegación                                                        */
/* -------------------------------------------------------------------------- */

function crearEstiloEnlace(primario = false) {
    const borde = primario
        ? '1px solid var(--accent-blue, #58a6ff)'
        : '1px solid transparent';
    const color = primario
        ? 'var(--accent-blue, #58a6ff)'
        : 'var(--text-muted, #8b949e)';

    return [
        'display: inline-flex',
        'align-items: center',
        'padding: 6px 10px',
        'border-radius: 6px',
        `border: ${borde}`,
        `color: ${color}`,
        'text-decoration: none',
        'font-size: 0.85rem',
        'transition: color 0.2s, border-color 0.2s'
    ].join(';');
}

function crearEnlaceAuth(texto, href, primario = false) {
    const enlace = document.createElement('a');

    enlace.textContent = texto;
    enlace.href = href;
    enlace.style.cssText = crearEstiloEnlace(primario);

    return enlace;
}

function obtenerContenedorNav() {
    const nav = document.querySelector('nav');

    if (!nav) return null;

    let contenedor = nav.querySelector('.nav-right');

    if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.className = 'nav-right';
        contenedor.style.cssText = 'display: flex; align-items: center; gap: 15px;';
        nav.appendChild(contenedor);
    }

    return contenedor;
}

function crearBotonCuenta(texto, titulo) {
    const boton = document.createElement('button');

    boton.type = 'button';
    boton.className = 'auth-account-btn';
    boton.textContent = texto;
    boton.title = titulo;
    boton.setAttribute('aria-haspopup', 'true');
    boton.setAttribute('aria-expanded', 'false');
    boton.style.cssText = [
        'background: #21262d',
        'border: 1px solid var(--border-color, #30363d)',
        'color: white',
        'padding: 6px 12px',
        'border-radius: 6px',
        'cursor: pointer',
        'font-size: 0.8rem',
        'font-weight: 600',
        'max-width: 150px',
        'overflow: hidden',
        'text-overflow: ellipsis',
        'white-space: nowrap'
    ].join(';');

    return boton;
}

function crearMenuCuenta(usuario) {
    const wrapper = document.createElement('div');
    wrapper.className = 'auth-nav';
    wrapper.style.cssText = [
        'position: relative',
        'display: flex',
        'align-items: center',
        'margin-left: 10px'
    ].join(';');

    const boton = crearBotonCuenta(
        usuario ? (usuario.nombre || 'Mi cuenta') : 'Ingresar',
        usuario
            ? `Sesión de ${usuario.nombre || 'usuario'}`
            : 'Iniciar sesión o registrarse'
    );

    const menu = document.createElement('div');
    menu.className = 'auth-menu';
    menu.style.cssText = [
        'display: none',
        'position: absolute',
        'top: calc(100% + 8px)',
        'right: 0',
        'min-width: 190px',
        'background: #161b22',
        'border: 1px solid var(--border-color, #30363d)',
        'border-radius: 8px',
        'padding: 10px',
        'box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45)',
        'z-index: 1000',
        'flex-direction: column',
        'gap: 8px'
    ].join(';');

    if (usuario) {
        const saludo = document.createElement('span');
        saludo.textContent = `Hola, ${usuario.nombre || 'usuario'}`;
        saludo.style.cssText = [
            'color: white',
            'font-size: 0.85rem',
            'font-weight: 600',
            'padding: 0 4px 4px'
        ].join(';');

        const perfil = crearEnlaceAuth('Mi Perfil', PAGINA_PERFIL);
        perfil.style.padding = '8px 10px';

        const botonSalir = document.createElement('button');
        botonSalir.type = 'button';
        botonSalir.textContent = 'Cerrar Sesión';
        botonSalir.style.cssText = [
            'background: rgba(218, 54, 51, 0.12)',
            'border: 1px solid var(--accent-red, #da3633)',
            'color: var(--accent-red, #da3633)',
            'padding: 8px 10px',
            'border-radius: 6px',
            'cursor: pointer',
            'font-size: 0.8rem',
            'font-weight: 600'
        ].join(';');

        botonSalir.addEventListener('click', () => {
            cerrarSesion();
        });

        menu.append(saludo, perfil, botonSalir);
    } else {
        const login = crearEnlaceAuth('Iniciar Sesión', PAGINA_LOGIN);
        const registro = crearEnlaceAuth(
            'Registrarse',
            PAGINA_REGISTRO,
            true
        );

        login.style.padding = '8px 10px';
        registro.style.padding = '8px 10px';
        menu.append(login, registro);
    }

    boton.addEventListener('click', (event) => {
        event.stopPropagation();

        const abierto = menu.style.display !== 'none';
        menu.style.display = abierto ? 'none' : 'flex';
        boton.setAttribute('aria-expanded', String(!abierto));
    });

    wrapper.append(boton, menu);

    return wrapper;
}

function crearAuthInline(usuario) {
    const authNav = document.createElement('div');

    authNav.className = 'auth-nav';
    authNav.style.cssText = [
        'display: flex',
        'align-items: center',
        'gap: 10px',
        'margin-left: 10px'
    ].join(';');

    if (usuario) {
        const nombre = document.createElement('span');
        nombre.textContent = `Hola, ${usuario.nombre || 'usuario'}`;
        nombre.style.cssText = [
            'color: white',
            'font-size: 0.85rem',
            'font-weight: 600',
            'white-space: nowrap'
        ].join(';');

        const perfil = crearEnlaceAuth('Mi Perfil', PAGINA_PERFIL);
        perfil.style.padding = '6px 10px';

        const botonSalir = document.createElement('button');
        botonSalir.type = 'button';
        botonSalir.textContent = 'Cerrar Sesión';
        botonSalir.style.cssText = [
            'background: #21262d',
            'border: 1px solid var(--border-color, #30363d)',
            'color: white',
            'padding: 6px 12px',
            'border-radius: 6px',
            'cursor: pointer',
            'font-size: 0.8rem'
        ].join(';');

        botonSalir.addEventListener('click', () => {
            cerrarSesion();
        });

        authNav.append(nombre, perfil, botonSalir);
    } else {
        authNav.append(
            crearEnlaceAuth('Iniciar Sesión', PAGINA_LOGIN),
            crearEnlaceAuth('Registrarse', PAGINA_REGISTRO, true)
        );
    }

    return authNav;
}

function cerrarMenusAuth(event) {
    document.querySelectorAll('.auth-menu').forEach((menu) => {
        if (menu.style.display === 'none') return;

        const wrapper = menu.closest('.auth-nav');

        if (wrapper && !wrapper.contains(event.target)) {
            menu.style.display = 'none';
            wrapper
                .querySelector('.auth-account-btn')
                ?.setAttribute('aria-expanded', 'false');
        }
    });
}

function asegurarCierreMenus() {
    if (document.body.dataset.authMenusBound === 'true') return;

    document.body.dataset.authMenusBound = 'true';

    document.addEventListener('click', cerrarMenusAuth);
    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;

        document.querySelectorAll('.auth-menu').forEach((menu) => {
            menu.style.display = 'none';
            menu.closest('.auth-nav')
                ?.querySelector('.auth-account-btn')
                ?.setAttribute('aria-expanded', 'false');
        });
    });
}

function renderizarEstadoAuth() {
    const contenedorNav = obtenerContenedorNav();

    if (!contenedorNav) return;

    contenedorNav
        .querySelectorAll('.auth-nav')
        .forEach((anterior) => anterior.remove());

    const usuario = obtenerUsuarioActual();
    const botonPerfil = contenedorNav.querySelector('.profile-btn');

    if (botonPerfil) {
        // En las pantallas de armado ya existe un botón de perfil.
        // Se oculta y se reemplaza por un menú de cuenta compacto.
        botonPerfil.style.display = 'none';
        botonPerfil.dataset.authOculto = 'true';
        contenedorNav.appendChild(crearMenuCuenta(usuario));
        return;
    }

    contenedorNav.appendChild(crearAuthInline(usuario));
}


/* -------------------------------------------------------------------------- */
/* Inicialización                                                             */
/* -------------------------------------------------------------------------- */

export function inicializarAuth() {
    renderizarEstadoAuth();
    inicializarFormularioLogin();
    inicializarFormularioRegistro();
    asegurarCierreMenus();

    window.addEventListener(EVENTO_SESION, renderizarEstadoAuth);

    // Mantiene sincronizada la sesión entre pestañas abiertas.
    window.addEventListener('storage', (event) => {
        if (
            event.key === 'auth_access_token'
            || event.key === 'auth_usuario'
            || event.key === null
        ) {
            renderizarEstadoAuth();
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarAuth, { once: true });
} else {
    inicializarAuth();
}
