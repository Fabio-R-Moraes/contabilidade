from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal

class ContaCredora(models.Model):
    """Contas que recebem recursos(banco, carteira, poupanca, etc...)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contas_credoras')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    saldo_inicial = models.DecimalField(
        max_digits=9, decimal_places=2, default=Decimal('0.00'), 
        help_text='Saldo no momento do cadastro da conta. Não altere manualmente.'
        )
    saldo = models.DecimalField(
        max_digits=9, decimal_places=2, default=Decimal('0.00'), 
        help_text='Calculado automaticamente a partir das partidas.'
        )
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conta Credora'
        verbose_name_plural = 'Contas Credoras'
        ordering = ['nome']
        unique_together = ['usuario', 'nome']

    def __str__(self):
        return f'{self.nome} (R$ {self.saldo:,.2f})'

class ContaDevedora(models.Model):
    """Contas que representam obrigacoes(cartao de credito, emprestimo, etc...)"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contas_devedoras')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    saldo_inicial = models.DecimalField(
        max_digits=9, decimal_places=2, default=Decimal('0.00'), 
        help_text='Saldo no momento do cadastro da conta. Não altere manualmente.'
        )
    saldo = models.DecimalField(
        max_digits=9, decimal_places=2, default=Decimal('0.00'), 
        help_text='Calculado automaticamente a partir das partidas.'
        )
    limite = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conta Devedora'
        verbose_name_plural = 'Contas Devedoras'
        ordering = ['nome']
        unique_together = ['usuario', 'nome']

    def __str__(self):
        return f'{self.nome} (R$ {self.saldo:,.2f})'

class Lancamento(models.Model):
    """
    Lancamento caontabil de dupla entrada.
    Cada lancamento possui multiplas partidas(debitos e creditos)
    que devem sempre serem iguais(metodo da partida dobrada).
    """
    TIPO_DESPESA_CHOICES = [
        ('NORMAL', 'Normal'),
        ('FIXA', 'Fixa'),
        ('VARIAVEL', 'Variável'),
        ('SUPERFLUA', 'Supérflua'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lancamentos')
    descricao = models.CharField(max_length=255)
    data = models.DateField()
    tipo_despesa = models.CharField(max_length=10, choices=TIPO_DESPESA_CHOICES, default='NORMAL')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lançamento'
        verbose_name_plural = 'Lançamentos'
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f'{self.data} - {self.descricao}'
    
    def total_debitos(self):
        return self.partidas.filter(tipo='DEBITO').aggregate( # type: ignore
            total = models.Sum('valor')
        )['total'] or Decimal('0.00')

    def total_creditos(self):
        return self.partidas.filter(tipo='CREDITO').aggregate( # type: ignore
            total = models.Sum('valor')
        )['total'] or Decimal('0.00')

    def esta_balanceado(self):
        return self.total_debitos() == self.total_creditos()
    
class Partida(models.Model):
    """
    Partida de um lancamento(linha do lancamento contabil).
    DEBITO = Saida de conta credora ou entrada em conta devedora.
    CREDITO = entrada em conta credora ou saida em conta devedora.
    """
    TIPO_CHOICES = [
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]
    lancamento = models.ForeignKey(Lancamento, on_delete=models.CASCADE, related_name='partidas')
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    conta_credora = models.ForeignKey(
        ContaCredora, on_delete=models.PROTECT,
        null=True, blank=True, related_name='partidas'
    )
    conta_devedora = models.ForeignKey(
        ContaDevedora, on_delete=models.PROTECT,
        null=True, blank=True, related_name='partidas'
    )
    historico = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'

    def __str__(self):
        conta = self.conta_credora or self.conta_devedora
        return f'{self.tipo} - {conta} - R$ {self.valor:,.2f}'
    
    def clean(self):
        if self.conta_credora and self.conta_devedora:
            raise ValidationError('Informa apenas uma conta: CREDORA ou DEVEDORA...')
        if not self.conta_credora and not self.conta_devedora:
            raise ValidationError('Informe pelo mernos uma conta: CREDORA ou DEVEDORA')
        if self.valor is not None and self.valor <= 0:
            raise ValidationError('O valor da partida deve ser positivo!!!')
        
    @property
    def conta(self):
        return self.conta_credora or self.conta_devedora

    @property
    def tipo_conta(self):
        if self.conta_credora:
            return 'credora'
        return 'devedora' 

