import talib, numpy

# STRATEGY SELECTOR
# All currently implemented strategies
# To select a strategy, provide one of the strategies from the list below as a command line argument when running the Python script.
# Example: python3 bot.py RSI


# == STRATEGIES ==
# List of all currently implemented strategies
# Ensure they are entered EXACTLY as shown as command line arguments
STRATEGY_LIST = ["RSI", "BBANDS", "BBANDS_REVERSION"]

# Bot configuration
TRADE_SYMBOL = 'ETHUSDT' # trade symbol (MAKE SURE IT IS SPELLED EXACTLY CORRECT)
TRADE_QUANTITY = 0.01 # quantity of asset per trade
POSITIONS_ALLOWED = 2 # number of open positions bot may have at once
KLINE_INTERVAL = '3m' # candlestick interval to trade on



class RSI:

    # Classic Relative Strength Index strategy
    # This strategy utilizes classic RSI with a default period of 14.
    # When the RSI of an asset is determined to be overbought or oversold
    # (default parameters are 70 and 30), sell and buy signals are triggered.
    def __init__(self, RSI_PERIOD=14, RSI_OVERBOUGHT=70.0, RSI_OVERSOLD=30.0):
        self.RSI_PERIOD = RSI_PERIOD
        self.RSI_OVERBOUGHT = RSI_OVERBOUGHT
        self.RSI_OVERSOLD = RSI_OVERSOLD

    def get_interval(self):
        return self.RSI_PERIOD

    def signal(self, closes, *_):
        rsi = talib.RSI(closes, self.RSI_PERIOD)
        # print(rsi)
        last_rsi = rsi[-1]
        #print("Current RSI is {}".format(last_rsi))

        if last_rsi > self.RSI_OVERBOUGHT:
            return "SELL"
        elif last_rsi < self.RSI_OVERSOLD:
            return "BUY"
        else:
            return None


class BBANDS:
    
    # Classic Bollinger Bands strategy
    # This strategy utilizes classic bollinger bands with simple moving average.
    # When the price of the asset closes below or above the lower or upper bands,
    # a buy or sell signal is triggered.

    def __init__(self, BBANDS_PERIOD=20):
        self.BBANDS_PERIOD = BBANDS_PERIOD

    def get_interval(self):
        return self.BBANDS_PERIOD

    def signal(self, closes, *_):
        upper, middle, lower = talib.BBANDS(closes, timeperiod=self.BBANDS_PERIOD, matype=0)
        upper = upper[-1]
        middle = middle[-1]
        lower = lower[-1]
        arrLen = len(closes)
        currPrice = closes[arrLen-1]
        # print("Current BBands: UPPER {}, MIDDLE {}, LOWER {}".format(upper, middle, lower))
        # print("Current close: {}".format(currPrice))
        if currPrice < lower:
            return "BUY"
        elif currPrice > upper:
            return "SELL"
        else:
            return None


class BBANDS_REVERSION:

    # Bollinger Bands Reversion Strategy
    # This strategy attempts to profit from the price of an asset
    # returning to its mean. While the price ranges up and down from its EMA,
    # EMA, if the price reaches its set upper or lower bounds and is within
    # an acceptable RSI range, the strategy will return buy or sell signals.
    
    def __init__(self, BBANDS_PERIOD=12, STDEVUP=2, STDEVDN=2, RSI_OVERBOUGHT=70.0, RSI_OVERSOLD=30.0):
        self.BBANDS_PERIOD = BBANDS_PERIOD
        # number of standard deviations from mean
        self.STDEVUP = STDEVUP
        self.STDEVDN = STDEVDN
        self.RSI_OVERBOUGHT = RSI_OVERBOUGHT
        self.RSI_OVERSOLD = RSI_OVERSOLD

    def get_interval(self):
        return self.BBANDS_PERIOD

    def signal(self, closes, highs, lows): 
        
        # Use MA Type EMA
        upper, middle, lower = talib.BBANDS(closes, timeperiod=self.BBANDS_PERIOD, nbdevup=self.STDEVUP, nbdevdn=self.STDEVDN, matype=talib.MA_Type.EMA)
        rsi = talib.RSI(closes, self.BBANDS_PERIOD)
        last_rsi = rsi[-1]

        upper = upper[-1]
        middle = middle[-1]
        lower = lower[-1]
        arrLen = len(closes)
        currPrice = closes[arrLen-1]
        low = lows[-1]
        high = highs[-1]

        # print("Upper: {} Middle: {} Lower: {}".format(upper, middle, lower))
        # print("Current RSI: {}".format(last_rsi))

        if low <= lower and currPrice > lower:
            
            #print("Bollinger buy condition ACCEPTED")
            if last_rsi < self.RSI_OVERSOLD:
                # buy signal
                #print("RSI buy condition ACCEPTED")
                return "BUY"

            else:
                #print("RSI buy condition FAILED - not executing buy.")
                return None
        
        elif high >= upper and currPrice < upper:

            #print("Bollinger sell condition ACCEPTED")
            if last_rsi > self.RSI_OVERBOUGHT:
                # sell signal
                #print("RSI sell condition ACCEPTED")
                return "SELL"

            else:
                #print("RSI sell condition FAILED - not executing sell.")
                return None

        else:
            return None
