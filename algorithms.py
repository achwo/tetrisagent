from collections import defaultdict
from itertools import groupby
import random
import utils
import world as w

from world import World

MAXIMUM_REWARD = 100

game_controller = None


class Algorithm(object):
    pass


class TemporalDifferenceLearningWithEpsilonGreedyPolicy(Algorithm):

    def __init__(self, world=World()):
        self.world = world

    def play(self, episodes, training, width, start_epsilon, start_alpha, Q_in,
             interactive, verbose):
        """
        Play a game of Tetris with the given parameters
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
        helper = self.playHelper(width, start_alpha, start_epsilon, Q_in,
                                 training, interactive, verbose, self.world)
        return helper.invoke(episodes)

    class playHelper(object):
        def __init__(self, width, start_alpha, start_epsilon, Q_in,
                     number_training_episodes, interactive, verbose, world):
            self.width = width
            self.previous_state = None
            self.optimal_strategy_found = False
            self.ACTIONS = range(0, self.width - 1)
            self.epsilon = start_epsilon
            self.alpha = start_alpha
            self.gamma = 0.8
            self.Q = Q_in or defaultdict(int)
            self.episodes_played = 0
            self.number_training_episodes = number_training_episodes
            self.interactive = interactive
            self.verbose = verbose
            self.world = world

        def print_output(self):
            utils.echofunc("", True)
            utils.print_state(self.previous_state)
            utils.echofunc(len(self.Q))
            utils.echofunc(self.episodes_played)

        def interactive_stuff(self):
            if self.interactive:
                utils.sleep(500)

        def verbose_stuff(self):
            if self.verbose and self.episodes_played % 1000 == 0:
                self.print_output()

        def end_training_if_enough_episodes(self):
            if self.training_done():
                self.set_epsilon_and_alpha_zero()

        def end_training_if_score_was_maximal(self):
            if self.should_end_training():
                self.end_training()

        def invoke(self, number_episodes):
            self.number_episodes = number_episodes
            while self.not_finished_with_episodes() \
                    or self.optimal_strategy_not_found():
                self.previous_state, self.previous_score = self.episode()

                self.end_training_if_enough_episodes()
                self.end_training_if_score_was_maximal()
                self.interactive_stuff()
                self.verbose_stuff()
            return self.Q, self.previous_state, self.episodes_played

        def td_learning(self, h, next_state, reward):
            # noinspection PyAugmentAssignment
            self.Q[h] = self.Q[h] + self.alpha * (reward + self.gamma * self.Q[(
                next_state, self.choose_action(next_state))] - self.Q[h])

        def episode(self):
            # reward
            self.state = w.S0
            last_field = self.state
            while not self.is_final_state():
                action = self.choose_action(self.state)
                if random.random() < self.epsilon:
                    idx_a = self.ACTIONS.index(action)
                    action = random.choice(
                        self.ACTIONS[:idx_a] + self.ACTIONS[(idx_a + 1):])
                reward, next_state = self.reward_and_end_episode(self.state,
                                                                 action)

                self.world.game_controller.setpos_callback(action)
                self.world.game_controller.up_callback(None)

                if self.interactive:
                    if next_state is not None:
                        utils.animate_piece_drop(self.world, self.state, action)
                h = (self.state, action)

                self.td_learning(h, next_state, reward)

                self.state = next_state
                if self.state is not None:
                    last_field = self.state
                utils.sleep(100)

            self.episodes_played += 1
            return last_field, reward

        def training_done(self):
            """
            should training phase be ended because training limit exceeded?
            """
            return self.number_training_episodes is not None and \
                self.episodes_played >= self.number_training_episodes

        def should_end_training(self):
            """
            should training be ended because previously the score was maximal?
            """
            return not self.optimal_strategy_found and \
                self.previous_score == MAXIMUM_REWARD

        def end_training(self):
            self.optimal_strategy_found = True
            self.set_epsilon_and_alpha_zero()

        def set_epsilon_and_alpha_zero(self):
            self.epsilon = 0
            self.alpha = 0

        def not_finished_with_episodes(self):
            return self.number_episodes is not None \
                and self.episodes_played < self.number_episodes

        def optimal_strategy_not_found(self):
            return self.number_episodes is None and not self.optimal_strategy_found

        def is_final_state(self):
            if self.state is None:
                return True

            consecutive_zeros = [len(list(v)) for g, v in
                                 groupby(self.state[len(self.state) - 1],
                                         lambda x: x == 0) if
                                 g]
            return len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2

        def choose_action(self, state):
            """
            Choose the action from ACTIONS to be executed

            :param Q:       Quality-Map of the state-action-combination
            :param ACTIONS: The available actions
            :param state:   The current state
            """

            candidates = [self.ACTIONS[0]]
            for action in self.ACTIONS:
                #print("Q({}, {}): {}".format(state, action, Q[(state, action)]))
                if self.Q[(state, action)] > self.Q[(state, candidates[0])]:
                    candidates = [action]
                elif self.Q[(state, action)] == self.Q[(state, candidates[0])]:
                    action in candidates or candidates.append(action)
                    #print("{}: {}".format(state, candidates))
            return random.choice(candidates)

        def reward_and_end_episode(self, state, action):

            row = len(state) - 1
            # find row where the piece will land on
            while row >= 0 and state[row][action] == 0 and state[row][
                        action + 1] == 0:
                row -= 1
            row += 1
            # piece hit the roof => gameover
            if row > len(state) - 2:
                return self.final_score(state), None

            new_state = self.world.create_new_state(state, row, action)
            # looks for more zero groups in a row
            # (ex. (0, 0, 1, 1, 0, 0, 1, 1, 0) result: (2, 2, 1))
            consecutive_zeros = [len(list(v)) for g, v in
                                 groupby(new_state[row], lambda x: x == 0) if g]

            # possibilities depleted => calculate final score
            if row == len(new_state) - 2:
                if len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2:
                    return self.final_score(new_state), new_state

            # otherwise, calculate current reward
            score_i = self.world.calculate_reward(consecutive_zeros)

            return score_i, new_state

        def final_score(self, state):
            self.world.game_controller.clear_callback(None)
            if state is None:
                return 0
            for row in state:
                # when at least one unfilled field, score is -100
                if len(row) != reduce(lambda x, y: x + y, row):
                    return -100
            return 100


class Bot(object):

    def __init__(self):
        self.training_episodes = None
        self.training = None

    def run(self):
        for _ in itertools.repeat(None, self.training_episodes):
            self.training()

