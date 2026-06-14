from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def brl(value):
    """
    Formata o número monetário brasileiro:
    1234567.89 --> 1.234.567,89
    retorna '0,00' para None ou valores inválidos
    """
    try:
        v = Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return '0,00'
    
    #Separa parte inteira e decimal
    inteira, decimal = f'{abs(v):.2f}'.split('.')

    #Insere ponto a cada três dígitos da parte inteira
    grupos = []
    while len(inteira) > 3:
        grupos.insert(0, inteira[-3:])
        inteira = inteira[:-3]

    grupos.insert(0, inteira)

    sinal = '-' if v < 0 else ''
    return f'{sinal}{"." .join(grupos)},{decimal}'
