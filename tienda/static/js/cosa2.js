/* ==========================================
   TOGGLE FILTROS DE CATEGORÍAS
   ========================================== */
function toggleFiltros() {
    const filtros = document.getElementById('filtros-categorias');
    if (filtros) {
        if (filtros.style.display === 'none' || filtros.style.display === '') {
            filtros.style.display = 'block';
        } else {
            filtros.style.display = 'none';
        }
    }
}
