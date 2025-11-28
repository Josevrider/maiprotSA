// carrito.js

// obtiene csrftoken desde cookie (función Django-friendly)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const csrftoken = getCookie('csrftoken');

// función para formatear número sin decimales
function fmt(n) {
    return Math.round(Number(n));
}

// actualizar cantidad - escucha inputs
document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.cantidad-input').forEach(input => {
        input.addEventListener('change', function () {
            const itemID = this.dataset.item;
            const cantidad = parseInt(this.value || 1, 10);

            fetch(`/carrito/actualizar/${itemID}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
                },
                body: new URLSearchParams({ cantidad })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    console.error('Error', data);
                    return;
                }

                if (data.eliminado) {
                    const el = document.querySelector(`#item-${itemID}`);
                    if (el) el.remove();
                } else {
                    const sub = document.querySelector(`#subtotal-${itemID}`);
                    if (sub) sub.textContent = '$' + fmt(data.subtotal);
                }

                // actualizar totales
                const t1 = document.querySelector('#total-carrito');
                const t2 = document.querySelector('#total-carrito2');
                if (t1) t1.textContent = fmt(data.total);
                if (t2) t2.textContent = fmt(data.total);

                // badge (si existe)
                actualizarBadgeCuenta();
            }).catch(err => console.error(err));
        });
    });

});

// eliminar por icono (usa misma vista con cantidad = 0)
function eliminarItem(itemID) {
    if (!confirm('¿Eliminar este producto del carrito?')) return;

    fetch(`/carrito/actualizar/${itemID}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        },
        body: new URLSearchParams({ cantidad: 0 })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            console.error(data);
            return;
        }

        const el = document.querySelector(`#item-${itemID}`);
        if (el) el.remove();

        const t1 = document.querySelector('#total-carrito');
        const t2 = document.querySelector('#total-carrito2');
        if (t1) t1.textContent = Math.round(data.total);
        if (t2) t2.textContent = Math.round(data.total);

        actualizarBadgeCuenta();
    })
    .catch(err => console.error(err));
}

// actualiza el badge del carrito en el header si existe
function actualizarBadgeCuenta() {
    const badge = document.querySelector('.carrito-badge');
    // si no existe, tratamos de contar items visibles
    const items = document.querySelectorAll('.carrito-item').length;
    if (badge) {
        if (items > 0) {
            badge.textContent = items;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}
