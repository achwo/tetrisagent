from __future__ import division
from collections import Counter
#import utils
import sys
from agent import TDLearningAgent
import environment


def process(alpha):
    stats = {}
    episodes = 500
    training = 550
    epsilon = 0.0
    accumulator = Counter({100: 0, -100: 0})
    global algo
    algo = TDLearningAgent()
    Q = None
    print "# episode, P(win), wins, losses"
    for e in range(1, episodes + 1):
        Q, last_s, episodes_played = \
            algo.play(1, 1, environment.FIELD_WIDTH, epsilon, alpha, Q, False, False)
        score = algo.final_score(last_s)
        if e >= training:
            epsilon = 0
            alpha = 0
        accumulator[score] += 1
        stats[e] = dict(accumulator)
        #utils.print_q_values(Q)
        #print "{},{}".format(accumulator[100], accumulator[-100])
    for episode in sorted(stats):
        wins = stats[episode][100]
        losses = stats[episode][-100]
        print "{},{},{},{}".format(
            episode, wins - losses, wins, losses)


def play_episodes(epsilon, row_no):
    episodes_played = []
    for i in range(0, 1000):
        Q, s, p = algo.play(None, None, 4, epsilon, 0.2, None, False, False)
        episodes_played.append(p)
    print "{}\t{}\t{}\t\t\t{}\t\t{}".format(
        row_no,
        epsilon, sum(episodes_played) / len(episodes_played),
        min(episodes_played), max(episodes_played))


def episodes_for_finding_optimal_strategy():
    row_no = 0
    print "# run\tepsilon\tavg. no. of episodes\tminimum no.\tmaximum no."

    for epsilon in map(lambda x: x/10.0, range(0, 10)):
        row_no += 1
        play_episodes(epsilon, row_no)


def usage():
    print '''Usage genstats.py OPTION

    -o           Find out how many episodes are needed to find the optimal
                 strategy.  This is carried out for epsilon values from 0
                 to 0.9 in steps of 0.1.
    -c [ALPHA]   Run the game 1000 times with alpha value ALPHA, saving Q
                 values and initializing each episode with the Q values from
                 the previous game.
    '''


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    elif sys.argv[1] == "-o":
        print "# reproduce with: python {} -o".format(sys.argv[0])
        episodes_for_finding_optimal_strategy()
    elif sys.argv[1] == "-c":
        alpha = float(sys.argv[sys.argv.index("-c") + 1])
        process(alpha)
    else:
        usage()
        sys.exit(1)
