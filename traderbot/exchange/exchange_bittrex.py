################################################################################

import time

from external.bittrex import bittrex
from traderbot.exchange import ExchangeBase

################################################################################

class Exchange(ExchangeBase):
    name = 'Bittrex'

    def __init__(self, tradebot, config):
        ExchangeBase.__init__(self)
        self.config = config
        self.bittrex = bittrex.Bittrex(config['API_KEY'], config['API_SECRET'], api_version='v2.0')

        # Tracking of markets
        self.data['last_market_poll'] = 0    # When was the last time we tried to get data from their API
        self.data['last_market_update'] = 0  # When was the last time we got any good data
        self._update_markets()

        # Tracking of balances
        self.data['last_balance_poll'] = 0
        self.data['last_balance_update'] = 0

        # Tracking of orders
        # FIXME: To come

        # Tracking of orderbooks
        # FIXME: To come

    def _update_markets(self, cached=True):
        # Make sure we don't poll for updates to frequently.
        if cached and time.time() - self.data['last_market_poll'] < self.config['POLL_FREQUENCY']:
            return False

        # We want to update the poll time, even if we don't get any data, just to avoid
        # flooding the api in case of a problem.
        self.data['last_market_poll'] = time.time()
        result = self.bittrex.get_market_summaries()
        if not result:
            return False

        if not result.get('success', False):
            return False

        for entry in result['result']:
            market_name  = entry['Market']['MarketName']
            self.market_data[market_name] = {
                'bid':      entry['Summary']['Bid'],
                'ask':      entry['Summary']['Ask'],
                'high':     entry['Summary']['High'],
                'low':      entry['Summary']['Low'],
                'volume':   entry['Summary']['Volume'],
            }

        self.data['last_market_update'] = time.time()
        return True

    def _update_balances(self, cached=True):
        if cached and time.time() - self.data['last_balance_poll'] < self.config['POLL_FREQUENCY']:
            return False

        self.data['last_balance_poll'] = time.time()

        result = self.bittrex.get_balances()
        if not result:
            return False

        if not result.get('success', False):
            return False

        for entry in result['result']:
            currency = entry['Currency']['Currency']
            self.balance_data[currency] = {
                'balance':      entry['Balance']['Balance'],
                'available':    entry['Balance']['Available'],
                'pending':      entry['Balance']['Pending'],
            }

        self.data['last_balance_update'] = time.time()
        return True    

    def limit_sell(self, market, rate, quantity):
        result = self.bittrex.trade_sell(
            market=market, 
            order_type='LIMIT', 
            quantity=quantity, 
            rate=rate, 
            time_in_effect='IMMEDIATE_OR_CANCEL'
        )
        print "LIMIT_SELL", result
        print market, 'LIMIT', "%0.8f" % quantity, rate, 'IMMEDIATE_OR_CANCEL'

        if not result or result['success'] != True:
            return False

        order_id = result['result']['OrderId']
        order = self.bittrex.get_order(uuid=order_id)
        print order

        if not order or order['success'] != True:
            return False

        order_rate      = order['result']['PricePerUnit']
        order_quantity  = order['result']['Quantity']-order['result']['QuantityRemaining']
        if order_quantity <= 0:
            return False

        return ((order_rate, order_quantity),)

    def limit_buy(self, market, rate, quantity):
        result = self.bittrex.trade_buy(
            market=market, 
            order_type='LIMIT', 
            quantity=quantity, 
            rate=rate, 
            time_in_effect='IMMEDIATE_OR_CANCEL'
        )

        print "LIMIT_BUY", result
        print market, 'LIMIT', "%0.8f" % quantity, rate, 'IMMEDIATE_OR_CANCEL'
        if not result or result['success'] != True:
            return False

        order_id = result['result']['OrderId']
        order = self.bittrex.get_order(uuid=order_id)
        print order

        if not order or order['success'] != True:
            return False

        order_rate      = order['result']['PricePerUnit']
        order_quantity  = order['result']['Quantity']-order['result']['QuantityRemaining']
        if order_quantity <= 0:
            return False

        return ((order_rate, order_quantity),)

    def run(self):
        self._update_markets()
        self._update_balances()

################################################################################
