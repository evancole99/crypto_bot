import talib, numpy

# STRATEGY SELECTOR
# All currently implemented strategies
# To select a strategy, provide one of the strategies from the list below as a command line argument when running the Python script.
# Example: python3 bot.py RSI
STRATEGY_LIST = ["RSI", "BBANDS"] # list of all currently implemented strategies

# Bot configuration
<<<<<<< HEAD
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.005
KLINE_INTERVAL = '1m'
=======
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.01
KLINE_INTERVAL = '3m'
>>>>>>> 1268adf91165d2538096e0c5d3e14411fb1479c2


# RSI config

class RSI_strategy:
    def __init__(self, RSI_PERIOD=14, RSI_OVERBOUGHT=70.0, RSI_OVERSOLD=30.0):
        self.RSI_PERIOD = RSI_PERIOD
        self.RSI_OVERBOUGHT = RSI_OVERBOUGHT
        self.RSI_OVERSOLD = RSI_OVERSOLD

<<<<<<< HEAD
=======
    def get_interval(self):
        return self.RSI_PERIOD

>>>>>>> 1268adf91165d2538096e0c5d3e14411fb1479c2
    def signal(self,closes):
        rsi = talib.RSI(closes, self.RSI_PERIOD)
        rsi = rsi[14:]
        # print("All RSI values so far:")
        # print(rsi)
        last_rsi = rsi[-1]
        print("Current RSI is {}".format(last_rsi))

        if last_rsi > self.RSI_OVERBOUGHT:
            return "SELL"
        elif last_rsi < self.RSI_OVERSOLD:
            return "BUY"
        else:
            return None

# Bollinger Bands config

class BB_strategy:
    
    def __init__(self, BBANDS_PERIOD=20):
        self.BBANDS_PERIOD = BBANDS_PERIOD

<<<<<<< HEAD
    def signal(self,closes):
        upper, middle, lower = talib.BBANDS(closes, timeperiod=self.BBANDS_PERIOD, matype=0)
        upper = upper[-1]
        middle = middle[-1]
        lower = lower[-1]
        arrLen = len(closes)
        currPrice = closes[arrLen-1]
        print("Current BBands: UPPER {}, MIDDLE {}, LOWER {}".format(upper, middle, lower))
        print("Current close: {}".format(currPrice))
        if currPrice < lower:
            return "BUY"
        elif currPrice > upper:
=======
    def get_interval(self):
       return self.BBANDS_PERIOD

    def signal(self,closes):
        upper, middle, lower = talib.BBANDS(closes, timeperiod=self.BBANDS_PERIOD, matype=0)
        u = upper[-1]
        m = middle[-1]
        l = lower[-1]
        arrLen = len(closes)
        currPrice = closes[arrLen-1]
        print("Current BBands: UPPER {}, MIDDLE {}, LOWER {}".format(u, m, l))
        print("Current close: {}".format(currPrice))
        if currPrice < l:
            return "BUY"
        elif currPrice > u:
>>>>>>> 1268adf91165d2538096e0c5d3e14411fb1479c2
            return "SELL"
        else:
            return None

<<<<<<< HEAD

def get_interval(strategy):
    if strategy == "RSI":
        return RSI_strategy.RSI_PERIOD
    elif strategy == "BBANDS":
        return BB_strategy.BBANDS_PERIOD

def generate_signal(strategy, closes):
    if strategy == "RSI":
        return RSI_strategy.signal(closes)
    elif strategy == "BBANDS":
        return BB_strategy.signal(closes)
    else:
        return None

=======
>>>>>>> 1268adf91165d2538096e0c5d3e14411fb1479c2
