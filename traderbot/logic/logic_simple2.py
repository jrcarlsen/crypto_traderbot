################################################################################
#
# Simple Logic Example
#
# Single exchange, buy immediately, wait for 1 minute then sell on 2% drop.
#
################################################################################

from traderbot.logic import LogicBase

################################################################################

class Logic(LogicBase):
    name = 'logic_simple2'
    interval = 60
    markets = {}
    
    def __init__(self, signal, config):
        print self.name, signal, config
        self.signal = signal
       
        # Try to get an exchange object we can work with, if we fail to get the
        # object, we kill ourself. 
        market = signal.get_market('Bittrex', 'BTC-'+signal.get('currency'))
        if not market:
            self.killed = True
        else:
            self.register_market(market)
        
            # Whenever the rates are updated, send them to the update() method.
            market.set_callback('market', self.update_market)

    def update_market(self, market):
        # If we haven't bought anything yet, then lets buy at the current rate.
        if not market.bought():
            market.buy(self.signal.get('amount'))
            return

        # If signal is less than 1 minute old, then lets not make any decisions
        # yet.
        if self.signal.age() < 60:
            return

        # If we drop more than 2% below the best rate, then we sell everything.
        if market.diff_high() < -5.0:
            market.sell()

    def run(self):
        self._update_markets()
        print self.name, "run"

################################################################################

