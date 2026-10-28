document.addEventListener('DOMContentLoaded', () => {
    const btnAmd = document.querySelector('.card-amd .btn-select');
    const btnIntel = document.querySelector('.card-intel .btn-select');

    // IDs iniciales de componentes según la plataforma elegida en PostgreSQL
    // (Ajusta estos IDs con los reales que tengas cargados en tu base de datos)
    const componentesAMD = [1, 9, 5, 13, 17, 21, 25, 29];    // Ejemplo: Mother AM5, Ryzen 5, DDR5...
    const componentesIntel = [2, 10, 6, 14, 18, 22, 26, 30]; // Ejemplo: Mother LGA1700, Intel i5, DDR4...

    if (btnAmd) {
        btnAmd.addEventListener('click', (e) => {
            // Guardar plataforma e IDs en localStorage
            localStorage.setItem('plataforma_seleccionada', 'AMD');
            localStorage.setItem('componentes_seleccionados', JSON.stringify(componentesAMD));
            // La redirección por href="armado-guiado-amd.html" ocurre automáticamente
        });
    }

    if (btnIntel) {
        btnIntel.addEventListener('click', (e) => {
            // Guardar plataforma e IDs en localStorage
            localStorage.setItem('plataforma_seleccionada', 'Intel');
            localStorage.setItem('componentes_seleccionados', JSON.stringify(componentesIntel));
            // La redirección por href="armado-guiado-intel.html" ocurre automáticamente
        });
    }
});