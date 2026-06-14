from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Case, When, Value, DecimalField
from decimal import Decimal
import datetime
from .models import ContaCredora, ContaDevedora, Lancamento, Partida
from .forms import (
    ContaCredoraForm, ContaDevedoraForm,
    LancamentoForm, PartidaFormSet
)

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
    
#Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = reverse_lazy('financeiro:login')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        contas_credoras = ContaCredora.objects.filter(usuario=user, ativa=True)
        contas_devedoras = ContaDevedora.objects.filter(usuario=user, ativa=True)

        total_credoras = contas_credoras.aggregate(t=Sum('saldo'))['t'] or Decimal('0')
        total_devedoras = contas_devedoras.aggregate(t=Sum('saldo'))['t'] or Decimal('0')

        hoje = datetime.date.today()
        lancamentos_mes = Lancamento.objects.filter(
            usuario=user,
            data__year=hoje.year,
            data__month=hoje.month
        )
        por_tipo = {}

        for tipo, label in Lancamento.TIPO_DESPESA_CHOICES:
            total = lancamentos_mes.filter(tipo_despesa=tipo).count()
            por_tipo[label] = total

        ctx.update({
            'contas_credoras': contas_credoras,
            'contas_devedoras': contas_devedoras,
            'total_credoras': total_credoras,
            'total_devedoras': total_devedoras,
            'saldo_liquido': total_credoras - total_devedoras,
            'ultimos_lancamentos': Lancamento.objects.filter(usuario=user)[:5],
            'lancamentos_por_tipo': por_tipo,
            'total_lancamentos_mes': lancamentos_mes.count(),
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
    login_url = reverse_lazy(':financeiro:login')

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
                    Case(When(partidas__tipo='DEBITO', then='partidas'), # type: ignore
                         default=zero, output_field=DecimalField()) # type: ignore
                ),
                _total_creditos = Sum(
                    Case(When(partidas__tipo='CREDITO', then='partidas'), # type: ignore
                         default=zero, output_field=DecimalField()) # type: ignore
                ),
            )
        )
        
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
    
        
