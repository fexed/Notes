#!\bin\python3

import pyshark
import APIForecast
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
	parser.add_argument('--interval', type=int, required=False, default=30, help='number of seconds of the interval')
	parser.add_argument('--alpha', type=float, required=True, help='alpha parameter for Holt-Winters forecasting')
	parser.add_argument('--beta', type=float, required=True, help='beta parameter for Holt-Winters forecasting')
	parser.add_argument('--gamma', type=float, required=True, help='gamma parameter for Holt-Winters forecasting')
	#TODO: Tradurre meglio
	return parser.parse_args()

# Pcap da cui leggere pacchetti
args = parse_args()
pcap = args.pcap
interval = args.interval
alpha = args.alpha
beta = args.beta
gamma = args.gamma
copyfile(pcap, "tmp.pcap")
capture = pyshark.FileCapture("tmp.pcap", keep_packets=False)

nums = [] # Byte
dates = [] # Timestamps
n = 0 # Temp (più che altro per output)
count = 0 # Conteggio (output)
errors = 0 # Errori (output)
itr = iter(capture) # Iteratore
while True:
	try:
		pkt = next(itr) # Nuovo pacchetto
		count = count + 1 # Contatore
		dates.append(float(pkt.frame_info.time_epoch)) # Timestamp
		n = int(pkt.length)
		nums.append(n) # Byte
		if ("IP" in pkt): # Output se IP, per testing
			print ("\r\033[F\033[K" + "#" + str(count) + " " + pkt.ip.src + " " + str(n))
	except StopIteration: # Fine pcap
		break
	except Exception as ex: # Errore, passo oltre
		errors = errors + 1
		print ("\r\033[F\033[K" + repr(ex))
		pass # Next!
del itr # Pulizia
print("Pacchetti: " + str(count)) # Output
print("\tErrori: " + str(errors))
print("Da " + str(datetime.fromtimestamp(dates[0])) + " a " + str(datetime.fromtimestamp(dates[len(dates) - 1])))
os.remove("tmp.pcap") # Pulizia

# Aggregazione dati su intervalli
intervals = [] # Intervalli orari
everytots = [] # Dato su ogni intervallo
start = -1
sum = 0
j = 0
for i in range(len(dates)):
	if (start == -1):
		start = i
		sum = sum + nums[i]
	else:
		elapsed = datetime.fromtimestamp(dates[i]) - datetime.fromtimestamp(dates[start]) # Guardo quanto è passato
		sum = sum + nums[i] # Sommo i byte
		if (elapsed.total_seconds() > interval): # Dati ogni interval secondi
			j = j + 1
			everytots.append(sum)
			intervals.append(datetime.fromtimestamp(dates[i]))
			lastdate = datetime.fromtimestamp(dates[i])
			sum = 0
			start = -1

for r in range(len(everytots) // 2):
	lastdate = lastdate + timedelta(0, interval)
	intervals.append(lastdate)

while True:
	try:
		res,dev = APIForecast.triple_exponential_smoothing(everytots, len(everytots) // 2, alpha, beta, gamma, len(everytots) // 2)
	except ZeroDivisionError:
		res,dev = APIForecast.triple_exponential_smoothing(everytots, 1, alpha, beta, gamma, len(everytots))

	ubound = []
	lbound = []
	for i in range(len(res)):
		ubound.append(res[i] + 2.5 * dev[i%(len(everytots)//2)])
		lbound.append(res[i] - 2.5 * dev[i%(len(everytots)//2)])

	xfmt = md.DateFormatter('%H:%M') # Etichette plot
	plt.gca().xaxis.set_major_formatter(xfmt) # ^

	plt.plot(intervals[0:len(everytots)], everytots) # Generazione grafico
	plt.plot(intervals[len(everytots):len(intervals)], res[len(everytots):len(intervals)], '--')
	plt.plot(intervals, ubound, ':')
	plt.plot(intervals, lbound, ':')

	plt.xticks(rotation=45) # Ruoto etichette per visibilità
	plt.xlabel("Time")
	plt.ylabel("Bytes")
	plt.title("Bytes from " + pcap + " every " + str(interval) + " seconds with Holt-Winters forecasting")
	plt.show() # Output grafico

	inp = input("Redo graph? Y/N ")
	if (inp.upper() == "Y"):
		alpha = float(input("Input alpha parameter (curr " + str(alpha) + ") "))
		beta = float(input("Input beta parameter (curr " + str(beta) + ") "))
		gamma = float(input("Input gamma parameter (curr " + str(gamma) + ") "))
	else:
		break
