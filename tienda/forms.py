from django import forms
from .models import Producto, Categoria, Inventario

class ProductoForm(forms.ModelForm):
    stock = forms.IntegerField(label='Stock', min_value=0, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    stock_critico = forms.BooleanField(
        label='Es producto crítico?', 
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio','proveedor', 'categoria', 'imagen', 'stock','stock_critico', 'codigo_barra', ] 
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.CheckboxSelectMultiple(),
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductoUpdateForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio','proveedor', 'categoria', 'imagen', 'codigo_barra', ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.CheckboxSelectMultiple(),
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['stock', 'stock_critico']
        widgets = {
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_critico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model=Categoria
        fields="__all__"