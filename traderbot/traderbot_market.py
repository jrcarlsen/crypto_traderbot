class Market:
    def __init__(self, exchange_object, market_name, simulated=True):
        self.simulated = simulated
        self.market_name = market_name
        self.exchange = exchange_object
        self.callback = {}
        self._init_values()

    def description(self):
        return "<market market='{market}' exchange='{exchange}' bid='{bid:0.8f}' highest='{highest:0.8f}' lowest='{lowest:0.8f}'>".format(**{
            'exchange':     self.exchange.get_name(),
            'market':       self.market_name,
            'bid':          self.bid_current(),
            'highest':      self.bid_highest(),
            'lowest':       self.bid_lowest(),
        })

    def _init_values(self):
        self.data = {
            'simulated':        self.simulated,
            'exchange_market':  self.market_name,
            'exchange_name':    self.exchange.name,
            'bought':           [],
            'sold':             [],
            'balance':          0,
            'bid_highest':      self.bid_current(),
            'bid_lowest':       self.bid_current(),
            'bid_highest':      self.ask_current(),
            'bid_lowest':       self.ask_current(),
            'ask_history':      [],
        }

    def _update_values(self):
        self.data['bid_lowest']  = min(self.bid_lowest(),  self.bid_current())
        self.data['bid_highest'] = max(self.bid_highest(), self.bid_current())
        self.data['ask_lowest']  = min(self.ask_lowest(),  self.ask_current())
        self.data['ask_highest'] = max(self.ask_highest(), self.ask_current())

        if not self.data.has_key('ask_history'):
            self.data['ask_history'] = []

        self.data['ask_history'].append(self.ask_current())
        self.data['ask_history'] = self.data['ask_history'][-50:]

    def _get_value(self, key):
        return self.data.get(key, None)

    def is_simulated(self):
        return self.data.get('simulated', True)

    def best_percent(self, cached=True):
        bar = self.bought_average_rate()
        if not bar:
            return False
        return (self.ask_highest()/bar*100)-100

    def status_percent(self, cached=True):
        bar = self.bought_average_rate()
        bas = self.sold_average_rate()
        if not bar or not bas:
            return False
        # FIXME: Not all coins may have sold, so this may not make sense
        return (bas/bar*100)-100

    def diff_highest(self, cached=True):
        """Difference in percent from the highest bid we've seen"""
        try:
            return (self.bid_current(cached)/self.bid_highest()*100)-100
        except ZeroDivisionError:
            # FIXME: What do I do here?
            return False

    def diff_lowest(self, cached=True):
        """Difference in percent from the highest bid we've seen"""
        try:
            return (self.bid_current(cached)/self.bid_lowest()*100)-100
        except ZeroDivisionError:
            # FIXME: What do I do here?
            return False

    def diff_bought(self, cached=True):
        """Difference in percent from the average buying rate"""
        try:
            return (self.bid_current(cached)/self.bought_average_rate()*100)-100
        except ZeroDivisionError:
            # FIXME: What do I do here?
            return False

    def ask_highest(self):
        """The highest bid we've seen so far"""
        return self._get_value('ask_highest')

    def ask_lowest(self):
        """The lowest bid we've seen"""
        return self._get_value('ask_lowest')

    def ask_current(self, cached=True):
        """Get the current bid"""
        return self.exchange.get_market(self.market_name, 'ask')

    def ask_trend_upwards(self, samples=8):
        # FIXME: This is not the right way to calculate this
        history = self.data['ask_history'][0-samples:]
        average = sum(history)/float(len(history))
        return average > self.ask_current()

    def ask_trend_downwards(self, samples=8):
        # FIXME: This is not the right way to calculate this
        history = self.data['ask_history'][0-samples:]
        average = sum(history)/float(len(history))
        return average < self.ask_current()

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
        try:
            value_sum   = sum([amount*rate for rate, amount in bought])
            amount_sum  = sum([amount for rate, amount in bought])
        except TypeError:
            return 0
        return value_sum/amount_sum

    def sold(self):
        return self._get_value('sold')

    def sold_average_rate(self):
        sold = self.sold()
        try:
            value_sum   = sum([amount*rate for rate, amount in sold])
            amount_sum  = sum([amount for rate, amount in sold])
        except TypeError:
            return 0

        if amount_sum == 0:
            return 0
        return value_sum/amount_sum

    def balance(self):
        return self.data.get('balance', 0)

    def buy(self, rate, quantity):
        print "market.buy %0.8f @ %0.8f" % (quantity, rate)
        if self.is_simulated():
            self.data['balance'] = self.balance()+quantity
            self.data['bought'].append((rate, quantity),)
            return True

        # FIXME: Real buy goes here
        txs = self.exchange.limit_buy(self.market_name, rate, quantity)
        if not txs:
            return False
        
        for rate, quantity in txs:
            self.data['balance'] = self.balance()+quantity
            self.data['bought'].append((rate, quantity),)
        return True
            
    def sell(self, rate, quantity=None):
        if not quantity:
            quantity = self.balance()

        if quantity <= 0:
            return False

        # Do not allow the sale of more coins than we bought
        quantity = min(quantity, self.balance())

        if self.is_simulated():
            self.data['balance'] = self.balance()-quantity
            self.data['sold'].append((rate, quantity))
            return True

        # FIXME: Real sell goes here
        txs = self.exchange.limit_sell(self.market_name, rate, quantity)
        if not txs:
            return False

        for rate, quantity in txs:
            self.data['balance'] = self.balance()-quantity
            self.data['sold'].append((rate, quantity),)
        return True

    def btc_to_coin(self, btc_amount, cached=True):
        return btc_amount/self.ask_current(cached)

################################################################################

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
