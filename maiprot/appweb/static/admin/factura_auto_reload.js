document.addEventListener("DOMContentLoaded", function () {
    const pedidoField = document.getElementById("id_pedido");

    if (pedidoField) {
        pedidoField.addEventListener("change", function () {
            const selectedPedido = this.value;

            if (selectedPedido) {
                const baseUrl = window.location.pathname;
                window.location.href = `${baseUrl}?pedido=${selectedPedido}`;
            }
        });
    }
});
