# Crypto Trade Bot

This trade bot utilizes websockets to read kline data from Binance datastreams, apply technical analysis, and automatically execute trades to the Binance broker.


## Installing Dependencies

To install the requires dependencies and libraries, the requirements can be found in requirements.txt. Simply run *pip3 install -r requirements.txt* in the command line.

In order for TALib to function properly, the prerequisite C library must be built and installed. See [how to install TALib dependencies](mrjbq7.github.io/ta-lib/install.html) for help.


## Configuring/Creating Strategies

All strategy configuration is done in strategies.py, which contains several starter strategies using technical analysis from TA-Lib.  

Each strategy is its own separate class. Strategies may be implemented in any way desired, but each class must contain the following methods:  
* \_\_init\_\_() - initializes class with default parameters 
* get\_interval() - returns integer value corresponding to the strategy's period
* signal(closes, highs, lows) - returns signal "BUY" or "SELL" for given price data. Highs and lows lists are optional, and may be voided.

## Running the bot

To run the bot, there are a few options.

### Start bot manually

To start the bot manually, simply execute the Python script with the following syntax:

```
python3 bot.py <STRATEGY> <PARAM1> <PARAM2> <...>
```

### Run bot through AIOHTTP server

If you do not wish to run the bot manually, you may optionally decide to configure an AIOHTTP server running in the cloud. The AIOHTTP server is pre-configured in server.py. To run it, ensure your ports are open to the necessary HTTP traffic, and simply execute the Python script to begin the web server.

To communicate with the AIOHTTP server, you can run the client.py file, which gives several basic commands to send to the server via HTTP POST. Ensure that config.py contains the correct server address for the web server.


## Backtester

There is a custom backtester library in the backtester/ directory. While the insights it provides is very rudimentary, it is helpful to get an idea of how your strategy might compare to the market as a whole.  

In order to backtest your strategy, see backtest\_strategy.py for an example. To download historical data on the symbol of choice, see backtest/getdata.py (an example of which is included in backtest\_strategy.py).  




