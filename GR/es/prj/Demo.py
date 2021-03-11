#!\bin\python3

import pyshark
import APIForecast
import Dataset
import matplotlib.pyplot as plt
import matplotlib.dates as md
import json
import argparse
from datetime import datetime, timedelta, time


# Custom print and input
def inputyellow(txt):
    cend = '\33[0m'
    cyellow = '\33[33m'
    r = input(cyellow + txt + cend)
    return r

def printyellow(txt):
    cend = '\33[0m'
    cyellow = '\33[33m'
    print(cyellow + txt + cend)

def printgreen(txt):
    cend = '\33[0m'
    cgreen = '\33[32m'
    print(cgreen + txt + cend)


# Params
def parse_args():
    parser = argparse.ArgumentParser(description='Simple script that generates a plot based on an input dataset.json')
    data_parser = parser.add_mutually_exclusive_group(required=False)
    data_parser.add_argument('--dataset', type=str, required=False, default="NULL",
                             help='dataset from which the script reads the values')
    data_parser.add_argument('--pcap', type=str, required=False, default="NULL",
                             help='pcap from which the script reads the packets')
    parser.add_argument('--alpha', type=float, required=False, default=-1,
                        help='alpha parameter for forecasting')
    parser.add_argument('--beta', type=float, required=False, default=-1,
                        help='beta parameter for forecasting')
    parser.add_argument('--gamma', type=float, required=False, default=-1,
                        help='gamma parameter for forecasting')
    iter_parser = parser.add_mutually_exclusive_group(required=False)
    iter_parser.add_argument('--iterative', dest='iter', action='store_true',
                             help='iterates the fitting process 100 times and picks the best result (default)')
    iter_parser.add_argument('--no-iterative', dest='iter', action='store_false',
                             help='execs the fitting process just once')
    parser.set_defaults(iter=True)
    parser.add_argument('--season', type=int, required=False, default=-1,
                             help='points in a season for Holt-Winters forecasting')
    parser.add_argument('--rsi', type=int, required=False, default=2,
                             help='points for RSI calculation')
    parser.add_argument('--interval', type=int, required=False, default=30,
                             help='number of seconds for aggregation')
    return parser.parse_args()


def sse(values, predictions):
    val = 0
    for n, r in zip(values, predictions):
        val = val + ((n - r) ** 2)
    return val


printgreen("********************************************")
printgreen("************* DEMO     CAPTURE *************")
printgreen("********************************************")

# Arguments
args = parse_args()
dataset = args.dataset  # Dataset if present
pcap = args.pcap  # PCAP if present

nums = []  # Data
dates = []  # Timestamps
count = 0  # Counting (output)
errors = 0  # Errors (output)
if dataset == "NULL" and pcap == "NULL":
    printgreen("Generating dataset...\n")
    for i in range(5):
        generated = Dataset.createDataset()
        for n in generated:
            nums.append(n)
    n = 0  # Temp (output)
    now = datetime.combine(datetime.today(), time.min)
    for n in nums:
        count = count + 1
        dates.append(now)
        now = now + timedelta(minutes=5)  # Every 5 mins TODO: parameter to specify
        printyellow("\r\033[F\033[KGenerating\t" + "#" + str(count) + " " + str(n) + "B")
else:
    if dataset != "NULL":
        printgreen("Loading dataset...\n")
        nums = json.load(open(dataset, "r"))
        n = 0
        now = datetime.combine(datetime.today(), time.min)
        for n in nums:
            count = count + 1
            dates.append(now)
            now = now + timedelta(minutes=5)
            printyellow("\r\033[F\033[KLoading\t" + "#" + str(count) + " " + str(n) + "B")

    elif pcap != "NULL":
        printgreen("Loading PCAP...\n")
        cap = pyshark.FileCapture(pcap)  # Reading from PCAP
        for pkt in cap:
            try:
                dates.append(float(pkt.frame_info.time_epoch))
                nums.append(int(pkt.length) / 1000)
                count += 1
                printyellow("\r\033[F\033[KLoading\t" + "#" + str(count) + " " + str(int(pkt.length)) + "B")
            except AttributeError:
                errors += 1
                continue

        # Aggregation
        interval = args.interval
        intervals = []
        series = []
        start = -1
        sum = 0
        j = 0
        for i in range(len(dates)):
            if start == -1:
                start = i
                sum += nums[i]
            else:
                elapsed = datetime.fromtimestamp(dates[i]) - datetime.fromtimestamp(dates[start])
                sum += nums[i]
                if elapsed.total_seconds() > interval:
                    j += 1
                    series.append(sum)
                    intervals.append(datetime.fromtimestamp(dates[i]))
                    lastdate = datetime.fromtimestamp(dates[i])
                    sum = 0
                    start = -1
        nums = series
        dates = intervals
print("\r\033[F\033[K", end="")
printyellow("Loaded\t" + str(count) + " data points")  # Output
printyellow("\t" + str(errors) + " errors")
printyellow("\tFrom " + dates[0].strftime("%Y-%m-%d %H:%M") + " to " +
            dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M"))

# Parameters
alpha = args.alpha
beta = args.beta
gamma = args.gamma
lastdate = dates[len(dates) - 1]
count = len(nums)

if alpha != -1 and beta != -1 and gamma != -1:  # All parameters specified, Holt-Winters forecasting
    season = args.season
    if season == -1: season = len(nums)//2  # TODO ugly
    res, dev, ubound, lbound = APIForecast.triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)  # API

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    SSE = sse(nums, res)
    MSE = SSE / count

    printgreen("\n\nHolt-Winters until " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%H:%M')  # Plot labels
    plt.gca().xaxis.set_major_formatter(xfmt)  # ^

    plt.plot(dates[0:count], nums)  # Plot generation
    plt.plot(dates, res, '--')
    plt.plot(dates, ubound, ':')
    plt.plot(dates, lbound, ':')

    plt.xticks(rotation=45)  # Labels rotation
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Holt-Winters forecasting (alpha = " + str(
        alpha) + ", beta = " + str(beta) + ", gamma = " + str(gamma) + ")\nSSE = " + str(SSE) + ", MSE = " + str(MSE))
    plt.show()  # Output
elif alpha != -1 and beta != -1:  # Only alpha and beta specified, Double Exponential forecasting
    res = APIForecast.double_exponential_smoothing(nums, alpha, beta)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    printgreen("\n\nDouble Exponential until " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)

    plt.plot(dates[:len(nums)], nums)
    plt.plot(dates, res, '--')

    plt.xticks(rotation=45)
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Double Exponential forecasting (alpha = " + str(
        alpha) + ", beta = " + str(beta) + ")")
    plt.show()
elif alpha != -1:  # Only alpha specified, Single Exponential forecasting
    res = APIForecast.exponential_smoothing(nums, alpha)

    dates.append(lastdate + timedelta(seconds=5))

    printgreen("\n\nSingle Exponential until " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)

    plt.plot(dates[:len(nums)], nums)
    plt.plot(dates, res, '--')

    plt.xticks(rotation=45)
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title(
        "Single Exponential forecasting (alpha = " + str(alpha) + ")")
    plt.show()
else:  # No parameters specified, auto fitting with Nelder-Mead
    season = args.season
    if season == -1: season = len(nums)//2  # TODO ugly
    start_time = datetime.now()
    itr = args.iter
    if itr:
        iterations = 100
    else:
        iterations = 1
    printgreen("\n\nFitting data...\n\n\n")

    bests = []
    for i in range(iterations):
        alpha, beta, gamma, SSE = APIForecast.fit_triple(nums, season)
        bests.append([[alpha, beta, gamma], SSE])
        printyellow("\r\033[F\033[K\r\033[F\033[K\r\033[F\033[KIterations\t" + str(len(bests)))
        printyellow("Best\talpha\tbeta\tgamma")
        printyellow("\t" + "{:.5f}".format(alpha) + "\t" + "{:.5f}".format(beta) + "\t" + "{:.5f}".format(gamma))

    bests.sort(key=lambda x: x[1])
    alpha = bests[0][0][0]
    beta = bests[0][0][1]
    gamma = bests[0][0][2]
    SSE = bests[0][1]
    MSE = SSE / count

    res, dev, ubound, lbound = APIForecast.triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)
    RSI = APIForecast.rsi(res, args.rsi)

    for f in res[len(nums):]:
        lastdate = lastdate + timedelta(minutes=5)
        dates.append(lastdate)

    # Formatting for better output
    strSSE = "{:.5f}".format(SSE)
    strMSE = "{:.5f}".format(MSE)
    stralpha = "{:.5f}".format(alpha)
    strbeta = "{:.5f}".format(beta)
    strgamma = "{:.5f}".format(gamma)
    elapsed = (datetime.now() - start_time)
    printyellow("\nFitted in " + str(
        elapsed) + "!\n\talpha = " + stralpha + "\n\tbeta = " + strbeta + "\n\tgamma = " + strgamma)
    printgreen("\n\nHolt-Winters until " + dates[len(dates) - 1].strftime("%Y-%m-%d %H:%M:%S"))

    xfmt = md.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(xfmt)

    plt.plot(dates[0:count], nums)
    plt.plot(dates, res, '--')
    plt.plot(dates[0:count], ubound[0:count], ':')
    plt.plot(dates[0:count], lbound[0:count], ':')
    plt.plot(dates, RSI)

    plt.xticks(rotation=45)
    plt.xlabel("Time")
    plt.ylabel("Bytes")
    plt.title("Holt-Winters forecasting (fitted alpha = " + stralpha +
              ", beta = " + strbeta + ", gamma = " + strgamma + ")\nSSE = " + strSSE + ", MSE = " + strMSE)
    plt.show()
