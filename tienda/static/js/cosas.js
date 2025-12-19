const btn = document.getElementById('toggle-carrito-btn');
const carrito = document.getElementById('carrito-container');
const productos = document.getElementById('productos-container');

if (btn) {
    btn.addEventListener('click', function () {
        if (carrito) carrito.classList.toggle('d-none');
        if (productos) {
            productos.classList.toggle('col-md-9');
            productos.classList.toggle('col-md-12');
        }
    });
}


