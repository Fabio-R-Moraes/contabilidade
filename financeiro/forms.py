from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Lancamento, Partida, ContaCredora, ContaDevedora

class ContaCredoraForm(forms.ModelForm):
    class Meta:
        model = ContaCredora
        fields = ['nome', 'descricao', 'saldo', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: NuBank, Caixa, Carteira...'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', "rows": 2}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome da Conta',
            'descricao': 'Descrição',
            'saldo': 'Saldo Inicial (R$)',
            'ativa': 'Conta Ativa',
        }

class ContaDevedoraForm(forms.ModelForm):
    class Meta:
        model = ContaDevedora
        fields = ['nome', 'descricao', 'saldo', 'limite', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Cartão Visa, Financiamento...'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', "rows": 2}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'limite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome': 'Nome da Conta',
            'descricao': 'Descrição',
            'saldo': 'Saldo Inicial (R$)',
            'limite': 'Limite (R$)',
            'ativa': 'Conta Ativa',
        }

class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = ['descricao', 'data', 'tipo_despesa', 'observacoes']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do lançamento'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tipo_despesa': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }
        labels = {
            'descricao': 'Descrição',
            'data': 'Data',
            'tipo_despesa': 'Tipo de Despesa',
            'observacoes': 'Observaçõoes',
        }

class PartidaForm(forms.ModelForm):
    TIPO_CONTA_CHOICES = [
        ('credora', 'Conta Credora'),
        ('devedora', 'Conta Devedora'),
    ]
    tipo_conta = forms.ChoiceField(
        choices=TIPO_CONTA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select tipo-conta-select'}),
        label = 'Tipo de Conta'
    )

    class Meta:
        model = Partida
        fields = ['tipo', 'tipo_conta', 'conta_credora', 'conta_devedora', 'valor', 'historico']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'conta_credora': forms.Select(attrs={'class': 'form-select conta-credora-field'}),
            'conta_devedora': forms.Select(attrs={'class': 'form-select conta-devedora-field'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control valor-partida',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0,00'
            }),
            'historico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Histórico da partida(opcional)'
            }),
        }
        labels = {
            'tipo': 'D/C',
            'conta_credora': 'Conta Credora',
            'conta_devedora': 'Conta Devedora',
            'valor': 'Valor (R$)',
            'histórico': 'Histórico',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['conta_credora'].queryset = ContaCredora.objects.filter(usuario=user, ativa=True)
            self.fields['conta_devedora'].queryset = ContaDevedora.objects.filter(usuario=user, ativa=True)

        self.fields['conta_credora'].required = False
        self.fields['conta_devedora'].required = False

        #Preenchimento do campo tipo_conta baseado em uma instancia existente
        if self.instance and self.instance.pk:
            if self.instance.conta_devedora:
                self.fields['tipo_conta'].initial = 'devedora'
            else:
                self.fields['tipo_conta'].initial = 'credora'

    def clean(self):
        cleaned_data = super().clean()
        tipo_conta = cleaned_data.get('tipo_conta')
        conta_credora = cleaned_data.get('conta_credora')
        conta_devedora = cleaned_data.get('conta_devedora')
        valor = cleaned_data.get('valor')

        if tipo_conta == 'credora':
            if not conta_credora:
                self.add_error('conta_credora', 'Selecione uma conta credora')
            cleaned_data['conta_devedora'] = None
        elif tipo_conta == 'devedora':
            if not conta_devedora:
                self.add_error('congta_devedora', 'Selecione uma conta devedora')
            cleaned_data['conta_credora'] = None

        if valor is not None and valor <= 0:
            self.add_error('valor', 'O valor decve ser maior que ZERO!!!')

        return cleaned_data
    
class BasePartidaFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user'] = self.user
        return super()._construct_form(i, **kwargs)
    
    def clean(self):
        if any(self.errors):
            return
        
        partidas_validas = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                partidas_validas.append(form.cleaned_data)

            if len(partidas_validas) < 2:
                raise ValidationError('Um lançamento deve ter ao menos 2 partidas!!!')
            
            total_debitos = sum(
                p.get('valor', Decimal('0')) for p in partidas_validas
                    if p.get('tipo') == 'DEBITO'
            )
            total_creditos = sum(
                p.get('valor', Decimal('0')) for p in partidas_validas
                    if p.get('tipo') == 'CREDITO'
            )

            if total_debitos != total_creditos:
                raise ValidationError(
                    f'O lançamento NÃO está balanceado!!! '
                    f'Débitos: R$ {total_debitos:,.2f} | '
                    f'Créditos: R$ {total_creditos:,.2f}. '
                    f'Diferença: R$ {abs(total_debitos - total_creditos):,.2f}...'
                )

#Fabrica com no minimo 4 partidas extras
PartidaFormSet = inlineformset_factory(
    Lancamento,
    Partida,
    form=PartidaForm,
    formset=BasePartidaFormSet,
    extra = 4,
    min_num=2,
    validate_min=True,
    can_delete=True,
    fields=['tipo', 'tipo_conta', 'conta_credora', 'conta_devedora', 'valor', 'historico']
)
