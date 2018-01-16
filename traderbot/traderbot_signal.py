###############################################################################

import time
import config

from traderbot_market import Market

###############################################################################

class Signal:
    def __init__(self, traderbot, load_id=None):
        self.traderbot = traderbot
        self.data = {'id': load_id, 'logic': {}, 'created': time.time()}
        self.logic = {}
        self.lastrun = 0
       
    def description(self):
        return "<signal id='%i'>" % self.data['id']

    def age(self):
        return time.time()-self.data.get('created', 0)

    def init(self):
        # Start logic engines
        for logic_uuid, logic_info in self.traderbot.logic.items():
            logic_class, config = logic_info
            logic_object = logic_class(self, config)
            self.logic[logic_uuid] = logic_object

    def set_data(self, data):
        self.data = data
        for logic_uuid in data.get('logic', {}):
            if not self.traderbot.logic.has_key(logic_uuid):
                print "Logic %s no longer exists" % logic_uuid
                print self.traderbot.logic
                continue

            logic_class, config = self.traderbot.logic[logic_uuid]
            logic_object = logic_class(self, config)
            if not logic_object.set_data(data['logic'][logic_uuid]):
                continue
            self.logic[logic_uuid] = logic_object

    def get_data(self):
        # Collect data from the logic engines
        if not self.data.has_key('logic'):
            self.data['logic'] = {}

        for name, logic_object in self.logic.items():
            self.data['logic'][name] = logic_object.get_data()
        return self.data

    def get(self, key):
        return self.data.get(key, None)

    def get_id(self):
        return self.data.get('id', -1)

    def get_market(self, exchange_name, market):
        print self.description, "get_market()"
        exchange_object = self.traderbot.exchanges.get(exchange_name.lower(), None)
        if not exchange_object:
            print "Unable to get Exchange for", exchange_name
            return False

        if not exchange_object.supports_market(market):
            print exchange_name, "does not support the market", market
            return False

        return Market(exchange_object, market)
        
    def load_market(self, data):
        print self.description, "load_market()"
        return None
        #print data
        #exchange_object = self.traderbot.exchanges.get(exchange_name.lower(), None)
        #raise SystemExit

    def run(self):
        logic_items = list(self.logic.items())
        for logic_name, logic_object in logic_items:
            if logic_object.killed():
                del self.logic[logic_name]

            now = time.time()
            if now-logic_object.lastrun < logic_object.interval:
                continue
            logic_object.lastrun = now
            logic_object.run()

###############################################################################

