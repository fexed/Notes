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


def TypeByNumber(number):
    if( number == "0x00000800"):
        result = "IP"
    elif(number == "0x000088e1"):
        result ="HOMEPLUG-AV"
    elif(number == "0x00008912"):
        result = "NON RICONOSCIUTO"
    elif(number == "0x00000806"):
        result = "ARP"
    elif(number == "0x000086dd"):
        result = "IPv6"
    else:
        result = "SCONOSCIUTO"
    return result


# Plotting
def plot(values, dates, predictions=None, upperbound=None, lowerbound=None, rsi=None, title=None):
    plt.gca().xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

    plt.plot(dates[0:len(values)], values)

    if not(predictions is None):
        plt.plot(dates[len(values):], predictions[len(values):], '--')

    if not (upperbound is None):
        plt.plot(dates[0:len(values)], upperbound[0:len(values)], ':')

    if not (lowerbound is None):
        plt.plot(dates[0:len(values)], lowerbound[0:len(values)], ':')

    if not (rsi is None):
        plt.plot(dates[0:len(values)], rsi[0:len(values)])

    plt.xticks(rotation=45)
    plt.xlabel("Time")
    plt.ylabel("Bytes")

    if not (title is None):
        plt.title(title)
    plt.show()
