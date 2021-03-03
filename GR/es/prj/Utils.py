



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