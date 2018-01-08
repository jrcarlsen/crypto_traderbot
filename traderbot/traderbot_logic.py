################################################################################

import time

################################################################################

confidence_levels = {}

################################################################################

def execute(trade):
    if not trade.summary:
        return

    # Check if the coin is already sold
    if trade.data.get('sold', False):
        return

    if trade.high_diff() < -1.5:
        print "SOLD:", trade.get_currency(), trade.high_diff(), trade.summary['Bid'], trade.data.get('bid_high', None)
        trade.sell(trade.summary['Bid'], trade.data['amount'])

    return
