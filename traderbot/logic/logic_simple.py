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
    name = 'logic_simple'
    interval = 15
    
    def __init__(self, signal, config):
        LogicBase.__init__(self)
        self.signal = signal
       
        # Try to get an exchange object we can work with, if we fail to get the
        # object, we kill ourself. 
        self.market = signal.get_market('Bittrex', 'BTC-'+signal.get('currency'))
        if not self.market:
            self.killed = True
        else:
            self.register_market(self.market)
        
            # Whenever the rates are updated, send them to the update() method.
            self.market.set_callback('market', self.market_update)

    def __repr__(self):
        return "<{name}>".format(**{
            'name': self.name,
        })

    def market_update(self, market):
        # If we haven't bought anything yet, then lets buy at the current rate.
        if not market.bought():
            market.buy(market.bid_current(), self.signal.get('amount'))
            return

        # If signal is less than 1 minute old, then lets not make any decisions
        # yet.
        if self.signal.age() < 60:
            return

        # If we drop more than 2% below the best rate, then we sell everything.
        if market.diff_highest() < -2.0:
            market.sell()
            self.killed = True
            return

    def run(self):
        self._update_markets()

################################################################################

