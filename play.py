# coding=utf8
import sys
import curses
import locale
import algorithms
import utils
import gui
from thread import start_new_thread
from algorithms import TemporalDifferenceLearningWithEpsilonGreedyPolicy
import world

algo = TemporalDifferenceLearningWithEpsilonGreedyPolicy()


def parse_command_line(argv):
    interactive = "-i" in argv
    very_verbose = "-vv" in argv
    verbose = very_verbose or "-v" in argv
    if "-e" in argv:
        episode_count_idx = argv.index("-e")
        episode_count = int(argv[episode_count_idx + 1])
    else:
        episode_count = None
    if "-t" in argv:
        training_count_idx = argv.index("-t")
        training_count = int(argv[training_count_idx + 1])
    else:
        training_count = episode_count
    return interactive, verbose, very_verbose, episode_count, training_count


def play(win, interactive, verbose, very_verbose, episode_count,
         training_count):
    utils.echofunc = lambda msg, clear: echo(win, msg, clear)
    utils.sleep = lambda ms: curses.napms(ms)

    Q, last_s, episodes = algo.play(episode_count, training_count,
                                    world.FIELD_WIDTH, world.FIELD_HEIGHT, 0.0,
                                    0.2, None, interactive, verbose)

    if very_verbose:
        print("# of Q values:".format(len(Q)))
        for sa, qval in Q.items():
            if sa[0] is None:
                print("None")
            else:
                utils.print_state(sa[0])
            print(sa[1])
            print(qval)
            print

    utils.echofunc(
        "game ended after {} episodes, final_score: {}, last state:"
        .format(episodes, algo.final_score(last_s)), False)
    utils.print_state(last_s)

    while True:
        c = win.getch()
        if c == ord('q'):
            break


def echo(win, msg, clear):
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    if clear:
        win.clear()
        win.move(0, 0)
    win.addstr(
        unicode(msg).encode("utf-8"), curses.color_pair(1) | curses.A_BOLD)
    win.move(win.getyx()[0] + 1, 0)
    win.refresh()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, "")
    tk_root = gui.init()
    controller = gui.game_controller(tk_root)
    algorithms.game_controller = controller
    # start_new_thread(gui.main, (tk_root,))
    curses.wrapper(play, *parse_command_line(sys.argv))
