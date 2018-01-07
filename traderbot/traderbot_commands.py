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

def cmd_list(traderbot, line):
    tradelist = list()
    tradeids = traderbot.trades.keys()
    tradeids.sort()
    print tradeids

    for tradeid in tradeids:
        print tradeid
        tradelist.append(str(traderbot.trades[tradeid]))

    result = "\n".join(tradelist)
    return result+"\n"

################################################################################

commands = {
    'json': json_command,
    'list': cmd_list,
    'stop': cmd_stop,
    '': cmd_noop,
}

################################################################################

# {"tradeid":208,"currency":"OMG","exchange":"HitBTC","confnumber":1,"maxamount":0.123,"command":"trade"}

