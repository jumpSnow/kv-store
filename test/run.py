import os


def sudo_run(password, command):
    os.system("echo {pwd}|sudo -S {cmd}".format(pwd=password, cmd=command))


if __name__ == '__main__':
    pwd = ""
    sudo_run(pwd, command="docker stop /node1")
    sudo_run(pwd, command="docker stop /node2")
    sudo_run(pwd, command="docker stop /node3")
    sudo_run(pwd, command="docker stop /node4")
    sudo_run(pwd, command="docker rm /node1")
    sudo_run(pwd, command="docker rm /node2")
    sudo_run(pwd, command="docker rm /node3")
    sudo_run(pwd, command="docker rm /node4")
    sudo_run(pwd, command="docker network create --subnet=10.10.0.0/16 kv_subnet")
    # sudo_run(pwd, command="docker network create --subnet=10.10.0.0/16 kv_subnet2")
    sudo_run(pwd, command="docker build -t cse138/kv-store:4.0 /home/jumpsnow/PycharmProjects/-cse138_assignment4")
    # sudo_run(pwd, command="docker build -t kv-store:4.0 /home/jumpsnow/PycharmProjects/-cse138_assignment4")