from django.urls import path
from .views import (ProductoListView, ProductoCreateView, ProductoDetailView, ProductoDeleteView, ProductoUpdateView,CategoriaListView, 
                    CategoriaCreateView, CategoriaDeleteView, CategoriaUpdateView, InventarioListView, InventarioUpdateView, 
                      agregar_al_carrito, eliminar_item, ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorDeleteView, ProveedorDetailView,
                    incrementar_item, disminuir_item, vaciar_carrito, resumen_pago, pagar, home, 
                    reporte_ventas_año, reporte_ventas_mes, reporte_ventas_dias, 
                    reporte_ventas, StockBajoListView, imprimir_etiqueta, agregar_por_codigo, exportar_productos_excel, HistorialInventarioView, boleta)  

urlpatterns=[ 
    path('inicio/', home, name='home'),
    path('inicio/stock_bajo/', StockBajoListView, name='stock_bajo_list'),
    # <---------------urls de producto------------>
    path('productos/', ProductoListView, name='producto-list'),
    path('producto/<int:id>/', ProductoDetailView, name='producto-detail'),

    
    path('producto/create/', ProductoCreateView, name='producto-create'),
    path('producto/delete/<int:id>', ProductoDeleteView, name='producto-delete'),
    path('producto/update/<int:id>', ProductoUpdateView, name='producto-update'),
    # <---------------urls de categoria------------>
    path('categoria/', CategoriaListView, name='categoria-list'),
    path('categoria/create/', CategoriaCreateView, name='categoria-create'),
    path('categoria/delete/<int:id>', CategoriaDeleteView, name='categoria-delete'),
    path('categoria/update/<int:id>', CategoriaUpdateView, name='categoria-update'),

    path('inventario/', InventarioListView, name='inventario-list'),
    path('inventario/update/<int:id>', InventarioUpdateView, name='inventario-update'),
    
    path('proveedores/', ProveedorListView, name='proveedor-list'),
    path('proveedor/<int:id>/', ProveedorDetailView, name='proveedor-detail'),
    path('proveedor/create/', ProveedorCreateView, name='proveedor-create'),
    path('proveedor/update/<int:id>/', ProveedorUpdateView, name='proveedor-update'),
    path('proveedor/delete/<int:id>/', ProveedorDeleteView, name='proveedor-delete'),

    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_item, name='eliminar_item'),
    path('carrito/incrementar/<int:item_id>/', incrementar_item, name='incrementar_item'),
    path('carrito/disminuir/<int:item_id>/', disminuir_item, name='disminuir_item'),
    path('carrito/vaciar/', vaciar_carrito, name='vaciar_carrito'),


    path('pago/resumen/', resumen_pago, name='resumen_pago'),
    path('carrito/pagar/', pagar, name='pagar'),
    
    path("reportes/años/", reporte_ventas_año, name="reporte_años"),
    path("reportes/mes/<int:año>/", reporte_ventas_mes, name="reporte_meses"),
    path("reportes/dias/<int:año>/<int:mes>/", reporte_ventas_dias, name="reporte_dias"),
    path("reportes/<fecha>/<int:año>/<int:mes>/", reporte_ventas, name="reporte_ventas"),

    path('producto/etiqueta/<int:id>/', imprimir_etiqueta, name='imprimir-etiqueta'),

    path('carrito/agregar-ajax/<str:codigo>/', agregar_por_codigo, name='agregar-barra'),

    path('productos/exportar/', exportar_productos_excel, name='exportar-productos-excel'),


    path('inventario/historial/', HistorialInventarioView, name='inventario-historial'),
    path('boleta/<int:id>/', boleta, name='boleta'),
]