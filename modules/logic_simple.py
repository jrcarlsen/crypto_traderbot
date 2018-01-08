################################################################################
#
# Simple Logic Example
#
# Single exchange, buy immediately, sell on 2% drop.
#
################################################################################

class Logic:
    def __init__(self, signal):
        self.signal = signal
       
        # Try to get an exchange object we can work with, if we fail to get the
        # object, we kill ourself. 
        exchange = signal.get_exchange('Bittrex', 'BTC-'+signal.get('currency'))
        if not exchange:
            signal.kill(self)
        
        # Whenever the rates are updated, send them to the update() method.
        exchange.update_callback(self.update)


    def update(self, exchange):
        # If we haven't bought anything yet, then lets buy at the current rate.
        if not self.exchange.bought():
            exchange.buy(self.signal.get('amount'))
            return

        # If signal is less than 1 minute old, then lets not make any decisions
        # yet.
        if self.signal.age() < 60:
            return

        # If we drop more than 2% below the best rate, then we sell everything.
        if exchange.diff_high() < -2.0:
            exchange.sell()

################################################################################

