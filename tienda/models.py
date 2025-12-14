from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Categoria(models.Model):
    nombre=models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.nombre
    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=254, unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre=models.CharField(max_length=254)
    precio=models.IntegerField()
    categoria=models.ManyToManyField(Categoria)
    imagen=models.ImageField(upload_to="productos")
    codigo_barra=models.CharField(max_length=254, unique=True, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, blank=True, null=True)
    descripcion=models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    stock_critico = models.BooleanField(default=False)

    def __str__(self):
        return self.producto.nombre, self.stock

class Venta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente', 
        choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada')])

    def total(self):
        total = 0
        for item in self.detalle_venta_set.all():
            total += item.subtotal()
        return total

    def __str__(self):
        return self.usuario.username

class Detalle_venta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    

    def subtotal(self):
        precio = self.precio_unitario or self.producto.precio
        return precio * self.cantidad
    
    def __str__(self):
        return self.producto.nombre
    

