curl -s --request PUT --header "Content-Type: application/json" --write-out "\n%{http_code}\n" --data '{"value":"1"}' http://localhost:13802/kv-store/view-change
curl -s --request PUT --header "Content-Type: application/json" --write-out "\n%{http_code}\n" --data '{"view":"10.10.0.2:13800,10.10.0.3:13800,10.10.0.4:13800"}' http://localhost:13802/kv-store/view-change
curl -s --request PUT --header "Content-Type: application/json" --write-out "\n%{http_code}\n" --data '{"view":"10.10.0.2:13800,10.10.0.3:13800,10.10.0.4:13800"}' http://localhost:13802/kv-store/view-change

curl -s --request PUT --header "Content-Type: application/json" --write-out "\n%{http_code}\n" --data '{"view":"10.10.0.2:13800,10.10.0.3:13800,10.10.0.4:13800"}' http://localhost:13802/kv-store/view-change
