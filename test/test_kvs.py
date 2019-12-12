import requests


class TestKvs:

    def __init__(self, ip="localhost", port=13802):
        self.ip = ip
        self.url = "http://{ip}:{port}/kv-store/keys/".format(ip=ip, port=port)
        self.header = {"Content-Type": "application/json"}

    def test_put_insert(self, key, value=None):
        json_form = {"value": value} if value else {}
        print(self.url + str(key))
        res = requests.put(url=self.url + str(key), json=json_form, headers=self.header)
        print(res.status_code)
        print(res.text)

    def test_get(self, key):
        print(self.url + key)
        res = requests.get(url=self.url + key, headers=self.header)
        print(res.status_code)
        if res.status_code != 200:
            raise NameError
        print(res.text)

    def test_check_data(self, n1, n2):
        view = ["10.10.0.2:13800", "10.10.0.3:13800", "10.10.0.4:13800", "10.10.0.5:13800"]
        # if ALL:
        #     for i in view[:n]:
        #         res = requests.get("http://{ip}/kv-store/data".format(ip=i))
        #         print(res.text)
        # else:
        #     res = requests.get("http://{ip}/kv-store/data".format(ip=view[n-1]))
        #     print(res.text)
        res1 = requests.get("http://{ip}/kv-store/data".format(ip=view[n1 - 1]))
        res2 = requests.get("http://{ip}/kv-store/data".format(ip=view[n2 - 1]))
        res3 = {**res1.json(), **res2.json()}
        print(len(res3))

    def test_delete(self, key):
        print(self.url + key)
        res = requests.delete(url=self.url + key, headers=self.header)
        print(res.status_code)
        print(res.text)

    def test_view_change(self):
        view = {"view": "10.10.0.2:13800,10.10.0.3:13800,10.10.0.4:13800,10.10.0.5:13800"}
        res = requests.put("http://localhost:13802/kv-store/view-change", json=view)
        print(res.status_code)
        print(res.json())

    def test_get_count(self, n):
        view = ["10.10.0.2:13800", "10.10.0.3:13800", "10.10.0.4:13800", "10.10.0.5:13800"]
        for i in view[0:n]:
            try:
                res = requests.get("http://{ip}/kv-store/key-count".format(ip=i))
                print(res.status_code)
                print(res.json()["key-count"])
            except:
                continue

    def test_shard(self, n):
        res = requests.get("http://10.10.0.2:13800/kv-store/shards/{shard_id}".format(shard_id=n))
        print(res.status_code)
        print(res.json())

    def test_shards(self):
        res = requests.get("http://10.10.0.2:13800/kv-store/shards")
        print(res.status_code)
        print(res.json())

    def test_gossip(self, n):
        res = requests.put("http://10.10.0.2:13800/kv-store/gossip_status/{stop}".format(stop=n))
        print(res.status_code)

    def test_value(self, n):
        view = ["10.10.0.2:13800", "10.10.0.3:13800", "10.10.0.4:13800", "10.10.0.5:13800"]
        for i in view[0:n]:
            res = requests.get("http://{ip}/kv-store/key-count".format(ip=i))
            print(res.status_code)
            print(res.json())


if __name__ == '__main__':
    test = TestKvs(port=13802)
    test_2 = TestKvs(port=13803)
    # test.test_put_insert("a", "b")
    # test_2.test_put_insert("a", "c")
    # test.test_put_insert("b", "C")
    # test.test_put_insert("a", "c")
    # test.test_get("a")
    # test.test_get_count(4)
    # test.test_shard(0)
    # test.test_shards()
    # test_2.test_view_change()
    # test.test_delete("a")
    # test.test_get("a")
    # test.test_get_data()
    # test.test_put_insert("A", "1")
    # test.test_put_insert("B", "2")
    # test.test_put_insert("C", "3")
    # test.test_put_insert("Djkhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"*100, "k")
    # for i in range(1, 100):
    #     test.test_put_insert(i, i)
    # test_2.test_get(str(1))
    # test_2.test_view_change()
    # test.test_get("Dfafasf")101
    # test.test_delete("Dfafafas")
    # test.test_get_data()
    # for i in range(1, 100):
    #     test.test_delete(str(i))
    # for i in range(1, 101):
    #     test.test_get(str(i))
    # test.test_get(str(1))
    # test.test_get("sampleKey")
    test.test_get_count(2)
    # test.test_check_data(1, 3)
    # test.test_gossip(1)
