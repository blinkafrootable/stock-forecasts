
from enum import Enum, auto

class Exchange(Enum):
    UNKNOWN = auto()
    NO_INFO = auto()
    UNKNOWN_EXCHANGE = auto()
    NYSE = auto()
    NASDAQ = auto()
    OTC = auto()
    AMERICAN = auto()
    BATS = auto()
    IEX = auto()

    def __str__(self):
        if self.value == Exchange.UNKNOWN.value:
            return 'Unknown'
        elif self.value == Exchange.NO_INFO.value:
            return 'No Info'
        elif self.value == Exchange.UNKNOWN_EXCHANGE.value:
            return 'Unknown Exchange'
        elif self.value == Exchange.NYSE.value:
            return 'NYSE'
        elif self.value == Exchange.NASDAQ.value:
            return 'NASDAQ'
        elif self.value == Exchange.AMERICAN.value:
            return 'American'
        elif self.value == Exchange.BATS.value:
            return 'BATS'
        elif self.value == Exchange.IEX.value:
            return 'IEX'
        else:
            return 'OTC'
