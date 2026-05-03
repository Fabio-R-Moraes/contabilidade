from django import forms
from .models import Contas, Operacao

class contasForm(forms.ModelForm):
    class Meta:
        model = Contas
        fields = ["nome", "descricao"]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome da Conta"}
            ),
            "descricao": forms.Textarea(
                attrs= {"class": "form-control", 
                        "placeholder": "Descrição da conta", 
                        "rows": 3}
            ),
        }
        labels = {
            "nome": "Nome da Conta", 
            "descricao": "Descrição",
        }

class operacaoForm(forms.ModelForm):
    class Meta:
        model = Operacao
        fields = ["conta", "descricao", "tipo", "valor", "data", "observacao"]
        widgets = {
            "conta": forms.Select(attrs={"class": "form-control"}),
            "descricao": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Descrição da Operação"}
            ),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "valor": forms.NumberInput(
                attrs={
                    "class": "form-control", 
                    "placeholder": "0,00", 
                    "step": "0.01", 
                    "min": "0",
                }
            ),
            "data": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, 
                format="%d-%m-%Y",
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control", 
                    "placeholder": "Observação", 
                    "rows": 3,
                }
            )
        }
        labels = {
            "conta": "Conta", 
            "descricao": "Descrição", 
            "tipo": "Tipo", 
            "valor": "Valor (R$)",
            "data": "Data", 
            "observacao": "Observação",
        }

def __init__(self, *args, conta=None, **kwargs):
    super().__init__(*args, **kwargs)

    if conta:
        self.fields["conta"].initial = conta
        self.fields["conta"].widget = forms.HiddenInput()
        