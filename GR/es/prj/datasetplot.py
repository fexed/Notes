#!\bin\python3

import pyshark
import APIForecast
import Dataset
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import random
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
	parser.add_argument('--alpha', type=float, required=False, default=-1, help='alpha parameter for Holt-Winters forecasting')
	parser.add_argument('--beta', type=float, required=False, default=-1, help='beta parameter for Holt-Winters forecasting')
	parser.add_argument('--gamma', type=float, required=False, default=-1, help='gamma parameter for Holt-Winters forecasting')
	#TODO: Tradurre meglio
	return parser.parse_args()

def SSE(values, predictions):
	SSE = 0
	for n, r in zip(values, predictions):
		SSE = SSE + (n - r)**2
	return SSE

# Pcap da cui leggere pacchetti
args = parse_args()
#dataset = args.dataset
#interval = args.interval

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

# TODO
alpha = args.alpha
beta = args.beta
gamma = args.gamma
# previsione a seconda dei parametri inseriti
# se -1 tutti e tre, fitting automatico

lastdate = dates[len(dates) - 1]

if (alpha != -1 and beta != -1 and gamma != -1): #Holt-Winters
	res,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)

	for f in res[len(nums):]:
		lastdate = lastdate + timedelta(minutes=5)
		dates.append(lastdate)

	SSE = SSE(nums, res)
	MSE = SSE / count

	print("Holt-Winters fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

	ubound = []
	lbound = []
	for i in range(len(res)):
		ubound.append(res[i] + 2.5 * dev[i%288])
		lbound.append(res[i] - 2.5 * dev[i%288])

	xfmt = md.DateFormatter('%Y-%m-%d %H:%M') # Etichette plot
	plt.gca().xaxis.set_major_formatter(xfmt) # ^

	plt.plot(dates[0:count], nums) # Generazione grafico
	plt.plot(dates, res, '--')
	plt.plot(dates, ubound, ':')
	plt.plot(dates, lbound, ':')

	plt.xticks(rotation=45) # Ruoto etichette per visibilità
	plt.xlabel("Time")
	plt.ylabel("Bytes")
	plt.title("Bytes from generated dataset every 5 minutes\nHolt-Winters forecasting (alpha = " + str(alpha) + ", beta = " + str(beta) + ", gamma = " + str(gamma) + ")\nSSE = " + str(SSE) + ", MSE = " + str(MSE))
	plt.show() # Output grafico
elif (alpha != -1 and beta != -1): # Double Exponential
	res = APIForecast.double_exponential_smoothing(nums, alpha, beta)

	for f in res[len(nums):]:
		lastdate = lastdate + timedelta(minutes=5)
		dates.append(lastdate)

	print("Double Exponential fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

	xfmt = md.DateFormatter('%Y-%m-%d %H:%M') # Etichette plot
	plt.gca().xaxis.set_major_formatter(xfmt) # ^

	plt.plot(dates[0:count], nums) # Generazione grafico
	plt.plot(dates[count:], res[count:], '--')

	plt.xticks(rotation=45) # Ruoto etichette per visibilità
	plt.xlabel("Time")
	plt.ylabel("Bytes")
	plt.title("Bytes from generated dataset every 5 minutes\nDouble Exponential forecasting (alpha = " + str(alpha) + ", beta = " + str(beta) + ")")
	plt.show() # Output grafico
elif (alpha != -1): # Single Exponential
	res = APIForecast.exponential_smoothing(nums, alpha)

	for f in res[len(nums):]:
		lastdate = lastdate + timedelta(minutes=5)
		dates.append(lastdate)

	print("Single Exponential fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

	xfmt = md.DateFormatter('%Y-%m-%d %H:%M') # Etichette plot
	plt.gca().xaxis.set_major_formatter(xfmt) # ^

	plt.plot(dates[0:count], nums) # Generazione grafico
	plt.plot(dates[count:], res[count:], '--')

	plt.xticks(rotation=45) # Ruoto etichette per visibilità
	plt.xlabel("Time")
	plt.ylabel("Bytes")
	plt.title("Bytes from generated dataset every 5 minutes\nSingle Exponential forecasting (alpha = " + str(alpha) + ")")
	plt.show() # Output grafico
else: # Fitting
	print("Fitting alpha, beta, gamma parameters for Holt-Winter forecasting")

	# Parametri di partenza
	alpha, beta, gamma = round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3)
	print("Starting with\n\talpha = " + str(alpha) + "\n\tbeta = " + str(beta) + "\n\tgamma = " + str(gamma))

	# Parametri Nelder-Mead
	a, g, r, s = 1., 2., -0.5, 0.5 # Parametri standard (Wikipedia)
	step = 0.01 # Step di modifica dei parametri
	noimprovthr = 10e-6 # Soglia di non miglioramento
	noimprovbrk = 10 # Ferma dopo 10 cicli dove non migliora abbastanza

	noimprov = 0 # Contatore di non miglioramento
	prev,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
	prevbest = SSE(nums, prev) # Funzione obiettivo
	res = [[[alpha, beta, gamma], prevbest]]

	alpha += step
	prev,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
	res.append([[alpha, beta, gamma], SSE(nums, prev)])
	beta += step
	prev,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
	res.append([[alpha, beta, gamma], SSE(nums, prev)])
	gamma += step
	prev,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
	res.append([[alpha, beta, gamma], SSE(nums, prev)])

	iterazioni = 0
	while True:
		# Ordinamento
		res.sort(key = lambda x : x[1])
		best = res[0][1]
		print("Migliore fin'ora: " + str(best))

		# TODO check max iterazioni
		iterazioni += 1

		if best < prevbest - noimprovthr:
			noimprov = 0
			prevbest = best
		else:
			noimprov += 1
		if noimprov >= noimprovbrk:
			break # grafico

		# Centroide
		alpha0, beta0, gamma0 = 0., 0., 0.
		for t in res[:-1]:
			alpha0 += t[0][0] / (len(res) - 1)
			beta0 += t[0][1] / (len(res) - 1)
			gamma0 += t[0][2] / (len(res) - 1)

		# Riflessione
		alphar = abs(alpha0 + a*(alpha0 - res[-1][0][0]))
		if alphar > 1: alphar = 1
		betar = abs(beta0 + a*(beta0 - res[-1][0][1]))
		if betar > 1: betar = 1
		gammar = abs(gamma0 + a*(gamma0 - res[-1][0][2]))
		if gammar > 1: gammar = 1
		rSSE = SSE(nums, APIForecast.triple_exponential_smoothing(nums, 288, alphar, betar, gammar, 288)[0])
		if res[0][1] <= rSSE < res[-2][1]:
			del res[-1]
			res.append([[alphar, betar, gammar], rSSE])
			continue

		# Espansione
		if rSSE < res[0][1]:
			alphae = abs(alpha0 + g*(alpha0 - res[-1][0][0]))
			if alphae > 1: alphae = 1
			betae = abs(beta0 + g*(beta0 - res[-1][0][1]))
			if betae > 1: betae = 1
			gammae = abs(gamma0 + g*(gamma0 - res[-1][0][2]))
			if gammae > 1: gammae = 1
			eSSE = SSE(nums, APIForecast.triple_exponential_smoothing(nums, 288, alphae, betae, gammae, 288)[0])
			if eSSE < rSSE:
				del res[-1]
				res.append([[alphae, betae, gammae], eSSE])
				continue
			else:
				del res[-1]
				res.append([[alphar, betar, gammar], rSSE])
				continue

		# Contrazione
		alphac = abs(alpha0 + r*(alpha0 - res[-1][0][0]))
		if alphac > 1: alphac = 1
		betac = abs(beta0 + r*(beta0 - res[-1][0][1]))
		if betac > 1: betac = 1
		gammac = abs(gamma0 + r*(gamma0 - res[-1][0][2]))
		if gammac > 1: gammac = 1
		cSSE = SSE(nums, APIForecast.triple_exponential_smoothing(nums, 288, alphac, betac, gammac, 288)[0])
		if cSSE < res[-1][1]:
			del res[-1]
			res.append([[alphac, betac, gammac], cSSE])
			continue

		# Riduzione
		alpha1 = res[0][0][0]
		beta1 = res[0][0][1]
		gamma1 = res[0][0][2]
		nres = []
		for t in res:
			ridalpha = abs(alpha1 + s*(t[0][0] - alpha1))
			if ridalpha > 1: ridalpha = 1
			ridbeta = abs(beta1 + s*(t[0][1] - beta1))
			if ridbeta > 1: ridbeta = 1
			ridgamma = abs(gamma1 + s*(t[0][2] - gamma1))
			if ridgamma > 1: ridgamma = 1
			ridSSE = SSE(nums, APIForecast.triple_exponential_smoothing(nums, 288, ridalpha, ridbeta, ridgamma, 288)[0])
			nres.append([[ridalpha, ridbeta, ridgamma], ridSSE])
		res = nres


	alpha = res[0][0][0]
	beta = res[0][0][1]
	gamma = res[0][0][2]
	stralpha = "{:.5f}".format(alpha)
	strbeta = "{:.5f}".format(beta)
	strgamma = "{:.5f}".format(gamma)
	print("Dopo " + str(iterazioni) + " iterazioni ho trovato:\n\talpha = " + stralpha + "\n\tbeta = " + strbeta + "\n\tgamma = " + strgamma)

	res,dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)

	for f in res[len(nums):]:
		lastdate = lastdate + timedelta(minutes=5)
		dates.append(lastdate)

	SSE = SSE(nums, res)
	MSE = SSE / count
	strSSE = "{:.5f}".format(SSE)
	strMSE = "{:.5f}".format(MSE)

	print("Holt-Winters fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

	ubound = []
	lbound = []
	for i in range(len(res)):
		ubound.append(res[i] + 2.5 * dev[i%288])
		lbound.append(res[i] - 2.5 * dev[i%288])

	xfmt = md.DateFormatter('%Y-%m-%d %H:%M') # Etichette plot
	plt.gca().xaxis.set_major_formatter(xfmt) # ^

	plt.plot(dates[0:count], nums) # Generazione grafico
	plt.plot(dates, res, '--')
	plt.plot(dates, ubound, ':')
	plt.plot(dates, lbound, ':')

	plt.xticks(rotation=45) # Ruoto etichette per visibilità
	plt.xlabel("Time")
	plt.ylabel("Bytes")
	plt.title("Bytes from generated dataset every 5 minutes\nHolt-Winters forecasting (fitted alpha = " + stralpha + ", beta = " + strbeta + ", gamma = " + strgamma + ")\nSSE = " + strSSE + ", MSE = " + strMSE)
	plt.show() # Output grafico
