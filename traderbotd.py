#!/usr/bin/env python
#
################################################################################

import time

import config
from traderbot import tcpserver
from traderbot import traderbot

################################################################################

trader     = traderbot.TraderBot(config.API_KEY, config.API_SECRET)
tcpserver  = tcpserver.TCPServer(port=config.TCP_PORT)
tcpserver.callback = trader.execute_command

ts = time.time()
while True:
    elapsed_time = time.time()-ts
    tcpserver.run(timeout=config.LOOP_DELAY-elapsed_time)
    
    elapsed_time = time.time()-ts
    if elapsed_time < config.LOOP_DELAY:
        continue

    trader.run()
    ts = time.time()

################################################################################

