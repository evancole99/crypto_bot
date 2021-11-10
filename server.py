import os, socket
import subprocess as sp
from aiohttp import web



async def handle(request):

    params = ['python3', 'bot.py']
    bot_type = request.args.get('type')
    botProc = None
    result = ""

    for key, val in request.args.items():
        params.append(val)

    if bot_type != "CLOSE":
        print("Starting bot process...")
        botProc = sp.Popen(params)
        status = sp.Popen.poll(botProc)
        print(status)
        result = "BOT OPENED"
    else:
        print("Killing process...")
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)
        result = "BOT CLOSED"

    return result

async def init() -> web.Application:
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    return app

if __name__ == "__main__":
    web.run_app(init())

    


