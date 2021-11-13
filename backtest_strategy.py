# Backtester program template

import sys
from backtester import backtest, getdata
import config
import strategies # Import strategy script


# Configure settings to backtest
symbol = "ETHUSDT"
interval = "4h"
numCandles = 300
amtPerTrade = 0.1
numPositionsAllowed = 1


# Retrieve kline data from getdata script
candles = getdata.get_historical(symbol, interval, numCandles)

closes = []
highs = []
lows = []

# Parse unformatted kline data
# Can store lots more data than shown below (see getdata function)
for i in candles:
    closes.append(float(i[4]))
    highs.append(float(i[2]))
    lows.append(float(i[3]))


# Initialize strategies to backtest


def backtest_MA_Crossover():
    # Backtest all MA types for MA crossover strategy
    shortPeriod = 5
    longPeriod = 9

    matypes = ['MA', 'EMA', 'SMA', 'DEMA', 'KAMA', 'MAMA', 'T3', 'TEMA', 'TRIMA', 'WMA']

    bestProfit = 0
    bestStrat = ""

    for m in matypes:
        print("Testing {}".format(m))
        strategy = strategies.MA_CROSSOVER(shortPeriod, longPeriod, m)
        profit = backtest.backtest(strategy, amtPerTrade, numPositionsAllowed, closes, highs, lows)
        if profit > bestProfit:
            bestProfit = profit
            bestStrat = m

    print("{}, {} timeframe, {} candles, {} positions allowed".format(symbol, interval, numCandles, numPositionsAllowed))

    print("Best MA type: {}".format(bestStrat))
    print("Return: {}".format(round(profit, 5)))

def backtest_STOCH():

    STOCH_OVERBOUGHT = 80.0
    STOCH_OVERSOLD = 20.0
    FASTK_PRDS = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    SLOWK_PRDS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    SLOWD_PRD = 3
    MATYPE = "MA"

    bestProfit = 0
    bestFastK = 0
    bestSlowK = 0

    for i in range(len(FASTK_PRDS)):
        FASTK_PRD = FASTK_PRDS[i]
        SLOWK_PRD = SLOWK_PRDS[i]

        strategy = strategies.STOCH(STOCH_OVERBOUGHT, STOCH_OVERSOLD, FASTK_PRD, SLOWK_PRD, SLOWD_PRD, MATYPE)
        profit = backtest.backtest(strategy, amtPerTrade, numPositionsAllowed, closes, highs, lows)
        if profit > bestProfit:
            bestProfit = profit
            bestFastK = FASTK_PRD
            bestSlowK = SLOWK_PRD

    print("Best Fast K period: {}".format(bestFastK))
    print("Best Slow K period: {}".format(bestSlowK))
    print("Profits: {}".format(bestProfit))

backtest_STOCH()

