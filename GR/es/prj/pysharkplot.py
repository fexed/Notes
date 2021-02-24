#!\bin\python3

import pyshark
import pandas as pd
import matplotlib.pyplot as plt
from shutil import copyfile
import argparse

# Params
def parse_args():
	parser = argparse.ArgumentParser(description='Simple scripts that produces a plot based on an input pcap')
	parser.add_argument('--pcap', type=str, required=True, help='pcap from which the script reads the packets')
	return parser.parse_args()

args = parse_args()
pcap = args.pcap
copyfile(pcap, "tmp.pcap")
capture = pyshark.FileCapture("tmp.pcap")
ip = []
counts = []
for pkt in capture:
	if ("IP" in pkt):
		if (not(pkt.ip.src in ip)):
			ip.append(pkt.ip.src)
			counts.append(0)
		else:
			idx = ip.index(pkt.ip.src)
			n = counts[idx]
			counts[idx] = n + 1
			print ("\r\033[F\033[K" + pkt.ip.src + " " + str(n))
plt.barh(ip, counts)
plt.show()
