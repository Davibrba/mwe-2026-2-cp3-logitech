from datetime import timedelta
from decimal import Decimal

import pytest

from garantia.credito import (
    FaixaDeAtraso,
    PoliticaPorFaixas,
    TipoClienteDesconhecido,
    calcular_credito,
    registro_padrao,
)

ACIMA_DA_TOLERANCIA = timedelta(hours=2, seconds=1)


def politica_parceiro():
    return PoliticaPorFaixas(
        faixas=(
            FaixaDeAtraso(timedelta(hours=2), Decimal("0.00")),
            FaixaDeAtraso(None, Decimal("0.15")),
        ),
        teto=Decimal("800.00"),
    )


def test_ct14_tipo_novo_e_registrado_sem_alterar_os_tipos_existentes():
    registro = registro_padrao()

    registro.registrar("PARCEIRO", politica_parceiro())

    frete = Decimal("300.00")
    assert registro.calcular("PARCEIRO", frete, ACIMA_DA_TOLERANCIA).credito == Decimal("45.00")
    assert registro.calcular("VAREJO", frete, ACIMA_DA_TOLERANCIA).credito == Decimal("30.00")
    assert registro.calcular("CORPORATIVO", frete, ACIMA_DA_TOLERANCIA).credito == Decimal("60.00")


def test_ct14_registro_de_tipo_novo_nao_vaza_para_o_registro_padrao():
    registro_padrao().registrar("PARCEIRO", politica_parceiro())

    with pytest.raises(TipoClienteDesconhecido):
        calcular_credito("PARCEIRO", Decimal("300.00"), ACIMA_DA_TOLERANCIA)


def test_ct14_tipo_nao_registrado_gera_erro():
    with pytest.raises(TipoClienteDesconhecido):
        registro_padrao().calcular("DESCONHECIDO", Decimal("300.00"), ACIMA_DA_TOLERANCIA)
