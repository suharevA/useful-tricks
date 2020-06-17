import subprocess
from time import sleep
from datetime import datetime


def getdate():
    """Date time Now"""
    return "%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-2]


def reload_prg():
    """
    Checks host availability if True
    will execute the command reload ...
    
    """
    reload_ip_pr = ping_ip("add you IP")
    if reload_ip_pr != 0:
        print("reload ...ok!")
        with open("error.txt", "a") as f:
            f.write("successful\t" + getdate() + "\tadd you IP" + '\n')
        subprocess.run('bucardo restart', shell=True)
    return check_ping()


def check_ping():
    """
    endless loop, if false
    write to error.txt file
    """
    target_ip = ping_ip("add you IP")
    while target_ip:
        sleep(1)
        print("Ping Successful")
        return check_ping()
    while True:
        if not target_ip:
            sleep(1)
            print("Ping Unsuccessful")
            with open("error.txt", "a") as f:
                f.write(getdate() + "\tadd you IP" + '\n')
                # write an error to the file and go to the function reload_prg()
        return reload_prg()


def ping_ip(ip_address):
    """
    Ping IP address and return tuple:
    On success:
        * True
    On failure:
        * False
    Command for linux ['ping', '-c', '3', '-n', 'you IP']
    """
    reply = subprocess.run(['ping', ip_address],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           )
    if reply.returncode == 0:
        return True
    else:
        return False


check_ping()
