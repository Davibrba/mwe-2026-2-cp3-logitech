from datetime import timedelta
from decimal import Decimal

from garantia.credito import calcular_credito


def atraso(horas=0, minutos=0, segundos=0):
    return timedelta(hours=horas, minutes=minutos, seconds=segundos)


def test_ct01_varejo_atraso_abaixo_da_tolerancia_nao_gera_credito():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(1, 59))
    assert apuracao.credito == Decimal("0.00")


def test_ct02_varejo_atraso_exatamente_no_limite_da_tolerancia_nao_gera_credito():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(2))
    assert apuracao.credito == Decimal("0.00")


def test_ct03_varejo_um_segundo_acima_da_tolerancia_gera_10_porcento():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(2, 0, 1))
    assert apuracao.credito == Decimal("30.00")


def test_ct04_varejo_exatamente_24h_ainda_gera_10_porcento():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(24))
    assert apuracao.credito == Decimal("30.00")
