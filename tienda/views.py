from calendar import calendar
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Inventario, Venta, Detalle_venta, Proveedor, MovimientoInventario
from .forms import ProductoForm, CategoriaForm, ProductoUpdateForm, InventarioForm, ProveedorForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from decimal import Decimal, InvalidOperation
from django.db.models import Q
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import random
import openpyxl
from django.http import HttpResponse
from .models import Producto
from django.http import JsonResponse
# Create your views here.

def administrador_required(user):
    return user.is_authenticated and user.usuarios.rol.nombre == 'Administrador'

def home(request):
    productos=Producto.objects.count()
    ventas=Venta.objects.count()
    all_stock_bajo = Inventario.objects.filter(stock_critico=True, stock__lte=5)
    stock_bajo = all_stock_bajo.count()
    # for i in stock_bajo:
    #     print(i.producto.nombre, i.stock)
    ventas_hoy=Venta.objects.filter(fecha_venta__date=datetime.date.today(), estado="pagada").count()
    ultimas_5_ventas=Venta.objects.filter(fecha_venta__date=datetime.date.today(), estado="pagada" ).order_by('-fecha_venta')[:5]
    return render(request, 'tienda/inicio/home.html', {'productos': productos, 'ventas': ventas, 'stock_bajo': stock_bajo, 'all_stock_bajo': all_stock_bajo, 'ventas_hoy': ventas_hoy, 'ultimas_5_ventas': ultimas_5_ventas})

def StockBajoListView(request):
    # Stock crítico: productos marcados como críticos con stock <= 5
    stock_critico = Inventario.objects.filter(stock_critico=True, stock__lte=5)
    # Stock bajo no crítico: productos NO marcados como críticos pero con stock <= 5
    stock_no_critico = Inventario.objects.filter(stock_critico=False, stock__lte=5)
    return render(request, 'tienda/inicio/stock_bajo_list.html', {
        'stock_critico': stock_critico,
        'stock_no_critico': stock_no_critico
    })

# <---------------vistas de producto------------>
@login_required
def ProductoListView(request):
    query = request.GET.get('q', '').strip()
    categorias_select = request.GET.getlist('categoria')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(Q(nombre__icontains=query)|Q(codigo_barra__icontains=query))

    if categorias_select:
        productos = productos.filter(categoria__id__in=categorias_select).distinct()

    categorias = Categoria.objects.all()

    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    items = venta.detalle_venta_set.all()
    total = venta.total()

    contexto = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categorias_seleccionadas': [int(cat_id) for cat_id in categorias_select],
        'venta': venta,
        'items': items,
        'total': total,
    }
    return render(request, 'tienda/producto/producto_list.html', contexto)

def ProductoDetailView(request, id):
    producto = get_object_or_404(Producto, pk=id)
    return render(request, 'tienda/producto/producto_detail.html', {'producto': producto})

@login_required
@user_passes_test(administrador_required)
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

@login_required
@user_passes_test(administrador_required)
def ProductoCreateView(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES or None)
        if form.is_valid():
            # 1. Guardamos el objeto pero NO en la base de datos aún (commit=False)
            producto = form.save(commit=False)
            
            # 2. Si no tiene código, le inventamos uno
            if not producto.codigo_barra:
                # Generamos un número aleatorio de 12 dígitos (para EAN-13)
                # O podrías usar '200' + id si guardaras primero, pero random es más fácil aquí
                numero_random = random.randint(100000000000, 999999999999) 
                producto.codigo_barra = f"{numero_random}"
            
            # 3. Ahora sí guardamos el producto definitivo
            producto.save()
            form.save_m2m()

            # ... (el resto de tu lógica de inventario sigue igual) ...
            stock = request.POST.get('stock')
            stock_critico = form.cleaned_data['stock_critico']
            Inventario.objects.create(producto=producto, stock=stock, stock_critico=stock_critico)
            
            messages.success(request, "Producto creado exitosamente")
            return redirect('inventario-list')
    else:
        form = ProductoForm()
    return render(request, 'tienda/producto/producto_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(administrador_required)
def ProductoDeleteView(request, id):
    producto=get_object_or_404(Producto, pk=id)
    if request.method=="POST":
        producto.delete()
        messages.success(request, "Producto eliminado exitosamente")
        return redirect('inventario-list')
    return render(request, 'tienda/producto/producto_delete.html', {'producto': producto})

@login_required
@user_passes_test(administrador_required)
def ProductoUpdateView(request, id):
    producto = get_object_or_404(Producto, pk=id) 
    if request.method == "POST":
        form = ProductoUpdateForm(request.POST, request.FILES or None, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto modificado exitosamente")
            return redirect('inventario-list')
    else:
        form = ProductoUpdateForm(instance=producto)
    return render(request, 'tienda/producto/producto_form.html', {'form': form, 'action': 'Modificar'})

@login_required
@user_passes_test(administrador_required)
# proyecto_mundo_cartasV4/tienda/views.py

@login_required
@user_passes_test(administrador_required)
def InventarioUpdateView(request, id):
    producto = get_object_or_404(Producto, pk=id)
    inventario, _ = Inventario.objects.get_or_create(producto=producto)
    
    if request.method == "POST":
        stock_antes = inventario.stock 
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            nuevo_inventario = form.save()
            diferencia = nuevo_inventario.stock - stock_antes

            if diferencia > 0:
                MovimientoInventario.objects.create(
                    producto=producto,
                    cantidad=diferencia,
                    tipo='entrada',
                    referencia="Reposición manual"
                )
            
            messages.success(request, f"Stock actualizado")
            return redirect('inventario-list')
    else:
        form = InventarioForm(instance=inventario)
    return render(request, 'tienda/inventario/inventario_form.html', {'form': form, 'producto': producto})


# proyecto_mundo_cartasV4/tienda/views.py

@login_required
@user_passes_test(administrador_required)
def HistorialInventarioView(request):
    movimientos = MovimientoInventario.objects.all().order_by('-fecha')
    return render(request, 'tienda/inventario/historial_list.html', {'movimientos': movimientos})
# <---------------vistas de categoria------------>

@login_required
@user_passes_test(administrador_required)
def CategoriaListView(request):
    return render(request, 'tienda/categoria/categoria_list.html', {'categorias':Categoria.objects.all()})

@login_required
@user_passes_test(administrador_required)
def CategoriaCreateView(request):
    if request.method=="POST":
        form=CategoriaForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria creada exitosamente")
            return redirect('categoria-list')
    else:
        form=CategoriaForm()
    return render(request, 'tienda/categoria/categoria_form.html', {'form':form, 'action':'Crear'})

@login_required
@user_passes_test(administrador_required)
def CategoriaDeleteView(request, id):
    categoria=get_object_or_404(Categoria, pk=id)
    if request.method=="POST":
        categoria.delete()
        messages.success(request, "Categoria eliminada exitosamente")
        return redirect('categoria-list')
    return render(request, 'tienda/categoria/categoria_delete.html', {'categoria': categoria})


@login_required
@user_passes_test(administrador_required)
def CategoriaUpdateView(request, id):
    categoria = get_object_or_404(Categoria, pk=id) 
    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES or None, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria modificada exitosamente")
            return redirect('categoria-list')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'tienda/categoria/categoria_form.html', {'form': form, 'action': 'Modificar'})

# <--------------- Vistas de Proveedor ------------>

@login_required
@user_passes_test(administrador_required)
def ProveedorListView(request):
    return render(request, 'tienda/proveedor/proveedor_list.html', {'proveedores': Proveedor.objects.all()})

@login_required
@user_passes_test(administrador_required)
def ProveedorCreateView(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor creado exitosamente")
            return redirect('proveedor-list')
    else:
        form = ProveedorForm()
    return render(request, 'tienda/proveedor/proveedor_form.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(administrador_required)
def ProveedorUpdateView(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor modificado exitosamente")
            return redirect('proveedor-list')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'tienda/proveedor/proveedor_form.html', {'form': form, 'action': 'Modificar'})

@login_required
@user_passes_test(administrador_required)
def ProveedorDeleteView(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    if request.method == "POST":
        proveedor.delete()
        messages.success(request, "Proveedor eliminado exitosamente")
        return redirect('proveedor-list')
    return render(request, 'tienda/proveedor/proveedor_delete.html', {'proveedor': proveedor})

@login_required
@user_passes_test(administrador_required)
def ProveedorDetailView(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    productos = Producto.objects.filter(proveedor=proveedor)
    return render(request, 'tienda/proveedor/proveedor_detail.html', {
        'proveedor': proveedor,
        'productos': productos
    })



@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.inventario.stock == 0: 
        messages.error(request, "No hay stock disponible para este producto")
        return redirect("producto-list")
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
    messages.success(request, "Producto agregado al carrito.")
    return redirect('producto-list')

"""def ver_carrito(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    
    items = venta.detalle_venta_set.all()
    total = venta.total()

    return render(request, 'tienda/carrito/ver_carrito.html', {
        'venta': venta,
        'items': items,
        'total': total,
    })
"""
@login_required
def incrementar_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    if item.cantidad + 1 > item.producto.inventario.stock:
        messages.error(request, "No hay suficiente stock disponible para este producto")
        return redirect("producto-list")
    item.cantidad += 1
    item.save()
    return redirect('producto-list')


@login_required
def disminuir_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()
    return redirect('producto-list')


@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(Detalle_venta, id=item_id)
    item.delete()
    messages.success(request, "Item eliminado del carrito.")
    return redirect('producto-list')


@login_required
def vaciar_carrito(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    venta.detalle_venta_set.all().delete()
    messages.success(request, "Se ha vaciado el carrito")
    return redirect('producto-list')


@login_required
def resumen_pago(request):
    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente', defaults={'estado': 'pendiente'})
    items = venta.detalle_venta_set.all()

    if not items.exists():
        return redirect('producto-list')

    # Handle discount application
    if request.method == 'POST':
        descuento_str = request.POST.get('descuento', '0')
        try:
            descuento = Decimal(descuento_str)
            if 0 <= descuento <= 100:
                venta.descuento = descuento
                venta.save()
        except (ValueError, InvalidOperation):
            pass  # Invalid input, ignore

    total_final = venta.total() 
    
    sin_iva = total_final / Decimal('1.19')
    iva = total_final - sin_iva
   
    # Calculate discount amount and total with discount
    descuento_dinero = total_final * (venta.descuento / 100)
    total_con_descuento = total_final - descuento_dinero

    contexto = {
        'venta': venta,
        'items': items,
        'sin_iva': sin_iva,
        'iva': iva,
        'total_final': total_final,
        'descuento_porcentaje': venta.descuento,
        'descuento_dinero': descuento_dinero,
        'total_con_descuento': total_con_descuento,
    }
    
    return render(request, 'tienda/carrito/resumen.html', contexto)

@login_required
def pagar(request):
    venta = get_object_or_404(Venta, usuario=request.user, estado='pendiente')
    if request.method == 'POST':
        metodo = request.POST.get('metodo_pago')
        items = venta.detalle_venta_set.all()

        for item in items:
            inventario = Inventario.objects.get(producto=item.producto)
            inventario.stock -= item.cantidad
            inventario.save()

            # --- NUEVO: REGISTRAR MOVIMIENTO DE SALIDA ---
            MovimientoInventario.objects.create(
                producto=item.producto,
                cantidad=item.cantidad,
                tipo='salida',
                referencia=f"Venta #{venta.id}"
            )

        venta.estado = 'pagada'
        venta.metodo_pago = metodo 
        venta.save()
        return render(request, 'tienda/carrito/pago.html', {'venta': venta})
    return redirect('resumen_pago')


@login_required
def reporte_ventas_año(request):
    años = (
        Venta.objects.filter(estado="pagada")
        .values_list("fecha_venta__year", flat=True)
        .distinct()
        .order_by("-fecha_venta__year")
    )
    return render(request, "tienda/reporte/venta_años.html", {"años": años})

@login_required
def reporte_ventas_mes(request, año):
    meses = (
        Venta.objects.filter(estado="pagada", fecha_venta__year=año)
        .values_list("fecha_venta__month", flat=True)
        .distinct()
        .order_by("-fecha_venta__month")
    )
    return render(request, "tienda/reporte/venta_meses.html", {"meses": meses, "año": año})

@login_required
def reporte_ventas_dias(request, año, mes):
    dias = (
        Venta.objects.filter(estado="pagada", fecha_venta__year=año, fecha_venta__month=mes)
        .values_list("fecha_venta__date", flat=True)
        .distinct()
        .order_by("-fecha_venta__date")
    )
    return render(request, "tienda/reporte/venta_dias.html", {"dias": dias, "mes": mes, "año": año})

@login_required
def boleta(request, id):
    venta = get_object_or_404(Venta, pk=id)
    return render(request, 'tienda/carrito/boleta.html', {'venta': venta})

@login_required
def reporte_ventas(request, fecha, año, mes):
    fecha_obj = datetime.datetime.strptime(str(fecha), '%Y-%m-%d').date()
    
    ventas = Venta.objects.filter(
        estado="pagada",
        fecha_venta__date=fecha_obj).prefetch_related("detalle_venta_set__producto", "usuario").order_by('-fecha_venta')
    
    total_ventas_dia = sum(venta.total_con_descuento() for venta in ventas)

    return render(request,"tienda/reporte/reporte_ventas.html",{
        "ventas": ventas, 
        "fecha": fecha_obj, 
        "año": año, 
        "mes": mes,
        "total_ventas_dia": total_ventas_dia
    })


def imprimir_etiqueta(request, id):
    producto = get_object_or_404(Producto, pk=id)
    return render(request, 'tienda/producto/etiqueta.html', {'producto': producto})




@login_required
def agregar_por_codigo(request, codigo):
    producto = Producto.objects.filter(codigo_barra=codigo).first()
    if not producto:
        return JsonResponse({'status': 'error', 'message': 'Producto no existe'}, status=404)
    
    if not hasattr(producto, 'inventario') or producto.inventario.stock <= 0:
        return JsonResponse({'status': 'error', 'message': 'Sin Stock'}, status=400)

    venta, _ = Venta.objects.get_or_create(usuario=request.user, estado='pendiente')
    item, creado = Detalle_venta.objects.get_or_create(
        venta=venta,
        producto=producto,
        defaults={'precio_unitario': producto.precio, 'cantidad': 1}
    )
    if not creado:
        item.cantidad += 1
        item.save()

    return JsonResponse({
        'status': 'ok',
        'nombre': producto.nombre,
        'nuevo_total': venta.total() 
    })


@login_required
def exportar_productos_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    headers = ['ID', 'Nombre', 'Precio', 'Stock Actual', 'Proveedor', 'Código de Barras']
    ws.append(headers)

    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)

    productos = Producto.objects.all().select_related('proveedor', 'inventario')

    for p in productos:
        ws.append([
            p.id,
            p.nombre,
            p.precio,
            p.inventario.stock if hasattr(p, 'inventario') else 0,
            p.proveedor.nombre if p.proveedor else "Sin proveedor",
            p.codigo_barra
        ])
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
    
    wb.save(response)
    return response