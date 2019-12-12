from functools import wraps
from flask import request, make_response, jsonify
from application import app
from ..func.common_routes_func import forward_to_address, multicast_view_change, re_shard, \
    multicast_shards, multicast_single_shard


def is_forwarding():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            kvs = app.config["KVS"]
            if_stop = request.args.get("if_stop") is None
            if request.method == "PUT":
                value = request.get_json()
            else:
                value = None
            if if_stop:
                forwarding_shard = kvs.allocated_shard(key=kwargs["key"])
                for forwarding_host in forwarding_shard:
                    try:
                        res = forward_to_address(methods=request.method, forwarding_host=forwarding_host,
                                                 key=kwargs["key"], value=value, params=1)
                        res_data = res.json()
                    except Exception as e:
                        continue
                    else:
                        res_data.update({"address": forwarding_host})
                        return make_response(jsonify(res_data), res.status_code)
            return function(*args, **kwargs)
        return wrapper

    return decorator


def is_forwarding_view_change():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            json_form = request.get_json()
            view = json_form["view"].split(",")
            if_stop = request.args.get("if_stop") is None
            kvs = app.config["KVS"]
            if if_stop:
                kvs.view_update(view)
                kvs.gossip_stop(if_request=True)
                res_data = multicast_view_change(json_form, kvs)
                res = re_shard(kvs=kvs, data=res_data)
                kvs.gossip_resume(if_request=True)
                return make_response(jsonify({"message": "View change successful",
                                              "causal-context": kvs.context, "shards": res}), 200)
            return function(*args, **kwargs)
        return wrapper
    return decorator


def is_forwarding_shards():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if_stop = request.args.get("if_stop") is None
            if if_stop:
                kvs = app.config["KVS"]
                res_data = multicast_shards(kvs)
                return make_response(jsonify({"message": "Shard membership retrieved successfully",
                                              "causal-context": kvs.context, "shards": res_data}), 200)
            return function(*args, **kwargs)
        return wrapper
    return decorator


def is_forwarding_single_shards():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            kvs = app.config["KVS"]
            if_stop = request.args.get("if_stop") is None
            if if_stop and (kvs.shards_id != int(kwargs["id"])):
                res_data = multicast_single_shard(kvs, kwargs["id"])
                return res_data
            return function(*args, **kwargs)
        return wrapper
    return decorator
