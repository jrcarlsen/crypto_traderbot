################################################################################

class ExchangeBase:
    name = None

    def __init__(self):
        self.balance_data = {}
        self.market_data = {}
        self.data = {}

    def get_name(self):
        return self.name

    def get_market(self, market, key, cached=True):
        self._update_markets(cached)
        print market, self.market_data[market]
        return self.market_data[market][key]

    def get_balance(self, currency, key, cached=True):
        self._update_balances(cached)
        return self.balance_data[currency][key]

    def supports_market(self, market):
        # FIXME: Not implemented
        return True

################################################################################

