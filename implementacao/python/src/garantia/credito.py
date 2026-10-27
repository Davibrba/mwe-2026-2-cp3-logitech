from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

TOLERANCIA = timedelta(hours=2)
TETO_VAREJO = Decimal("500.00")


@dataclass(frozen=True)
class Apuracao:
    credito: Decimal


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso: timedelta) -> Apuracao:
    if atraso <= TOLERANCIA:
        return Apuracao(credito=Decimal("0.00"))
    if atraso <= timedelta(hours=24):
        percentual = Decimal("0.10")
    elif atraso <= timedelta(hours=72):
        percentual = Decimal("0.25")
    else:
        percentual = Decimal("0.50")
    return Apuracao(credito=min(frete * percentual, TETO_VAREJO))
