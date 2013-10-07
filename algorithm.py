from collections import defaultdict
from itertools import groupby
import random
import utils


class TemporalDifferenceLearning:

    def choose_action(self, Q, A, s):
        candidates = [A[0]]
        for action in A:
            #print("Q({}, {}): {}".format(s, action, Q[(s, action)]))
            if Q[(s, action)] > Q[(s, candidates[0])]:
                candidates = [action]
            elif Q[(s, action)] == Q[(s, candidates[0])]:
                action in candidates or candidates.append(action)
            #print("{}: {}".format(s, candidates))
        return random.choice(candidates)

    def create_new_state(self, s, row, a):
        s_new = []
        for i in s:
            s_new.append(tuple(i))
        s_new[row] = list(s_new[row])
        s_new[row+1] = list(s_new[row+1])
        s_new[row][a] = 1
        s_new[row][a+1] = 1
        s_new[row+1][a] = 1
        s_new[row+1][a+1] = 1
        s_new[row] = tuple(s_new[row])
        s_new[row+1] = tuple(s_new[row+1])
        ret = tuple(s_new)
        return ret

    def final_score(self, s):
        if s is None:
            return 0
        for row in s:
            if len(row) != reduce(lambda x, y: x+y, row):
                return -100
        return 100

    def reward(self, s, a):
        row = len(s)-1
        # find row where the piece will land on
        while row >= 0 and s[row][a] == 0 and s[row][a+1] == 0:
            row -= 1
        row += 1
        # piece hit the roof => gameover
        if row > len(s) - 2:
            return (self.final_score(s), None)

        new_s = self.create_new_state(s, row, a)
        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(new_s[row], lambda x: x == 0) if g]

        # possibilities depleted => calculate final score
        if row == len(new_s) - 2:
            if len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2:
                return (self.final_score(new_s), new_s)

        # otherwise, calculate current reward
        if len(consecutive_zeros) > 0 and max(consecutive_zeros) < 2:
            score_i = -10
        elif len(consecutive_zeros) == 0:
            score_i = 10
        else:
            score_i = 0
        return (score_i, new_s)

    def is_final_state(self, s):
        if s is None:
            return True
        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(s[len(s)-1], lambda x: x == 0) if g]
        return len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2

    # noinspection PyAugmentAssignment
    def episode(self, S0, Q, A, epsilon, alpha, interactive):
        """
        Run one episode of the learning algorithm
        An episode ends, when the next state is a final state

        :param S0:              start state
        :param Q:               Quality of the state-action-combination
        :param A:               list with possible actions
        :param epsilon          epsilon greedy probability
        :param alpha:           learning rate
        :param interactive:     If True, things will be animated
        :return:
        """
        gamma = 0.8     # weighting of future rewards in comparison to current
        # reward
        s = S0
        last_field = s
        while not self.is_final_state(s):
            a = self.choose_action(Q, A, s)
            if random.random() < epsilon:
                idx_a = A.index(a)
                a = random.choice(A[:idx_a] + A[(idx_a+1):])
            r, next_s = self.reward(s, a)
            if interactive:
                if next_s is not None:
                    utils.animate_piece_drop(s, a)
            h = (s, a)

            # TD-Learning Algorithm:
            Q[h] = Q[h] + alpha * (
                r + gamma * Q[(next_s, self.choose_action(Q, A, next_s))] - Q[h]
            )

            s = next_s
            if s is not None:
                last_field = s
        return (last_field, r)

    def play(self, episodes, training, width, height, start_epsilon, start_alpha, Q_in,
             interactive, verbose):
        """
        Play a game of tetris with the given parameters
        Temporal Difference Learning

        Returns a tuple (Q, last_s, episodes_played) containing the Q values, the
        last state and the number of episodes played.
        :param episodes:        Number of episodes to be played. If None,
                                run until optimal strategy is found
        :param training:        number of training rounds (?)
        :param start_epsilon:   used for epsilon-greedy. probability to choose an
                                option other than the current optimum to learn
                                new paths
        :param start_alpha:     learning rate (weighting of new rewards in contrast
                                to older ones
        :param Q_in:            dictionary with q-values
        :param interactive:     sleep between episodes..
        :param verbose:         if True, console output will be longer
        """
        alpha = start_alpha
        A = range(0, width-1)
        S0 = tuple([tuple(0 for i in range(0, width)) for i in range(0, height)])
        Q = Q_in or defaultdict(int)
        last_s = None
        episodes_played = 0
        epsilon = start_epsilon
        optimal_strategy_found = False
        while episodes is not None and episodes_played < episodes or \
                                episodes is None and not optimal_strategy_found:
            last_s, last_score = self.episode(S0, Q, A, epsilon, alpha, interactive)
            episodes_played += 1
            if training is not None and \
                            episodes_played >= training:  # training done
                epsilon = 0
                alpha = 0
            if not optimal_strategy_found and last_score == 100:  # end training
                optimal_strategy_found = True
                epsilon = 0
                alpha = 0
            if interactive:
                utils.sleep(100)
            if verbose:
                if episodes_played % 1000 == 0:
                    utils.echofunc("", True)
                    utils.print_state(last_s)
                    utils.echofunc(len(Q), False)
                    utils.echofunc(episodes_played, False)
        return (Q, last_s, episodes_played)
