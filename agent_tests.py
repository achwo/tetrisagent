# todo: given the learning rate is 0.0
#       when the field is empty in one episode and it is again in the following episode
#       then the agent will execute the same action
# maybe not because of reward
import unittest
from mock import MagicMock
from agent import TDLearningAgent
from environment import Environment, OShape, IShape, Action


class AgentTest(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.agent = TDLearningAgent()
        self.agent.environment = self.env

    def test_givenQisEmpty_whenChoosingAction_thenItShouldBeAnyPossibleAction(self):
        self.assertEqual(self.env.possible_actions(), list(self.agent._find_best_actions_in_q()))

    def test_givenQisNotEmptyAndLearningRateIs0_ShouldChooseBestActionFromQ(self):
        shape = OShape()

        state1 = self.agent.current_state

        self.env.current_shape = shape
        self.agent._update_perceived_state()

        # run the rest of the episode
        self.agent._step()

        choose_action = self.agent._choose_action
        self.agent._choose_action = MagicMock(return_value=Action(3))
        while not self.env.is_game_over():
            self.env.current_shape = IShape()
            self.agent._update_perceived_state()
            self.agent._step()

        self.agent._choose_action = choose_action

        self.agent._initialize_state()

        state2 = self.agent.current_state

        self.assertEqual(state2, state1)
        self.assertTrue(len(self.agent.Q) != 0)

        self.env.current_shape = shape
        self.agent._update_perceived_state()

        self.env._choose_next_shape()

        self.assertNotEqual(self.env.possible_actions(), list(self.agent._find_best_actions_in_q()))



    @unittest.skip("this test is not ready")
    def test_givenLearningRateIs0AndQisEmpty_whenSameState_thenExecuteSameAction(self):
        self.agent.alpha = 0.0

        old_action = self.agent.Q[(self.agent.current_state, self.env.current_shape)]

        self.assertEqual(self.agent._choose_action(), old_action)
