from django.contrib import admin
from .models import ContaCredora, ContaDevedora, Lancamento, Partida

class PartidaInline(admin.TabularInline):
    model = Partida
    extra = 2
    fields = ['tipo', 'conta_credora', 'cnta_devedora', 'valor', 'historico']

@admin.register(ContaCredora)
class ContaCredoraAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'saldo', 'ativa']
    list_filter = ['ativa', 'usuario']
    search_fields = ['nome', 'usuario__username']

@admin.register(ContaDevedora)
class ContaDevedoraAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario', 'saldo', 'ativa']
    list_filter = ['ativa', 'usuario']
    search_fields = ['nome', 'usuario__username']

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'tipo_despesa', 'usuario', 'esta_balanceado']
    list_filter = ['tipo_despesa', 'data', 'usuario']
    search_fields = ['descricao', 'usuario__username']
    date_hierarchy = 'data'

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ['lancamento', 'tipo', 'conta_credora', 'conta_devedora', 'valor']
    list_filter = ['tipo']
