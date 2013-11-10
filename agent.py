from collections import defaultdict
import random
import time

from environment import Environment

MAXIMUM_REWARD = 100


class TDLearningAgent(object):
    def __init__(self, environment=Environment()):
        self.environment = environment
        self._update_perceived_state()
        self.random = random.Random()
        self.Q = defaultdict(int)
        self.alpha = 0.1  # lernrate
        self.gamma = 0.8  # discount rate

    def _update_perceived_state(self):
        self.current_state = self._perceived_state()

    def run(self, episodes):
        for i in range(0, episodes):
            self._episode()

    def _episode(self):
        self._initialize_state()
        while not self.current_state.is_terminal():
            self._step()

    def _initialize_state(self):
        self.environment = Environment()
        self._update_perceived_state()

    def _step(self):
        action = self._choose_action()
        reward = self._take_action(action)
        new_state = self._perceived_state()
        self._q(new_state, action, reward)
        self._update_perceived_state()

    def _choose_action(self):
        actions = self._find_best_actions(self.current_state,
                                          self.environment.possible_actions())

        return self.random.sample(actions, 1)[0]

    def _take_action(self, action):
        self.environment.execute_action(action)
        return 10  # todo real reward calculation

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

    def _find_best_actions(self, state, actions):
        best_actions = list(actions)
        best_value = 0
        for action in actions:
            value = self.Q[(state, action)]
            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return set(best_actions)

    def _perceived_state(self):
        return PerceivedState(self.environment)


class TDLearningAlgorithmSlow(TDLearningAgent):
    def _step(self):
        TDLearningAgent._step(self)
        time.sleep(0.5)
        self.dataQ.put(1)

    def _episode(self):
        self._initialize_state()
        while (not self.stop_event.is_set() and
                   not self.current_state.is_terminal()):
            self._step()


class PerceivedState(object):
    def __init__(self, environment):
        self.blocks = environment.blocks
        self.possible_actions = environment.possible_actions()
        self.terminal = environment.is_game_over()

    def is_terminal(self):
        # return self.possible_actions.__len__() == 0
        return self.terminal