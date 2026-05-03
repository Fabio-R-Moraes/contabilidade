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
