from ..import app


@app.before_first_request
def start_sync_gossip():
    kvs = app.config["KVS"]
    kvs.gossip_start()
