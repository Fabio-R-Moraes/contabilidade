from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Contas(models.Model):
    """Tabela de contas financeiras"""
    nome = models.CharField(max_length=100, verbose_name="Nome da Conta")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    criado_em = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)
    dono = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
    
    def saldo(self):
        """Calcula o saldo da conta somando todas as operações"""
        total = self.operacoes.aggregate(
            total = models.Sum("valor")
        )["total"]

        return total or 0
    
class Operacao(models.Model):
    """Tabela de operações financeiras vinculadas a uma conta"""
    TIPO_CHOICES = [
        ("receita", "Receita"),
        ("despesa", "Despesa"),
    ]

    conta = models.ForeignKey(
        Contas,
        on_delete=models.CASCADE,
        related_name="operacoes",
        verbose_name="Conta",
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default="despesa",
        verbose_name="Tipo"
    )
    valor = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name="Valor"
    )
    data = models.DateField(default=timezone.now, verbose_name="Data")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(verbose_name="Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField(verbose_name="Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Operação"
        verbose_name_plural = "Operações"
        ordering = ["-data", "-criado_em"]

    def __str__(self):
        return f"{self.descricao} - {self.conta.nome}"
    
    def save(self, *args, **kwargs):
        """Garante que despesas sejam salvas com valor negativo"""
        if self.tipo == "despesa" and self.valor > 0:
            self.valor = -self.valor
        elif self.tipo == "receita" and self.valor < 0:
            self.valor = abs(self.valor)

        super().save(*args, **kwargs)
