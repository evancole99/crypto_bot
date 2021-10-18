import websocket, json, pprint, talib, numpy

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

closes = [3868.2, 3866.1, 3860.0, 3862.56, 3860.1, 3861.1, 3859.0, 3856.2, 3854.51, 3851.0, 3845.6, 3843.2, 3841.0, 3839.65, 3839.88]

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.005

def on_open(ws):
    print("connection opened")

def on_close(ws):
    print("connection closed")

def on_message(ws, message):
    print("message received")
    json_msg = json.loads(message)
    # pprint.pprint(json_msg)

    candle = json_msg['k']
    is_closed = candle['x']
    close = candle['c']

    if is_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("Num of closes so far: {}".format(len(closes)))
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All RSI values so far:")
            print(rsi)
            last_rsi = rsi[-1]
            print("Current RSI is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                print("OVERBOUGHT SIGNAL: SELL")
            if last_rsi < RSI_OVERSOLD:
                print("OVERSOLD SIGNAL: BUY")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)

ws.run_forever()

# Crypto trading bot

# Get kline data from Binance streams
    # look for end of candle, add to array of candles
# apply technical indicator (rsi? macd? research further)
# generate buy/sell signal
# Send purchase or sell request to Binance broker

# Things we want to track in a database:
# Orders placed by bot
    # Primary key OrderID - int
    # Coin name - string
    # Order type (BUY/SELL) - string
    # Timestamp (utc?) - datetime/string
    # Price - float
    # Foreign key SignalID - int (reference to signal that produced this order)
    # Foreign key BotID - int (reference to bot)
# Signals produced by bot
    # Primary key SignalID - int
    # Coin name - string
    # Indicator - string (which strategy? RSI/MACD/etc)
    # Signal type - string (BUY/SELL)
    # Signal threshold - float (value of indicator e.g. rsi=70.0)
    # Timestamp (utc?) - datetime/string
# Bots
    # Primary key BotID - int
    # Indicator - string (strategy of bot)
    # Settings - research further into this
    # Balance - float (bots current USD balance)
    # Profit - float (tracks all time p/l of bot)



