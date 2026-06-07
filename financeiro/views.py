from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
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
        return redirect(self.success_url)
    
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
    
    
