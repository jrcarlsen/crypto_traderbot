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
        traderbot.new_signal(jsondict)
    except Exception as e:
        raise 
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

################################################################################

def cmd_list_exchanges(traderbot, cmd_line):
    return `traderbot.exchanges`+'\n'

def cmd_list_signals(traderbot, cmd_line):
    result = []
    for signal_name, signal_object in traderbot.signals.items():
        result.append(signal_object.description())
        for logic_uuid, logic_object in signal_object.logic.items():
            result.append("  "+logic_object.description())
            for market_name, market_object in logic_object.markets.items():
                result.append("    "+market_object.description())
    return '\n'.join(result)+"\n"

def cmd_list_logic(traderbot, cmd_line):
    args = cmd_line.split(' ', 1)
    if len(args) < 2:
        return "usage: logic <name>\n"
    search_name = args[1]

    result = []
    for signal_name, signal_object in traderbot.signals.items():
        for logic_uuid, logic_object in signal_object.logic.items():
            if logic_object.name == search_name:
                result.append(signal_object.description())
                result.append("  "+logic_object.description())
    return '\n'.join(result)+"\n"

def cmd_list_servers(traderbot, cmd_line):
    return `traderbot.servers`+'\n'

################################################################################

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
    'json':         json_command,
    'exchanges':    cmd_list_exchanges,
    'signals':      cmd_list_signals,
    'servers':      cmd_list_servers,
    'logic':        cmd_list_logic,
    'list':         cmd_list_active,
    'active':       cmd_list_active,
    'sold':         cmd_list_sold,
    'invalid':      cmd_list_invalid,
    'stop':         cmd_stop,
    '':             cmd_noop,
}

################################################################################

def execute_command(traderbot, full_command):
    # Return if we got no command to execute
    if not full_command:
        return ""

    # JSON commands starts with "{"
    if full_command[0] == '{':
        full_command = "json "+full_command

    command = full_command.split(' ', 1)[0]
    if commands.has_key(command):
        try:
            return commands[command](traderbot, full_command)
        except Exception as e:
            print "COMMAND EXCEPTION:", command
            print e
            raise
            return "Error: Command did not execute correctly.\n"
    return "Error: Bad command.\n"

################################################################################
