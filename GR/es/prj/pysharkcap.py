#!\bin\python3

import pyshark
import argparse
from datetime import datetime

# Params parsing
def parse_args():
	parser = argparse.ArgumentParser(description='Simple script that captures packets and writes trivial data onto a dated pcap')
	parser.add_argument('--interface', type=str, required=False, default='wlp1s0', help='interface from which to sniff packets')
	return parser.parse_args()

dt = datetime.now()
if (dt.month < 10):
	m = "0" + str(dt.month)
else:
	m = str(dt.month)
if (dt.day < 10):
	d = "0" + str(dt.day)
else:
	d = str(dt.day)
pcap = str(dt.year) + m + d + "_pkts.pcap"

args = parse_args()
iface = args.interface # Interfaccia d'ascolto, default wlp1s0
cap = pyshark.LiveCapture(interface=iface, output_file=pcap)
print("Capturing on " + iface + "\n")
i = 0
for rawpkt in cap.sniff_continuously():
	i = i + 1;
	if hasattr(rawpkt, 'ip'):
		print("\r\033[F\033[K " + str(i) + ". " + rawpkt.ip.src + " " + str(rawpkt.sniff_time))
