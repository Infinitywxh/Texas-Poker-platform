from lib.texaspoker import Hand
from lib.texaspoker import id2color
from lib.texaspoker import id2num
import random


def test1():
    A = [0] * 7
    for i in range(7):
        A[i] = random.randint(0, 51)
    print(A)
    B = [[0 for col in range(2)] for row in range(7)]
    for i in range(7):
        B[i][0] = id2color(A[i])
        B[i][1] = id2num(A[i])
    B.sort(key=lambda f: f[1])
    for i in B:
        print("color = %s, num = %s" % (i[0], i[1]))
    a = Hand(A)
    print(a.level)

def test2():
    while True:
        A = [0] * 7
        for i in range(7):
            A[i] = random.randint(0, 51)
        print(A)
        B = [[0 for col in range(2)] for row in range(7)]
        for i in range(7):
            B[i][0] = id2color(A[i])
            B[i][1] = id2num(A[i])

        B.sort(key=lambda f: f[1])
        # for i in B:
        #    print("color = %s, num = %s" % (i[0], i[1]))
        a = Hand(A)
        print(a.level)
        if a.level == 10:
            # print(A)
            for i in B:
                print("color = %s, num = %s" % (i[0], i[1]))
            # print(a.level)
            break

