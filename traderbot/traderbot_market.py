class Market:
    data = {}

    def __init__(self, exchange_object, market_name):
        self.exchange = exchange_object
        self.market = market_name
        self.callback = {}
        print self, "created"

    def diff_highest(self):
        """Difference in percent from the highest bid we've seen"""
        return (self.bid_current()/self.bid_highest()*100)-100

    def diff_buy(self):
        pass

    def bid_highest(self):
        pass

    def bid_lowest(self):
        """The lowest bid we've seen"""
        return self._get('bid_lowest')

    def bid_average(self):
        pass

    def bid_current(self, cached=True):
        """Get the current bid"""
        return self.exchange.get_bid(self.market)

    def set_callback(self, event, callback):
        self.callback['event'] = [callback, 0]

    def run(self):
        print self.market, "run"
        for event in ('balance', 'market'):
            if not self.callback.has_key(event):
                continue
            if self.exchange.data['last_%s_update'] < self.callback[event][1]:
                continue
            self.callback[event][1] = self.exchange.data['last_%s_update']
            self.callback[event][0](self)
