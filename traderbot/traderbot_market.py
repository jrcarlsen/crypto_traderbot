class Market:
    def __init__(self, exchange_object, market_name):
        self.market_name = market_name
        self.exchange = exchange_object
        self.callback = {}
        self._init_values()

    def description(self):
        return "<market market='{market}' exchange='{exchange}' bid='{bid}' highest='{highest}' lowest='{lowest}'>".format(**{
            'exchange':     self.exchange.get_name(),
            'market':       self.market_name,
            'bid':          self.bid_current(),
            'highest':      self.bid_highest(),
            'lowest':       self.bid_lowest(),
        })

    def _init_values(self):
        self.data = {
            'exchange_market':  self.market_name,
            'exchange_name':    self.exchange.name,
            'bought':           [],
            'sold':             [],
            'bid_highest':      self.bid_current(),
            'bid_lowest':       self.bid_current(),
        }

    def _update_values(self):
        self.data['bid_lowest'] = min(self.bid_lowest(), self.bid_current())
        self.data['bid_highest'] = max(self.bid_highest(), self.bid_current())

    def _get_value(self, key):
        return self.data.get(key, None)

    def diff_highest(self, cached=True):
        """Difference in percent from the highest bid we've seen"""
        return (self.bid_current(cached)/self.bid_highest()*100)-100

    def diff_bought(self, cached=True):
        """Difference in percent from the average buying rate"""
        return (self.bid_current(cached)/self.bought_average_rate(cached)*100)-100

    def bid_highest(self):
        """The highest bid we've seen so far"""
        return self._get_value('bid_highest')

    def bid_lowest(self):
        """The lowest bid we've seen"""
        return self._get_value('bid_lowest')

    def bid_current(self, cached=True):
        """Get the current bid"""
        return self.exchange.get_market(self.market_name, 'bid')

    def bought(self):
        return self._get_value('bought')

    def bought_average_rate(self):
        bought      = self.bought()
        value_sum   = sum([amount*rate for amount, rate in bought])
        amount_sum  = sum([amount for amount, rate in bought])
        return value_sum/amount_sum

    def sold(self):
        return self._get_value('sold')

    def sold_average_rate(self):
        sold        = self.sold()
        value_sum   = sum([amount*rate for amount, rate in sold])
        amount_sum  = sum([amount for amount, rate in sold])
        return value_sum/amount_sum

    def balance(self):
        return 0

    def buy(self, rate, amount):
        print "BUY", self, rate, amount
        self.data['bought'].append((rate, amount))

    def sell(self, rate, amount=None):
        print "SELL", self, rate, amount
        self.data['sold'].append((rate, amount))

    def set_callback(self, event, callback):
        self.callback[event] = [callback, 0]

    def set_data(self, data):
        self.data = data

    def run(self):
        self._update_values()
        for event in ('balance', 'market'):
            if not self.callback.has_key(event):
                continue
            update_key = 'last_%s_update' % event
            if self.exchange.data[update_key] <= self.callback[event][1]:
                continue
            self.callback[event][1] = self.exchange.data[update_key]
            self.callback[event][0](self)
