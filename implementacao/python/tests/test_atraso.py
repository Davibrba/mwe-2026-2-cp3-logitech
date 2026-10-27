from datetime import datetime, timedelta

from garantia.atraso import calcular_atraso

PRAZO_PROMETIDO = datetime(2026, 10, 27, 10, 0, 0)


def test_ct15_atraso_e_a_diferenca_entre_confirmacao_e_prazo_prometido():
    confirmacao = datetime(2026, 10, 27, 12, 0, 1)
    assert calcular_atraso(PRAZO_PROMETIDO, confirmacao) == timedelta(hours=2, seconds=1)


def test_ct15_entrega_antecipada_nao_gera_atraso_negativo():
    confirmacao = datetime(2026, 10, 27, 9, 30, 0)
    assert calcular_atraso(PRAZO_PROMETIDO, confirmacao) == timedelta(0)
