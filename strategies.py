import talib, numpy

# STRATEGY SELECTOR
# To select a strategy, provide one of the strategies from the list below as a command line argument when running the Python script.
# Example: python3 bot.py RSI <PARAM1> <PARAM2> <...>


# == STRATEGIES ==
# List of all currently implemented strategies
# Ensure the strings below EXACTLY match the class name
STRATEGY_LIST = ["RSI", "BBANDS", "BBANDS_REVERSION", "MA_CROSSOVER", "STOCH", "MACD_CROSSOVER"]

# Bot configuration
TRADE_SYMBOL = 'ETHUSDT' # trade symbol (MAKE SURE IT IS SPELLED EXACTLY CORRECT)
TRADE_QUANTITY = 0.01 # quantity of asset per trade
INVESTMENT_AMOUNT = 100.0 # amount of paired asset allowed to trade
POSITIONS_ALLOWED = 2 # number of open positions bot may have at once
KLINE_INTERVAL = '5m' # candlestick interval to trade on
SL_ENABLED = True
SL_TYPE = 'TRAILING' # trailing or limit
SL_PERCENT = 0.05 # percent below stop loss to sell

# All types of moving averages supported by TA Lib
matypes = {
            'MA': 0, # moving average
            'EMA': talib.MA_Type.EMA, # exponential moving average
            'SMA': talib.MA_Type.SMA, # simple moving average
            'DEMA': talib.MA_Type.DEMA, # double exponential moving average
            'KAMA': talib.MA_Type.KAMA, # kaufman adaptive moving average
            'MAMA': talib.MA_Type.MAMA, # mesa adaptive moving average
            'T3': talib.MA_Type.T3, # triple exponential moving average (T3)
            'TEMA': talib.MA_Type.TEMA, # triple exponential moving average
            'TRIMA': talib.MA_Type.TRIMA, # triangular moving average
            'WMA': talib.MA_Type.WMA # weighted moving average
            }

def get_strat(s, params):
    if s not in STRATEGY_LIST:
        print("Error: Invalid strategy selected.")
        return None
    obj = eval("%s(%r)" % (s, params))
    return obj

def get_np_list(candles, key):
    closes = []
    for i in candles:
        closes.append(i.get(key))
    
    data = numpy.array(closes)
    return data

def stop_loss(currClose, candles, open_positions):

    currPrice = currClose

    if len(open_positions) == 0:
        return -1

    for i in range(len(open_positions)):
        stopPrice = 0

        if SL_TYPE == 'LIMIT':
            # Stop limit
            stopPrice = open_positions[i][0] * (1 - SL_PERCENT)

        elif SL_TYPE == 'TRAILING':
            # Trailing stop
            entryID = open_positions[i][2]
            entryCandle = candles[entryID]

            # Get all closing prices from entry candle to now (inclusive)
            closes = get_np_list(candles[entryID-1:], 'close')
            localHigh = numpy.max(closes)

            stopPrice = localHigh * (1 - SL_PERCENT)

        if currPrice <= stopPrice:
            return i


class RSI:

    # Classic Relative Strength Index strategy
    # This strategy utilizes classic RSI with a default period of 14.
    # When the RSI of an asset is determined to be overbought or oversold
    # (default parameters are 70 and 30), sell and buy signals are triggered.
    def __init__(self, params):
        if len(params) != 3:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)

        self.RSI_PERIOD = params[0]
        self.RSI_OVERBOUGHT = params[1]
        self.RSI_OVERSOLD = params[2]

    def get_interval(self):
        return self.RSI_PERIOD

    def signal(self, candles):

        closes = get_np_list(candles, 'close')
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

    def __init__(self, params):
        if len(params) != 1:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)
        self.BBANDS_PERIOD = params[0]

    def get_interval(self):
        return self.BBANDS_PERIOD

    def signal(self, candles):
        
        closes = get_np_list(candles, 'close')

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
    
    def __init__(self, params):
        if len(params) != 6:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)

        self.BBANDS_PERIOD = params[0]
        # number of standard deviations from mean
        self.STDEVUP = params[1]
        self.STDEVDN = params[2]
        self.RSI_OVERBOUGHT = params[3]
        self.RSI_OVERSOLD = params[4]
        self.MATYPE = params[5]

    def get_interval(self):
        return self.BBANDS_PERIOD

    def signal(self, candles): 
        
        closes = get_np_list(candles, 'close')
        lows = get_np_list(candles, 'low')
        highs = get_np_list(candles, 'high')

        MA_TYPE = matypes.get(self.MATYPE, 0)

        upper, middle, lower = talib.BBANDS(closes, timeperiod=self.BBANDS_PERIOD, nbdevup=self.STDEVUP, nbdevdn=self.STDEVDN, matype=MA_TYPE)
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


class MA_CROSSOVER:

    # Moving Average crossover strategy
    # This strategy attempts to profit from using short-term moving average
    # timeframes as crossover indicators.
    # When the short MA crosses from below the long MA, a buy signal is generated.
    # When the short MA crosses from above the long MA, a sell signal is generated.
  

    def __init__(self, params):
        if len(params) != 3:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)

        self.MA_PERIOD_SHORT = params[0]
        self.MA_PERIOD_LONG = params[1]
        self.MATYPE = params[2]

    def get_interval(self):
        return self.MA_PERIOD_LONG

    def signal(self, candles):
    
        closes = get_np_list(candles, 'close')

        MA_TYPE = matypes.get(self.MATYPE, 0)
        
        MAShort = talib.MA(closes, timeperiod=self.MA_PERIOD_SHORT, matype=MA_TYPE)
        MALong = talib.MA(closes, timeperiod=self.MA_PERIOD_LONG, matype=MA_TYPE)

        prevMAShort = MAShort[-2]
        prevMALong = MALong[-2]
        currMAShort = MAShort[-1]
        currMALong = MALong[-1]

        if prevMAShort < prevMALong:
            if currMAShort >= currMALong:
                # BULLISH CROSSOVER
                return "BUY"
        elif prevMAShort > prevMALong:
            if currMAShort <= currMALong:
                # BEARISH CROSSOVER
                return "SELL"
        return None
        


class STOCH:

    def __init__(self, params):
        if len(params) != 6:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)

        self.STOCH_OVERBOUGHT = params[0]
        self.STOCH_OVERSOLD = params[1]
        self.FASTK_PRD = params[2]
        self.SLOWK_PRD = params[3]
        self.SLOWD_PRD = params[4]
        self.MATYPE = params[5]

    def get_interval(self):
        return max([self.FASTK_PRD, self.SLOWK_PRD, self.SLOWD_PRD])

    def signal(self, candles):

        closes = get_np_list(candles, 'close')
        highs = get_np_list(candles, 'high')
        lows = get_np_list(candles, 'low')

        MA_TYPE = matypes.get(self.MATYPE, 0)

        slowk, slowd = talib.STOCH(highs, lows, closes, fastk_period=self.FASTK_PRD, slowk_period=self.SLOWK_PRD, slowd_period=self.SLOWD_PRD, slowk_matype=MA_TYPE, slowd_matype=MA_TYPE)

        if slowk[-1] < self.STOCH_OVERSOLD and slowd[-1] < self.STOCH_OVERSOLD:
            return "BUY"
        elif slowk[-1] > self.STOCH_OVERBOUGHT and slowd[-1] > self.STOCH_OVERBOUGHT:
            return "SELL"

        return None

class MACD_CROSSOVER:

    def __init__(self, params):
        if len(params) != 4:
            print("Error: Strategy initialize with wrong number of parameters.")
            exit(1)

        self.FASTPERIOD = params[0]
        self.SLOWPERIOD = params[1]
        self.SIGNALPERIOD = params[2]
        self.MATYPE = params[3]

    def get_interval(self):
        return self.SLOWPERIOD

    def signal(self, candles):
 
        closes = get_np_list(candles, 'close')
         
        MA_TYPE = matypes.get(self.MATYPE, 0)

        prevCloses = closes[:-1]

        macd, macdsignal, hist = talib.MACDEXT(closes, fastperiod=self.FASTPERIOD, slowperiod=self.SLOWPERIOD, signalperiod=self.SIGNALPERIOD, fastmatype=MA_TYPE, slowmatype=MA_TYPE, signalmatype=MA_TYPE)

        currHist = hist[-1]
        prevHist = hist[-2]


        if currHist >= 0:
            # check if histogram switched directions
            if prevHist < 0:
                return "BUY"
        elif currHist < 0:
            if prevHist > 0:
                return "SELL"
        return None



