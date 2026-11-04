const API_BASE = 'http://127.0.0.1:8000/api/v1';

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Leer la plataforma elegida en eleccion-mother.html (por defecto AMD)
    const plataforma = localStorage.getItem('plataforma_seleccionada') || 'AMD';

    // 2. Ajustar la imagen y los textos de la vista
    const imgMother = document.querySelector('.motherboard-img');
    const centerHeader = document.querySelector('.center-header p');
    const dropzoneSub = document.querySelector('.dropzone-sub');

    if (plataforma === 'Intel') {
        if (imgMother) imgMother.src = 'mother-intel.jpg';
        if (centerHeader) centerHeader.textContent = 'Placa madre B760 • LGA 1700 • Micro-ATX';
        if (dropzoneSub) dropzoneSub.textContent = 'SOCKET LGA 1700';
    } else {
        if (imgMother) imgMother.src = 'mother-amd.jpg';
        if (centerHeader) centerHeader.textContent = 'Placa madre B650 • AM5 • Micro-ATX';
        if (dropzoneSub) dropzoneSub.textContent = 'SOCKET AM5';
    }

    // 3. Consultar los procesadores disponibles a la API en PostgreSQL
    try {
        const response = await fetch(`${API_BASE}/componentes`);
        if (response.ok) {
            const componentes = await response.json();
            
            // Buscar un procesador según la plataforma seleccionada
            const cpuProcesador = componentes.find(c => {
                const tipoNombre = typeof c.tipo === 'object' ? c.tipo.nombre : c.tipo;
                const esCPU = tipoNombre && tipoNombre.toUpperCase() === 'CPU';
                return esCPU && c.nombre.toLowerCase().includes(plataforma.toLowerCase());
            });

            // Si armado.js ya renderizó el inventario dinámico, no se pisa
            // la tarjeta con un CPU distinto al que muestran los datos.
            const inventarioDinamico = document.querySelector('.inventory-box[data-dinamico="true"]');

            if (cpuProcesador && !inventarioDinamico) {
                // Actualizar la tarjeta del inventario con los datos reales
                const nameElem = document.querySelector('.comp-name');
                const wattsElem = document.querySelector('.comp-watts');
                if (nameElem) nameElem.textContent = cpuProcesador.nombre;
                if (wattsElem) wattsElem.textContent = `${cpuProcesador.consumo_watts || 65} W`;

                // Guardar el ID del CPU seleccionado en el inventario activo
                localStorage.setItem('cpu_seleccionado_id', cpuProcesador.id_componente);
            }
        }
    } catch (e) {
        console.warn("No se pudieron cargar los datos dinámicos del servidor, usando vista estática:", e);
    }
});