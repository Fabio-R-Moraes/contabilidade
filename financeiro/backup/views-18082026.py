from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Case, When, Value, DecimalField
from decimal import Decimal
import datetime
from .models import ContaCredora, ContaDevedora, Lancamento
from .forms import (
    ContaCredoraForm, ContaDevedoraForm,
    LancamentoForm, PartidaFormSet
)
from itertools import groupby
from django.views import View
from django.http import HttpResponse, JsonResponse
import calendar
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io

#Autenticacao
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('financeiro:dashboard')

class RegistroView(CreateView):
    form_class = UserCreationForm
    template_name = 'auth/registro.html'
    success_url = reverse_lazy('financeiro:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Bem-vindo, { user.username }! Sua conta foi criada...')
        return redirect(self.success_url) # type: ignore
    
class AutoLogoutView(View):
    """
    Endpoint chamado pelo sendBeacon do browser ao fechar aba/janela.
    Recebe POST com CSRF token embutido no corpo e encerra a sessão.
    """
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)

        return HttpResponse(status=204) #Sem conteúdo

def home(request):
    return render(request, 'index.html')

#Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = reverse_lazy('financeiro:login')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        hoje = datetime.date.today()
        ano, mes = hoje.year, hoje.month

        contas_credoras = ContaCredora.objects.filter(usuario=user, ativa=True).order_by('nome').annotate(
            saldo_mes = Sum(
                Case(
                    When(
                        partidas__lancamento__data__year = ano,
                        partidas__lancamento__data__month = mes,
                        partidas__tipo = 'CREDITO',
                        then='partidas__valor',
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=9, decimal_places=2),
                )
            ) - Sum(
                Case(
                    When(
                        partidas__lancamento__data__year = ano,
                        partidas__lancamento__data__month = mes,
                        partidas__tipo = 'DEBITO',
                        then='partidas__valor',
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=9, decimal_places=2),
                )
            )
        )
        contas_devedoras = ContaDevedora.objects.filter(usuario=user, ativa=True).order_by('nome').annotate(
            saldo_mes = Sum(
                Case(
                    When(
                        partidas__lancamento__data__year = ano,
                        partidas__lancamento__data__month = mes,
                        partidas__tipo = 'CREDITO',
                        then='partidas__valor',
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=9, decimal_places=2),
                )
            ) - Sum(
                Case(
                    When(
                        partidas__lancamento__data__year = ano,
                        partidas__lancamento__data__month = mes,
                        partidas__tipo = 'DEBITO',
                        then='partidas__valor',
                    ),
                    default=Value(0),
                    output_field=DecimalField(max_digits=9, decimal_places=2),
                )
            )
        )

        total_credoras = contas_credoras.aggregate(t=Sum('saldo'))['t'] or Decimal('0')
        total_devedoras = contas_devedoras.aggregate(t=Sum('saldo'))['t'] or Decimal('0')

        lancamentos_mes = Lancamento.objects.filter(
            usuario=user,
            data__year=hoje.year,
            data__month=hoje.month
        )
        por_tipo = {}

        for tipo, label in Lancamento.TIPO_DESPESA_CHOICES:
            total = lancamentos_mes.filter(tipo_despesa=tipo).count()
            por_tipo[label] = total

        # Lançamento das duas semanas credoras
        # Semana = Segunda a domingo
        dia_semana = hoje.weekday()   # 0 = segunda, 6 = domingo
        inicio_semana_atual = hoje - datetime.timedelta(days=dia_semana)
        fim_semana_atual = inicio_semana_atual + datetime.timedelta(days=6)
        inicio_semana_prox = fim_semana_atual + datetime.timedelta(days=1)
        fim_semana_prox = inicio_semana_prox + datetime.timedelta(days=6)
        zero_dc = Value(0, output_field=DecimalField(max_digits=9, decimal_places=2))

        def _lanc_semana(inicio, fim):
            return (
                Lancamento.objects.filter(
                    usuario=user,
                    data__range=(inicio, fim),
                    partidas__conta_credora__isnull=False,
                ).distinct().annotate(
                    valor_resultado = Sum(
                        Case(
                            When(partidas__tipo='DEBITO', then='partidas__valor'),
                            When(partidas__tipo='CREDITO', then='partidas__valor'),
                            default=zero_dc, output_field=DecimalField(max_digits=9, decimal_places=2),
                        )
                    ),
                    _total_debitos = Sum(
                        Case(
                            When(partidas__tipo='DEBITO', then='partidas__valor'),
                            default=zero_dc, output_field=DecimalField(max_digits=9, decimal_places=2),
                        )
                    ),
                    _total_creditos = Sum(
                        Case(
                            When(partidas__tipo='CREDITO', then='partidas__valor'),
                            default=zero_dc, output_field=DecimalField(max_digits=9, decimal_places=2),
                        )
                    ),
                ).order_by('-data', '-criado_em')
            )

        ctx.update({
            'contas_credoras': contas_credoras,
            'contas_devedoras': contas_devedoras,
            'total_credoras': total_credoras,
            'total_devedoras': total_devedoras,
            'saldo_liquido': total_credoras - total_devedoras,
            'lancamentos_por_tipo': por_tipo,
            'total_lancamentos_mes': lancamentos_mes.count(),
            #Semanas
            'semana_atual': {
                'inicio': inicio_semana_atual,
                'fim': fim_semana_atual,
                'lancamentos': list(_lanc_semana(inicio_semana_atual, fim_semana_atual).exclude(
                    tipo_despesa='NORMAL'
                ).order_by(
                    '-data', '-criado_em'
                )[:10]),
            },
            'semana_proxima': {
                'inicio': inicio_semana_prox,
                'fim': fim_semana_prox,
                'lancamentos': _lanc_semana(inicio_semana_prox, fim_semana_prox).exclude(
                    tipo_despesa='NORMAL')[:10],
            },
            'hoje': hoje,
        })

        return ctx
    
#Contas Credoras
class ContaCredoraListView(LoginRequiredMixin, ListView):
    model = ContaCredora
    template_name = 'conta_credora/list.html'
    context_object_name = 'contas'
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaCredora.objects.filter(usuario=self.request.user)
    
class ContaCredoraCreateView(LoginRequiredMixin, CreateView):
    model = ContaCredora
    form_class = ContaCredoraForm
    template_name = 'conta_credora/form.html'
    success_url = reverse_lazy('financeiro:conta_credora_list')
    login_url = reverse_lazy(':financeiro:login')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Conta credora criada com sucesso!!!')
        return super().form_valid(form)
    
class ContaCredoraUpdateView(LoginRequiredMixin, UpdateView):
    model = ContaCredora
    form_class = ContaCredoraForm
    template_name = 'conta_credora/form.html'
    success_url = reverse_lazy('financeiro:conta_credora_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaCredora.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta credora atualizada com sucesso!!!')
        return super().form_valid(form)
    
class ContaCredoraDeleteView(LoginRequiredMixin, DeleteView):
    model = ContaCredora
    template_name = 'conta_credora/confirm_delete.html'
    success_url = reverse_lazy('financeiro:conta_credora_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaCredora.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta credora removida!!!')
        return super().form_valid(form) # type: ignore
    
#Contas Devedoras
class ContaDevedoraListView(LoginRequiredMixin, ListView):
    model = ContaDevedora
    template_name = 'conta_devedora/list.html'
    context_object_name = 'contas'
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaDevedora.objects.filter(usuario=self.request.user)
    
class ContaDevedoraCreateView(LoginRequiredMixin, CreateView):
    model = ContaDevedora
    form_class = ContaDevedoraForm
    template_name = 'conta_devedora/form.html'
    success_url = reverse_lazy('financeiro:conta_devedora_list')
    login_url = reverse_lazy('financeiro:login')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Conta devedora criada com sucesso!!!')
        return super().form_valid(form)
    
class ContaDevedoraUpdateView(LoginRequiredMixin, UpdateView):
    model = ContaDevedora
    form_class = ContaDevedoraForm
    template_name = 'conta_devedora/form.html'
    success_url = reverse_lazy('financeiro:conta_devedora_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaDevedora.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta devedora atualizada com sucesso!!!')
        return super().form_valid(form)
    
class ContaDevedoraDeleteView(LoginRequiredMixin, DeleteView):
    model = ContaDevedora
    template_name = 'conta_devedora/confirm_delete.html'
    success_url = reverse_lazy('financeiro:conta_devedora_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return ContaDevedora.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Conta devedora removida!!!')
        return super().form_valid(form)   # type: ignore

#Lancamentos
class LancamentoListView(LoginRequiredMixin, ListView):
    model = Lancamento
    template_name = 'lancamento/list.html'
    context_object_name = 'lancamentos'
    paginate_by = 20
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        zero = Value(0, output_field=DecimalField()) # type: ignore
        qs = (
            Lancamento.objects.filter(usuario=self.request.user).annotate(
                _total_debitos = Sum(
                    Case(When(partidas__tipo='DEBITO', then='partidas__valor'), # type: ignore
                         default=zero, output_field=DecimalField()) # type: ignore
                ),
                _total_creditos = Sum(
                    Case(When(partidas__tipo='CREDITO', then='partidas__valor'), # type: ignore
                         default=zero, output_field=DecimalField()) # type: ignore
                ),
            )
        ).order_by('-data')
        
        tipo = self.request.GET.get('tipo')

        if tipo:
            qs = qs.filter(tipo_despesa=tipo)

        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tipo_choices'] = Lancamento.TIPO_DESPESA_CHOICES
        ctx['tipo_atual'] = self.request.GET.get('tipo', '')

        return ctx
    
class LancamentoDetailView(LoginRequiredMixin, DetailView):
    model = Lancamento
    template_name = 'lancamento/detail.html'
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return Lancamento.objects.filter(usuario=self.request.user)
    
class LancamentoCreateView(LoginRequiredMixin, CreateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = 'lancamento/form.html'
    success_url = reverse_lazy('financeiro:lancamento_list')
    login_url = reverse_lazy('financeiro:login')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.POST:
            ctx['formset'] = PartidaFormSet(
                self.request.POST, 
                user=self.request.user
            )
        else:
            ctx['formset'] = PartidaFormSet(
                user=self.request.user
            )

        return ctx
    
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']

        if formset.is_valid():
            with transaction.atomic():
                form.instance.usuario = self.request.user
                self.object = form.save()
                formset.instance = self.object
                formset.save()

            messages.success(self.request, 'Lançamento registrado com sucesso!!!')
            return redirect(self.success_url) # type: ignore
        else:
            return super().form_invalid(form)
    
class LancamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = 'lancamento/form.html'
    success_url = reverse_lazy('financeiro:lancamento_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return Lancamento.objects.filter(usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        if self.request.POST:
            ctx['formset'] = PartidaFormSet(
                self.request.POST,
                instance=self.object,
                user=self.request.user
            )
        else:
            ctx['formset'] = PartidaFormSet(
                instance=self.object,
                user=self.request.user
            )

        return ctx
    
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']

        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()

            messages.success(self.request, 'Lançamento atualizado com sucesso!!!')
            return redirect(self.success_url) # type: ignore
        else:
            return self.form_invalid(form)
    
class LancamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Lancamento
    template_name = 'lancamento/confirm_delete.html'
    success_url = reverse_lazy('financeiro:lancamento_list')
    login_url = reverse_lazy('financeiro:login')

    def get_queryset(self):
        return Lancamento.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Lançamento removido!!!')
        return super().form_valid(form) # type: ignore
    
#Extrato por conta
def _qs_lancamentos_anotados(lancamentos_qs, filtro_conta):
    """
    Anota totais globais e dados da partida desta conta específica.
    filtro_conta: dict com o filtro da partida, ex: {'partidas__conta-credora':conta}
    """
    zero = Value(0, output_field=DecimalField(max_digits=9, decimal_places=2))

    #Filtro para as partidas desta conta específica
    when_debito_conta = {**filtro_conta, 'partidas__tipo': 'DEBITO'}
    when_credito_conta = {**filtro_conta, 'partidas__tipo': 'CREDITO'}

    return lancamentos_qs.annotate(
        #Valor e tipo da partida desta conta no lançamento
        total_debitos = Sum(
            Case(
                When(partidas__tipo='DEBITO', then='partidas__valor'),
                output_field=DecimalField()
            )
        ),
        total_creditos = Sum(
            Case(
                When(partidas__tipo='CREDITO', then='partidas__valor'),
                output_field=DecimalField()
            )
        ),
        valor_partida_lancamento = Sum(
            Case(
                When(**when_debito_conta, then='partidas__valor'),
                When(**when_credito_conta, then='partidas__valor'),
                default=zero, output_field=DecimalField()
            )
        ),
        debito_conta_lancamentos = Sum(
            Case(
                When(**when_debito_conta, then='partidas__valor'),
                output_field=DecimalField()
            )
        ),
        credito_conta_lancamentos = Sum(
            Case(
                When(**when_credito_conta, then='partidas__valor'),
                output_field=DecimalField()
            )
        ),
    ).order_by('data', 'valor_partida_lancamento', 'criado_em')

def _agrupar_por_data(lancamentos, saldo_inicial):
    """
    Agrupa lançamentos por data(ordem cronológica) calculando subtotal diário
    e saldo acumulado. Retorna lista sde dicts pronto para o template.
    """
    grupos = []
    saldo_acumulado = saldo_inicial
    for data, items in groupby(lancamentos, key=lambda l: l.data):
        items = list(items)
        debitos_dia = sum(l.debito_conta_lancamentos or Decimal('0') for l in items)
        creditos_dia = sum(l.credito_conta_lancamentos or Decimal('0') for l in items)
        saldo_acumulado = saldo_acumulado + creditos_dia - debitos_dia
        grupos.append({
            'data': data,
            'lancamentos': items,
            'debitos_dia': debitos_dia,
            'creditos_dia': creditos_dia,
            'saldo_acumulado': saldo_acumulado,
        })

    return grupos

def _dados_grafico_mes(lancamentos_qs, filtro_conta, ano, mes):
    """
    Retorna dados diarios para o grafico: labels, creditos, debitos e saldo acumulado.
    """
    zero = Value(0, output_field=DecimalField(max_digits=9, decimal_places=2))
    when_deb = {**filtro_conta, 'partidas__tipo': 'DEBITO'}
    when_cred = {**filtro_conta, 'partidas__tipo': 'CREDITO'}

    registros = (
        lancamentos_qs.filter(data__year=ano, data__month=mes).values('data').annotate(
            debitos = Sum(Case(When(**when_deb, then='partidas__valor'), default=zero, output_field=DecimalField())),
            creditos = Sum(Case(When(**when_cred, then='partidas__valor'), default=zero, output_field=DecimalField())),
        ).order_by('data')
    )

    #Montar o dicionario data --> valores
    por_dia = {r['data']: r for r in registros}

    #Preencher todos os dias do mes
    _, num_dias = calendar.monthrange(ano, mes)
    labels, debitos, creditos, saldos = [], [], [], []
    saldo = Decimal('0')
    for d in range(1, num_dias + 1):
        data = datetime.date(ano, mes, d)
        reg = por_dia.get(data)
        deb = float(reg['debitos'] or 0) if reg else 0
        cred = float(reg['creditos'] or 0) if reg else 0
        labels.append(f'{d:02d}')
        debitos.append(deb)
        creditos.append(cred)

    return {'labels': labels, 'debitos': debitos, 'creditos': creditos}

def _fmt_brlv(v):
    """Formatar valor float como R$ no padrão pt-BR"""
    return f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def _gerar_grafico_png(dados, titulo, ano, mes):
    """Gera o gráfico como PNG em memória usando Matplotlib e retorna HHttpResponse"""
    matplotlib.use('Agg') #Backend sem tela - obrigatório no servidor

    MESES_PT = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    labels = dados['labels']
    debitos = dados['debitos']
    creditos = dados['creditos']
    xs = list(range(1, len(labels) + 1))

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor('#f0f4f8')
    ax.set_facecolor('#f8fafc')

    #Linhas
    ax.plot(xs, creditos, color='#27ae60', linewidth=1.5, label='Créditos', marker='o', markersize=2, zorder=2)
    ax.plot(xs, debitos, color='#e74c3c', linewidth=1.5, label='Débitos', marker='o', markersize=2, zorder=2)

    #Linha de zero
    ax.axhline(0, color='#aaa', linewidth=0.8, linestyle='--')

    #Anotações de valor nos pontos com movimentos
    def anotar(serie, cor, offset_y):
        for x, v in zip(xs, serie):
            if v != 0:
                ax.annotate(
                    _fmt_brlv(v),
                    xy = (x,v),
                    xytext = (0, offset_y),
                    textcoords = 'offset points',
                    ha = 'center',
                    va = 'bottom' if offset_y > 0 else 'top',
                    fontsize = 6.5,
                    color = cor,
                    fontweight = 'bold',
                    bbox = dict(boxstyle='round, pad=0.15', fc='white', ec=cor, alpha=0.7, linewidth=0.5),
                )

    anotar(creditos, '#27ae60', offset_y=10)  #créditos: valor acima do ponto
    anotar(debitos, '#e74c3c', offset_y=10)   #débitos: valor acima do ponto

    #Formatação dos eixos
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=7)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _: f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    )
    ax.tick_params(axis='y', labelsize=8)

    ax.set_title(f'{titulo} - {MESES_PT[mes - 1]}/{ano}', fontsize=12, fontweight='bold', color='#1a3a5c', pad=12)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(axis='y', color='#ddd', linewidth=0.7)
    ax.spines[['top', 'right']].set_visible(False)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.read(), content_type='image/png')

class GraficoExtratoCredoraView(LoginRequiredMixin, View):
    """Endpoint JSON para o grafico do extrato de conta credora"""
    login_url = reverse_lazy('financeiro:login')

    def get(self, request, pk, *args, **kwargs):
        conta = get_object_or_404(ContaCredora, pk=pk, usuario=request.user)

        try:
            ano = int(request.GET.get('ano', datetime.date.today().year))
            mes = int(request.GET.get('mes', datetime.date.today().month))
        except ValueError:
            return JsonResponse({'error': 'Parâmetro Inválidos'}, status=400)

        qs = Lancamento.objects.filter(usuario=request.user, partidas__conta_credora=conta).distinct()
        dados = _dados_grafico_mes(qs, {'partidas__conta_credora': conta}, ano, mes)

        return _gerar_grafico_png(dados, conta.nome, ano, mes)

class GraficoExtratoDevedoraView(LoginRequiredMixin, View):
    """Endpoint JSON para o grafico do extrato de conta devedora"""
    login_url = reverse_lazy('financeiro:login')

    def get(self, request, pk, *args, **kwargs):
        conta = get_object_or_404(ContaDevedora, pk=pk, usuario=request.user)

        try:
            ano = int(request.GET.get('ano', datetime.date.today().year))
            mes = int(request.GET.get('mes', datetime.date.today().month))
        except ValueError:
            return JsonResponse({'error': 'Parâmetro Inválidos'}, status=400)

        qs = Lancamento.objects.filter(usuario=request.user, partidas__conta_devedora=conta).distinct()
        dados = _dados_grafico_mes(qs, {'partidas__conta_devedora': conta}, ano, mes)

        return _gerar_grafico_png(dados, conta.nome, ano, mes)

class ExtratoContaCredoraView(LoginRequiredMixin, TemplateView):
    template_name = 'extrato_conta.html'
    login_url = reverse_lazy('financeiro:login')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        conta = get_object_or_404(
            ContaCredora, pk=self.kwargs['pk'], usuario=self.request.user
        )
        qs = Lancamento.objects.filter(
            usuario=self.request.user,
            partidas__conta_credora=conta,
        ).distinct()
        lancamentos = list(_qs_lancamentos_anotados(qs, {'partidas__conta_credora': conta}))
        total_debitos = sum(l.debito_conta_lancamentos or Decimal('0') for l in lancamentos)
        total_creditos = sum(l.credito_conta_lancamentos or Decimal('0') for l in lancamentos)
        ctx['conta'] = conta
        ctx['tipo_conta'] = 'credora'
        ctx['grupos'] = _agrupar_por_data(lancamentos, conta.saldo_inicial)
        ctx['total_debitos'] = total_debitos
        ctx['total_creditos'] = total_creditos
        ctx['saldo_real'] = (conta.saldo_inicial + total_creditos) - total_debitos
        MESES_PT = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
        ]
        mes_grafico = int(self.request.GET.get('g_mes', datetime.date.today().month))
        ano_grafico = int(self.request.GET.get('g_ano', datetime.date.today().year))
        ctx['grafico_url'] = reverse('financeiro:grafico_credora', kwargs={'pk':conta.pk})
        ctx['mes_grafico'] = mes_grafico
        ctx['ano_grafico'] = ano_grafico
        ctx['meses_choices'] = MESES_PT
        
        return ctx
    
class ExtratoContaDevedoraView(LoginRequiredMixin, TemplateView):
    template_name = 'extrato_conta.html'
    login_url = reverse_lazy('financeiro:login')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        conta = get_object_or_404(
            ContaDevedora, pk=self.kwargs['pk'], usuario=self.request.user
        )
        qs = Lancamento.objects.filter(
            usuario=self.request.user,
            partidas__conta_devedora=conta,
        ).distinct()
        lancamentos = list(_qs_lancamentos_anotados(qs, {'partidas__conta_devedora': conta}))
        total_debitos = sum(l.debito_conta_lancamentos or Decimal('0') for l in lancamentos)
        total_creditos = sum(l.credito_conta_lancamentos or Decimal('0') for l in lancamentos)


        ctx['conta'] = conta
        ctx['tipo_conta'] = 'devedora'
        ctx['grupos'] = _agrupar_por_data(lancamentos, conta.saldo_inicial)
        ctx['total_debitos'] = total_debitos
        ctx['total_creditos'] = total_creditos
        ctx['saldo_real'] = (conta.saldo_inicial + total_creditos) - total_debitos
        MESES_PT = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
            (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
            (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
        ]
        mes_grafico = int(self.request.GET.get('g_mes', datetime.date.today().month))
        ano_grafico = int(self.request.GET.get('g_ano', datetime.date.today().year))
        ctx['grafico_url'] = reverse('financeiro:grafico_devedora', kwargs={'pk':conta.pk})
        ctx['mes_grafico'] = mes_grafico
        ctx['ano_grafico'] = ano_grafico
        ctx['meses_choices'] = MESES_PT
        
        return ctx
