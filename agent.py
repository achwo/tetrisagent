from collections import defaultdict
import copy
import random
import time

from environment import Environment
import environment
from state import *


class TDLearningAgent(object):
    def __init__(self, state_class=FirstPerceivedState):
        self.state_class = state_class
        self.environment = Environment()
        self._initialize_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.1  # lernrate
        self.gamma = 0.8  # discount rate
        self.iterations = 0

    def _initialize_state(self):
        self.environment.initialize_field()
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
            c] + self.alpha * self._learned_value(reward, self.current_state)

    def _learned_value(self, reward, new_state):
        return reward + self.gamma * self._find_best_Q_value(new_state)

    def _find_best_Q_value(self, state):
        actions = self.environment.possible_actions()
        best = 0
        for action in actions:
            value = self.Q[(state, action)]
            if value > best:
                best = value

        return best

    def _perceived_state(self):
        return self.state_class(self.environment)


class TDLearningAgentSlow(TDLearningAgent):
    def _step(self):
        TDLearningAgent._step(self)
        time.sleep(0.5)
        self.dataQ.put(1)

    def _episode(self):
        self._initialize_state()
        while (not self.stop_event.is_set() and
                   not self.environment.is_game_over()):
            self._step()
