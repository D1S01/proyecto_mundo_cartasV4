from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Inventario, Venta, Detalle_venta
from .forms import ProductoForm, CategoriaForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from decimal import Decimal
from django.db.models import Q

# Create your views here.


def home(request):
    return render(request, 'tienda/inicio/home.html')
# <---------------vistas de producto------------>
@login_required
def ProductoListView(request):
    query = request.GET.get('q', '').strip()
    categorias_select = request.GET.getlist('categoria')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(Q(nombre__icontains=query))

    if categorias_select:
        productos = productos.filter(categoria__id__in=categorias_select).distinct()

    categorias = Categoria.objects.all()

    contexto = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categorias_seleccionadas': [int(cat_id) for cat_id in categorias_select]
    }
    return render(request, 'tienda/producto/producto_list.html', contexto)

def InventarioListView(request):
    query = request.GET.get('q', '').strip()
    productos = Producto.objects.all()
    if query:
        productos = productos.filter(Q(nombre__icontains=query))
    
    contexto = {
        'productos': productos, 
        'query': query
    }
    return render(request, 'tienda/inventario/inventario_list.html', contexto)

def ProductoCreateView(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES or None)
        if form.is_valid():
            producto = form.save()
            stock = request.POST.get('stock')
            Inventario.objects.create(producto=producto, stock=stock)
            return redirect('inventario-list')
    else:
        form = ProductoForm()
    return render(request, 'tienda/producto/producto_form.html', {'form': form, 'action': 'Crear'})

@login_required
def ProductoDeleteView(request, id):
    producto=get_object_or_404(Producto, pk=id)
    if request.method=="POST":
        producto.delete()
        return redirect('inventario-list')
    return render(request, 'tienda/producto/producto_delete.html')

@login_required
def ProductoUpdateView(request, id):
    producto = get_object_or_404(Producto, pk=id) 
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES or None, instance=producto)
        if form.is_valid():
            producto = form.save()
            stock = request.POST.get('stock')
            Inventario.objects.update_or_create(producto=producto, defaults={'stock': stock})
            return redirect('inventario-list')
    else:
        form = ProductoForm(instance=producto, initial={'stock': producto.inventario.stock})
    return render(request, 'tienda/producto/producto_form.html', {'form': form, 'action': 'Modificar'})
# <---------------vistas de categoria------------>
@login_required
def CategoriaListView(request):
    return render(request, 'tienda/categoria/categoria_list.html', {'categorias':Categoria.objects.all()})

@login_required
def CategoriaCreateView(request):
    if request.method=="POST":
        form=CategoriaForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('categoria-list')
    else:
        form=CategoriaForm()
    return render(request, 'tienda/categoria/categoria_form.html', {'form':form, 'action':'Crear'})

@login_required
def CategoriaDeleteView(request, id):
    categoria=get_object_or_404(Categoria, pk=id)
    if request.method=="POST":
        categoria.delete()
        return redirect('categoria-list')
    return render(request, 'tienda/categoria/categoria_delete.html')

def CategoriaUpdateView(request, id):
    categoria = get_object_or_404(Categoria, pk=id) 
    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES or None, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria-list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'tienda/categoria/categoria_form.html', {'form': form, 'action': 'Modificar'})


@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    item, creado = Detalle_venta.objects.get_or_create(
        venta=venta,
        producto=producto,
        defaults={'precio_unitario': producto.precio, 'cantidad': 1}
    )
    if not creado:
        item.cantidad += 1
        item.precio_unitario = producto.precio 
        item.save()

    return redirect('producto-list')

def ver_carrito(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    
    items = venta.detalle_venta_set.all()
    total = venta.total()

    return render(request, 'tienda/carrito/ver_carrito.html', {
        'venta': venta,
        'items': items,
        'total': total,
    })

@login_required
def incrementar_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    item.cantidad += 1
    item.save()
    return redirect('ver_carrito')


@login_required
def disminuir_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()
    return redirect('ver_carrito')


@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    item.delete()
    return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    venta.detalle_venta_set.all().delete()
    return redirect('ver_carrito')


@login_required
def resumen_pago(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    items = venta.detalle_venta_set.all()

    if not items.exists():
        return redirect('ver_carrito')

    total_final = venta.total() 
    
    sin_iva = total_final / Decimal('1.19')
    iva = total_final - sin_iva
   

    contexto = {
        'venta': venta,
        'items': items,
        'sin_iva': sin_iva,
        'iva': iva,
        'total_final': total_final,
    }
    
    return render(request, 'tienda/carrito/resumen.html', contexto)

@login_required
def pagar(request):
    venta = get_object_or_404(Venta, usuario=request.user, estado='pendiente')
    items = venta.detalle_venta_set.all()

    for item in items:
        try:
            inventario = Inventario.objects.get(producto=item.producto)
            inventario.stock -= item.cantidad
            inventario.save()
        except Inventario.DoesNotExist:
           pass
    
    
    venta.estado = 'pagada'
    venta.save()
    
    return render(request, 'tienda/carrito/pago.html')

@login_required
def reporte_ventas_dias(request):
    dias = (
        Venta.objects.filter(estado="pagada")
        .values_list("fecha_venta__date", flat=True)
        .distinct()
        .order_by("-fecha_venta__date")
    )
    return render(request, "tienda/reporte/venta_dias.html", {"dias": dias})

@login_required
def reporte_ventas(request, fecha):
    ventas = Venta.objects.filter(
        estado="pagada",
        fecha_venta__date=fecha).prefetch_related("detalle_venta_set__producto", "usuario")

    return render(request,"tienda/reporte/reporte_ventas.html",{"ventas": ventas, "fecha": fecha})