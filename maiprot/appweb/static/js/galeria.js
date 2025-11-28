// galeria.js
document.addEventListener('DOMContentLoaded', function () {

    // protege si no hay carruseles
    const galerias = document.querySelectorAll('.galeria-hover');
    if (!galerias.length) return;

    function showSlide(carrusel, index) {
        const images = carrusel.querySelectorAll('.carrusel-img');
        if (!images.length) return;

        // normalizar index
        if (index >= images.length) index = 0;
        if (index < 0) index = images.length - 1;

        images.forEach((img, i) => {
            img.classList.toggle('active', i === index);
        });

        carrusel.dataset.currentSlide = index;
    }

    // inicializar cada galería
    galerias.forEach(galeria => {
        const carrusel = galeria.querySelector('.carrusel-imagenes');
        if (!carrusel) return;
        // asegura que haya al menos una imagen activa
        showSlide(carrusel, 0);
    });

    // listeners en flechas
    document.querySelectorAll('.prev-btn, .next-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const gal = btn.closest('.galeria-hover');
            if (!gal) return;
            const carrusel = gal.querySelector('.carrusel-imagenes');
            if (!carrusel) return;
            let current = parseInt(carrusel.dataset.currentSlide || 0, 10);

            if (btn.classList.contains('next-btn')) {
                current++;
            } else {
                current--;
            }
            showSlide(carrusel, current);
        });
    });

    // si el usuario sale del hover, volvemos a slide 0 (opcional)
    galerias.forEach(gal => {
        gal.addEventListener('mouseleave', () => {
            const carrusel = gal.querySelector('.carrusel-imagenes');
            if (carrusel) showSlide(carrusel, 0);
        });
    });

});
