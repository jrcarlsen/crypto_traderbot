#!/usr/bin/env python
#
################################################################################

import os
import time
import pickle
import config

from traderbot_signal import Signal
from traderbot_commands import execute_command

################################################################################

class TraderBot:
    def __init__(self, config):
        self.config = config
        self.running = True # When set to False the bot will quit
        self.signals = {}
        self.servers = {}
        self.exchanges = {}
        self.logic = {}
        self.lastsave = 0

    ############################################################################
    
    def _load_signals(self):
        for signal_id in os.listdir(config.SIGNAL_PATH):
            # There may be other files than just the signals here, we only want
            # to load the files where the name can be converted to and integer.
            try:
                signal_id_int = int(signal_id)
            except ValueError:
                continue

            signal_data = pickle.load(open(config.SIGNAL_PATH+signal_id, 'rb'))
            signal = Signal(self, signal_id_int)
            signal.set_data(signal_data)
            self.signals[signal_id_int] = signal

    def _save_signals(self):
        for signal_id, signal_object in self.signals.items():
            data = signal_object.get_data()
            pickle.dump(data, open(config.SIGNAL_PATH+str(signal_id), 'wb'))

    def new_signal(self, newdata):
        signal = Signal(self)
        signal.data = {
            'id':           int(newdata['tradeid']),
            'created':      time.time(),
            'confidence':   int(newdata['confnumber']),
            'exchange':     newdata['exchange'].lower(),
            'currency':     newdata['currency'].upper(),
            'amount':       float(newdata['maxamount']),
        }
        signal.init()
        self.signals[signal.get_id()] = signal

    ############################################################################

    def execute_command(self, full_command):
        return execute_command(self, full_command)

    ############################################################################
 
    def register_server(self, server_module, config):
        server_object = server_module.Server(self, config)
        server_object.register_callback(self.execute_command)
        self.servers[server_object.name] = server_object

    def register_exchange(self, exchange_module, config):
        exchange_object = exchange_module.Exchange(self, config)
        self.exchanges[exchange_object.name.lower()] = exchange_object

    def register_logic(self, logic_module, config):
        """Register logic modules that will executed by Signals"""
        # The Logic will instantiated by the Signals
        self.logic[logic_module.uuid] = (logic_module, config)
 
    ############################################################################
    
    def run_signals(self, max_time=1):
        ts = time.time()
        for signal in self.signals.values():
            remaining_time = max_time-(time.time()-ts)
            if remaining_time < 0:
                break
            signal.run()

    def run_servers(self, max_time):
        # Split our available time evenly between the registered servers
        each_timeout = max_time/len(self.servers.keys())
        for server in self.servers.values():
            server.run(timeout=each_timeout)

    def run_exchanges(self):
        for exchange_name, exchange_object in self.exchanges.items():
            exchange_object.run()

    def run(self):
        # Start our timer and run through the exchange updates
        ts = time.time()
        self.run_exchanges()

        # Run our signals
        remaining_time = max(0, self.config.LOOP_DELAY-(time.time()-ts))
        self.run_signals(max_time=remaining_time)

        # Save every 5 seconds
        if time.time()-self.lastsave > 5:
            self.lastsave = time.time()
            self._save_signals()

        # Spend the rest of our loop time listening for commands
        remaining_time = max(0, self.config.LOOP_DELAY-(time.time()-ts))
        self.run_servers(max_time=remaining_time)

        return self.running

    def load(self):
        self._load_signals()

################################################################################
