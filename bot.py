# Crypto trade bot
# Specify API keys in file config.py
# Strategies can be customized in strategies.py
# Ensure your API keys are kept secret!

import websocket, json, requests, talib, numpy, time
import sys
import config, strategies
from binance.client import Client
from binance.enums import *

# TODO:
# Ensure bot CONVERTS ALL HOLDINGS TO USDT when termination signal is given
# Stop loss (trailing stop %, stop % below entry)


# All symbols for Binance webstreams are lowercase
symbol_lower = strategies.TRADE_SYMBOL.lower()

SOCKET = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(symbol_lower,strategies.KLINE_INTERVAL)


closes = []

open_positions = []
account_balance = strategies.INVESTMENT_AMOUNT

client = Client(config.API_KEY, config.API_SECRET, tld='us')

strategy = None

# determine bot strategy

n = len(sys.argv)
s = sys.argv[1]

# initialize full list of parameters from command line args
params = []
for x in range(2, n):
    val = sys.argv[x]
    if (float(val) != 0):
        params.append(float(val))


if s not in strategies.STRATEGY_LIST:
    print("Error: Invalid strategy selected.")
    exit(1)
if s == "RSI":
    strategy = strategies.RSI(*params)

elif s == "BBANDS":
    print("Bollinger Bands strategy selected")
    strategy = strategies.BBANDS(*params)

elif s == "BBANDS_REVERSION":
    print("Bollinger Bands Reversion strategy selected")
    strategy = strategies.BBANDS_REVERSION(*params)

else:
    print("Error")
    exit(1)

strategy_interval = strategy.get_interval()
# print("Interval: {}".format(strategy_interval))

def notify_user(order_type, symbol, price, qty):
    report = {}
    report["order_type"] = order_type
    report["symbol"] = symbol
    report["price"] = price
    report["qty"] = qty
    response = requests.post(config.IFTTT_WEBHOOK, json=report, headers={'Content-Type': 'application/json'})
    
    if response.status_code != 200:
        raise ValueError(
                'Request to IFTTT webhook returned error %s.\nThe response:\n%s' % (response.status_code, response.text))

def order(symbol, side, quantity, order_type=Client.ORDER_TYPE_MARKET):
    global open_positions, account_balance

    try:
        print("Sending order")
        # CREATE ORDER
        order_data = client.create_order(symbol=symbol,side=side,type=order_type,quantity=quantity)

        filled = order_data['fills']
        price = filled[0]['price']
        qty = filled[0]['qty']
        comm = filled[0]['commission']
        amtTraded = float(price) * float(qty)
        qty = float(qty) - float(comm)

        if side == Client.SIDE_BUY:
            candleID = len(candles)-1
            open_positions.append((float(price), qty, candleID))
            account_balance -= amtTraded
        elif side == Client.SIDE_SELL:
            amtTraded = float(price) * qty # update amtTraded to account for commission
            account_balance += amtTraded

        # Send notification
        notify_user(side, symbol, price, quantity)

    except Exception as e:
        print("Order error: Exception occurred.")
        print(e)
        return False

    return True

def on_open(ws):
    print("connection opened")

def on_close(ws):
    print("connection closed")

def on_message(ws, message):
    global open_positions, account_balance
    
    json_msg = json.loads(message)

    candle = json_msg['k']
    is_closed = candle['x']
    openPrice = candle['o']
    close = candle['c']
    high = candle['h']
    low = candle['l']
    closeTime = candle['T']
    vol = candle['v']

    if is_closed:

        print("Candle closed at {}".format(close))
        # Initialize new dictionary for candle and add to list of closes
        candleDict = dict('open': float(openPrice), 'close': float(close), 'high': float(high), 'low': float(low), 'vol': float(vol), 'time': closeTime)
        closes.append(candleDict)

        if len(closes) > strategy_interval: 

            if strategies.SL_ENABLED:
                # Check if stop loss hit
                sl_id = strategies.stop_loss(float(close), candles, open_positions)

                if sl_id >= 0:
                    print("{} STOP LOSS TRIGGERED".format(strategies.SL_TYPE))
                    sellQty = open_positions[sl_id][1]
                    print("SELLING {} {}, ENTRY {}".format(sellQty, strategies.TRADE_SYMBOL, open_positions[sl_id][0]))
                    order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_SELL, sellQty, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        print("ORDER SUCCESS")
                        open_positions.pop(sl_id)


            signal = strategy.signal(closes)

            if signal == "SELL":
                print("SELL SIGNAL RECEIVED")
                
                if open_positions:

                    # Sell all open positions 
                    print("PLACING SELL ORDER")

                    sellQty = sum(q for p, q, i in open_positions)
                    order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_SELL, sellQty, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        print("ORDER SUCCESS")
                        open_positions = []
                
                else:
                    print("Not in position. Nothing to do.")

            elif signal == "BUY":
                print("BUY SIGNAL RECEIVED")

                if len(open_positions) >= strategies.POSITIONS_ALLOWED:
                    print("Already in position. Nothing to do.")
                
                else:
                    spendAmt = float(close) * strategies.TRADE_QUANTITY

                    if spendAmt <= account_balance:
                        print("PLACING BUY ORDER")
                        # binance buy order
                        order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_BUY, strategies.TRADE_QUANTITY, Client.ORDER_TYPE_MARKET)
                        
                        if order_success:
                            print("ORDER SUCCESS")


# Uncomment this line to view verbose connection information
# websocket.enableTrace(True)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever(ping_interval=300)


