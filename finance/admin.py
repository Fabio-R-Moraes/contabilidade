from django.contrib import admin
from .models import Contas, Operacao

@admin.register(Contas)
class ContasAdmin(admin.ModelAdmin):
    list_display = ["nome", "saldo", "criado_em"]
    search_fields = ["nome"]

@admin.register(Operacao)
class OperacaoAdmin(admin.ModelAdmin):
    list_display = ["descricao", "conta", "tipo", "valor", "data"]
    list_filter = ["tipo", "conta"]
    search_fields = ["descricao", "conta__nome"]
    date_hierarchy = "data"
