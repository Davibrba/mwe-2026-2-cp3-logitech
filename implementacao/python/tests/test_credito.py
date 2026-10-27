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


def test_ct05_varejo_um_segundo_acima_de_24h_gera_25_porcento():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(24, 0, 1))
    assert apuracao.credito == Decimal("75.00")


def test_ct06_varejo_exatamente_72h_ainda_gera_25_porcento():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(72))
    assert apuracao.credito == Decimal("75.00")


def test_ct07_varejo_um_segundo_acima_de_72h_gera_50_porcento():
    apuracao = calcular_credito("VAREJO", Decimal("300.00"), atraso(72, 0, 1))
    assert apuracao.credito == Decimal("150.00")


def test_ct08_varejo_50_porcento_coincide_com_o_teto():
    apuracao = calcular_credito("VAREJO", Decimal("1000.00"), atraso(72, 0, 1))
    assert apuracao.credito == Decimal("500.00")


def test_ct09_varejo_credito_um_centavo_acima_do_teto_e_limitado_a_500():
    apuracao = calcular_credito("VAREJO", Decimal("1000.02"), atraso(72, 0, 1))
    assert apuracao.credito == Decimal("500.00")


def test_ct16_varejo_credito_arredondado_ao_centavo_half_up():
    apuracao = calcular_credito("VAREJO", Decimal("123.45"), atraso(2, 0, 1))
    assert apuracao.credito == Decimal("12.35")
    assert apuracao.credito.as_tuple().exponent == -2


def test_ct10_corporativo_tolerancia_igual_e_percentual_dobrado_na_primeira_faixa():
    assert calcular_credito("CORPORATIVO", Decimal("300.00"), atraso(2)).credito == Decimal("0.00")
    assert calcular_credito("CORPORATIVO", Decimal("300.00"), atraso(2, 0, 1)).credito == Decimal("60.00")


def test_ct11_corporativo_percentuais_dobrados_nos_limites_das_faixas():
    frete = Decimal("300.00")
    assert calcular_credito("CORPORATIVO", frete, atraso(24)).credito == Decimal("60.00")
    assert calcular_credito("CORPORATIVO", frete, atraso(24, 0, 1)).credito == Decimal("150.00")
    assert calcular_credito("CORPORATIVO", frete, atraso(72)).credito == Decimal("150.00")
    assert calcular_credito("CORPORATIVO", frete, atraso(72, 0, 1)).credito == Decimal("300.00")


def test_ct12_corporativo_credito_limitado_ao_teto_de_2000():
    assert calcular_credito("CORPORATIVO", Decimal("2000.00"), atraso(72, 0, 1)).credito == Decimal("2000.00")
    assert calcular_credito("CORPORATIVO", Decimal("2000.01"), atraso(72, 0, 1)).credito == Decimal("2000.00")


def test_ct13_cortesia_nao_recebe_credito_mas_e_notificada_do_atraso():
    apuracao = calcular_credito("CORTESIA", Decimal("0.00"), atraso(100))
    assert apuracao.credito == Decimal("0.00")
    assert apuracao.notificar_atraso is True
