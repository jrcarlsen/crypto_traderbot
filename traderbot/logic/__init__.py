################################################################################

import os

################################################################################

class LogicBase:
    # How often do we want run() to be called?
    interval = 5
    
    def __init__(self, signal, config):
        self.signal = signal
        self.config = config
        self.data = {'market_data': {}}
        self.markets = {}
        self.killed = False
        self.lastrun = 0

    def _set_name(self, name):
        self.name = name.replace('.pyc', '.py')
        if self.name.find('/') != -1:
            self.name = self.name.rsplit('/',1)[1]

    def description(self):
        return "<{name}>".format(**{
            'name': self.name,
        })

    def get_data(self):
        self.data['market_data'] = {}
        for market_name, market_object in self.markets.items():
            self.data['market_data'][market_name] = market_object.data
        return self.data

    def run(self):
        self._update_markets()

    def register_market(self, market_object, market_name='default'):
        if not market_object:
            return False
        self.markets[market_name] = market_object
        market_object.set_callback(self.market_update)

    def _update_markets(self):
        for market_name, market_object in self.markets.items():
            market_object.run()

    def market_update(self, market):
        return

################################################################################
