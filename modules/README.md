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
#### exchange.buy(amount, rate=None)
Try to buy on the exchange.
 * amount:  the amount of coins to try and buy.
 * rate:    if provided, the rate to try and buy the coins at, or if not provided buy at the current rate.
The return value is `True` if the order was atleast partially completed, otherwise `False` is returned.
Usage:
```python
if exchange.buy(amount=0.20, rate=0.80):
    print "success"
```

#### exchange.sell(amount=None, rate=None)
Try to sell on the exchange. 
 * amount:  if provided, the amount of coins to try and sell, or if not provided try to sell all coins.
 * rate:    if provided, the rate to try and sell the coins at, or if not provided sell at the current rate.
The return value is `True` if the order was atleast partially completed, otherwise `False` is returned. 
Usage:
```python
if exchange.sell(amount=0.16, rate=0.88):
    print "success"
```
Returns the traded rate and amount


#### exchange.bought()
Get list of bought coins
#### exchange.sold()
Get list of sold coins
#### exchange.orderbook()
Get the current orderbook
#### exchange.openorders()
Get a list of the current open orders
