from django import forms
from .models import Veiculo, Categoria


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'nome', 'telefone', 'marca', 'modelo', 'categoria', 'tipo_cliente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()