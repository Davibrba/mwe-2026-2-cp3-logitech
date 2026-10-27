from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


@dataclass(frozen=True)
class FaixaDeAtraso:
    """Faixa (limite anterior, limite_superior]. limite_superior None = sem limite."""

    limite_superior: timedelta | None
    percentual: Decimal

    def contem(self, atraso: timedelta) -> bool:
        return self.limite_superior is None or atraso <= self.limite_superior


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


@dataclass(frozen=True)
class Apuracao:
    credito: Decimal


def _percentual(faixas: tuple[FaixaDeAtraso, ...], atraso: timedelta) -> Decimal:
    return next(faixa.percentual for faixa in faixas if faixa.contem(atraso))


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso: timedelta) -> Apuracao:
    if tipo_cliente == "CORPORATIVO":
        faixas, teto = FAIXAS_CORPORATIVO, TETO_CORPORATIVO
    else:
        faixas, teto = FAIXAS_VAREJO, TETO_VAREJO
    percentual = _percentual(faixas, atraso)
    credito = (frete * percentual).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return Apuracao(credito=min(credito, teto))
