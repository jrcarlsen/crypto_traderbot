#!/usr/bin/env python
#
################################################################################

import config

from traderbot.traderbot import TraderBot
from traderbot.logic import logic_simple
from traderbot.logic import logic_simple2
from traderbot.server import server_tcpserver
from traderbot.exchange import exchange_bittrex

################################################################################

traderbot = TraderBot(config)

# Register servers
traderbot.register_server(server_tcpserver, config.tcpserver)

# Register Exchanges
traderbot.register_exchange(exchange_bittrex, config.bittrex)

# Register Logic
traderbot.register_logic(logic_simple.Logic, config.logic)
traderbot.register_logic(logic_simple2.Logic, config.logic)

# Load data from disk
traderbot.load()

# Run the traderbot loop until it wants to quit
while True:
    if not traderbot.run():
        raise SystemExit
   
################################################################################

