#!\bin\python3

import pyshark
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from shutil import copyfile
import argparse
from inspect import getmembers
from datetime import datetime, timedelta
import os

# Params
def parse_args():
	parser = argparse.ArgumentParser(description='Simple scripts that produces a plot based on an input pcap')
	parser.add_argument('--pcap', type=str, required=True, help='pcap from which the script reads the packets')
	return parser.parse_args()

args = parse_args()
pcap = args.pcap
copyfile(pcap, "tmp.pcap")
capture = pyshark.FileCapture("tmp.pcap", keep_packets=False)
nums = []
dates = []
n = 0
count = 0
errors = 0
itr = iter(capture)
while True:
	try:
		pkt = next(itr)
		count = count + 1
		dates.append(float(pkt.frame_info.time_epoch))
		n = int(pkt.length)
		nums.append(n)
		if ("IP" in pkt):
			print ("\r\033[F\033[K" + "#" + str(count) + " " + pkt.ip.src + " " + str(n))
	except StopIteration:
		break
	except Exception as ex:
		errors = errors + 1
		print ("\r\033[F\033[K" + repr(ex))
		pass
del itr
print("Pacchetti: " + str(count))
print("\tErrori: " + str(errors))
print("Da " + str(datetime.fromtimestamp(dates[0])) + " a " + str(datetime.fromtimestamp(dates[len(dates) - 1])))
os.remove("tmp.pcap")

intervals = []
everytots = []
start = -1
sum = 0
j = 0
for i in range(len(dates)):
	if (start == -1):
		start = i
		sum = sum + nums[i]
	else:
		elapsed = datetime.fromtimestamp(dates[i]) - datetime.fromtimestamp(dates[start])
		sum = sum + nums[i]
		if (elapsed.total_seconds() > 30):
			j = j + 1
			everytots.append(sum)
			intervals.append(datetime.fromtimestamp(dates[i]))
			sum = 0
			start = -1
xfmt = md.DateFormatter('%H:%M')
plt.gca().xaxis.set_major_formatter(xfmt)
plt.plot(intervals, everytots)
plt.xticks(rotation=45)
plt.show()
