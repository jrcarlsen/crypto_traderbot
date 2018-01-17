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
    uuid = '46eafb97-d536-44c9-ba42-b356454ed9d2'
    interval = 60
    period = 60*60*24 # 24 hours
    
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
        
    def description(self):
        time_left = (self.period)-self.signal.age()
        return "<%s time_left='%i'>" % (self.name, time_left)

    def market_update(self, market):
        # If we haven't bought anything yet, then lets buy at the current rate.
        if not market.bought():
            market.buy(market.bid_current(), self.signal.get('amount'))
            return

        if self.signal.age() > self.period:
            market.sell(market.bid_current(cached=False))
            self.log_status()
#            self.log_write('DONE: {"signal": %i, "market": "%s", "bought": %0.8f, "sold": %0.8f, "best": %0.8f, "period": %i}' % (
#                self.signal.get_id(), market.market_name, market.bought_average_rate(), market.sold_average_rate(), market.bid_highest(), self.period))
            self.kill()

################################################################################

