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
    interval = 5
    uuid = 'dd481183-fca4-4526-aeb6-1fc6495438e6'
    
    def __init__(self, signal, config):
        LogicBase.__init__(self, signal, config)
        self._set_name(__file__)
       
        # Try to get an exchange object we can work with, if we fail to get the
        # object, we kill ourself. 
        self.market = signal.get_market('Bittrex', 'BTC-'+signal.get('currency'))
        if not self.market:
            self.kill()
        else:
            self.register_market(self.market)
        
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
            market.sell(market.bid_current(cached=False))
            self.log_status()
#            self.log_write('DONE: {"signal": %i, "market": "%s", "bought": %0.8f, "sold": %0.8f, "best": %0.8f}' % (
#                self.signal.get_id(), market.market_name, market.bought_average_rate(), market.sold_average_rate(), market.bid_highest()))
            self.kill()
            return

################################################################################

