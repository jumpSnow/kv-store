from .. import app
from flask import make_response, jsonify, request
from ..utils.decorators import is_forwarding
from ..func.common_routes_func import multicast_has


@app.route('/kv-store/keys/<key>', methods=['DELETE'])
@is_forwarding()
def kvs_delete(key):
    kvs = app.config["KVS"]
    if_stop = request.args.get("if_stop") == "1"
    value = request.json().get("value") if "value" in request.args else None
    timestamp = request.json().get("timestamp") if "timestamp" in request.args else None
    if not kvs.has(key):
        return make_response(jsonify({"doesExist": False, "causal-context": kvs.context,
                                      "error": "Key does not exist", "message": "Error in DELETE"}), 404)
    if if_stop:
        kvs.multiple_thread_delete(key=key, val=value)
    kvs.delete(key, value, timestamp)
    return make_response(jsonify({"doesExist": True, "causal-context": kvs.context,
                                  "message": "Deleted successfully"}), 200)
