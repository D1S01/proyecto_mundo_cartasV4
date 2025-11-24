from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    stock = forms.IntegerField(label='Stock', min_value=0, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'categoria', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.CheckboxSelectMultiple(),
        }

        

class CategoriaForm(forms.ModelForm):
    class Meta:
        model=Categoria
        fields="__all__"