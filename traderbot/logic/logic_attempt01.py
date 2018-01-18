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
    uuid = 'd11a1762-ffcc-47a2-944e-07be77c6ac4e'
    
    def __init__(self, signal, config):
        LogicBase.__init__(self, signal, config)
        self._set_name(__file__)
 
        # Try to get an exchange object we can work with, if we fail to get the
        # object, we kill ourself. 
        self.market = signal.get_market('Bittrex', 'BTC-'+signal.get('currency'), simulated=False)
        if not self.market:
            self.kill()
        else:
            self.register_market(self.market)
    
    def description(self):
        return "<%s buy_diff='%0.8f' bought_rate='%0.8f' balance='%0.8f' age='%i'>" % (
            self.name, self.market.diff_bought(), self.market.bought_average_rate(), 
            self.market.balance(), self.signal.age())
 
    def market_update(self, market):
        # If we haven't bought anything yet, then lets buy at the current rate.
        if not market.bought():
            ask_current = market.ask_current(cached=False)
            ask_amount  = market.btc_to_coin(max(self.signal.get('amount'), 0.0006))
            market.buy(ask_current*1.02, ask_amount)
            self.log_write('BUY %s: %0.8f @ %0.8f' % (
                market.market_name, ask_amount, ask_current))
            return

        sell = False
        # If we held this coin for 12 hours and we are above a 2% loss, sell!
        if self.signal.age() > 60*60*12 and market.diff_bought() > -2.0 and market.ask_trend_downwards:
            sell = True

        # If we held this coin for 24 hours and we are above a 4% loss, sell!
        if self.signal.age() > 60*60*24 and market.diff_bought() > -4.0 and market.ask_trend_downwards:
            sell = True

        # If we can get more than 5% on a sale, sell as soon as the value drops:
        if market.diff_bought() > 5.0 and market.diff_highest() > -1.0:
            sell = True

        if not sell:
            return
   
        # Sell 
        bid_current = market.bid_current(cached=False)
        bid_amount  = market.balance()
        market.sell(bid_current, bid_amount)
        self.log_write('SELL %s: %0.8f @ %0.8f' % (
            market.market_name, bid_amount, bid_current))
        self.log_status()
        self.kill()

################################################################################
