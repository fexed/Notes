import pyshark
import APIForecast as api
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime, timedelta, time
from random import *

# Custom print and input
def inputYellow(str):
    CEND = '\33[0m'
    CYELLOW = '\33[33m'
    r = input(CYELLOW + str + CEND)
    return r

def printYellow(str):
    CEND = '\33[0m'
    CYELLOW = '\33[33m'
    print(CYELLOW + str + CEND)

def printGreen(str):
    CEND = '\33[0m'
    CGREEN  = '\33[32m'
    print(CGREEN + str + CEND)

# Funzioni per la generazione di grafici
def myplot(res, series, intervals):
    # TODO da correggere le etichette del tempo
    xfmt = md.DateFormatter('%d %H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)
    plt.plot(intervals[0:len(series)],series)
    plt.plot(intervals[0:len(res)], res, '--')
    plt.xticks(rotation = 45)
    plt.xlabel("Time")
    plt.ylabel("KBytes")
    plt.show()

def myplotHW(res, dev, series, intervals, ubound, lbound):
    xfmt = md.DateFormatter('%d %H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)
    plt.xticks(rotation = 45)
    plt.xlabel("Time")
    plt.ylabel("KBytes")
    plt.plot(intervals[0:len(series)],series)
    plt.plot(intervals[0:len(res)], res, '--')
    plt.plot(intervals[0:len(series)], ubound[0:len(series)], ':')
    plt.plot(intervals[0:len(series)], lbound[0:len(series)], ':')
    
    plt.show()

# Creazione del dataset
def createDataset():
    dataset = []
    for i in range(108): # 00 to 09
        dataset.append(randint(0,10))
    for i in range(48): # 09 to 13 (Work)
        elem = randint(30,90)
        dataset.append(elem)
    for i in range(12): # 13 to 14
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(48): # 14 to 18 (Work)
        elem = randint(40,80)
        dataset.append(elem)
    for i in range(36): # 18 to 21
        elem = randint(0,10)
        dataset.append(elem)
    for i in range(24): # 21 to 23 (It's time for Netflix)
        elem = randint(100,350)
        dataset.append(elem)
    for i in range(12): # 23 to 24
        dataset.append(randint(0,10))
    return dataset

# MAIN
print("")
printGreen("********************************************")
printGreen("************* DEMO LIVECAPTURE *************")
printGreen("********************************************")

# Creazione Dataset
printYellow("Generazione del dataset")
series = []
intervals = []
interval = 300 # 5 minuti
for i in range(5):
    series += createDataset()
now = datetime.combine(datetime.today(), time.min)
for i in series:
    intervals.append(now)
    now = now + timedelta(0, interval) 
lastdate = now

# Interfaccia utente
while(True):
    print("")
    command = inputYellow("Inserisci il comando da eseguire: ")
    command.lower()
    if (command == "help"):
        print("-- Elenco dei comandi disponibili:")
        print("-- <exp> Genera grafico per exponential smoothing")
        print("-- <2exp> Genera grafico per double exponential smoothing")

    elif (command == "exp"):
        intervals_exp = intervals
        lastdate = lastdate + timedelta(0, interval)
        intervals_exp.append(lastdate)
        alpha = float(input("-- Inserisci alpha: "))
        res = api.exponential_smoothing(series, alpha)
        myplot(res, series, intervals)

    elif (command  == "2exp"):
        intervals_exp = intervals
        lastdate = lastdate + timedelta(0, interval)
        intervals_exp.append(lastdate)    
        lastdate = lastdate + timedelta(0, interval)
        intervals_exp.append(lastdate)  
        alpha = float(input("-- Inserisci alpha: "))
        beta = float(input("-- Inserisci beta: "))
        res = api.double_exponential_smoothing(series, alpha, beta) 
        myplot(res, series, intervals)

    elif (command == "hw"):
        n_preds = int(input("-- Inserisci il numero di predizioni: "))
        intervals_hw = intervals
        for i in range (n_preds):
            lastdate = lastdate + timedelta(0, interval)
            intervals_hw.append(lastdate)
        alpha = float(input("-- Inserisci alpha: "))
        beta = float(input("-- Inserisci beta: "))
        gamma = float(input("-- Inserisci gamma: "))
        res, dev = api.triple_exponential_smoothing(series, 288, alpha, beta, gamma, n_preds)
        ubound = []
        lbound = []
        for i in range(len(res)):
            ubound.append(res[i] + 2.5 * dev[i])
            lbound.append(res[i] - 2.5 * dev[i])
        myplotHW(res, dev, series, intervals, ubound, lbound)

    elif (command == "hwfit"):
        n_preds = int(input("-- Inserisci il numero di predizioni: "))
        intervals_hw = intervals
        for i in range (n_preds):
            lastdate = lastdate + timedelta(0, interval)
            intervals_hw.append(lastdate)
        # TODO

    elif (command == "exit"):
        printYellow("Chiudo il programma")
        break
    else:
        printYellow("Comando non riconosciuto")