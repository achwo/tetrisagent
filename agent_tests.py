import unittest
from agent import TDLearningAgent
from environment import Environment


class AgentTest(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.agent = TDLearningAgent()
        self.agent.environment = self.env

    def test_on_empty_q_all_actions_are_possible(self):
        self.assertEqual(self.env.possible_actions(),
                         list(self.agent._find_best_actions_in_q()))


