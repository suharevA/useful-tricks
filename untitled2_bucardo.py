#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:46:32 2019

@author: A.Suharev
"""

import sys
import os
import subprocess
from datetime import datetime
from time import sleep

# destinations
ping_destinations = {
    'host.bucardo2': '192.168.50.35'  # bucardo2
}


# Pings the hostname to see if the ping succeeds. Returns boolean. True = OK, False = Failure
def check_ping(hostname):
    with open(os.devnull, 'w') as DEVNULL:
        response = subprocess.call("ping -c 1 " + ping_destinations[hostname], shell=True, stdout=DEVNULL, stderr=file_)
        if response == 0:
            return True
        else:
            return False

    # with open(os.devnull, 'w') as DEVNULL:
    #     try:
    #         subprocess.check_call("ping -c 1 " + ping_destinations[hostname], shell=True, stdout=DEVNULL)
    #         file_.write("\n" + date + " PING to " + ping_destinations[hostname] + " is OK.")
    #         file_.flush()
    #         return True
    #     except subprocess.CalledProcessError:
    #         return False


# Returns formatted date string
def getdate():
    return "%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


# Restarts bucardo when ping fails and logs it.
def start_bucardo_watch(hostname):
    has_ping = True
    file_.write("\n\n" + getdate() + " BUCARDO_WATCH to " + ping_destinations[hostname] + " was started.")
    if check_ping(hostname):
        file_.write("\n" + getdate() + " PING to " + ping_destinations[hostname] + " is OK.")
    else:
        file_.write("\n" + getdate() + " PING to " + ping_destinations[hostname] + " FAILS.")
        has_ping = False
    file_.flush()
    while True:
        sleep(5)
        if not check_ping(hostname):  # ping host fail
            if has_ping:  # if ping was OK at start but fails later
                date = getdate()
                file_.write("\n\n" + date + " PING to " + ping_destinations[hostname] + " FAILS.")
                file_.flush()
                has_ping = False
            while True:
                sleep(5)
                if check_ping(hostname):
                    file_.write("\n" + getdate() + " PING to " + ping_destinations[hostname] + " is OK.")
                    has_ping = True
                    sleep(10)
                    file_.write("\n" + getdate() + " RESTARING bucardo." + "\n")
                    file_.flush()
                    response = subprocess.call("bucardo restart", shell=True, stdout=file_, stderr=file_)
                    if response == 0:
                        file_.write(getdate() + " BUCARDO was restarted normally with result code: "
                                    + str(response))
                    else:
                        file_.write(getdate() + " BUCARDO was restarted abnormally with result code: "
                                    + str(response))
                    file_.flush()
                    break


if __name__ == "__main__":
    file_ = open(sys.argv[2], 'a+')  # .py file start parameter [2] - file path /bucardo_replication_log.txt
    # sys.stdout = open('/bucardo_replication_log.txt', 'a+')
    host = sys.argv[1]  # .py file start parameter [1] - hostname ; [0] parameter is the name of .py file
    start_bucardo_watch(host)
    # Example script start command: python2.7 /opt/bucardo_watch2.py host.bucardo2 /bucardo_replication_log.txt
