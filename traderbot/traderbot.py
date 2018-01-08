#!/usr/bin/env python
#
################################################################################

import os
import time
import pickle

from bittrex import bittrex
import traderbot_commands
import traderbot_logic

################################################################################

TRADE_PATH="data/"

################################################################################

class Trade:
    def __init__(self, traderbot):
        self.tb = traderbot
        self.data = None
        self.summary = None
        self.summary_age = 0

    def __repr__(self):
        if not self.summary:
            return "<Trade id='%s' currency='%s'>" % (self.get_id(), self.data.get('currency', '-'))
        return "<Trade id='%i' currency='%s' buy='%0.8f' bid_current='%0.8f' bid_high='%f' buy_diff='%0.2f' high_diff='%0.2f' best='%0.2f' profit='%s'>" % (
                self.get_id(), self.data.get('currency', '-'), self.data.get('buy', 0), self.current_bid(), self.data['bid_high'], self.buy_diff(), 
                self.high_diff(), self.best_diff(), self.get_profit())
    
    def _update_summary(self):
        if time.time() - self.summary_age < 15: # FIXME: Poll delay configured here
            return False
        self.summary_age = time.time()

        result = self.tb.api.get_marketsummary('BTC-%s' % self.get_currency())
        if not result.has_key('success'):
            print self.get_id(), "bt req failed"
            return False
        if result['success'] != True:
            print self.get_id(), "bt req failed, not success"
            self.summary_age = time.time()+300 # Retry in 5 minutes
            return False
        self.summary = result['result'][0]
        self._update_data()

    def _update_data(self):
        self.data['bid_high'] = max(self.current_bid(), self.data.get('bid_high', 0))
        # FIXME: FAKE BUY
        if not self.data.has_key('buy'):
            self.data['buy'] = self.current_bid()
        self.save()

    def get_id(self):
        return self.data.get('id', -1)

    def get_profit(self):
        sold_rate = self.data.get('sold', False)
        if not sold_rate:
            return None
        bought_rate = self.data.get('buy', False)
        if not bought_rate:
            return None
        return (sold_rate/bought_rate*100)-100

    def filename(self, tradeid):
        return '%s/%s' % (TRADE_PATH, tradeid)

    def load(self, tradeid=None):
        if tradeid:
            filename = self.filename(tradeid)
        else:
            filename = self.filename(self.get_id())

        self.data = pickle.load(open(filename, 'rb'))
        print "Loaded data for:", self.data['currency']

    def save(self):
        filename = self.filename(self.get_id())
        pickle.dump(self.data, open(filename, 'wb'))

    def buy_diff(self):
        """Difference in percent from the buying price"""
        return (self.current_bid()/self.data['buy']*100)-100

    def high_diff(self):
        """Difference in percent from the highest bid we've seen"""
        return (self.current_bid()/self.data['bid_high']*100)-100

    def best_diff(self):
        return (self.data['bid_high']/self.data['buy']*100)-100

    def get_currency(self):
        if not self.data:
            return None
        return self.data['currency']

    def current_bid(self):
        return self.summary.get('Bid', None)

    def buy(self, rate, amount):
#        print "BTC:", self.api.get_balance('BTC')['result']['Balance']
        return False

    def sell(self, rate, amount):
        self.data['sold'] = rate
        return False

    def update(self):
        return self._update_summary()

    def run(self):
        traderbot_logic.execute(self)

################################################################################

class TraderBot:
    def __init__(self, api_key, api_secret):
        self.api = bittrex.Bittrex(api_key, api_secret)
        self.trades = {}
        self._load_trades()

    def _load_trades(self):
        for tradeid in os.listdir(TRADE_PATH):
            if tradeid[0] == '.':
                continue

            t = Trade(self)
            t.load(tradeid)
            self.trades[tradeid] = t

    def status(self):
        tradeids = self.trades.keys()
        tradeids.sort()
        print "Tracked coins:"
        for tradeid in tradeids:
            print self.trades[tradeid]
        print

    def execute_command(self, line):
        if not line:
            return "" # FIXME: Should be \n only

        if line[0] == '{':
            line = "json "+line 

        cmd = line.split(' ', 1)[0]
        if traderbot_commands.commands.has_key(cmd):
            try:
                return traderbot_commands.commands[cmd](self, line)
            except Exception as e:
                print e
                return "Error: Command did not execute correctly.\n"
        else:
            return "Error: Bad command.\n"

    def new_trade(self, newdata):
        t = Trade(self)
        t.data = {
            'id': int(newdata['tradeid']),
            'created': time.time(),
            'confidence': int(newdata['confnumber']),
            'exchange': newdata['exchange'].lower(),
            'currency': newdata['currency'],
            'amount':   float(newdata['maxamount']),
        }
        t.save()
        self.trades[t.get_id()] = t

    def run(self, timeout=1):
        ts = time.time()
        for trade in self.trades.values():
            if time.time()-ts > timeout:
                break
            trade.update()

        for trade in self.trades.values():
            trade.run()

################################################################################
