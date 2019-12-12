import requests


def verify_key(key):
    return len(key) <= 50


def verify_value(json_form):
    if not json_form:
        return "", False
    if "value" not in json_form:
        return "", False
    if not json_form["value"]:
        return "", False
    return json_form["value"], True


def verify_context(json_form):
    if not json_form:
        return "", False
    if "causal-context" not in json_form:
        return "", False
    if not json_form["causal-context"]:
        return "", False
    return json_form["causal-context"], True


def multicast_shards(kvs):
    params = {"if_stop": 1}
    res_list = []
    for view in kvs.nodes_view:
        for host in view:
            res = requests.get("http://{host}/kv-store/shards".format(host=host), params=params)
            if res.status_code == 200:
                res_list.append(res.json()["id"])
                break
    return res_list


def multicast_single_shard(kvs, shard_id):
    params = {"if_stop": 1}
    view = kvs.nodes_view[shard_id]
    res = {}
    for i in view:
        res = requests.get("http://{host}/kv-store/shards/{shard_id}".format(host=i, shard_id=shard_id), params=params)
        if res.status_code == 200:
            return res.json()
    return res.json()


def multicast_has(kvs, key):
    view = kvs.nodes_view[kvs.shards_id]
    for i in view:
        res = requests.get("http://{host}/kv-store/hash/{key}".format(host=i, key=key))
        if res.status_code == 200:
            return True
    return False


def multicast_view_change(json_form, kvs):
    res_list_detail = {}
    params = {"if_stop": 1}
    nodes_view = kvs.nodes_view
    for view in nodes_view:
        for host in view:
            host = host.strip()
            res_detail = requests.get("http://{host}/kv-store/data".format(host=host))
            if res_detail.status_code == 200:
                res_list_detail.update(res_detail.json())
                res = requests.put("http://{host}/kv-store/view-change".format(host=host), params=params,
                                   json=json_form)
    return res_list_detail


def re_shard(kvs, data):
    res_list = []
    for key in data:
        forwarding_shard = kvs.allocated_shard(key=key)
        for forwarding_host in forwarding_shard:
            res = forward_to_address(methods="PUT", forwarding_host=forwarding_host, key=key,
                                     value={"value": data[key][0]}, params=2)
    for shards in kvs.nodes_view:
        for host in shards:
            res = requests.get("http://{ip}/kv-store/desc".format(ip=host))
            if res.status_code == 200:
                res_list.append(res.json())
                break
    return res_list


def gossip(kvs, methods, key, value):
    res = {}
    shards = kvs.shards
    for host in shards:
        if host != kvs.host:
            res = forward_to_address(methods=methods, forwarding_host=host, key=key,
                                     value=value, params=2)
    return res


def gossip_view_change(kvs, json_form):
    res = {}
    params = {"if_stop": 1}
    shards = kvs.shards
    for host in shards:
        if host != kvs.host:
            res = requests.put("http://{host}/kv-store/view-change".format(host=host), params=params, json=json_form)
    return res


def check_put(kvs, key, value):
    forwarding_address = kvs.allocated_shard(key=key)
    res = forward_to_address(methods="GET", forwarding_host=forwarding_address, key=key, value=value)
    if res.status_code == 200:
        res = forward_to_address(methods="PUT", forwarding_host=forwarding_address, key=key, value=value)
    return res, forwarding_address


def forward_to_address(methods, forwarding_host, key, value=None, params=None):
    url = "http://{ip}/kv-store/keys/{key}".format(ip=forwarding_host.strip(), key=key)
    headers = {"Content-Type": "application/json"}
    params = {"if_stop": params} if params else None
    res = {}
    if methods == "PUT":
        res = requests.put(url=url, json=value, headers=headers, params=params)
    elif methods == "GET":
        res = requests.get(url=url, headers=headers, params=params)
    elif methods == "DELETE":
        res = requests.delete(url=url, headers=headers, params=params)
    return res
