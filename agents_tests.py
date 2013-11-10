import unittest

from mock import MagicMock

from agent import TDLearningAgent
from environment import Action

# algorithm has perception of the current state

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = TDLearningAgent()

    def test_algorithm_runs_n_episodes(self):
        self.episodes = 0

        def episode():
            self.episodes += 1

        self.agent._episode = episode

        self.agent.run(100)
        self.assertEqual(100, self.episodes)

    def test_episode_initializes_state(self):
        self.init = False
        self.agent.environment.current_state.terminal = True

        def initialize_state():
            self.init = True

        self.agent._initialize_state = initialize_state

        self.agent._episode()
        self.assertTrue(self.init)

    def test_step_choose_action(self):
        self.chosen = False

        def choose_action():
            self.chosen = True
            a1 = Action(1)
            return a1

        self.agent._choose_action = choose_action

        self.agent._step()

        self.assertTrue(self.chosen)

    def test_step_takes_action(self):
        self.agent._take_action = MagicMock(
            return_value=(self.agent.environment.current_state, 0))
        self.agent._step()

        self.assertTrue(self.agent._take_action.called)

    def test_step_runs_q(self):
        self.agent._q = MagicMock()
        self.agent._step()

        self.assertTrue(self.agent._q.called)

    def test_choose_action(self):
        a1 = Action(1)
        a2 = Action(2)

        self.agent.environment.possible_actions = MagicMock(return_value={a1, a2})
        self.agent._step()

        self.assertTrue(self.agent.environment.possible_actions.called)

    def test_take_action(self):
        self.agent.environment.execute_action = MagicMock(
            return_value=(self.agent.environment.current_state, 0))
        self.agent._step()

        self.assertTrue(self.agent.environment.execute_action.called)


if __name__ == '__main__':
    unittest.main()