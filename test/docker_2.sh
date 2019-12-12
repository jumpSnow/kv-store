
# example node addresses
addr1="10.10.0.2:13800"
addr2="10.10.0.3:13800"
addr3="10.10.0.4:13800"
addr4="10.10.0.5:13800"

# convenience variables
initial_full_view="${addr1},${addr2}"
full_view=${initial_full_view},${addr3},${addr4}

read -d '' view_change_data << "VIEW_STR"
{
    "causal-context": {},
    "repl-factor"   : 2,
    "view"          : [
        "10.10.0.2:13800",
        "10.10.0.3:13800",
        "10.10.0.4:13800",
        "10.10.0.5:13800"
    ]
}
VIEW_STR

docker run --name="node2"        --net=kv_subnet     \
           --ip=10.10.0.3        -p 13803:13800      \
           -e ADDRESS="${addr2}"                     \
           -e VIEW=${initial_full_view}              \
           -e REPL_FACTOR=2                          \
           -e PYTHONUNBUFFERED=1                     \
           kv-store:4.0