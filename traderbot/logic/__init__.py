class LogicBase:
    # How often do we want run() to be called?
    interval = 5
    
    def __init__(self):
        self.data = {'market_data': {}}
        self.markets = {}
        self.killed = False
        self.lastrun = 0

    def description(self):
        return "<{name}>".format(**{
            'name': self.name,
        })

    def save(self):
        self.data['market_data'] = {}
        for market_name, market_object in self.markets.items():
            self.data['market_data'][market_name] = market_object.data

    def run(self):
        self._update_markets()

    def register_market(self, market_object, market_name='default'):
        if not market_object:
            return False
        self.markets[market_name] = market_object

    def _update_markets(self):
        for market_name, market_object in self.markets.items():
            market_object.run()
