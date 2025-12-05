from enum import StrEnum


class SalaryCurrency(StrEnum):
    RUR = "RUR"  # российский рубль
    EUR = "EUR"  # евро
    USD = "USD"  # доллар
    KZT = "KZT"  # тенге
    BYR = "BYR"  # белорусский рубль
    GEL = "GEL"  # грузинский лари
    UZS = "UZS"  # узбекский сум
    KGS = "KGS"  # киргизский сом
    AZN = "AZN"  # азербайджанский манат

    def humanize(self) -> str:
        match self:
            case self.RUR:
                return "RUB"
            case self.BYR:
                return "BYN"

        return str(self.value)


class SalaryMode(StrEnum):
    MONTH = "MONTH"

    def humanize(self) -> str | None:
        match self:
            case self.MONTH:
                return "в месяц"

        return None
