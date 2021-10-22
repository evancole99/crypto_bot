# Crypto trade bot
# Specify API keys in file config.py
# Ensure your API keys are kept secret!

import websocket, json, pprint, talib, numpy
import sys
import config, strategies
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(config.TRADE_SYMBOL,config.KLINE_INTERVAL)

closes = []

in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

strategy = None

# determine bot strategy
n = len(sys.argv)
if (n != 2):
    print("Error: Wrong command line arguments provided.")
    exit(1)
else:
    s = argv[1]
    if s not in strategies.STRATEGY_LIST:
        print("Error: Invalid strategy selected.")
        exit(1)
    if s == "RSI":
        strategy = strategies.RSI_strategy()
    elif s == "BBANDS":
        strategy = strategies.BB_strategy()
    else:
        print("Error")
        exit(1)


def order(symbol, side, quantity, order_type=Client.ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        # CREATE TEST ORDER
        order = client.create_order(symbol=symbol,side=side,type=order_type,quantity=quantity)
        print(order)
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
    global in_position # ensure function knows variable should be referenced globally
    print("message received")
    json_msg = json.loads(message)
    # pprint.pprint(json_msg)

    candle = json_msg['k']
    is_closed = candle['x']
    close = candle['c']

    if is_closed:
        # print("Candle closed at {}".format(close))
        closes.append(float(close))
        # print("Num of closes so far: {}".format(len(closes)))

        if len(closes) > strategy_interval:

            np_closes = numpy.array(closes)

            signal = strategies.generate_signal(strategy)

            if signal == "SELL":
                print("SELL SIGNAL RECEIVED")
                
                if in_position:
                    print("PLACING SELL ORDER")
                    # binance sell order
                    order_success = order(TRADE_SYMBOL, Client.SIDE_SELL, TRADE_QUANTITY, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        in_position = False
                
                else:
                    print("Not in position. Nothing to do.")

            elif signal == "BUY":
                print("BUY SIGNAL RECEIVED")
                if in_position:
                    print("Already in position. Nothing to do.")
                
                else:
                    print("PLACING BUY ORDER")
                    # binance buy order
                    order_success = order(TRADE_SYMBOL, Client.SIDE_BUY, TRADE_QUANTITY, Client.ORDER_TYPE_MARKET)
                    
                    if order_success:
                        in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever(ping_interval=300)


