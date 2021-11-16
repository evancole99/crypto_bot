# Crypto Trade Bot

This trade bot utilizes websockets to read kline data from Binance datastreams, apply technical analysis, and automatically execute trades to the Binance broker.


## Installing Dependencies

To install the requires dependencies and libraries, the requirements can be found in requirements.txt. Simply run *pip3 install -r requirements.txt* in the command line.

In order for TALib to function properly, the prerequisite C library must be built and installed. See [how to install TALib dependencies](https://mrjbq7.github.io/ta-lib/install.html) for help.

## Setting Up

In order for the bot to be able to execute trades, a configuration file is needed containing our API keys, webhooks, server addresses, and anything else that we want to ensure is not hard-coded (keep your API keys safe!).  

If you do not have Binance API keys configured, see [Binance's FAQ](http://binance.com/en/support/faq/360002502072) for help.

To do this, create a file config.py with the following variables:
* API\_KEY = 'YOUR API KEY'
* API\_SECRET = 'YOUR API SECRET'
* IFTTT\_WEBHOOK = 'YOUR IFTTT PUSH NOTIFY WEBHOOK'
* SERVER\_ADDR = "YOUR AIOHTTP SERVER ADDRESS"  

If you wish to be notified via push notifications through IFTTT, sign up for IFTTT Maker and create a push notify applet using WebHooks. You may configure the applet to provide a basic notification, or to provide more data using a JSON payload. If you don't wish to use IFTTT notifications, simply remove all references to the notify\_user() function.  

And that's it! Make sure this file stays safe - anyone who has access to your API key and API secret has access to your Binance account.

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

The parameters differ depending on the selected strategy. See strategies.py for clarification.  

### Run bot through AIOHTTP server

If you do not wish to run the bot manually, you may optionally decide to configure an AIOHTTP server. The AIOHTTP server is pre-configured in server.py. To run it, ensure your ports are open to the necessary HTTP traffic (default is port 8080), and simply execute the Python script to begin the web server.

To communicate with the AIOHTTP server, you can run the client.py file, which gives several basic commands to send to the server via HTTP POST. Ensure that config.py contains the correct server address for the web server.


## Backtester

There is a custom backtester library in the backtester/ directory. While the insights it provides is very rudimentary, it is helpful to get an idea of how your strategy might compare to the market as a whole.  

In order to backtest your strategy, see backtest\_strategy.py for an example. To download historical data on the symbol of choice, see backtest/getdata.py (an example of which is included in backtest\_strategy.py).  




