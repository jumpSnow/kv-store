from .. import app
from flask import make_response, jsonify
from ..utils.decorators import is_forwarding, is_forwarding_shards, is_forwarding_single_shards


@app.route('/kv-store/keys/<key>', methods=['GET'])
@is_forwarding()
def kvs_read(key):
    kvs = app.config["KVS"]
    if not kvs.has(key):
        return make_response(jsonify({"doesExist": False, "causal-context": kvs.context,
                                      "error": "Key does not exist", "message": "Error in GET"}),
                             404)
    value = kvs.read(key)
    return make_response(jsonify({"doesExist": True,  "causal-context": kvs.context,
                                  "message": "Retrieved successfully", "value": value}), 200)


@app.route('/kv-store/key-count', methods=['GET'])
def kvs_key_count():
    kvs = app.config["KVS"]
    return make_response(jsonify({"message": "Key count retrieved successfully", "key-count": kvs.count,
                                  "shard-id": kvs.shards_id, "causal-context": kvs.context}), 200)


@app.route('/kv-store/shards', methods=['GET'])
@is_forwarding_shards()
def kvs_all_shards():
    kvs = app.config["KVS"]
    return make_response(jsonify({"id": str(kvs.shards_id)}), 200)


@app.route('/kv-store/shards/<id>', methods=['GET'])
@is_forwarding_single_shards()
def kvs_single_shards(id):
    kvs = app.config["KVS"]
    return make_response(jsonify({"message": "Shard information retrieved successfully", "shard-id": id,
                                  "key-count": kvs.count, "causal-context": kvs.context, "replicas": kvs.shards}))


@app.route('/kv-store/data', methods=['GET'])
def kvs_data():
    kvs = app.config["KVS"]
    return make_response(jsonify(kvs.data), 200)


@app.route('/kv-store/desc', methods=['GET'])
def kvs_re_shard():
    kvs = app.config["KVS"]
    return make_response(jsonify(kvs.desc), 200)


@app.route('/kv-store/has/<key>', methods=['GET'])
def kvs_has(key):
    kvs = app.config["KVS"]
    if kvs.has(key):
        return make_response(jsonify({"res": kvs.has(key)}), 200)
    else:
        return make_response(jsonify({"res": kvs.has(key)}), 404)
