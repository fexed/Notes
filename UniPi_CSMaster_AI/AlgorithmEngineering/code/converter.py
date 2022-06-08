def converter(x, k):
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