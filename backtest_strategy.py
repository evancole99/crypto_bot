# Backtester program template

import sys
from backtester import backtest, getdata
import config
import strategies # Import strategy script


# Configure settings to backtest
symbol = "ETHUSDT"
interval = "1d"
numCandles = 365
amtPerTrade = 0.01
numPositionsAllowed = 1

# Initialize strategy to backtest
strategy = strategies.MA_CROSSOVER()


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

profit = backtest.backtest(strategy, amtPerTrade, numPositionsAllowed, closes, highs, lows)


