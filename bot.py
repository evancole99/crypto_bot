
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



