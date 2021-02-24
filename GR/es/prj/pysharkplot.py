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
nums = []
dates = []
n = 0
try:
	for pkt in capture:
		n = n + int(pkt.length)
		nums.append(n)
		dates.append(float(pkt.frame_info.time_epoch))
		if ("IP" in pkt):
			print ("\r\033[F\033[K" + pkt.ip.src + " " + str(n))
except:
	print("\r\033[F\033[K" + "Err")
plt.plot(dates, nums)
plt.show()
