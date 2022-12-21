from django.contrib import admin
from .models import Cargo, Equipe, Conta, Nota, Razao

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'criado', 'modificado', 'ativo')

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sobrenome', 'dataNascimento', 'email', 'cargo', 'criado', 'modificado', 'ativo')

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'nomConta', 'slug', 'criado', 'modificado', 'ativo')

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('dataNota', 'contaCredito', 'contaDebito', 'valor', 'imprimir', 'criado', 'modificado', 'ativo')

@admin.register(Razao)
class RazaoAdmin(admin.ModelAdmin):
    list_display = ('nomeConta', 'periodoInicial', 'periodoFinal', 'saldoAnterior', 'entradas', 'saidas', 'situacao', \
        'criado', 'modificado', 'ativo')
        