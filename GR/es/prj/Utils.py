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