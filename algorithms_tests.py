import unittest

from mock import MagicMock

from algorithms import TDLearningAlgorithm
from world import Action


class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.algorithm = TDLearningAlgorithm()

    def test_algorithm_runs_n_episodes(self):
        self.episodes = 0

        def episode():
            self.episodes += 1

        self.algorithm._episode = episode

        self.algorithm.run(100)
        self.assertEqual(100, self.episodes)

    def test_episode_initializes_state(self):
        self.init = False
        self.algorithm.world.current_state.terminal = True

        def initialize_state():
            self.init = True

        self.algorithm._initialize_state = initialize_state

        self.algorithm._episode()
        self.assertTrue(self.init)

    def test_step_choose_action(self):
        self.chosen = False

        def choose_action():
            self.chosen = True
            a1 = Action(1)
            return a1

        self.algorithm._choose_action = choose_action

        self.algorithm._step()

        self.assertTrue(self.chosen)

    def test_step_takes_action(self):
        self.algorithm._take_action = MagicMock(
            return_value=(self.algorithm.world.current_state, 0))
        self.algorithm._step()

        self.assertTrue(self.algorithm._take_action.called)

    def test_step_runs_q(self):
        self.algorithm._q = MagicMock()
        self.algorithm._step()

        self.assertTrue(self.algorithm._q.called)

    def test_choose_action(self):
        a1 = Action(1)
        a2 = Action(2)

        self.algorithm.world.actions = MagicMock(return_value={a1, a2})
        self.algorithm._step()

        self.assertTrue(self.algorithm.world.actions.called)

    def test_take_action(self):
        self.algorithm.world.execute_action = MagicMock(
            return_value=(self.algorithm.world.current_state, 0))
        self.algorithm._step()

        self.assertTrue(self.algorithm.world.execute_action.called)


if __name__ == '__main__':
    unittest.main()