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
    uuid = '29a976e5-6e6c-46af-b82e-dfbce3fec497'
    
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
            ask_current = market.ask_current(cached=False)
            ask_amount  = self.signal.get('amount')
            market.buy(ask_current, ask_amount)
            self.log_write('BUY %s: %0.8f @ %0.8f' % (
                market.market_name, ask_amount, ask_current))
            return

        # If signal is less than 1 minute old, then lets not make any decisions
        # yet.
        if self.signal.age() < 60:
            return

        # If we drop more than 2% below the best rate, then we sell everything.
        if market.diff_highest() < -5.0:
            bid_current = market.bid_current(cached=False)
            bid_amount  = market.balance()
            market.sell(bid_current, bid_amount)
            self.log_write('SELL %s: %0.8f @ %0.8f' % (
                market.market_name, bid_amount, bid_current))
            self.log_status()
            self.kill()
            return

################################################################################
