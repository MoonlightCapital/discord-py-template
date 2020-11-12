from flask import Flask
from threading import Thread
from gevent.pywsgi import WSGIServer
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "I'm alive"

def run():
    """
    Serves the purpose of keeping the repl instance alive trough a webhook. Setting the webhook pinger part is up to the host
    """

    http_server = WSGIServer(('', os.getenv('WEBHOOK_PORT', 8080)), app)
    http_server.serve_forever()

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
    return t
