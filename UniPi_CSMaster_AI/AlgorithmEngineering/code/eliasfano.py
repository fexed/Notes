import math


def EF_encode(x : list):
    H, L = "", ""

    n = len(x)
    u = x[-1]+1
    b = math.ceil(math.log(u, 2))
    l = math.ceil(math.log(u/n, 2))
    h = b - l
    
    curh = 0
    curbin = 0
    for num in x:
        binx = ("{0:0"+str(b)+"b}").format(num)
        L += binx[-l:]
        Hx = int(binx[:h], 2)
        if (Hx == curh):
            curbin += 1
        else:
            H += ("1"*curbin) + "0"
            for i in range(Hx-curh-1):
                H += "0"
            curh = Hx
            curbin = 1
    H += ("1"*curbin) + "0"
    maxbin = 2**h
    for i in range(maxbin-curh-1):
        H += "0"

    return H, L, n, u, b, l, h


def select(H : str, pos : int, b : str = "0"):
    num = 0
    for i in range(len(H)):
        if H[i] == b: num += 1
        if num == pos: return i


def group(L : str, pos : int, l : int):
    return L[pos*l:pos*l + l]


def access(pos : int, H : str, L : str, h : int, l : int):
    H = ("{0:0"+str(h)+"b}").format((select(H, pos+1, "1")) - pos)
    L = group(L, pos, l)
    return H + L


def nextgeq(val : int, H : str, L : str, h : int, l : int):
    binval = ("{0:0"+str(b)+"b}").format(val)
    Hval = binval[:h]
    Lval = binval[-l:]
    eta = select(H, int(Hval, 2), "0") + 1
    if H[eta] == "1":
        while H[eta] == "1":
            grp = eta - int(Hval, 2)
            Lgrp = group(L, grp, l)
            if int(Lval, 2) < int(Lgrp, 2): return Hval+Lgrp
            else:
                eta += 1
    if H[eta] == "0":
        return access(eta - int(Hval, 2), H, L, h, l)


def check(x : list, H : str, L : str):
    for i in range(len(nums)):
        assert (int(access(i, H, L, h, l), 2)) == nums[i]  # compression check


nums = [1, 3, 4, 5, 9, 16, 23, 27, 28, 31, 40]
pos = 8
H, L, n, u, b, l, h = EF_encode(nums)
check(nums, H, L)

elem = access(pos, H, L, h, l)
first = nextgeq(8, H, L, h, l)
second = nextgeq(32, H, L, h, l)
assert int(first, 2) == 9
assert int(second, 2) == 40

print("S =", nums)
print("H", H)
print("L", L)
print("S[" + str(pos) + "] =", elem, "=", int(elem, 2))
print("NextGeq(8) =", first, "=", int(first, 2))
print("NextGeq(32) =", second, "=", int(second, 2))