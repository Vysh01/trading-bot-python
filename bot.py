from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.stream import TradingStream
# from alpaca.data.historical import StockHistoricalDataClient
# from alpaca.data.requests import StockBarsRequest
# from alpaca.data.timeframe import TimeFrame
import alpaca_trade_api as tradeapi
# import datetime
# import pytz
import config
import numpy as np
import time


pos_held = False
symbol="SPY"

client = TradingClient(config.KEY, config.SECRET, paper=True)
# account = dict(client.get_account())
# for k, v in account.items():
#     print(f"{k:30}{v}")
#order_details = MarketOrderRequest(symbol=symbol, qty=10,side = OrderSide.BUY, time_in_force=TimeInForce.DAY)
#order = client.submit_order(order_data=order_details)
#trades = TradingStream(config.KEY, config.SECRET, paper=True)

# async def trade_status(data):
#     print(data)

#trades.subscribe_trade_updates(trade_status)
#trades.run()


#NEW SDK, DOESN'T ALLOW GETTING DATA FROM LAST 15 MINUTES
# bar_req = StockBarsRequest(symbol_or_symbols=[symbol], start=datetime.datetime.now(pytz.utc), timeframe=TimeFrame.Minute)
# client = StockHistoricalDataClient(secret_key=config.SECRET, api_key=config.KEY)
# market_data = client.get_stock_bars(bar_req)
# print(market_data)

api = tradeapi.REST(key_id=config.KEY, secret_key=config.SECRET)

market_data = api.get_bars(symbol, tradeapi.TimeFrame.Minute).df
#print(market_data.shape[0])
# Get close list of the last 5 data points
close_list  = market_data.tail(5)['close'].values
close_list = np.array(close_list, dtype=np.float64) # Convert to numpy array
ma = np.mean(close_list)
last_price = close_list[4] # Most recent closing price
print(market_data)
print(close_list)
print("Moving Average: " + str(ma))
print("Last Price: " + str(last_price))


while True:
    if ma + 0.1 < last_price and not pos_held: # If MA is more than 10 cents under price, and we haven't already bought
            print("Buy")
            api.submit_order(
                symbol=symbol,
                qty=1,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            pos_held = True
    elif ma - 0.1 > last_price and pos_held: # If MA is more than 10 cents above price, and we already bought
            print("Sell")
            api.submit_order(
                symbol=symbol,
                qty=1,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            pos_held = False
    time.sleep(60)