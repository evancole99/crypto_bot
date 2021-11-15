# Backtester program template

import sys, itertools
from backtester import backtest, getdata
import config
import strategies # Import strategy script


# Configure settings to backtest
symbol = "ETHUSDT"
interval = "4h"
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


# Initialize strategies to backtest


def backtest_MA_CROSSOVER(shortPeriod, longPeriod, matype):

    print("Testing {}".format(m))
    strategy = strategies.MA_CROSSOVER(shortPeriod, longPeriod, matype)
    profit = backtest.backtest(strategy, c, amtPerTrade, numPositionsAllowed)

    return profit

def backtest_STOCH():

    STOCH_OVERBOUGHT = 80.0
    STOCH_OVERSOLD = 20.0
    # [[fastk periods], [slowk periods], [slowd periods]]
    FASTK_PRDS = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    SLOWK_PRDS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    SLOWD_PRD = [3, 4, 5, 6, 7, 8, 9]

    TEST_PRDS = [FASTK_PRDS, SLOWK_PRDS, SLOWD_PRDS, matypes]

    bestProfit = 0
    bestFastK = 0
    bestSlowK = 0
    bestSlowD = 0
    bestMA = ''

    test_possibilities = list(itertools.product(*TEST_PRDS))

    for i in range(len(test_possibilities)):
        FASTK_PRD = test_possibilities[i][0]
        SLOWK_PRD = test_possibilities[i][1]
        SLOWD_PRD = test_possibilities[i][2]
        MATYPE = test_possibilities[i][3]

        strategy = strategies.STOCH(STOCH_OVERBOUGHT, STOCH_OVERSOLD, FASTK_PRD, SLOWK_PRD, SLOWD_PRD, MATYPE)
        profit = backtest.backtest(strategy, c, amtPerTrade, numPositionsAllowed)
        if profit > bestProfit:
            bestProfit = profit
            bestFastK = FASTK_PRD
            bestSlowK = SLOWK_PRD
            bestSlowD = SLOWD_PRD
            bestMA = MATYPE

    print("Best parameters:")
    print("FastK: {}, SlowK: {}, SlowD: {}".format(bestFastK, bestSlowK, bestSlowD))
    print("Best MA: {}".format(bestMA))
    print("Profits: {}".format(bestProfit))

def backtest_BBANDS_REVERSION():

    BBANDS_PERIODS = [7, 8, 9, 10, 11, 12, 13, 14]
    STDEVUP = 2
    STDEVDN = 2
    RSI_OVERBOUGHT = 70.0
    RSI_OVERSOLD = 30.0

    bestProfit = 0.0
    bestPeriod = 0

    for i in BBANDS_PERIODS:
        strategy = strategies.BBANDS_REVERSION(i, STDEVUP, STDEVDN, RSI_OVERBOUGHT, RSI_OVERSOLD)

        profit = backtest.backtest(strategy, c, amtPerTrade, numPositionsAllowed)
        if profit > bestProfit:
            bestProfit = profit
            bestPeriod = i
        
    print("Best BB Period: {}".format(bestPeriod))
    print("Profit: {}".format(bestProfit))


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

        profit = backtest.backtest(strat, c, amtPerTrade, numPositionsAllowed)

        if profit > best_profit:
            best_profit = profit
            best_params = params
    
    print("Best profit achieved: {}".format(best_profit))
    print("Best parameters:")
    for p in range(len(paramNames)):
        print("{}: {}".format(paramNames[p], best_params[p]))
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
        param_names = ['bb_period', 'stdevup', 'stdevdn', 'rsi_overbought', 'rsi_oversold']
    
    best_params = optimize_params(strategy, param_names, test_combinations)
 
    

def main():

    # Initialize list of parameters to optimize
    bb_prds = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    stdevups = [2, 3]
    stdevdns = [2, 3]
    rsi_overboughts = [60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0]
    rsi_oversolds = [40.0, 35.0, 30.0, 25.0, 20.0, 15.0, 10.0]

    # Compile parameters to one list
    params = [bb_prds, stdevups, stdevdns, rsi_overboughts, rsi_oversolds]

    # Optimize strategy
    strat = "BBANDS_REVERSION"
    optimize_strategy(strat, params)

if __name__ == "__main__":
    main()
