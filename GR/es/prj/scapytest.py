#!\bin\python3

from scapy.all import *
from scapy.utils import PcapWriter
from collections import Counter
from datetime import datetime
import argparse

dt = datetime.now()
pcap = str(dt.year) + str(dt.month) + str(dt.day) + "_pkts.pcap"
pktdump = PcapWriter(pcap, append=True, sync=True)

# Params parsing
def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple script that captures packets and writes trivial data onto a dated pcap')
    parser.add_argument('--interface', type=str, required=False,
                        default='wlp1s0',
                        help='interface from which to sniff packets')
    return parser.parse_args()

def captured(packet):
    global pkts
    global packet_counts
    pkts += 1
    pktdump.write(packet)
    try:
        return f"\r\033[F\033[K #{str(pkts)}: {packet[0][1].src} -> {packet[0][1].dst}"
    except Exception as ex:
        return f"\r\033[F\033[K" + repr(ex)

packet_counts = Counter()
args = parse_args()
iface = args.interface
print("Sniffing on " + iface)
pkts = 0
sniff(prn=captured)
print(str(pkts) + " packets")
