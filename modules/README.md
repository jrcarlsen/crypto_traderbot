# MODULES
## Logic modules

### Signal
#### get_exchange(exchange_name, market))
Returns an Exchange object, or False if the market or Exchange is not supported.
```python
exchange = signal.get_exchange('Bittrex', 'BTC-LTC')
```
#### age()
How many seconds since the signal was generated.

### Exchange
#### exchange**.buy**(amount, rate=None)
Returns True if the trade went through. If a rate it 
```python
rate, amount = exchange.buy(0.00021, rate)
```

#### exchange.**sell(amount=None, rate=None)**
Try to sell on the exchange. If amount is not supplied, it will try and sell 
all. If rate is not supplied it will try and sell at the current rate.
```python
rate, amount = exchange.sell(amount, rate)
```
Returns the traded rate and amount


#### exchange.bought()
Get list of bought coins
#### exchange.sold()
Get list of sold coins
#### exchange.orderbook()
Get the current orderbook
#### exchange.**openorders**()
Get a list of the current open orders
