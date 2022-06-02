import sys


def burrowswheeler(text, verbose=True):
    text = text.replace("#", "") + "#"
    bwt = []
    for i in range(len(text)):
        if (i > 0):
            curr = text[i:len(text)] + "" + text[0:i]
        else:
            curr = text[i:len(text)]
        bwt.append(curr)
        if (verbose): print("\t" + curr)
    bwt = sorted(bwt)
    if (verbose):
        print("Sorted:")
        for s in bwt:
            print("\t" + s)
    L = ""
    for s in bwt:
        L = L + s[-1]
    pos = L.find("#")
    return L.replace("#", ""), pos


def LtoF(L):
    F = ""
    return F.join(sorted(L))


def reconstruct(F, L, verbose=True):
    F_idx, L_idx = 0, 0
    text = ""
    if (verbose): 
        print("\nF", F)   
        print("L", L)
    for i in range(len(F)):
        occ = F.count(F[F_idx], 0, F_idx+1)
        start = -1
        for j in range(occ):
            L_idx = L.find(F[F_idx], start+1)
            start = L_idx
        print("Map", F[F_idx], "(" + str(occ), "occurrence) in index", str(L_idx), "("+ L[L_idx], "->", F[L_idx] + ")")
        text = text + F[L_idx]
        F_idx = L_idx
    return text


def encode(text):
    print("***ENCODING")
    print("String to be encoded:\t" + text)
    print("Burrows-Wheeler Transform")
    L, pos = burrowswheeler(text, verbose=True)
    print("BW(" + text + ") = <" + L + ", " + str(pos) + "> = " + L[0:pos] + "#" + L[pos:len(L)])
    return L, pos


def decode(L, pos):
    L_ = L[0:pos] + "#" + L[pos:len(L)]
    print("***DECODING")
    print("String to be decoded", L_)
    F = LtoF(L_)
    print("F =", F)
    text = reconstruct(F, L_, verbose=True)
    print("Reconstructed text:", text)
    return text


def main():
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], " <string>")
        exit()
    L, pos = encode(sys.argv[1])
    print("Compressing <L, pos> = <" + L + ", " + str(pos) + "> with some pipeline")
    print("...")
    print("Decompressing <L, pos> = <" + L + ", " + str(pos) + "> with some pipeline")
    text = decode(L, pos)
    print(sys.argv[1], "->", "<" + L + ", " + str(pos) + ">", "->", text.replace("#", ""))
    

if __name__ == "__main__":
    main()