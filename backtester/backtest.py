import numpy


# Parameter "strategy" must be a class containing the methods as defined in the README

SL_ENABLED = True
SL_TYPE = 'TRAILING'
SL_PERCENT = 0.05


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

    return -1



def backtest(strategy, cs, amtPerTrade, numPositionsAllowed):

    get_int = getattr(strategy, "get_interval", None)
    if not callable(get_int):
        print("Error: Provided strategy class does not have the required methods.")
        exit(1)

    period = strategy.get_interval()

    positions = [] # list of tuples (price, amount, id) of open positions
    entries = []
    exits = []
    numOrders = 0
    profit = 0.0

    if (len(cs) <= period):
        print("Error: Indicator period exceeds amount of available price data.")
        exit(1)

    n = period

    while n < len(cs):
        
        candles = numpy.array(cs[:n])
        currClose = candles[-1].get('close')

        if len(positions) > 0:
            if SL_ENABLED:
                # Check if stop loss hit
                sl_id = stop_loss(float(currClose), candles, positions)

                if sl_id >= 0:
                    print("{} STOP LOSS TRIGGERED".format(SL_TYPE))
                    sellQty = positions[sl_id][1]
                    print("SELLING {}, ENTRY {}".format(sellQty, positions[sl_id][0]))
                    exits.append((currClose, sellQty))
                    profit += (currClose * sellQty) - (positions[sl_id][0] * sellQty)
                    numOrders += 1
                    positions.pop(sl_id)



        signal = strategy.signal(candles)

        if signal == "BUY":

            if len(positions) < numPositionsAllowed:
                positions.append((currClose, amtPerTrade, len(candles)-1))
                entries.append((currClose, amtPerTrade))
                numOrders += 1

        elif signal == "SELL": # sell ALL positions

            if len(positions) > 0:
                exits.append((currClose, amtPerTrade))
                sellPrice = currClose
                numOrders += 1
                for entry, amt, cID in positions:
                    profit += (sellPrice * amt) - (entry * amt)
                positions = []
        n += 1

    if (len(entries)) == 0:
        print("No trades executed in given timeline.")
        return 0
    if (len(positions)) > 0:
        #print("Not all positions were closed.")
        #print("Remaining positions: ")
        #print(positions)
        #print("\nClosing remaining positions at last closing value and calculating profits...")

        totAmt = sum(amt for entry, amt, cID in positions)
        totSpentRemaining = sum(amt*entry for entry, amt, cID in positions)
        lastClose = candles[-1].get('close')
        exits.append((lastClose, totAmt))
        profit += (lastClose * totAmt) - (totSpentRemaining)
        
        positions = []
    

    totalSpent = sum(x*amt for x, amt in entries)
    totalReturned = sum(x*amt for x, amt in exits)
    percentReturn = float((totalReturned - totalSpent) / (totalSpent))
    buyHoldReturn = float((candles[-1].get('close') - candles[0].get('close')) / candles[0].get('close'))

    print("BACKTESTING STRATEGY: {}".format(type(strategy).__name__))
    print("Total profits made: {}".format(round(profit, 5)))
    print("Return percent: {:.0%}".format(percentReturn))
    print("Number of orders executed: {}".format(numOrders))
    print("\nCompare to return from buying and holding: {:.0%}".format(buyHoldReturn))
    print("\n")
    return profit



    
