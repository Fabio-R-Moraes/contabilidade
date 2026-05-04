from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from .models import User, Contas, Operacao
from .forms import contasForm, operacaoForm


#-----------------------------------
# Views da conta
#-----------------------------------
class ContaListView(ListView):
    #Lista todas as contas com seus saldos
    model = Contas
    template_name = "finance/conta_list.html"
    context_object_name = "contas"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()

        if q:
            qs = qs.filter(nome__icontains=q)

        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_geral"] = sum(c.saldo() for c in ctx["contas"])
        ctx["q"] = self.request.GET.get("q", "")

        return ctx

class contaDetailView(DetailView):
    #Detalhe de uma conta com suas operações
    model = Contas
    template_name = "finance/conta_detail.html"
    context_object_name = "conta"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        operacoes = self.object.operacoes.all()

        #filtros opcionais
        #tipo = self.request.GET.get("tipo","")
        #data_inicio = self.request.GET.get("data_inicio", "")
        data_fim = self.request.GET.get("data_fim", "")

        #if tipo:
        #    operacoes = operacoes.filter(tipo=tipo)

        #if data_inicio:
        #    operacoes = operacoes.filter(data__gte=data_inicio)

        if data_fim:
            operacoes = operacoes.filter(data__lte=data_fim)

        ctx["operacoes"] = operacoes
        ctx["total_receitas"] = operacoes.filter(tipo="receita").aggregate(t=Sum("valor"))["t"] or 0
        ctx["total_despesas"] = operacoes.filter(tipo="despesa").aggregate(t=Sum("valor"))["t"] or 0
        #ctx["filtro_tipo"] = tipo
        #ctx["filtro_data_inicio"] = data_inicio
        ctx["filtro_data_fim"] = data_fim

        return ctx
    
class contaCreateView(CreateView):
    model = Contas
    form_class = contasForm
    template_name = "finance/conta_form.html"
    success_url = reverse_lazy("conta_list")

    def form_valid(self, form):
        messages.success(self.request, "Conta criada com sucesso!!!")
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Conta"
        ctx["botao"] = "Criar Conta"

        return ctx
        
class contaUpdateView(UpdateView):
    model = Contas
    form_class = contasForm
    template_name = "finance/conta_form.html"
    success_url = reverse_lazy("conta_list")

    def form_valid(self, form):
        messages.success(self.request, "Conta atualizada com sucesso!!!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Edirtar conta: {self.object.nome}"
        ctx["botao"] = "Salvar Alterações"

        return ctx
    
class contaDeleteView(DeleteView):
    model = Contas
    template_name = "finance/conta_confirme_delete.html"
    success_url = reverse_lazy("conta_list")

    def form_valid(self, form):
        messages.success(self.request, "Conta excluída com sucesso!!!")
        return super().form_valid(form)
    
#-----------------------------------
# Views das operações
#----------------------------------- 
class operacaoListView(ListView):
    #Lista todas as operações com filtros
    model = Operacao
    template_name = "finance/operacao_list.html"
    context_object_name = "operacoes"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("contas")
        conta_id = self.request.GET.get("contas", "")
        tipo = self.request.GEt.get("tipo", "")
        q = self.request.GET.get("q", "").strip()
        data_inicio = self.request.GET.get("data_inicio", "")
        data_fim = self.request.GET.get("data_fim", "")

        if conta_id:
            qs = qs.filter(conta_id=conta_id)

        if tipo:
            qs = qs.filter(tipo=tipo)

        if q:
            qs = qs.filter(
                Q(descricao__icontens=q) | Q(observacao__icontains=q)
            )
        
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)

        if data_fim:
            qs = qs.filter(data__lte=data_fim)

        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contas"] = Contas.objects.all()
        ctx["filtro_conta"] = self.request.GET.get("conta", "")
        ctx["filtro_tipo"] = self.request.GET.get("tipo", "")
        ctx["q"] = self.request.GET.get("q", "")
        ctx["data_inicio"] = self.request.GET.get("data_inicio", "")
        ctx["data_fim"] = self.request.GET.get("data_fim", "")
        qs = self.get_queryset()
        ctx["total_receitas"] = qs.filter(tipo="receita").aggregate(t=Sum("valor"))["t"] or 0
        ctx["total_despesas"] = qs.filter(tipo="despesa").aggregate(t=Sum("valor"))["t"] or 0

        return ctx
    
class operacaoCreateView(CreateView):
    model = Operacao
    form_class = operacaoForm
    template_name = "finance/operacao_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        conta_id = self.request.GET.get("conta") or self.kwargs.get("conta_pk")

        if conta_id:
            try:
                kwargs["conta"] = Contas.objects.get(pk=conta_id)
            except Contas.DoesNotExist:
                pass

        return kwargs
    
    def get_success_url(self):
        conta_pk = self.request.GET.get("conta") or self.kwargs.get("conta_pk")

        if conta_pk:
            return reverse_lazy("conta-detail", kwargs={"pk": conta_pk})
        
        return reverse_lazy("operacao-list")
    
    def form_valid(self, form):
        messages.success(self.request, "Operação registrada com sucesso!!!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nova Operação"
        ctx["botao"] = "Registrar"

        return ctx
    
class operacaoUpdateView(UpdateView):
    model = Operacao
    form_class = operacaoForm
    template_name = "finance/operacao_form.html"
    success_url = reverse_lazy("operacao-list")

    def form_valid(self, form):
        messages.success(self.request, "Operação atualizada com sucesso!!!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.descricao}"
        ctx["botao"] = "Salvar Alterações"

        return ctx
    
class operacaoDeleteView(DeleteView):
    model = Operacao
    template_name = "finance/operacao_confirm_delete.html"
    success_url = reverse_lazy("operacao-list")

    def form_valid(self, form):
        messages.success(self.request, "Operação excluída com sucesso...")
        return super().form_valid(form)
             
