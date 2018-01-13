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
        self.bittrex = bittrex.Bittrex(config['API_KEY'], config['API_SECRET'])

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

        print self, "market update"
        # We want to update the poll time, even if we don't get any data, just to avoid
        # flooding the api in case of a problem.
        self.data['last_market_poll'] = time.time()
        result = self.bittrex.get_market_summaries()
        if not result:
            return False

        if not result.get('success', False):
            return False

        for coin in result['result']:
            market_name = coin['MarketName']
            
            self.market_data[market_name] = {
                'bid':      coin['Bid'],
                'ask':      coin['Ask'],
                'high':     coin['High'],
                'low':      coin['Low'],
                'volume':   coin['Volume'],
            }
        self.data['last_market_update'] = time.time()
        return True

    def _update_balances(self, cached=True):
        if cached and time.time() - self.data['last_balance_poll'] < self.config['POLL_FREQUENCY']:
            return False

        print self, "balance update"

        self.data['last_balance_poll'] = time.time()

        result = self.bittrex.get_balances()
        if not result:
            return False

        if not result.get('success', False):
            return False

        for coin in result['result']:
            currency = coin['Currency']
            self.balance_data[currency] = {
                'balance':      coin['Balance'],
                'available':    coin['Available'],
                'pending':      coin['Pending'],
            }

        self.data['last_balance_update'] = time.time()
        return True    

    def run(self):
        self._update_markets()
        self._update_balances()

################################################################################
