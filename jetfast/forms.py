from django import forms
from .models import Veiculo, Categoria


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'nome', 'telefone', 'marca', 'modelo', 'categoria'] # Alterado plano para categoria

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.all()