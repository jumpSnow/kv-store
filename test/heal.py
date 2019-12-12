import os


def sudo_run(password, command):
    os.system("echo {pwd}|sudo -S {cmd}".format(pwd=password, cmd=command))


if __name__ == '__main__':
    pwd = ""
    sudo_run(pwd, command="docker network disconnect kv_subnet2 node1")
    sudo_run(pwd, command="docker network connect kv_subnet node1")
