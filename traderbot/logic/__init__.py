################################################################################

import os
from datetime import datetime

################################################################################

class LogicBase:
    # How often do we want run() to be called?
    interval = 5
    
    def __init__(self, signal, config):
        self.signal = signal
        self.config = config
        self.data = {'market_data': {}, 'uuid': self.uuid}
        self.markets = {}
        self.lastrun = 0

    def _set_name(self, name):
        self.name = name.replace('.pyc', '.py')
        if self.name.find('/') != -1:
            self.name = self.name.rsplit('/',1)[1]

    def log_write(self, message):
        timestamp = str(datetime.now())
        log_entry = "[%s](%i) %s" % (timestamp, self.signal.get_id(), message)

        path = "logs/%s" % self.signal.get_id()
        if not os.path.exists(path):
            print path
            os.system('mkdir -p %s' % path)
        
        print log_entry
        open('%s/%s.log' % (path, self.name), 'a').write(log_entry+'\n')

    def description(self):
        return "<{name}>".format(**{
            'name': self.name,
        })

    def get_data(self):
        self.data['market_data'] = {}
        for market_name, market_object in self.markets.items():
            self.data['market_data'][market_name] = market_object.data
        return self.data

    def set_data(self, data):
        self.data = data
        if self.killed():
            return False

        for market_name in self.data['market_data']:
            self.markets[market_name].set_data(self.data['market_data'][market_name])
        return True

    def log_status(self):
        self.log_write('DONE: {"signal": %i, "market": "%s", "bought": %0.8f, "sold": %0.8f, "best": %0.8f, "best-pct": %0.1f, "sale-percent": %0.1f}' % (
            self.signal.get_id(), 
            self.market.market_name, 
            self.market.bought_average_rate(), 
            self.market.sold_average_rate(), 
            self.market.bid_highest(),
            self.market.best_percent(), 
            self.market.status_percent()))
        return True
 
    def kill(self):
        self.data['killed'] = True
        return True

    def killed(self):
        return self.data.get('killed', False)

    def run(self):
        self._update_markets()

    def register_market(self, market_object, market_name='default'):
        if not market_object:
            return False
        self.markets[market_name] = market_object
        market_object.set_callback('market', self.market_update)

    def _update_markets(self):
        for market_name, market_object in self.markets.items():
            market_object.run()

    def market_update(self, market):
        """Catch a callback whenever there are market updates"""
        return

################################################################################
