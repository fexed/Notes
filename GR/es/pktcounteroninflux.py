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
# python3 pktcounter.py interface
# ####

import pyshark
import rrdtool as rrd
import signal
import sys
import argparse
from datetime import datetime
from influxdb import InfluxDBClient

# Signal handler
def signal_handler(sig, frame):
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

# Params check
def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple script that captures packets and writes trivial data onto a RRD and a InfluxDB')
    parser.add_argument('--interface', type=str, required=False,
                        default='eth0',
                        help='interface from which to sniff packets')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB')
    return parser.parse_args()

args = parse_args()
iface = args.interface

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
client = InfluxDBClient('127.0.0.1', '8086', 'root', 'root', influxname)
client.create_database(influxname)
client.create_retention_policy('awesome_policy', '3d', 3, default=True)
client.switch_user('usr', 'pwd')

pkts = 0
def captured(packet):
    global pkts
    pkts += 1
    print("\r\033[F\033[K Captured: " + str(pkts))
    rrd.update([rrdname, "--template", "packets", "N:" + str(pkts)])
    json_body = [
        {
            "measurement": "packets",
            "time": datetime.now(),
            "fields": {
                "number": pkts
            }
        }
    ]
    client.write_points(json_body)

capture = pyshark.LiveCapture(interface=iface)

capture.apply_on_packets(captured)
