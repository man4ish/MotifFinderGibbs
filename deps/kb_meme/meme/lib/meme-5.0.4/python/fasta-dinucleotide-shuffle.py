#!/usr/bin/python

import copy, random, string, sys
# MEME Suite libraries
sys.path.append('/home/manish/meme/lib/meme-5.0.4/python')
import alphabet
import sequence

# altschulEriksonDinuclShuffle.py
# P. Clote, Oct 2003

def computeCounts(s, alph):
    alen = alph.getFullLen()
    nuclCnt = [0 for i in xrange(alen)]
    dinuclCnt = [[0 for i in xrange(alen)] for j in xrange(alen)]
    # compute counts
    if len(s) > 0:
        y = alph.getIndex(s[0])
        nuclCnt[y] = 1
        for i in xrange(len(s) - 1):
            x = y
            y = alph.getIndex(s[i + 1])
            nuclCnt[y] += 1
            dinuclCnt[x][y] += 1
    return nuclCnt, dinuclCnt

def chooseEdge(x, dinuclCnt, alph):
    z = random.random()
    denom = sum(dinuclCnt[x])
    numerator = 0
    for y in xrange(len(dinuclCnt[x]) - 1):
        numerator += dinuclCnt[x][y]
        if z < float(numerator)/float(denom):
            dinuclCnt[x][y] -= 1
            return y
    y = len(dinuclCnt[x]) - 1
    dinuclCnt[x][y] -= 1
    return y

def connectedToLast(edgeList, usedSymI, lastSymI):
    D = {}
    for x in usedSymI:
        D[x] = 0
    for a, b in edgeList:
        if b == lastSymI:
            D[a] = 1
    for i in xrange(len(usedSymI) - 1):
        for a, b in edgeList:
            if D[b] == 1:
                D[a] = 1
    for x in usedSymI:
        if x != lastSymI and D[x] == 0:
            return False
    return True

def eulerian(s, alph):
    nuclCnt, dinuclCnt = computeCounts(s, alph)
    #compute nucleotides appearing in s
    usedSymI = [x for x in xrange(len(nuclCnt)) if nuclCnt[x] > 0]
    #create dinucleotide shuffle L
    lastSymI = alph.getIndex(s[-1])
    ok = False
    while not ok:
        counts = copy.deepcopy(dinuclCnt)
        edgeList = []
        for x in usedSymI:
            if x != lastSymI:
                edgeList.append( (x, chooseEdge(x, counts, alph)) )
        ok = connectedToLast(edgeList, usedSymI, lastSymI)
    return edgeList

def computeList(s, alph):
    out = [[] for i in xrange(alph.getFullLen())]
    if len(s) > 0:
        y = alph.getIndex(s[0])
        for i in xrange(len(s) - 1):
            x = y
            y = alph.getIndex(s[i + 1])
            out[x].append(y)
    return out

def dinuclShuffle(s, alph = alphabet.dna()):
    # check we can actually shuffle it
    if len(s) <= 2:
        return s
    # determine how to end the sequence
    edgeList = eulerian(s, alph)
    # turn the sequence into lists of following symbols
    symIList = computeList(s, alph)
    # remove last edges from each vertex list, shuffle, then add back
    # the removed edges at end of vertex lists.
    for [x,y] in edgeList:
        symIList[x].remove(y)
    for x in xrange(len(symIList)):
        random.shuffle(symIList[x])
    for [x,y] in edgeList:
        symIList[x].append(y)
    #construct the eulerian path
    prevSymI = alph.getIndex(s[0])
    L = [alph.getSymbol(prevSymI)]
    for i in xrange(len(s)-2):
        symI = symIList[prevSymI].pop(0)
        L.append(alph.getSymbol(symI))
        prevSymI = symI
    symI = alph.getIndex(s[-1])
    L.append(alph.getSymbol(symI))
    return string.join(L,"")

def main():

    #
    # defaults
    #
    file_name = None
    alphabet_file_name = None
    seed = 1
    copies = 1

    #
    # get command line arguments
    #
    usage = """USAGE:
    %s [options]

    -f <filename>   file name (required)
    -t <tag>        added to shuffled sequence names
    -s <seed>       random seed; default: %d
    -c <n>          make <n> shuffled copies of each sequence; default: %d
    -a <filename>   alphabet file to use non-DNA alphabets
    -h              print this usage message

    Note that fasta-shuffle-letters also supports dinucleotide shuffling and is faster.
    """ % (sys.argv[0], seed, copies)

    # no arguments: print usage
    if len(sys.argv) == 1:
        print >> sys.stderr, usage; sys.exit(1)

    tag = ""

    # parse command line
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if (arg == "-f"):
            i += 1
            try: file_name = sys.argv[i]
            except: print >> sys.stderr, usage; sys.exit(1)
        elif (arg == "-t"):
            i += 1
            try: tag = sys.argv[i]
            except: print >> sys.stderr, usage; sys.exit(1)
        elif (arg == "-s"):
            i += 1
            try: seed = string.atoi(sys.argv[i])
            except: print >> sys.stderr, usage; sys.exit(1)
        elif (arg == "-c"):
            i += 1
            try: copies = string.atoi(sys.argv[i])
            except: print >> sys.stderr, usage; sys.exit(1)
        elif (arg == "-a"):
            i += 1
            try: alphabet_file_name = sys.argv[i]
            except: print >> sys.stderr, usage; sys.exit(1)
        elif (arg == "-h"):
            print >> sys.stderr, usage; sys.exit(1)
        else:
            print >> sys.stderr, "Unknown command line argument: " + arg
            sys.exit(1)
        i += 1

    # check that required arguments given
    if (file_name == None):
        print >> sys.stderr, usage; sys.exit(1)

    # get the alphabet, defaulting to DNA if it is not provided
    if alphabet_file_name != None:
        alph = alphabet.loadFromFile(alphabet_file_name)
    else:
        alph = alphabet.dna()

    random.seed(seed)

    # read sequences
    seqs = sequence.readFASTA(file_name, alph)

    for s in seqs:
        seq = s.getString()
        name = s.getName()
        for i in range(copies):
            shuffledSeq = dinuclShuffle(seq, alph)
            if (copies == 1):
                print >> sys.stdout, ">%s\n%s" % (name+tag, shuffledSeq)
            else:
                print >> sys.stdout, ">%s_%d\n%s" % (name+tag, i, shuffledSeq)

if __name__ == '__main__': main()
