#!\bin\python3

import pyshark
import pandas as pd
import matplotlib.pyplot as plt
from shutil import copyfile

copyfile("pkts.pcap", "pkts_tmp.pcap")
capture = pyshark.FileCapture("pkts.pcap")
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
