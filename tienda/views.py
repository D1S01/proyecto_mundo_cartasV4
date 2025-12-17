from calendar import calendar
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Inventario, Venta, Detalle_venta
from .forms import ProductoForm, CategoriaForm, ProductoUpdateForm, InventarioForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from decimal import Decimal
from django.db.models import Q
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import calendar
from django.utils import timezone
import locale
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

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
    ventas_hoy=Venta.objects.filter(fecha_venta__date=timezone.now().date(), estado="pagada").count()
    ultimas_5_ventas=Venta.objects.filter(fecha_venta__date=timezone.now().date(), estado="pagada" ).order_by('-fecha_venta')[:5]
    return render(request, 'tienda/inicio/home.html', {'productos': productos, 'ventas': ventas, 'stock_bajo': stock_bajo, 'all_stock_bajo': all_stock_bajo, 'ventas_hoy': ventas_hoy, 'ultimas_5_ventas': ultimas_5_ventas})

def StockBajoListView(request):
    all_stock_bajo = Inventario.objects.filter(stock_critico=True, stock__lte=5)
    return render(request, 'tienda/inicio/stock_bajo_list.html', {'all_stock_bajo': all_stock_bajo})

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
            producto = form.save()
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
    return render(request, 'tienda/producto/producto_delete.html')

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
def InventarioUpdateView(request, id):
    producto = get_object_or_404(Producto, pk=id)
    inventario, created = Inventario.objects.get_or_create(producto=producto, defaults={'stock': 0})
    
    if request.method == "POST":
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Stock de {producto.nombre} actualizado exitosamente")
            return redirect('inventario-list')
    else:
        form = InventarioForm(instance=inventario)
    
    return render(request, 'tienda/inventario/inventario_form.html', {
        'form': form, 
        'producto': producto,
        'action': 'Modificar Stock'
    })
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
    return render(request, 'tienda/categoria/categoria_delete.html')


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
@user_passes_test(administrador_required)
def reporte_ventas_año(request):
    años = (
        Venta.objects.filter(estado="pagada")
        .values_list("fecha_venta__year", flat=True)
        .distinct()
        .order_by("-fecha_venta__year")
    )
    return render(request, "tienda/reporte/venta_años.html", {"años": años})

@login_required
@user_passes_test(administrador_required)
def reporte_ventas_mes(request, año):
    # se procedera a mandar los nombres de los meses con ventas en el año seleccionado
    meses_venta = (
        Venta.objects.filter(estado="pagada", fecha_venta__year=año)
        .values_list("fecha_venta__month", flat=True)
        .distinct()
        .order_by("-fecha_venta__month")
    )

    # for i in meses:
        # i = calendar.month_name[i]  # Imprime el nombre del mes correspondiente
        # print(calendar.month_name[i], "this os the month name")
        # i = i.strftime("%B")  # Formatea el mes como nombre completo

    
    # Convertir números a nombres
    # meses = [{"numero": m, "nombre": calendar.month_name[m]} for m in meses]

    # meses_legibles = []
    # for mes in meses_venta:
    #     nombre_mes = calendar.month_name[mes]
    #     meses_legibles.append({"numero": mes, "nombre": nombre_mes})
    # meses = [m['numero'] for m in meses_legibles]
    meses_legibles = [{"numero": m, "nombre": calendar.month_name[m]} for m in meses_venta]


    
    return render(request, "tienda/reporte/venta_meses.html", {"meses": meses_legibles, "año": año})

@login_required
@user_passes_test(administrador_required)
def reporte_ventas_dias(request, año, mes):
    dias = (
        Venta.objects.filter(estado="pagada", fecha_venta__year=año, fecha_venta__month=mes)
        .values_list("fecha_venta__date", flat=True)
        .distinct()
        .order_by("-fecha_venta__date")
    )
    # dias_legibles = [dia.day for dia in dias]
    mes_legible = calendar.month_name[mes]
    return render(request, "tienda/reporte/venta_dias.html", {"dias": dias, "mes": mes, "mes_legible": mes_legible, "año": año})

@login_required
@user_passes_test(administrador_required)
def reporte_ventas(request, fecha):
    ventas = Venta.objects.filter(
        estado="pagada",
        fecha_venta__date=fecha).prefetch_related("detalle_venta_set__producto", "usuario")
    
    total_ventas_dia = sum(venta.total() for venta in ventas)
    
    #extrayendo mes y año de la fecha
    formatted_date = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    mes = formatted_date.month
    año = formatted_date.year

    return render(request,"tienda/reporte/reporte_ventas.html",{"ventas": ventas, "total_ventas_dia": total_ventas_dia, "fecha": fecha, "mes": mes, "año": año})