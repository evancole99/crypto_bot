import numpy
# Parameter "strategy" must be a class containing the following functions:
# get_interval():
#       returns an integer value corresponding to the strategy's period
# signal(closes, highs, lows):
#       takes list of closes, optional list of highs and lows (may void the parameter) and returns one of the following signals as a STRING:
#       BUY AMT, SELL AMT, LONG AMT (todo), SHORT AMT (todo)




def backtest(strategy, amtPerTrade, numPositionsAllowed, closes, highs, lows):

    get_int = getattr(strategy, "get_interval", None)
    if not callable(get_int):
        print("Error: Provided strategy class does not have the required methods.")
        exit(1)

    period = strategy.get_interval()

    positions = [] # list of tuples (price, amount) of open positions
    entries = []
    exits = []
    numOrders = 0
    profit = 0.0


    # BOUNDS CHECKING
    if (len(closes) != len(highs)) or (len(highs) != len(lows)):
        print("Error: Lists of prices not equal length.")
        exit(1)

    if (len(closes) <= period):
        print("Error: Indicator period exceeds amount of available price data.")
        exit(1)

    n = period

    while n < len(closes):
        currCloses = numpy.array(closes[:n])
        currHighs = numpy.array(highs[:n])
        currLows = numpy.array(lows[:n])

        signal = strategy.signal(currCloses, currHighs, currLows)
        if signal == "BUY":
            if len(positions) < numPositionsAllowed:
                positions.append((currCloses[-1], amtPerTrade))
                entries.append((currCloses[-1], amtPerTrade))
                numOrders += 1
        elif signal == "SELL": # sell ALL positions
            if len(positions) > 0:
                exits.append((currCloses[-1], amtPerTrade))
                sellPrice = currCloses[-1]
                numOrders += 1
                for entry, amt in positions:
                    profit += (sellPrice * amt) - (entry * amt)
                positions = []
        n += 1

    if (len(entries)) == 0:
        print("No trades executed in given timeline.")
        return 0
    if (len(positions)) > 0:
        print("Not all positions were closed.")
        print("Closing remaining positions at last closing value and calculating profits...")

        totAmt = sum(amt for entry, amt in positions)
        exits.append((closes[-1], totAmt))
        positions = []

    totalSpent = sum(x for x, amt in entries)
    totalReturned = sum(x for x, amt in exits)
    percentReturn = float((totalReturned - totalSpent) / (totalSpent))
    buyHoldReturn = float((closes[-1] - closes[0]) / closes[0])
    print("Total profits made: {}".format(round(profit, 4)))
    print("Return percent: {:.0%}".format(percentReturn))
    print("Number of orders executed: {}".format(numOrders))
    print("\nCompare to return from buying and holding: {:.0%}".format(buyHoldReturn))
    return profit



    
