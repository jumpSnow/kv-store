from flask import Flask
from .func.kvs.kvs import Kvs
import os

app = Flask(__name__)


app.config.update(
    HOST="0.0.0.0",
    VIEW=os.environ["VIEW"],
    ADDRESS=os.environ["ADDRESS"],
    REPL_FACTOR=os.environ["REPL_FACTOR"],
    PORT=13800,
)

app.config["KVS"] = Kvs(host=app.config["ADDRESS"], view=app.config["VIEW"], repl_factor=app.config["REPL_FACTOR"])
app.logger.info(app.config["VIEW"])


from application.route.kvs_put import *
from application.route.kvs_get import *
from application.route.kvs_delete import *
from application.route.kvs_gossip import *
