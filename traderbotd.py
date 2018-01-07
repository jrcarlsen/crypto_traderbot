#!/usr/bin/env python
#
################################################################################

import time

import config
from bittrex import bittrex

################################################################################

class TraderBot:
    def __init__(self, api_key, api_secret):
        self.api = bittrex.Bittrex(api_key, api_secret)

    def run_once(self):
        print "BTC:", self.api.get_balance('BTC')['result']['Balance']

tb = TraderBot(config.API_KEY, config.API_SECRET)
while True:
    tb.run_once()
    time.sleep(5)

