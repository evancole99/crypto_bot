import numpy


# Parameter "strategy" must be a class containing the methods as defined in the README

SL_ENABLED = True
SL_TYPE = 'TRAILING'
SL_PERCENT = 0.05
INVESTMENT_AMOUNT = 100.0
binance_fee = 0.001

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
    account_balance = INVESTMENT_AMOUNT

    get_int = getattr(strategy, "get_interval", None)
    if not callable(get_int):
        print("Error: Provided strategy class does not have the required methods.")
        exit(1)

    period = strategy.get_interval()

    positions = [] # list of tuples (price, amount, id) of open positions
    entries = []
    exits = []
    numOrders = 0

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
                    sellQty = positions[sl_id][1]
                    #print("{} STOP LOSS TRIGGERED".format(SL_TYPE))
                    #print("SELLING {}, ENTRY {}".format(sellQty, positions[sl_id][0]))

                    exits.append((currClose, (sellQty * (1 - binance_fee))))
                    account_balance += (currClose * sellQty)
                    numOrders += 1
                    positions.pop(sl_id)

        signal = strategy.signal(candles)

        if signal == "BUY":

            if len(positions) < numPositionsAllowed:
                amtSpent = amtPerTrade * currClose

                if amtSpent <= account_balance:
                    # Enough funds exist
                    account_balance =  account_balance - amtSpent
                    amtBought = amtPerTrade * (1 - binance_fee) # reflect binance's fee
                    positions.append((currClose, amtBought, len(candles)-1))
                    entries.append((currClose, amtBought))
                    numOrders += 1

        elif signal == "SELL": # sell ALL positions

            if len(positions) > 0:
                sellQty = sum(amt for entry, amt, cID in positions)
                amtReceived = (sellQty * currClose) * (1 - binance_fee)
                account_balance += amtReceived
                exits.append((currClose, sellQty))
                numOrders += 1
                positions = []
        n += 1

    
    if (len(entries)) == 0:
        # print("No trades executed in given timeline.")
        return 0

    if (len(positions)) > 0:
        # Some positions remained open at the end
        # Close positions and add profits
        totAmt = sum(amt for entry, amt, cID in positions)
        lastClose = candles[-1].get('close')
        exits.append((lastClose, totAmt))
        amtReceived = (totAmt * lastClose) * (1 - binance_fee)
        account_balance += amtReceived
        
        positions = []
    
    profit = account_balance - INVESTMENT_AMOUNT
    percentReturn = float(profit / INVESTMENT_AMOUNT)
    buyHoldReturn = float((candles[-1].get('close') - candles[0].get('close')) / candles[0].get('close'))

    print("\n")
    print("==============================")
    print("BACKTESTING STRATEGY: {}".format(type(strategy).__name__))
    print("Total profits: {}".format(round(profit, 5)))
    print("Return: {:.0%}".format(percentReturn))
    print("Number of orders executed: {}".format(numOrders))
    print("\nCompare to return from buying and holding: {:.0%}".format(buyHoldReturn))
    print("==============================")
    return profit



    
