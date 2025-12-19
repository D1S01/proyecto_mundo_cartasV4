from django.contrib import admin
from .models import Categoria, Producto, Inventario, Proveedor
# Register your models here.
admin.site.register(Categoria)
admin.site.register(Producto)   
admin.site.register(Inventario)
admin.site.register(Proveedor)