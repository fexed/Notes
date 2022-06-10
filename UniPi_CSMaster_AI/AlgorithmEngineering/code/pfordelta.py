import math


def analyze(S : list):
    # 0 <= S[i] <= 2^w
    w = len(bin(S[-1])[2:])
    # Most S[i] are < 2^b -1 (simple middle element in this case, should perform a more precise analysis)
    b = len(bin(S[math.floor(len(S)/2)])[2:])-1
    return w, b


def pfordeltaencoding(S : list):
    w, b = analyze(S)
    W = ""
    B = ""
    for s in S:
        bins = bin(s)[2:]
        if len(bins) > b:
            B += ("1"*b)  # mark is all bits to 1
            W += ("{0:0"+str(w)+"b}").format(s)
        elif len(bins) < b:
            B += ("{0:0"+str(b)+"b}").format(s)
        else:
            B += bins
            if bins == ("1"*b):
                # s is the maximum value representable on b bits, so I add s to W as well
                W += ("{0:0"+str(w)+"b}").format(s)
    return W, B


S = [1, 3, 4, 5, 9, 16, 23, 27, 28, 31, 40]
w, b = analyze(S)
W, B = pfordeltaencoding(S)
assert len(B) == b*len(S)
assert len(W) % w == 0
print("w =", w)
print("b =", b)
print("W", W)
print("B", B)