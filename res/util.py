from collections import Counter
import json

def loadPlaylists():
    return json.load(open('playlistPairs.json'))

def dotProduct(d1, d2):
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

def increment(d1, scale, d2):
    for f, v in d2.items():
        d1[f] = d1.get(f, 0) + v * scale

def countDiffs(originals, calculated):
    p1 = originals[0]
    p2 = originals[1]

    c1 = calculated[:len(p1)]
    c2 = calculated[-len(p2):]

    c3 = calculated[-len(p1):]
    c4 = calculated[:len(p2)]

    # Compare p1/c1 and p2/c2
    numWrong = 0
    numWrong += sum(0 if song in p1 else 1 for song in c1)
    numWrong += sum(0 if song in p2 else 1 for song in c2)
    print numWrong

    # Compare p1/c3 and p2/c4
    numWrong = 0
    numWrong += sum(0 if song in p1 else 1 for song in c3)
    numWrong += sum(0 if song in p2 else 1 for song in c4)
    print numWrong
