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
    # parser.add_argument('--dataset', type=str, required=False, default="NULL", help='dataset from which the script reads the values')
    # parser.add_argument('--interval', type=int, required=False, default=30, help='number of seconds of the interval')
    parser.add_argument('--alpha', type=float, required=False, default=-1,
                        help='alpha parameter for Holt-Winters forecasting')
    parser.add_argument('--beta', type=float, required=False, default=-1,
                        help='beta parameter for Holt-Winters forecasting')
    parser.add_argument('--gamma', type=float, required=False, default=-1,
                        help='gamma parameter for Holt-Winters forecasting')
    # TODO: Tradurre meglio
    return parser.parse_args()


def sse(values, predictions):
    SSE = 0
    for n, r in zip(values, predictions):
        SSE = SSE + (n - r) ** 2
    return SSE


# Pcap da cui leggere pacchetti
args = parse_args()
# dataset = args.dataset
# interval = args.interval

nums = []
for i in range(5):
    l = Dataset.createDataset()
    for n in l:
        nums.append(n)  # Byte
dates = []  # Timestamps
n = 0  # Temp (più che altro per output)
count = 0  # Conteggio (output)
errors = 0  # Errori (output)
now = datetime.combine(datetime.today(), time.min)
for n in nums:
    count = count + 1
    dates.append(now)
    now = now + timedelta(minutes=5)
    print("\r\033[F\033[K" + "#" + str(count) + " " + str(n) + "B")

print("Dati: " + str(count))  # Output
print("-\tErrori: " + str(errors))
print("Da " + dates[0].strftime("%Y-%m-%d %H:%M:%S") + " a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

# TODO
alpha = args.alpha
beta = args.beta
gamma = args.gamma
# previsione a seconda dei parametri inseriti
# se -1 tutti e tre, fitting automatico

lastdate = dates[len(dates) - 1]

if alpha != -1 and beta != -1 and gamma != -1:  # Holt-Winters
    res, dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    SSE = sse(nums, res)
    MSE = SSE / count

    print("Holt-Winters fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    ubound = []
    lbound = []
    for i in range(len(res)):
        ubound.append(res[i] + 2.5 * dev[i % 288])
        lbound.append(res[i] - 2.5 * dev[i % 288])

    xfmt = md.DateFormatter('%Y-%m-%d %H:%M')  # Etichette plot
    plt.gca().xaxis.set_major_formatter(xfmt)  # ^

    plt.plot(dates[0:count], nums)  # Generazione grafico
    plt.plot(dates, res, '--')
    plt.plot(dates, ubound, ':')
    plt.plot(dates, lbound, ':')

    plt.xticks(rotation=45)  # Ruoto etichette per visibilità
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Bytes from generated dataset every 5 minutes\nHolt-Winters forecasting (alpha = " + str(
        alpha) + ", beta = " + str(beta) + ", gamma = " + str(gamma) + ")\nSSE = " + str(SSE) + ", MSE = " + str(MSE))
    plt.show()  # Output grafico
elif alpha != -1 and beta != -1:  # Double Exponential
    res = APIForecast.double_exponential_smoothing(nums, alpha, beta)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    print("Double Exponential fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%Y-%m-%d %H:%M')  # Etichette plot
    plt.gca().xaxis.set_major_formatter(xfmt)  # ^

    plt.plot(dates[0:count], nums)  # Generazione grafico
    plt.plot(dates[count:], res[count:], '--')

    plt.xticks(rotation=45)  # Ruoto etichette per visibilità
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Bytes from generated dataset every 5 minutes\nDouble Exponential forecasting (alpha = " + str(
        alpha) + ", beta = " + str(beta) + ")")
    plt.show()  # Output grafico
elif alpha != -1:  # Single Exponential
    res = APIForecast.exponential_smoothing(nums, alpha)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    print("Single Exponential fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%Y-%m-%d %H:%M')  # Etichette plot
    plt.gca().xaxis.set_major_formatter(xfmt)  # ^

    plt.plot(dates[0:count], nums)  # Generazione grafico
    plt.plot(dates[count:], res[count:], '--')

    plt.xticks(rotation=45)  # Ruoto etichette per visibilità
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title(
        "Bytes from generated dataset every 5 minutes\nSingle Exponential forecasting (alpha = " + str(alpha) + ")")
    plt.show()  # Output grafico
else:  # Fitting
    print("Fitting data...")
    alpha, beta, gamma, sse = APIForecast.fit(nums)

    print("Holt-Winters fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))
    res, dev = APIForecast.triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    SSE = sse(nums, res)
    MSE = SSE / count
    strSSE = "{:.5f}".format(SSE)
    strMSE = "{:.5f}".format(MSE)

    print("Holt-Winters fino a " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    ubound = []
    lbound = []
    for i in range(len(res)):
        ubound.append(res[i] + 2.5 * dev[i % 288])
        lbound.append(res[i] - 2.5 * dev[i % 288])

    xfmt = md.DateFormatter('%Y-%m-%d %H:%M')  # Etichette plot
    plt.gca().xaxis.set_major_formatter(xfmt)  # ^

    plt.plot(dates[0:count], nums)  # Generazione grafico
    plt.plot(dates, res, '--')
    plt.plot(dates, ubound, ':')
    plt.plot(dates, lbound, ':')

    plt.xticks(rotation=45)  # Ruoto etichette per visibilità
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Bytes from generated dataset every 5 minutes\nHolt-Winters forecasting (fitted alpha = " + stralpha +
              ", beta = " + strbeta + ", gamma = " + strgamma + ")\nSSE = " + strSSE + ", MSE = " + strMSE)
    plt.show()  # Output grafico