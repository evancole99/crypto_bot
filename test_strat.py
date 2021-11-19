# Backtester program template

import sys, itertools
from backtester import backtest, getdata
import config
import strategies # Import strategy script


# Configure settings to backtest
symbol = "ETHUSDT"
interval = "1h"
numCandles = 300
amtPerTrade = 0.01
numPositionsAllowed = 1


# Retrieve kline data from getdata script
candles = getdata.get_historical(symbol, interval, numCandles)

c = []

matypes = ['MA', 'EMA', 'SMA', 'DEMA', 'KAMA', 'MAMA', 'T3', 'TEMA', 'TRIMA', 'WMA']

# Parse unformatted kline data
# Can store lots more data than shown below (see getdata function)
for i in range(len(candles)):

    cDict = {'open': float(candles[i][1]), 'close': float(candles[i][4]), 'high': float(candles[i][2]), 'low': float(candles[i][3]), 'vol': float(candles[i][5]), 'time': candles[i][6]}
    c.append(cDict)

def optimize_params(strategy, paramNames, test_combinations):

    best_profit = 0.0
    best_params = []

    for i in range(len(test_combinations)):
        params = test_combinations[i]
        strat = None

        if strategy == "MA_CROSSOVER":
            strat = strategies.MA_CROSSOVER(params)
        elif strategy == "STOCH":
            strat = strategies.STOCH(params)
        elif strategy == "BBANDS_REVERSION":
            strat = strategies.BBANDS_REVERSION(params)
        elif strategy == "MACD_CROSSOVER":
            strat = strategies.MACD_CROSSOVER(params)

        profit = backtest.backtest(strat, c, amtPerTrade, numPositionsAllowed)

        if profit > best_profit:
            best_profit = profit
            best_params = params
    
    percentReturn = float(best_profit / backtest.INVESTMENT_AMOUNT)
    print("Best profit achieved: {}".format(round(best_profit, 5)))
    print("Return: {:.0%}".format(percentReturn))
    print("Best parameters:")
    for p in range(len(paramNames)):
        print("{}: {}".format(paramNames[p], best_params[p]))
    print("\n")
    return best_params



def optimize_strategy(strategy, params):
    # Params is list of lists, containing all parameter values to optimize

    test_combinations = list(itertools.product(*params))
    best_params = []
    param_names = []

    if strategy == "MA_CROSSOVER":
        param_names = ['shortPeriod', 'longPeriod', 'matype']
    elif strategy == "STOCH":
        param_names = ['stoch_overbought', 'stoch_oversold', 'fastk', 'slowk', 'slowd', 'matype']
    elif strategy == "BBANDS_REVERSION":
        param_names = ['bb_period', 'stdevup', 'stdevdn', 'rsi_overbought', 'rsi_oversold', 'matype']
    elif strategy == "MACD_CROSSOVER":
        param_names = ['fastperiod', 'slowperiod', 'signalperiod', 'matype']
    
    best_params = optimize_params(strategy, param_names, test_combinations)
 
    

def main():

    # Initialize list of parameters to optimize


    # MA_CROSSOVER PARAMETERS
    short_prds = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    long_prds = [12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 30, 35, 40, 45, 50, 100, 200]

    # BBANDS_REVERSION PARAMETERS
    bb_prds = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    stdevups = [2, 3]
    stdevdns = [2, 3]
    rsi_overboughts = [60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0]
    rsi_oversolds = [40.0, 35.0, 30.0, 25.0, 20.0, 15.0, 10.0]

    # STOCH PARAMETERS
    stoch_overboughts = [55.0, 60.0, 65.0, 70.0, 75.0, 80.0]
    stoch_oversolds = [45.0, 40.0, 35.0, 30.0, 25.0, 20.0]
    fastks = [9, 10, 11, 12, 13, 14]
    slowks = [1, 2, 3, 4]
    slowds = [1, 2, 3, 4, 5]

    # MACD_CROSSOVER PARAMETERS
    fast_prds = [9, 10, 11, 12, 13, 14, 15, 16]
    slow_prds = [21, 22, 23, 24, 25, 26, 27, 28]
    signal_prds = [6, 7, 8, 9, 10, 11, 12]
    


    # Compile parameters to one list
    macross_params = [short_prds, long_prds, matypes]
    bbreversion_params = [bb_prds, stdevups, stdevdns, rsi_overboughts, rsi_oversolds, matypes]
    stoch_params = [stoch_overboughts, stoch_oversolds, fastks, slowks, slowds, matypes]
    macd_params = [fast_prds, slow_prds, signal_prds, matypes]

    # Optimize strategy
    optimize_strategy("MA_CROSSOVER", macross_params)
    optimize_strategy("BBANDS_REVERSION", bbreversion_params)
    optimize_strategy("STOCH", stoch_params)
    optimize_strategy("MACD", macd_params)

if __name__ == "__main__":
    main()


