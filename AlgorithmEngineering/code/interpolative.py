# sample implementation of interpolative code
#  encoding is complete, but untested
#  decoding is incomplete


# main interpolative code procedure
# input is an array of increasing integers
def icode(a):
    n = len(a)  # integers in a in a
    lo = a[0]   # minimum value
    hi = a[-1]  # last (largest) value)in a
    # recursively encode the array
    s = code(a, lo, hi)
    # build and return the complete output
    output = [n, lo, hi, s]
    return output


# encode the array a[] knowing that
#  a[0] >= lo && a[-1] <= hi
# return a binary string which is the interpolative
# encoding of a[]
def code(a, lo, hi):
    n = len(a)  # number of elements in sequence
    if n == 0:
        return ""
    assert a[0] >= lo and a[-1] <= hi
    p = (n - 1) // 2  # position of the element to encode
    # encode a[p] by first establishing a range [apmin, apmax] it must belong
    # Notice:
    #   a[0] >= lo
    #   a[1] >= lo+1
    #   hence: a[p] >= lo + p
    apmin = lo + p
    # Notice:
    #   a[n-1] <= hi
    #   a[n-2] <= hi - 1
    #   hence a[n-i] <= hi - i + 1
    #   hence: a[p] = a[n-(n-p)] <= hi - (n-p) + 1
    apmax = hi - (n - p) + 1
    # Both coder and decoder knows that
    #       apmin <= a[p] <= apmax
    assert apmin <= a[p] <= apmax
    # compute number of bits to encode a[p]
    pcode_len = bits(apmax - apmin + 1)
    # codeword for p: pcode_len least significant bits of bin(a[p]-apmin)
    if pcode_len > 0:
        pcode = dec2bin(a[p] - apmin)[-pcode_len:]
    else:
        pcode = ""
    # FOR DEBUGGING PURPOSES: next line shows the integer being encoded
    # pcode = '%d "%s", ' % (a[p], pcode)
    # recursively encode
    before = a[:p]   # elements before a[p]
    after = a[p+1:]  # elements after a[p]
    beforecode = code(before, lo, a[p] - 1)
    aftercode = code(after, a[p] + 1, hi)
    return pcode + beforecode + aftercode


# main interpolative decoding procedure
def idecode(c):
    assert len(c) == 4, "Invalid compressed string"
    # extract lenght, lo, hi, and binary string
    n = c[0]
    lo = c[1]
    hi = c[2]
    s = c[3]
    a, bits = decode(n, lo, hi, s)
    return a


# recursive decoding procedure
# return de decode array and the number of bits
# consumed by the decoding
# TO BE WRITTEN
def decode(n, lo, hi, s):
    pass


# --- auxiliary functions


# convert to and from binary
def dec2bin(n):
    return "{0:032b}".format(n)


def bin2dec(s):
    return int(s, 2)


# number of bits required to encode k different values
def bits(k):
    assert k > 0
    if k == 1:
        return 0
    bits = 1
    values = 2  # 1 bit -> 2 values
    while values < k:
        bits += 1
        values *= 2
    return bits


# ----- sample array

a = [1, 2, 3, 5, 7, 9, 11, 15, 18, 19, 20, 21]
