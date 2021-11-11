import signal
import subprocess as sp
from aiohttp import web



class BotProc(object):
    @classmethod
    def start(self, params):
        self.process = sp.Popen(params)
    @classmethod
    def stop(self):
        status = sp.Popen.poll(self.process)
        if status == None:
            self.process.send_signal(signal.SIGTERM)

async def handle(request):

    params = ['python3', 'bot.py']
    bot_type = request.rel_url.query['type']
    
    for key, val in request.rel_url.query.items():
        params.append(val)

    if bot_type != "CLOSE":
        print("Starting bot process...")
        BotProc.start(params)
        return web.Response(text="BOT OPENED")
    else:
        print("Killing process...")
        BotProc.stop()
        signal.raise_signal(signal.SIGTERM)
        return web.Response(text="BOT CLOSED")

app = web.Application()
app.add_routes([web.post('/', handle)])

if __name__ == "__main__":
    web.run_app(app)

    

