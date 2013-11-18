from collections import defaultdict
import random

from environment import Environment
import settings
from state import *


class TDLearningAgent(object):
    def __init__(self, state_class=BlockPerceivedState):
        self.iterations = 0
        self.state_class = state_class
        self.environment = Environment()
        self._initialize_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.9  # lernrate
        self.gamma = 0.8  # discount rate

    def _initialize_state(self):
        if self.iterations >= settings.ITERATIONS_BEFORE_ALPHA_CHANGE:
            self.alpha = 0.1
        self.environment.initialize()
        self._update_perceived_state()


    def _update_perceived_state(self):
        self.current_state = self._perceived_state()

    def run(self, episodes):
        for i in range(0, episodes):
            self._episode()
            self.iterations += 1

    def _episode(self):
        self._initialize_state()
        while not self.environment.is_game_over():
            self._step()

    def _step(self):
        action = self._choose_action()
        reward = self.environment.execute_action(action)
        old_state = self.current_state
        self._update_perceived_state()
        self._q(old_state, action, reward)

    def _choose_action(self):
        actions = self._find_best_actions()
        return self.random.sample(actions, 1)[0]

    def _find_best_actions(self):
        actions = self.environment.possible_actions()
        best_actions = list(actions)
        best_value = 0
        for action in actions:
            value = self.Q[(self.current_state, action)]
            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return set(best_actions)

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
        # return self.state_class(self.environment, features.individual_height)
        return self.state_class(self.environment)