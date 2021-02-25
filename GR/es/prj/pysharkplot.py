#!\bin\python3

import pyshark
import pandas as pd
import matplotlib.pyplot as plt
from shutil import copyfile
import argparse
from inspect import getmembers
from datetime import datetime

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
count = 0
itr = iter(capture)
try:
	while True:
		try:
			pkt = next(itr)
			count = count + 1
			dates.append(float(pkt.frame_info.time_epoch))
			n = int(pkt.length)
			nums.append(n)
			if ("IP" in pkt):
				print ("\r\033[F\033[K" + pkt.ip.src + " " + str(n))
		except StopIteration:
			break
		except:
			print ("\r\033[F\033[K" + "Error")
except StopIteration:
	pass
finally:
	del itr
print("Pacchetti: " + str(count))
print("Da " + str(datetime.fromtimestamp(dates[0])) + " a " + str(datetime.fromtimestamp(dates[len(dates) - 1])))
plt.plot(dates, nums)
plt.show()
