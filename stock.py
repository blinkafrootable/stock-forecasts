
from exchange import Exchange

class Stock:
    def __init__(self, name, symbol, price, forecast14d, forecast3m, forecast6m, forecast1y, forecast5y, rating):
        self.name = name
        self.symbol = symbol
        self.price = price
        self.forecast14d = forecast14d
        self.forecast3m = forecast3m
        self.forecast6m = forecast6m
        self.forecast1y = forecast1y
        self.forecast5y = forecast5y
        self.rating = rating

        self.exchange = Exchange.UNKNOWN

        self.price_num = float(self.price[1: len(self.price)])
        self.forecast14d_value = self.price_num * (float(self.forecast14d.replace('%', '').replace('+', ''))/100)
        self.forecast3m_value = self.price_num * (float(self.forecast3m.replace('%', '').replace('+', ''))/100)
        self.forecast6m_value = self.price_num * (float(self.forecast6m.replace('%', '').replace('+', ''))/100)
        self.forecast1y_value = self.price_num * (float(self.forecast1y.replace('%', '').replace('+', ''))/100)
        self.forecast5y_value = self.price_num * (float(self.forecast5y.replace('%', '').replace('+', ''))/100)

    def __str__(self):
        return self.rating + '   ' + self.name + self.symbol + ' [' + self.price + ']: 14D: ' + self.forecast14d + ', 3M: ' + self.forecast3m + ', 6M: ' + self.forecast6m + ', 1Y: ' + self.forecast1y + ', 5Y: ' + self.forecast5y

    def __repr__(self):
        return self.rating + '   ' + self.name + self.symbol + ' [' + self.price + ']: 14D: ' + self.forecast14d + ', 3M: ' + self.forecast3m + ', 6M: ' + self.forecast6m + ', 1Y: ' + self.forecast1y + ', 5Y: ' + self.forecast5y
