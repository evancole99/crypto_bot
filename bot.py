# Crypto trade bot
# Specify API keys in file config.py
# Strategies can be customized in strategies.py
# Ensure your API keys are kept secret!

import websocket, json, requests, talib, numpy, time
import sys
import config, strategies
from binance.client import Client
from binance.enums import *

# All symbols for Binance webstreams are lowercase
symbol_lower = strategies.TRADE_SYMBOL.lower()

SOCKET = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(symbol_lower,strategies.KLINE_INTERVAL)

closes = []
highs = []
lows = []

open_positions = []

client = Client(config.API_KEY, config.API_SECRET, tld='us')

strategy = None

# determine bot strategy
n = len(sys.argv)
if (n != 2):
    print("Error: Wrong command line arguments provided.")
    exit(1)
else:
    s = sys.argv[1]
    if s not in strategies.STRATEGY_LIST:
        print("Error: Invalid strategy selected.")
        exit(1)
    if s == "RSI":
        strategy = strategies.RSI()

    elif s == "BBANDS":
        print("Bollinger Bands strategy selected")
        strategy = strategies.BBANDS()

    elif s == "BBANDS_REVERSION":
        print("Bollinger Bands Reversion strategy selected")
        strategy = strategies.BBANDS_REVERSION()

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
    global open_positions

    try:
        print("Sending order")
        # CREATE ORDER
        order_data = client.create_order(symbol=symbol,side=side,type=order_type,quantity=quantity)

        filled = order_data['fills']
        price = filled[0]['price']
        
        if side == Client.SIDE_BUY:
            open_positions.append(float(price))
        elif side == Client.SIDE_SELL:
            entry = open_positions.pop(len(open_positions) - 1)

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
    global open_positions
    # print("message received")
    json_msg = json.loads(message)

    candle = json_msg['k']
    is_closed = candle['x']
    close = candle['c']
    high = candle['h']
    low = candle['l']

    if is_closed:

        print("Candle closed at {}".format(close))
        closes.append(float(close))
        highs.append(float(high))
        lows.append(float(low))
        # print("Num of closes so far: {}".format(len(closes)))

        if len(closes) > strategy_interval: 

            np_closes = numpy.array(closes)
            signal = strategy.signal(np_closes, highs, lows)

            if signal == "SELL":
                print("SELL SIGNAL RECEIVED")
                
                if open_positions:

                    # Sell all open positions 
                    print("PLACING SELL ORDER")

                    # binance sell order
                    # subtract binance's 0.1% spot trading fee
                    commission = strategies.TRADE_QUANTITY * 0.001
                    sellQty = (strategies.TRADE_QUANTITY - commission) * len(open_positions)
                    order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_SELL, sellQty, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        print("ORDER SUCCESS")
                
                else:
                    print("Not in position. Nothing to do.")

            elif signal == "BUY":
                print("BUY SIGNAL RECEIVED")

                if len(open_positions) >= strategies.POSITIONS_ALLOWED:
                    print("Already in position. Nothing to do.")
                
                else:
                    print("PLACING BUY ORDER")
                    # binance buy order
                    order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_BUY, strategies.TRADE_QUANTITY, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        print("ORDER SUCCESS")


# Uncomment this line to view verbose connection information
# websocket.enableTrace(True)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever(ping_interval=300)


