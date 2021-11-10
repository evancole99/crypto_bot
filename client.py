import requests, sys, json
import aiohttp, asyncio
import config, strategies

# CLIENT SIDE SCRIPT
# This script allows the user to send commands to the server hosting the bot
# The server receives HTTP post request and commands the bot depending on
# the given parameters.

# Current client options:
# Open new bot
    # Types: RSI, BBANDS, BBANDS_REVERSION
# Close current bot


async def main():
    async with aiohttp.ClientSession() as session:
        print("Options:")
        print("1 to open new bot")
        print("2 to close existing bot")
        choice = input("Enter your choice (1 or 2): ")

        params = {}

        if choice == "1":
            print("OPENING BOT")
            
            print("Options:")
            print(strategies.STRATEGY_LIST)
            bot_type = input("Select a bot type (exactly as shown above): ")

            print("\nConfigure your bot")
            print("Enter a value for each following field, or enter 0 for default")
            if bot_type == "RSI":
                rsi_period = int(input("RSI period: "))
                rsi_oversold = float(input("RSI oversold: "))
                rsi_overbought = float(input("RSI overbought: "))

                params = {
                        'type': bot_type,
                        'period': rsi_period,
                        'rsi_oversold': rsi_oversold,
                        'rsi_overbought': rsi_overbought
                        }
            elif bot_type == "BBANDS":
                bbands_period = int(input("Bollinger Bands period: "))

                params = {
                        'type': bot_type,
                        'period': bbands_period
                        }
            elif bot_type == "BBANDS_REVERSION":
                bbands_period = int(input("Bollinger Bands period: "))
                stdevup = int(input("Standard deviations above: "))
                stdevdn = int(input("Standard deviations below: "))
                rsi_oversold = float(input("RSI oversold: "))
                rsi_overbought = float(input("RSI overbought: "))

                params = {
                        'type': bot_type,
                        'period': bbands_period,
                        'stdevup': stdevup,
                        'stdevdn': stdevdn,
                        'rsi_oversold': rsi_oversold,
                        'rsi_overbought': rsi_overbought
                        }
            else:
                print("Error: Wrong bot type selected")
                exit(1)

        elif choice == "2":
            print("CLOSING BOT")
            params = {'type': 'CLOSE'}

        else:
            print("Error: Invalid choice")
            exit(1)
            
        async with session.post(config.SERVER_ADDR, params=params) as r:
            #r = requests.post(config.SERVER_ADDR, params=params)
            #r = requests.post('http://localhost:8080', params=params)
            print(await r.text())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
