from django.db.models.signals import post_save, post_delete,pre_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from .models import Partida, ContaCredora, ContaDevedora

#------------- Regras de Movimentação de Saldo ------------------
# CONTA CREDORA: Ex.: Banco, Caixa, etc...
# DÈBITO --> Saída --> Saldo Diminui
# CRÉDITO --> Entrada --> Saldo Aumenta
#
# CONTA DEVEDORA: Ex.: Cartão de Crédito, Financiamento, etc...
# DÉBITO --> Pagamento da dívida --> Saldo Diminui
# CRÉDITO --> Nova dívida --> Saldo Aumenta
#----------------------------------------------------------------
def _recalcular_saldo_credora(conta: ContaCredora):
    """Recalcula o saldo da conta credora somando todas as partidas"""
    creditos = conta.partidas.filter(tipo='CREDITO').aggregate( # type: ignore
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    debitos = conta.partidas.filter(tipo='DEBITO').aggregate( # type: ignore
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    novo_saldo = (conta.saldo_inicial + creditos) - debitos
    #Update() faz SQL direto - não dispara save() nem signals, evitando recursão
    ContaCredora.objects.filter(pk=conta.pk).update(saldo=novo_saldo)

def _recalcular_saldo_devedora(conta: ContaDevedora):
    """Recalcula o saldo da conta devedora somando todas as partidas"""
    creditos = conta.partidas.filter(tipo='CREDITO').aggregate( # type: ignore
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    debitos = conta.partidas.filter(tipo='DEBITO').aggregate( # type: ignore
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    novo_saldo = (conta.saldo_inicial + creditos) - debitos
    ContaDevedora.objects.filter(pk=conta.pk).update(saldo=novo_saldo)

def _atualizar_contas_da_partida(partida: Partida):
    """Dispara o recálculo das contas envolvidas em uma partida"""
    if partida.conta_credora_id: # type: ignore
        _recalcular_saldo_credora(partida.conta_credora) # type: ignore

    if partida.conta_devedora_id: # type: ignore
        _recalcular_saldo_devedora(partida.conta_devedora) # type: ignore

@receiver(pre_save, sender=Partida)
def partida_pre_save(sender, instance, **kwargs):
    """
    Antes de salvar, guarda as contas ANTIGAS da partida(se for edição).
    Isso permite recalcular a conta anterior caso o usuário troque de conta.
    """
    if instance.pk:
        try:
            anterior = Partida.objects.get(pk=instance.pk)
            instance._conta_credora_anterior = anterior.conta_credora
            instance._conta_devedora_anterior = anterior.conta_devedora
        except Partida.DoesNotExist:
            instance._conta_credora_anterior = None
            instance._conta_devedora_anterior = None
    else:
        instance._conta_credora_anterior = None
        instance._conta_devedora_anterior = None

@receiver(post_save, sender=Partida)
def partida_post_save(sender, instance, **kwargs):
    """Após salvar uma partida, recalcula as contas afetadas"""
    contas_credoras_afetadas = set()
    contas_devedoras_afetadas = set()

    #Conta Atual
    if instance.conta_credora_id:
        contas_credoras_afetadas.add(instance.conta_credora_id)

    if instance.conta_devedora_id:
        contas_devedoras_afetadas.add(instance.conta_devedora_id)

    #Conta Anterior(Caso tenha trocado de conta na edição)
    if instance._conta_credora_anterior:
        contas_credoras_afetadas.add(instance._conta_credora_anterior.pk)

    if instance._conta_devedora_anterior:
        contas_devedoras_afetadas.add(instance._conta_devedora_anterior.pk)

    for pk in contas_credoras_afetadas:
        try:
            _recalcular_saldo_credora(ContaCredora.objects.get(pk=pk))
        except ContaCredora.DoesNotExist:
            pass

    for pk in contas_devedoras_afetadas:
        try:
            _recalcular_saldo_devedora(ContaDevedora.objects.get(pk=pk))
        except ContaDevedora.DoesNotExist:
            pass

@receiver(post_delete, sender=Partida)
def partida_post_delete(sender, instance, **kwargs):
    """Após excluir uma partida, recalcula as contas que ela afetava"""
    _atualizar_contas_da_partida(instance)
    