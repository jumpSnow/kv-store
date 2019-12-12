import hashlib
from datetime import datetime
import time
from threading import Thread
import requests
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class Kvs:

    def __init__(self, host, view, repl_factor):
        self._data = dict()
        self._recover_data = dict()
        self._host = host
        self._view = view.split(",")
        self._repl_factor = int(repl_factor)
        self._nodes_view = list()
        self._shards_id = -12
        self._host_id = 0
        self._vector_clock = [0 for i in range(0, len(self.shards))]
        self._vector_clock.insert(0, int(datetime.timestamp(datetime.now())))
        self._stop_gossip = False
        self._gossip = Thread(target=self.sync_kvs)
        self._delete_pool = ThreadPoolExecutor(max_workers=1000)
        self._if_delete = False

    def __repr__(self):
        return repr(self._data)

    @property
    def data(self):
        return self._data

    @property
    def shards(self):
        node_view = self.nodes_view
        for i in range(0, len(node_view)):
            if self._host in node_view[i]:
                return node_view[i]
        return []

    @property
    def shards_id(self):
        node_view = self.nodes_view
        for i in range(0, len(node_view)):
            if self._host in node_view[i]:
                self._shards_id = i
                return self._shards_id
        return str(self._shards_id)

    @property
    def host_id(self):
        self._host_id = self.shards.index(self.host)
        return self._host_id

    @property
    def nodes_view(self):
        self._nodes_view = [self._view[i:i + self._repl_factor] for i in range(0, len(self._view), self._repl_factor)]
        return self._nodes_view

    @property
    def count(self):
        return len(self._data.keys())

    @property
    def host(self):
        return self._host

    @property
    def view(self):
        return self._view

    @property
    def keys(self):
        return self._data.keys()

    @property
    def now_time(self):
        return int(datetime.timestamp(datetime.now()))

    @property
    def view_size(self):
        return len(self.nodes_view)

    @property
    def detail(self):
        return {
            "address": self.host,
            "key-count": self.count,
            "data": self.data
        }

    @property
    def context(self):
        return {
            "shards_id": self.shards_id,
            "key-count": self.count,
            "data": self.data
        }

    @property
    def desc(self):
        return {
            "replicas": self.shards,
            "key-count": self.count,
            "shard-id": self.shards_id,
        }

    # def update_recover_data(self, shard_id,  key, val):
    #     self.update_vector_clock()
    #     data = {key: [val, self._vector_clock]}
    #     if shard_id not in self._recover_data:
    #         self._recover_data[shard_id] = []
    #     self._recover_data[shard_id].append(data)

    def gossip_status(self):
        return self._stop_gossip

    def gossip_start(self):
        self._gossip.start()

    def gossip_resume(self, if_request=False, if_shard=False):
        self._stop_gossip = False
        if if_request:
            for host in self.view:
                if host != self.host:
                    requests.put("http://{ip}/kv-store/gossip_status/0".format(ip=host))
        time.sleep(3)

    def gossip_stop(self, if_request=False):
        self._stop_gossip = True
        if if_request:
            for host in self.view:
                if host != self.host:
                    requests.put("http://{ip}/kv-store/gossip_status/1".format(ip=host))
        time.sleep(3)

    def sync_kvs(self):
        shards = self.shards.copy()
        header = {"Content-Type": "application/json"}
        while not self._stop_gossip:
            for host in shards:
                if host != self.host:
                    try:
                        res = requests.put("http://{ip}/kv-store/sync-kvs".format(ip=host), json=self.data,
                                           headers=header)
                    except Exception as e:
                        continue
            time.sleep(2)

    def multiple_thread_delete(self, key, val):
        if not val:
            shards = self.shards.copy()
            val = self.data.get(key)
            val = val.copy()
            delete_thread = Thread(target=self.delete_kvs, args=(shards, key, val))
            # self._delete_pool.submit(self.delete_kvs, args=(shards=shards, key=key, val=val))
            delete_thread.start()

    def delete_kvs(self, shards, key, val):
        header = {"Content-Type": "application/json"}
        params = {"value": val[0], "timestamp": val[1][0]}
        stop_delete_gossip = True
        self.gossip_stop()
        print("*"*100)
        print(shards)
        print("*"*100)
        n = len(shards)
        while stop_delete_gossip:
            for host in shards:
                if host != self.host:
                    try:
                        res = requests.post("http://{ip}/kv-store/keys/delete/{key}".format(ip=host, key=key),
                                            headers=header, json=params)
                        if res.status_code == 200 or res.status_code == 404:
                            n -= 1
                        if n == 1:
                            stop_delete_gossip = False
                            time.sleep(3)
                            self._if_delete = True
                            self.gossip_resume()
                            return
                    except Exception as e:
                        continue

    def allocated_shard(self, key):
        hash_res = hashlib.md5(key.encode("utf-8"))
        index = int(hash_res.hexdigest(), 16) % self.view_size
        return self.nodes_view[index]

    def empty(self):
        self._data = {}

    @staticmethod
    def compare_vector_clock(vector_clock_a, vector_clock_b):
        cmp_timestamp = vector_clock_a[0] > vector_clock_b[0]
        count = 0
        for i in range(1, len(vector_clock_a) - 1):
            if vector_clock_a[i] < vector_clock_b[i]:
                return False
            elif vector_clock_a[i] == vector_clock_b[i]:
                count += 1
        if count == len(vector_clock_a) - 1:
            return cmp_timestamp
        return True

    def update_vector_clock(self):
        index = self.shards.index(self.host) + 1
        self._vector_clock[index] += 1
        self._vector_clock[0] = self.now_time

    def add_vector_clock(self):
        add_num = len(self.shards) - len(self._vector_clock) - 1
        for i in range(0, add_num):
            self._vector_clock.append(0)

    def sync(self, msg_data):
        for i in self.data:
            if i in msg_data:
                if self.compare_vector_clock(self.data[i][1], msg_data[i][1]):
                    msg_data[i] = self.data[i]
                else:
                    self.data[i] = msg_data[i]
        self._data = {**msg_data, **self.data}

    def sync_context(self, context):
        shards_id = context["shards_id"]
        if shards_id != self.shards_id:
            return
        data = context["data"]
        self.sync(data)

    def insert(self, k, v):
        self.update_vector_clock()
        if self._if_delete:
            self._stop_gossip = False
            self.gossip_start()
        self._data.update({k: [v, self._vector_clock.copy()]})

    def update(self, k, v):
        self.update_vector_clock()
        if self._if_delete:
            self._stop_gossip = False
            self.gossip_start()
        self._data.update({k: [v, self._vector_clock.copy()]})

    def read(self, k):
        return self._data.get(k)[0]

    def delete(self, k, value=None, timestamp=None):
        if value:
            data = self.data.get(k)
            if data[0] != value:
                return
            if data[1][0] != timestamp:
                return
        self.data.pop(k)

    def has(self, k):
        return k in self._data.keys()

    def view_update(self, view):
        self._view = view

    def data_update(self, data):
        self._data = data
