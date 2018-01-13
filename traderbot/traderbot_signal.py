###############################################################################

import time
import pickle
import config

from traderbot_market import Market

###############################################################################

class Signal:
    def __init__(self, traderbot, load_id=None):
        self.traderbot = traderbot
        self.data = {'id': load_id, 'logic': {}}
        self.logic = {}
        self.lastrun = 0
       
        # If an ID was provided, then we need to load it from disk
        if load_id:
            self.load()

    def __repr__(self):
        return "<Signal %i>" % self.data['id']

    def _myfilename(self):
        return '%s/%s' % (config.SIGNAL_PATH, self.get_id())

    def init(self):
        self.save()
        # Start logic engines
        for logic_class, config in self.traderbot.logic.items():
            logic_object = logic_class(self, config)
            self.logic[logic_object.name] = logic_object

    def load(self):
        self.data = pickle.load(open(self._myfilename(), 'rb'))
        print "Loaded data for:", self.get_id()
#        for logic_name in self.data['logic']:
#            logic = self.traderbot 

    def save(self):
        # Collect data from the logic engines
        for name, logic_object in self.logic.values():
            self.data['logic'][name] = logic_object.get_data()
        pickle.dump(self.data, open(self._myfilename(), 'wb'))

    def get(self, key):
        return self.data.get(key, None)

    def get_id(self):
        return self.data.get('id', -1)

    def get_market(self, exchange_name, market):
        exchange_object = self.traderbot.exchanges.get(exchange_name.lower(), None)
        if not exchange_object:
            print "Unable to get Exchange for", exchange_name
            return False

        if not exchange_object.supports_market(market):
            print exchange_name, "does not support the market", market
            return False

        return Market(exchange_object, market)
        
    def run(self):
        logic_items = list(self.logic.items())
        for logic_name, logic_object in logic_items:
            if logic_object.killed:
                del self.logic[logic_name]

            now = time.time()
            if now-logic_object.lastrun < logic_object.interval:
                continue
            logic_object.lastrun = now
            logic_object.run()

###############################################################################

