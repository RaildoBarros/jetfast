from django import forms
from .models import Veiculo, Plano

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'nome', 'telefone', 'modelo_veiculo', 'plano']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plano'].queryset = Plano.objects.all()