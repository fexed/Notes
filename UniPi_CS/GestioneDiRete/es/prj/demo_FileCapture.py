import pyshark
import APIForecast as api
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime, timedelta


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

def myplot(res, series, intervals):
    xfmt = md.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)
    plt.plot(intervals[0:len(series)],series)
    plt.plot(intervals[0:len(res)], res, '--')
    plt.xticks(rotation = 45)
    plt.xlabel("Time")
    plt.ylabel("KBytes")
    plt.show()

# MAIN
print("")
printGreen("********************************************")
printGreen("************* DEMO LIVECAPTURE *************")
printGreen("********************************************")

'''
file = inputYellow("Inserisci il nome del file di cattura: ")
cap = pyshark.FileCapture(file)
'''
cap = pyshark.FileCapture("prova.pcap")
print("")

# Lettura file di cattura
nums = []
dates = []
count = 0
for pkt in cap:
    dates.append(float(pkt.frame_info.time_epoch))
    nums.append(int(pkt.length)/1000)
    count = count + 1 
    print ("\r\033[F\033[K-- Pacchetti esaminati: " + "#" + str(count) + " " + str(int(pkt.length)))
print(f"-- Il numero di pacchetti è: {len(nums)}")

# Aggregazione dati su intervalli
interval = 5
intervals = []
series = []
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
        if (elapsed.total_seconds() > interval):
            j = j + 1
            series.append(sum)
            intervals.append(datetime.fromtimestamp(dates[i]))
            lastdate = datetime.fromtimestamp(dates[i])
            sum = 0
            start = -1

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

    elif (command == "exit"):
        printYellow("Chiudo il programma")
        break
    else:
        printYellow("Comando non riconosciuto")
    
    