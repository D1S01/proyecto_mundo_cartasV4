from django.urls import path
from .views import (ProductoListView, ProductoCreateView, ProductoDetailView, ProductoDeleteView, ProductoUpdateView,CategoriaListView, 
                    CategoriaCreateView, CategoriaDeleteView, CategoriaUpdateView, InventarioListView, 
                     ver_carrito, agregar_al_carrito, eliminar_item,
                    incrementar_item, disminuir_item, vaciar_carrito, resumen_pago, pagar, home, reporte_ventas_dias, reporte_ventas, StockBajoListView)  

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
    

    path('carrito/', ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', eliminar_item, name='eliminar_item'),
    path('carrito/incrementar/<int:item_id>/', incrementar_item, name='incrementar_item'),
    path('carrito/disminuir/<int:item_id>/', disminuir_item, name='disminuir_item'),
    path('carrito/vaciar/', vaciar_carrito, name='vaciar_carrito'),


    path('pago/resumen/', resumen_pago, name='resumen_pago'),
    path('carrito/pagar/', pagar, name='pagar'),
    
    path("reportes/", reporte_ventas_dias, name="reporte_dias"),
    path("reportes/<fecha>/", reporte_ventas, name="reporte_ventas"),


 
]