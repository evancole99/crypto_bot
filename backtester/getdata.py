import datetime, time
import config
from dateutil.relativedelta import relativedelta
from binance.client import Client

# Candles are formatted as shown below:
# [
# [0]   open timestamp 
# [1]   open price
# [2]   high price
# [3]   low price
# [4]   close price
# [5]   volume
# [6]   close timestamp
# [7]   quote asset volume
# [8]   number of trades
# [9]   taker buy base asset volume
# [10]  taker buy quote asset volume
# [11]  ignore
# [12]  ignore
# ]


client = Client(config.API_KEY, config.API_SECRET, tld='us')

def get_client_interval(interval):
    switch = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '3m': Client.KLINE_INTERVAL_3MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '30m': Client.KLINE_INTERVAL_30MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '2h': Client.KLINE_INTERVAL_2HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '6h': Client.KLINE_INTERVAL_6HOUR,
            '8h': Client.KLINE_INTERVAL_8HOUR,
            '12h': Client.KLINE_INTERVAL_12HOUR,
            '1d': Client.KLINE_INTERVAL_1DAY,
            '3d': Client.KLINE_INTERVAL_3DAY,
            '1w': Client.KLINE_INTERVAL_1WEEK,
            '1M': Client.KLINE_INTERVAL_1MONTH
            }
    # defaults to 1HOUR if interval is invalid
    return switch.get(interval, Client.KLINE_INTERVAL_1HOUR)


def get_historical(symbol, interval, numCandles):
    endDate = datetime.datetime.now()
    startDate = None

    kline_interval = get_client_interval(interval)

    timeframe = interval[-1]
    amtTime = interval[:-1]
    totalNumCandles = numCandles * int(amtTime)

    candles = None

    if timeframe == 'm':
        startDate = endDate - datetime.timedelta(minutes=totalNumCandles)
    elif timeframe == 'h':
        startDate = endDate - datetime.timedelta(hours=totalNumCandles)
    elif timeframe == 'd':
        startDate = endDate - datetime.timedelta(days=totalNumCandles)
    elif timeframe == 'w':
        startDate = endDate - datetime.timedelta(weeks=totalNumCandles)
    elif timeframe == 'M':
        startDate = endDate - relativedelta(months=totalNumCandles)
    else:
        print("Error: Unrecognized interval provided.")
        exit(1)

    candles = client.get_historical_klines(symbol, kline_interval, str(startDate), str(endDate))
    
    return candles


