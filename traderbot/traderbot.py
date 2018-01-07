#!/usr/bin/env python
#
################################################################################

import os
import time
import pickle

from bittrex import bittrex

################################################################################

TRADE_PATH="data/"

################################################################################

class Trade:
    def __init__(self, traderbot):
        self.tb = traderbot
        self.data = None
        self.summary = None

    def __repr__(self):
        return "<Trade currency='%s' buy='%s' bid_current='%s' bid_high='%s' buy_diff='%s' high_diff='%s'>" % (
                self.get_currency(), self.data.get('buy', 0), self.current_bid(), self.data['bid_high'], self.buy_diff(), self.high_diff())
    
    def _update_summary(self):
        result = self.tb.api.get_marketsummary('BTC-%s' % self.get_currency())
        if not result.has_key('success'):
            return False
        if result['success'] != True:
            return False
        self.summary = result['result'][0]
        self._update_data()

    def _update_data(self):
        self.data['bid_high'] = max(self.current_bid(), self.data.get('bid_high', 0))
        # FIXME: FAKE BUY
        if not self.data.has_key('buy'):
            self.data['buy'] = self.current_bid()
        self.save()

    def load(self, filename):
        self.filename = filename
        self.data = pickle.load(open(self.filename, 'rb'))
        print "Loaded data for:", self.data['currency']

    def save(self):
        pickle.dump(self.data, open(self.filename, 'wb'))

    def buy_diff(self):
        """Difference in percent from the buying price"""
        return (self.current_bid()/self.data['buy']*100)-100

    def high_diff(self):
        """Difference in percent from the highest bid we've seen"""
        return (self.current_bid()/self.data['bid_high']*100)-100

    def get_currency(self):
        if not self.data:
            return None
        return self.data['currency']

    def current_bid(self):
        return self.summary['Bid']

    def run(self):
        self._update_summary()


################################################################################

class TraderBot:
    def __init__(self, api_key, api_secret):
        self.api = bittrex.Bittrex(api_key, api_secret)
        self.trades = {}
        self._load_trades()

    def _load_trades(self):
        for filename in os.listdir(TRADE_PATH):
            if filename[0] == '.':
                continue

            t = Trade(self)
            t.load(TRADE_PATH+filename)
            self.trades[t.get_currency()] = t

    def run(self):
#        print "BTC:", self.api.get_balance('BTC')['result']['Balance']
        for trade in self.trades.values():
            trade.run()

    def status(self):
        currencies = self.trades.keys()
        currencies.sort()
        print "Tracked coins:"
        for currency in currencies:
            print self.trades[currency]
        print

    def execute_command(self, command):
        print "execute", command
        return "{'success': true}\n"

################################################################################
