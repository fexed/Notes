#!\bin\python3

import pyshark
import APIForecast
import Dataset
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from shutil import copyfile
import argparse
from inspect import getmembers
from datetime import datetime, timedelta, time
import os

# Params
def parse_args():
	parser = argparse.ArgumentParser(description='Simple scripts that produces a plot based on an input dataset')
	#parser.add_argument('--dataset', type=str, required=False, default="NULL", help='dataset from which the script reads the values')
	#parser.add_argument('--interval', type=int, required=False, default=30, help='number of seconds of the interval')
	parser.add_argument('--alpha', type=float, required=True, help='alpha parameter for Holt-Winters forecasting')
	parser.add_argument('--beta', type=float, required=True, help='beta parameter for Holt-Winters forecasting')
	parser.add_argument('--gamma', type=float, required=True, help='gamma parameter for Holt-Winters forecasting')
	#TODO: Tradurre meglio
	return parser.parse_args()

# Pcap da cui leggere pacchetti
args = parse_args()
#dataset = args.dataset
#interval = args.interval
alpha = args.alpha
beta = args.beta
gamma = args.gamma

nums = []
for i in range(5):
	l = Dataset.createDataset()
	for n in l:
		nums.append(n) # Byte
dates = [] # Timestamps
n = 0 # Temp (più che altro per output)
count = 0 # Conteggio (output)
errors = 0 # Errori (output)
now = datetime.combine(datetime.today(), time.min)
for n in nums:
	count = count + 1
	dates.append(now)
	now = now + timedelta(minutes=5)
	print ("\r\033[F\033[K" + "#" + str(count) + " " + str(n) + "B")

print("Dati: " + str(count)) # Output
print("-\tErrori: " + str(errors))
print("Da " + dates[0].strftime("%Y-%m-%d %H:%M:%S") + " a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

# Aggregazione dati su intervalli
intervals = dates # Intervalli orari
everytots = nums # Dato su ogni intervallo
lastdate = dates[len(dates) - 1]

try:
	res,dev = APIForecast.triple_exponential_smoothing(everytots, 288, alpha, beta, gamma, 288)
except ZeroDivisionError:
	res,dev = APIForecast.triple_exponential_smoothing(everytots, 288, alpha, beta, gamma, 288)

for f in range(288):
	lastdate = lastdate + timedelta(minutes=5)
	intervals.append(lastdate)

print("Holt-Winters fino a " + intervals[len(intervals) - 1].strftime("%Y-%m-%d %H:%M:%S"))
ubound = []
lbound = []
for i in range(len(res)):
	ubound.append(res[i] + 2.5 * dev[i%(len(everytots)//2)])
	lbound.append(res[i] - 2.5 * dev[i%(len(everytots)//2)])

xfmt = md.DateFormatter('%H:%M') # Etichette plot
plt.gca().xaxis.set_major_formatter(xfmt) # ^

plt.plot(intervals[0:len(everytots)], everytots) # Generazione grafico
plt.plot(intervals[len(nums):], res[len(nums):], '--')
plt.plot(intervals, ubound, ':')
plt.plot(intervals, lbound, ':')

plt.xticks(rotation=45) # Ruoto etichette per visibilità
plt.xlabel("Time")
plt.ylabel("Bytes")
plt.title("Bytes from generated dataset every 5 minutes\nHolt-Winters forecasting (alpha = " + str(alpha) + ", beta = " + str(beta) + ", gamma = " + str(gamma) + ")")
plt.show() # Output grafico
