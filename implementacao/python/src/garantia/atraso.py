from datetime import datetime, timedelta


def calcular_atraso(prazo_prometido: datetime, confirmacao_entrega: datetime) -> timedelta:
    """RF01: atraso = confirmação da entrega - prazo prometido pelo Frete, nunca negativo."""
    return max(confirmacao_entrega - prazo_prometido, timedelta(0))
