from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class FaixaDeAtraso:
    """Faixa (limite anterior, limite_superior]. limite_superior None = sem limite."""

    limite_superior: timedelta | None
    percentual: Decimal

    def contem(self, atraso: timedelta) -> bool:
        return self.limite_superior is None or atraso <= self.limite_superior


@dataclass(frozen=True)
class Apuracao:
    credito: Decimal
    notificar_atraso: bool = False


class TipoClienteDesconhecido(LookupError):
    pass


class PoliticaDeCredito(Protocol):
    """Strategy: cada tipo de cliente tem a sua política de crédito (RF04)."""

    def calcular(self, frete: Decimal, atraso: timedelta) -> Apuracao: ...


@dataclass(frozen=True)
class PoliticaPorFaixas:
    faixas: tuple[FaixaDeAtraso, ...]
    teto: Decimal

    def calcular(self, frete: Decimal, atraso: timedelta) -> Apuracao:
        percentual = next(faixa.percentual for faixa in self.faixas if faixa.contem(atraso))
        credito = (frete * percentual).quantize(CENTAVO, rounding=ROUND_HALF_UP)
        return Apuracao(credito=min(credito, self.teto))


class PoliticaCortesia:
    """Frete zero: nunca há crédito, mas o cliente é notificado do atraso (RF03)."""

    def calcular(self, frete: Decimal, atraso: timedelta) -> Apuracao:
        return Apuracao(credito=ZERO, notificar_atraso=atraso > timedelta(0))


# A primeira faixa é a tolerância: atraso de até 2 h não gera crédito.
FAIXAS_VAREJO = (
    FaixaDeAtraso(timedelta(hours=2), Decimal("0.00")),
    FaixaDeAtraso(timedelta(hours=24), Decimal("0.10")),
    FaixaDeAtraso(timedelta(hours=72), Decimal("0.25")),
    FaixaDeAtraso(None, Decimal("0.50")),
)
TETO_VAREJO = Decimal("500.00")

# RF03: os percentuais do Varejo dobram para o Corporativo.
FAIXAS_CORPORATIVO = tuple(
    FaixaDeAtraso(faixa.limite_superior, faixa.percentual * 2) for faixa in FAIXAS_VAREJO
)
TETO_CORPORATIVO = Decimal("2000.00")

POLITICA_VAREJO = PoliticaPorFaixas(FAIXAS_VAREJO, TETO_VAREJO)
POLITICA_CORPORATIVO = PoliticaPorFaixas(FAIXAS_CORPORATIVO, TETO_CORPORATIVO)
POLITICA_CORTESIA = PoliticaCortesia()


class RegistroDePoliticas:
    """Escolhe a política pelo tipo de cliente. Tipo novo = registrar, sem editar as demais."""

    def __init__(self) -> None:
        self._politicas: dict[str, PoliticaDeCredito] = {}

    def registrar(self, tipo_cliente: str, politica: PoliticaDeCredito) -> None:
        self._politicas[tipo_cliente] = politica

    def calcular(self, tipo_cliente: str, frete: Decimal, atraso: timedelta) -> Apuracao:
        try:
            politica = self._politicas[tipo_cliente]
        except KeyError:
            raise TipoClienteDesconhecido(tipo_cliente) from None
        return politica.calcular(frete, atraso)


def registro_padrao() -> RegistroDePoliticas:
    registro = RegistroDePoliticas()
    registro.registrar("VAREJO", POLITICA_VAREJO)
    registro.registrar("CORPORATIVO", POLITICA_CORPORATIVO)
    registro.registrar("CORTESIA", POLITICA_CORTESIA)
    return registro


_REGISTRO = registro_padrao()


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso: timedelta) -> Apuracao:
    return _REGISTRO.calcular(tipo_cliente, frete, atraso)
