# coding=utf8

import tetris
import time


def echofunc(msg, clear):
    print msg


def sleep(ms):
    time.sleep(ms/1000)


def animate_piece_drop(s, a):
    row = len(s)-2
    while row >= 0 and s[row][a] == 0 and s[row][a+1] == 0:
        echofunc("", True)
        print_state(tetris.create_new_state(s, row, a))
        row -= 1
        time.sleep(0.02)


def print_state(S):
    for row in reversed(S):
        out = u""
        for i in row:
            out += u"{} ".format(u"-" if i == 0 else u"#")
        echofunc(out, False)


def print_q_values(Q):
    echofunc("Q values: {}".format(len(Q)), False)
    for s, a in sorted(Q.items()):
        echofunc("{}: {}".format(s, a), False)
