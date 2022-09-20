import subprocess
import time


def ping_ip(hosts):
    """
    return True / False
    """
    for host in hosts.split():
        time.sleep(0.5)
        reply = subprocess.run(['ping', '-c', '1', '-n', host],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               encoding='utf-8')
        if reply.returncode == 0:
            print(True, host)
        else:
            print(False, host)

# Список хостов
hosts = """

"""
ping_ip(hosts)
