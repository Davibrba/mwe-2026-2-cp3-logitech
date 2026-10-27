from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

TOLERANCIA = timedelta(hours=2)


@dataclass(frozen=True)
class Apuracao:
    credito: Decimal


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso: timedelta) -> Apuracao:
    if atraso <= TOLERANCIA:
        return Apuracao(credito=Decimal("0.00"))
    return Apuracao(credito=frete * Decimal("0.10"))
