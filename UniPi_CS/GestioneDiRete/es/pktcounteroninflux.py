#! /usr/bin/python3

# ####
# Author: Federico Matteoni
# Simple script that captures packets and writes
# trivial data onto a RRD and a InfluxDB
#
# Installation
# apt install python3 python3-pip rrdtool librrd8 librrd-dev
# pip3 install pyshark
# pip3 install rrdtool
# pip3 install influxdb
#
# Usage
# python3 pktcounter.py [--interface <interface>]
#                       [--port <InfluxDB server port>]
#                       [--adminname <InfluxDB admin username>]
#                       [--adminpwd <InfluxDB admin password>]
#                       [--username <InfluxDB user username>]
#                       [--userpwd <InfluxDB user password>]
# ####

import pyshark
import rrdtool as rrd
import signal
import sys
import argparse
from datetime import datetime
from influxdb import InfluxDBClient
from threading import Timer
from time import sleep

# Timer that ticks every interval seconds and execs function
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

# Signal handler to build the rrd graph and stop the timer
def signal_handler(sig, frame):
    rt.stop()
    graphv_args = [
        rrdname + '.png',
        '--title', "Packets count",
        '--start', 'now-1h',
        '--end', 'now',
        '--slope-mode',
        '--font', 'DEFAULT:7:',
        'DEF:PKT=' + rrdname + ':packets:MAX',
        'LINE1:PKT#0000FF:PKT',
        'GPRINT:PKT:LAST:Ultimo valore\: %5.2lf'
    ]
    print("\nGraph image: " + rrdname + ".png")
    rrd.graphv(*graphv_args)
    print(client.query("select number from packets"))
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Params parsing
def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple script that captures packets and writes trivial data onto a RRD and a InfluxDB')
    parser.add_argument('--interface', type=str, required=False,
                        default='eth0',
                        help='interface from which to sniff packets')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB'),
    parser.add_argument('--adminname', type=str, required=False, default='root',
                        help='admin username of InfluxDB')
    parser.add_argument('--adminpwd', type=str, required=False, default='root',
                        help='admin password of InfluxDB')
    parser.add_argument('--username', type=str, required=False, default='usr',
                        help='username of InfluxDB')
    parser.add_argument('--userpwd', type=str, required=False, default='pwd',
                        help='user password of InfluxDB')
    return parser.parse_args()

args = parse_args()
iface = args.interface
aname = args.adminname
apwd = args.adminpwd
uname = args.username
upwd = args.userpwd

oldpkts = 0
# Timed job that puts data into RRD and InfluxDB
def doJob():
    global pkts
    global oldpkts
    print("\r\033[F\033[K Captured: " + str(pkts))
    rrd.update([rrdname, "--template", "packets", "N:" + str(pkts)])
    newpkts = pkts - oldpkts
    oldpkts = pkts
    json_body = [
        {
            "measurement": "packets",
            "time": datetime.now(),
            "fields": {
                "number": newpkts
            }
        }
    ]
    client.write_points(json_body)

# Starting the timed job
rt = RepeatedTimer(1, doJob)

# RRD database
rrdname = iface + "packets.rrd"
try:
    f = open(rrdname)
    f.close()
except FileNotFoundError:
    print("Creating RRD \"" + rrdname + "\"")
    rrd.create(
        rrdname,
        "--start", "now",
        "--step", "1",
        "RRA:MAX:0.5:1:3600",
        "DS:packets:COUNTER:10:0:9999999")
print("Using \"" + rrdname + "\"")

# Influx database
influxname = iface + "packetsdb"
client = InfluxDBClient('127.0.0.1', '8086', aname, apwd, influxname)
client.create_database(influxname)
client.create_retention_policy('awesome_policy', '3d', 3, default=True)
client.switch_user(uname, upwd)

# Trivial capture and count
pkts = 0
def captured(packet):
    global pkts
    pkts += 1

capture = pyshark.LiveCapture(interface=iface)

capture.apply_on_packets(captured)
