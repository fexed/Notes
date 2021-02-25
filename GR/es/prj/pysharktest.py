#!\bin\python3

import pyshark
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
list = []
try:
	for pkt in capture:
		for layer in pkt.layers:
			print("\r\033[F\033[K" + layer.layer_name)
			if (not(layer.layer_name in list)):
				list.append(layer.layer_name)
except:
	print("\r\033[F\033[K Error")
for layer in list:
	print("- " + str(layer))
