# MODULES
## Logic

### Signal
#### get_exchange()
```python
exchange = signal.get_exchange(exchange, market)
```
Returns an Exchange object, or False if the market or Exchange is not supported.
#### age()
How many seconds since the signal was generated.

### Exchange
#### buy()
```python
rate, amount = exchange.buy(amount, rate)
```
Returns the traded rate and amount

#### sell()
Try to sell on the exchange.
```python
rate, amount = exchange.sell(amount, rate)
```
Returns the traded rate and amount

```

#### bought()
Get list of bought coins
#### sold()
Get list of sold coins
#### orderbook()
Get the current orderbook
#### openorders()
Get a list of the current open orders
