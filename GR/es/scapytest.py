#!\bin\python3

from scapy.all import *
from collections import Counter
import argparse

# Params parsing
def parse_args():
    parser = argparse.ArgumentParser(
        description='Simple script that captures packets and writes trivial data onto a RRD and a InfluxDB')
    parser.add_argument('--interface', type=str, required=False,
                        default='wlp1s0',
                        help='interface from which to sniff packets')
    return parser.parse_args()

def captured(packet):
    global pkts
    global packet_counts
    pkts += 1
    try:
        key = tuple(sorted([packet[0][1].src, packet[0][1].dst]))
        packet_counts.update([key])
        return f"\r\033[F\033[K #{sum(packet_counts.values())}: {packet[0][1].src} > {packet[0][1].dst}"
    except:
        return ""

packet_counts = Counter()
args = parse_args()
iface = args.interface
print("Sniffing on " + iface)
pkts = 0
sniff(prn=captured)
print(str(pkts))
print("\n".join(f"{f'{key[0]} - {key[1]}'}\t\t{count} packets" for key, count in packet_counts.items()))
