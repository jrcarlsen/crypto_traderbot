# MODULES
## Logic modules

### Signal
#### signal.get_exchange(exchange_name, market))
Get an `Exchange` object so we can perform trades and track exchange rates.

 * exchange_name:   Name of the exchange. (case insensitve)
 * market:          Which market we wish to trade on.

The return value is an `Exchange` object, or `None` if the exchange or market is not supported.

Usage:
```python
exchange = signal.get_exchange('Bittrex', 'BTC-LTC')
```


#### signal.age()
The return value the time in seconds since the signal was created.

Usage:
```python
if signal.age() > 60:
    print "Signal was created more than 1 minute ago"
```


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


#### exchange.bought()
Get list of bought coins.

The return value is a list of `(amount, rate)`.

Usage:
```python
buys = exchange.bought()
for buy in buys:
    print amount, rate
```

#### exchange.sold()
Get list of sold coins
#### exchange.orderbook()
Get the current orderbook
#### exchange.openorders()
Get a list of the current open orders
#### exchange.diff_high()
The return value is the difference between the highest rate and the current rate in percent.
#### exchange.diff_buy()
The return value is the difference between the buy rate and the current rate in percent.

