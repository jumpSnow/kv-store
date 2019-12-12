from .. import app
from flask import request, make_response, jsonify
from ..func.common_routes_func import verify_key, verify_value, verify_context
from ..utils.decorators import is_forwarding_view_change, is_forwarding


@app.route('/kv-store/keys/<key>', methods=['PUT'])
@is_forwarding()
def kvs_insert_or_update(key):
    json_form = request.get_json()
    kvs = app.config["KVS"]
    value, verify_value_res = verify_value(json_form)
    context, verify_contexts = verify_context(json_form)
    if verify_contexts:
        kvs.sync_context(context)
    if not verify_key(key):
        return make_response(jsonify({"message": "Error in PUT", "causal-context": kvs.context,
                                      "error": "Key is too long"}), 400)
    if not verify_value_res:
        return make_response(jsonify({"message": "Error in PUT", "causal-context": kvs.context,
                                      "error": "Value is missing"}), 400)
    if not kvs.has(key):
        success_res = make_response(jsonify({"message": "Added successfully", "causal-context": kvs.context,
                                             "replaced": False}), 201)
    else:
        success_res = make_response(jsonify({"message": "Updated successfully", "causal-context": kvs.context,
                                             "replaced": True}), 200)
    kvs.update(key, value)
    return success_res


@app.route('/kv-store/view-change', methods=['PUT'])
@is_forwarding_view_change()
def kvs_view_change():
    json_form = request.get_json()
    view = json_form["view"].split(",")
    kvs = app.config["KVS"]
    kvs.view_update(view)
    desc = kvs.desc
    kvs.empty()
    return make_response(jsonify(desc), 200)


@app.route('/kv-store/sync-kvs', methods=['PUT'])
def kvs_sync_kvs():
    data = request.get_json()
    kvs = app.config["KVS"]
    if not kvs.gossip_status():
        kvs.sync(msg_data=data)
    return make_response(jsonify(kvs.data), 200)


@app.route('/kv-store/gossip_status/<status>', methods=['PUT'])
def kvs_gossip_status(status):
    kvs = app.config["KVS"]
    if int(status) == 1:
        kvs.gossip_stop()
    else:
        kvs.gossip_resume()
    return make_response(jsonify({}), 200)


@app.route('/kv-store/keys/delete/<key>', methods=['POST'])
def kvs_delete_keys(key):
    kvs = app.config["KVS"]
    value = request.json["value"]
    timestamp = request.json["timestamp"]
    if not kvs.has(key):
        return make_response(jsonify({"doesExist": False, "causal-context": kvs.context,
                                      "error": "Key does not exist", "message": "Error in DELETE"}), 404)
    kvs.delete(key, value, timestamp)
    return make_response(jsonify({"doesExist": True, "causal-context": kvs.context,
                                  "message": "Deleted successfully"}), 200)

