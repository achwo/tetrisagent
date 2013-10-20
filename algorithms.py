from collections import defaultdict
from itertools import groupby
import random
import utils
import world as w

from world import World


class Algorithm(object):
    pass


class TemporalDifferenceLearningWithEpsilonGreedyPolicy(Algorithm):

    def __init__(self, world=World()):
        self.world = world

    def end_episode(self, state, action):
        pass

    def reward_and_end_episode(self, state, action):

        row = len(state) - 1
        # find row where the piece will land on
        while row >= 0 and state[row][action] == 0 and state[row][
                    action + 1] == 0:
            row -= 1
        row += 1
        # piece hit the roof => gameover
        if row > len(state) - 2:
            return (self.final_score(state), None)

        new_state = self.world.create_new_state(state, row, action)
        # looks for more zero groups in a row
        # (ex. (0, 0, 1, 1, 0, 0, 1, 1, 0) result: (2, 2, 1))
        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(new_state[row], lambda x: x == 0) if g]

        # possibilities depleted => calculate final score
        if row == len(new_state) - 2:
            if len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2:
                return (self.final_score(new_state), new_state)

        # otherwise, calculate current reward
        score_i = self.world.calculate_reward(consecutive_zeros)

        return (score_i, new_state)

    def choose_action(self, Q, ACTIONS, state):
        """
        Choose the action from ACTIONS to be executed

        :param Q:       Quality-Map of the state-action-combination
        :param ACTIONS: The available actions
        :param state:   The current state
        """

        candidates = [ACTIONS[0]]
        for action in ACTIONS:
            #print("Q({}, {}): {}".format(state, action, Q[(state, action)]))
            if Q[(state, action)] > Q[(state, candidates[0])]:
                candidates = [action]
            elif Q[(state, action)] == Q[(state, candidates[0])]:
                action in candidates or candidates.append(action)
                #print("{}: {}".format(state, candidates))
        return random.choice(candidates)

    def final_score(self, state):
        """
        Returns the score once the episode is finished

        :param state:
        :return:
        """
        # todo  could be abstracted, since it would be great as a parameter
        #       or maybe changed entirely
        if state is None:
            return 0
        for row in state:
            # when at least one unfilled field, score is -100
            if len(row) != reduce(lambda x, y: x + y, row):
                return -100
        return 100

    def is_final_state(self, state):
        """

        :param state:
        :return:
        """
        if state is None:
            return True

        # looks something like [
        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(state[len(state) - 1], lambda x: x == 0) if
                             g]
        return len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2

    # noinspection PyAugmentAssignment
    def episode(self, S0, Q, ACTIONS, epsilon, alpha, interactive):
        """
        Run one episode of the learning algorithm
        An episode ends, when the next state is a final state

        :param S0:              start state
        :param Q:               Quality-Map of the state-action-combination
        :param ACTIONS          list of possible actions
        :param epsilon          epsilon greedy probability
        :param alpha:           learning rate
        :param interactive:     If True, things will be animated
        :return:
        """
        gamma = 0.8     # weighting of future rewards in comparison to current
        # reward
        state = S0
        last_field = state
        while not self.is_final_state(state):
            action = self.choose_action(Q, ACTIONS, state)
            if random.random() < epsilon:
                idx_a = ACTIONS.index(action)
                action = random.choice(ACTIONS[:idx_a] + ACTIONS[(idx_a + 1):])
            reward, next_state = self.reward_and_end_episode(state, action)

            if interactive:
                if next_state is not None:
                    utils.animate_piece_drop(self.world, state, action)
            h = (state, action)

            # TD-Learning Algorithm:
            Q[h] = Q[h] + alpha * (
                reward + gamma * Q[
                    (next_state, self.choose_action(Q, ACTIONS, next_state))] -
                Q[h]
            )

            self.world.game_controller.setpos_callback(action)
            self.world.game_controller.up_callback(None)

            state = next_state
            if state is not None:
                last_field = state

            utils.sleep(800)
        return (last_field, reward)

    def play(self, episodes, training, width, height, start_epsilon,
             start_alpha, Q_in, interactive, verbose):
        """
        Play a game of tetris with the given parameters
        Temporal Difference Learning

        Returns a tuple (Q, last_s, episodes_played) containing the Q values,
        the last state and the number of episodes played.
        :param episodes:        Number of episodes to be played. If None,
                                run until optimal strategy is found
        :param training:        number of training rounds (?)
        :param start_epsilon:   used for epsilon-greedy. probability to choose
                                an option other than the current optimum to
                                learn new paths
        :param start_alpha:     learning rate (weighting of new rewards in
                                contrast to older ones
        :param Q_in:            dictionary with q-values
        :param interactive:     sleep between episodes..
        :param verbose:         if True, console output will be longer
        """
        alpha = start_alpha
        ACTIONS = range(0, width - 1)

        Q = Q_in or defaultdict(int)
        last_state = None
        episodes_played = 0
        epsilon = start_epsilon
        optimal_strategy_found = False
        while episodes is not None and episodes_played < episodes or episodes \
            is None and not optimal_strategy_found:
            last_state, last_score = self.episode(w.S0, Q, ACTIONS, epsilon,
                                                  alpha,
                                                  interactive)
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
                utils.sleep(2000)
            if verbose:
                if episodes_played % 1000 == 0:
                    utils.echofunc("", True)
                    utils.print_state(last_state)
                    utils.echofunc(len(Q))
                    utils.echofunc(episodes_played)
            # clear GUI board
            self.world.game_controller.clear_callback(None)
        return (Q, last_state, episodes_played)
