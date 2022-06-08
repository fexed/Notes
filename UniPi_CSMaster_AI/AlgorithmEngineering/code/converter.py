def converter(x : float, k : int):
    assert x >= 0
    assert x < 1
    out = "."
    for i in range(k):
        x *= 2
        if (x < 1): out += "0"
        else:
            out += "1"
            x -= 1
    
    return out


def parse(x : str):
    x = x[1:]
    orig = 0.0
    for i, d in enumerate(x):
        orig += float(int(d)*(2**(-(i+1))))
    return orig


num = 0.53928457
k = 1
conv = converter(num, k)
orig = parse(conv)
err = num-orig
print("converter(" + str(num) + ", " + str(k) + ") = " + conv)
print("Parsed yields\t" + str(orig))
print("Estimated error is 2^(-" + str(k) + ") = " + str(2**-k))
print("Computed error = " + ("{:.10f}").format(err))
