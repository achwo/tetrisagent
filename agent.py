from collections import defaultdict
import copy
import random
import time
import threading
import sys

from environment import Environment


class TDLearningAgent(object):
    def __init__(self):
        self._initialize_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.1  # lernrate
        self.gamma = 0.8  # discount rate

    def _initialize_state(self):
        self.environment = Environment()
        self._update_perceived_state()

    def _update_perceived_state(self):
        self.current_state = self._perceived_state()

    def run(self, episodes):
        for i in range(0, episodes):
            self._episode()

    def _episode(self):
        self._initialize_state()
        while not self.environment.is_game_over():
            self._step()

    def _step(self):
        action = self._choose_action()
        self.environment.execute_action(action)
        new_state = self._perceived_state()
        reward = self._calculate_reward(new_state)
        self._q(new_state, action, reward)
        self._update_perceived_state()

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

    def _q(self, new_state, action, reward):
        c = (self.current_state, action)

        self.Q[c] = (1 - self.alpha) * self.Q[
            c] + self.alpha * self._learned_value(reward, new_state)

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
        return SimplePerceivedState(self.environment)

    def _calculate_reward(self, new_state):
        return 10  # todo real reward calculation


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


class PerceivedState(object):
    pass


class SimplePerceivedState(PerceivedState):
    def __init__(self, environment):
        self.blocks = copy.deepcopy(environment.blocks)
        self.shape = environment.current_shape
        self.terminal = environment.is_game_over()