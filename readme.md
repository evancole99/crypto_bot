# Crypto Trade Bot

This trade bot utilizes websockets to read kline data from Binance datastreams, apply technical analysis, and automatically execute trades to the Binance broker.


## Installing Dependencies

To install the requires dependencies and libraries, the requirements can be found in requirements.txt. Simply run *pip3 install -r requirements.txt* in the command line.

In order for TALib to function properly, the prerequisite C library must be built and installed. See [how to install TALib dependencies](mrjbq7.github.io/ta-lib/install.html) for help.


## Running the bot

To run the bot, simply execute the Python script with the following syntax:

```
python3 bot.py <STRATEGY>
```

For the full list of strategies, or to customize your strategy's parameters, visit the strategies.py file.


