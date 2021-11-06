import os
import subprocess as sp
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])

def receive():

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
    

if __name__ == "__main__":
    app.run()

    


