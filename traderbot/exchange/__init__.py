################################################################################

class ExchangeBase:
    name = None

    def get_name(self):
        return self.name

    def get_market(self, market, key, cached=True):
        self._update_markets(cached)
        return self.markets[market][key]

    def get_balance(self, currency, key, cached=True):
        self._update_balances(cached)
        return self.balance_data[currency][key]

    def supports_market(self, market):
        # FIXME: Not implemented
        return True

################################################################################

