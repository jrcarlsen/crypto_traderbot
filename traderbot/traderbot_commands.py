################################################################################

import json

################################################################################

def json_command(traderbot, line):
    jsondata = line.split(' ',1)[1]
    try:
        jsondict = json.loads(jsondata)
    except Exception as e:
        return '{"success": false, "reason": "failed to parse json"}\n'

    if not jsondict.get('command') == 'trade':
        return '{"success": false, "reason": "bad commands"}\n'

    try:
        traderbot.new_trade(jsondict)
    except Exception as e:
        return '{"success": false, "reason": "exception in code: `%s`"}\n' % e

    return '{"success": true}\n'

def cmd_noop(traderbot, line):
    return "\n"

def cmd_stop(traderbot, line):
    raise SystemExit

def cmd_list_invalid(traderbot, line):
    return func_list(traderbot, show='invalid')

def cmd_list_sold(traderbot, line):
    return func_list(traderbot, show='sold')

def cmd_list_active(traderbot, line):
    return func_list(traderbot, show='active')

def func_list(traderbot, show):
    tradelist = list()
    tradeids = traderbot.trades.keys()
    #tradeids = [int(x) for x in tradeids]
    tradeids.sort()

    for tradeid in tradeids:
        trade = traderbot.trades[tradeid]
        if trade.data.get('sold', False):
            ttype = 'sold'
        else:
            ttype = 'active'

        if not trade.summary:
            ttype = 'invalid'

        #  tradelist.append('[31m'+str(trade)+'[0m')
        if ttype == show:
            tradelist.append(str(trade))

    result = "\n".join(tradelist)
    return result+"\n"

################################################################################

commands = {
    'json': json_command,
    'list': cmd_list_active,
    'active': cmd_list_active,
    'sold': cmd_list_sold,
    'invalid': cmd_list_invalid,
    'stop': cmd_stop,
    '': cmd_noop,
}

################################################################################

# {"tradeid":208,"currency":"OMG","exchange":"HitBTC","confnumber":1,"maxamount":0.123,"command":"trade"}

