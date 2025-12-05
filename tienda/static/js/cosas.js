const btn = document.getElementById('toggle-carrito-btn');
const carrito = document.getElementById('carrito-container');
const productos = document.getElementById('productos-container');

btn.addEventListener('click', function () {
    carrito.classList.toggle('d-none');
    productos.classList.toggle('col-md-9');
    productos.classList.toggle('col-md-12');
});
