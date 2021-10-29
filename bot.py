# Crypto trade bot
# Specify API keys in file config.py
# Strategies can be customized in strategies.py
# Ensure your API keys are kept secret!

import websocket, json, pprint, talib, numpy, time
import sys
import config, strategies
from binance.client import Client
from binance.enums import *

# All symbols for Binance webstreams are lowercase
symbol_lower = strategies.TRADE_SYMBOL.lower()

SOCKET = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(symbol_lower,strategies.KLINE_INTERVAL)
logfile = "log.txt"

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
print("Interval: {}".format(strategy_interval))

def order(symbol, side, quantity, order_type=Client.ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        # CREATE ORDER
        order = client.create_order(symbol=symbol,side=side,type=order_type,quantity=quantity)

        json_msg = json.loads(order)
        pprint.pprint(json_msg)
        filled = json_msg['fills']
        price = filled['price']

        if side == Client.SIDE_BUY:
            open_positions.append(price)
        elif side == Client.SIDE_SELL:
            entry = open_positions.pop(len(open_positions) - 1)
            profit = (price * quantity) - (entry * quantity)
            print("Trade executed for profit of {}".format(profit))
            f = open(logfile, "a")
            # write to log file: bot type, timestamp, profit
            writestr = "{} {} {}".format(s, time.time(), profit)
            f.write(writestr)
            f.close()


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
    # print("message received")
    json_msg = json.loads(message)
    # pprint.pprint(json_msg)

    candle = json_msg['k']
    is_closed = candle['x']
    close = candle['c']
    high = candle['h']
    low = candle['l']

    if is_closed:

        # print("Candle closed at {}".format(close))
        closes.append(float(close))
        highs.append(float(high))
        lows.append(float(low))
        # print("Num of closes so far: {}".format(len(closes)))

        if len(closes) >= strategy_interval:

            # Keep only the necessary number of closes to calculate our indicators
            # I believe the lists becoming too long was causing the script to quit prematurely
            closes = closes[-strategy_interval:]
            highs = highs[-strategy_interval:]
            lows = lows[-strategy_interval:]

            np_closes = numpy.array(closes)
            signal = strategy.signal(np_closes, highs, lows)

            if signal == "SELL":
                print("SELL SIGNAL RECEIVED")
                
                if open_positions:
                    for i in open_positions:
                        print("PLACING SELL ORDER")
                        # binance sell order
                        # subtract binance's 0.1% spot trading fee
                        commission = strategies.TRADE_QUANTITY * 0.001
                        order_success = order(strategies.TRADE_SYMBOL, Client.SIDE_SELL, strategies.TRADE_QUANTITY - commission, Client.ORDER_TYPE_MARKET)
                        
                        if order_success:
                            print("ORDER SUCCESS")
                
                else:
                    print("Not in position. Nothing to do.")

            elif signal == "BUY":
                print("BUY SIGNAL RECEIVED")
                if len(open_positions) > strategies.POSITIONS_ALLOWED:
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


