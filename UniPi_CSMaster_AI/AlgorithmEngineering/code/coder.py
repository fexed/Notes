def unary(x):
    return ("0"*(x-1)) + "1"


def gamma(x):
    binx = bin(x)[2:]  # removes "0b" prefix
    l = len(binx)
    return ("0"*(l-1)) + binx


def delta(x):
    binx = bin(x)[2:]  # removes "0b" prefix
    prefix = gamma(len(binx))
    return prefix + binx


def rice(x, k=3):
    import math
    q = math.floor(x/(2**(k)))
    r = x - (2**k)*q
    binr = bin(r)[2:]  # removes "0b" prefix
    binr = ("0"*(k-len(binr))) + binr # append "0" to get length up to k bits
    return unary(q+1) + binr