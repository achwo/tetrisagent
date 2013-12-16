from collections import defaultdict
import random
import sys

from environment import Environment
import features


class PerceivedState(object):
    def __init__(self, environment, *features):
        self.shape = environment.current_shape.__repr__()
        self.features = []
        for f in features:
            r = f(environment)
            if isinstance(r, list):
                r = tuple(r)
            self.features.append(r)

    def __hash__(self):
        return hash((self.shape, tuple(self.features)))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.features == other.features
        return True

    def __repr__(self):
        return hash(self).__str__()


class Agent(object):
    def __init__(self, state_class=PerceivedState):
        self.features = [features.column_height_differences]
        self.state_class = state_class
        self.environment = Environment()
        self._initialize_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.9  # lernrate
        self.gamma = 0.8  # discount rate
        self.epsilon = 0.3  # probability of random action in epsilon greedy policy
        self.action_from_q = False
        self.latest_reward = 0

    def _initialize_state(self):
        self.environment.initialize()
        self._update_perceived_state()

    def _update_perceived_state(self):
        self.current_state = self._perceived_state()

    def run(self, episodes):
        for i in range(0, episodes):
            self._episode()

    def _episode(self):
        self._initialize_state()
        while not self._is_game_over():
            self._step()

    def _step(self):
        action = self._choose_action()
        self.latest_reward = reward = self.environment.execute_action(action)
        old_state = self.current_state
        self._update_perceived_state()
        self._q(old_state, action, reward)

    def _is_game_over(self):
        return self.environment.is_game_over()

    def _choose_action(self):
        actions = []
        if self.random.random() <= self.epsilon:
            actions, value = self._find_best_actions_in_q()
            self.action_from_q = 'Best: {0}'.format(value)

        if len(actions) == 0:
            self.action_from_q = 'Random'
            actions = self.environment.possible_actions()

        return self.random.sample(actions, 1)[0]

    def _find_best_actions_in_q(self):
        possible_actions = self.environment.possible_actions()
        best_actions = []
        best_value = -sys.maxint - 1
        for action in possible_actions:
            tup = (self.current_state, action)
            if tup in self.Q:
                value = self.Q[tup]
                if value > best_value:
                    best_value = value
                    best_actions = [action]
                elif value == best_value:
                    best_actions.append(action)

        return set(best_actions), best_value

    def _q(self, old_state, action, reward):
        c = (old_state, action)
        self.Q[c] = (1 - self.alpha) * self.Q[
            c] + self.alpha * self._learned_value(reward)

    def _learned_value(self, reward):
        return reward + self.gamma * self._find_best_Q_value()

    def _find_best_Q_value(self):
        actions = self.environment.possible_actions()
        best = 0
        for action in actions:
            value = self.Q[(self.current_state, action)]
            if value > best:
                best = value
        return best

    def _perceived_state(self):
        return self.state_class(self.environment, *self.features)

    def all_values(self):
        state = self.current_state
        Q = self.Q
        values = []
        for key, value in Q.iteritems():
            if key[0] == state:
                values.append(value)

        return values
