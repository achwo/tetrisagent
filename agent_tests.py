# todo: given the learning rate is 0.0
#       when the field is empty in one episode and it is again in the following episode
#       then the agent will execute the same action
# maybe not because of reward
import unittest
from mock import MagicMock
from agent import TDLearningAgent
from environment import Environment, OShape, IShape, Action


class AgentTest(unittest.TestCase):

    def test_givenQisEmpty_whenChoosingAction_thenItShouldBeAnyPossibleAction(self):
        env = Environment()
        agent = TDLearningAgent()

        self.assertEqual(env.possible_actions(), list(agent._find_best_actions()))

    def test_givenQisNotEmptyAndLearningRateIs0_whenChoosingAction_thenItShouldBeTheBestPossibleOne(self):
        env = Environment()
        agent = TDLearningAgent()
        shape = OShape()

        state1 = agent.current_state

        env.current_shape = shape
        agent._update_perceived_state()

        print agent._choose_action()
        # run the rest of the episode
        agent._step()


        print env.blocks
        self.fail()

        # choose_action = agent._choose_action
        # agent._choose_action = MagicMock(return_value=Action(3))
        # while not env.is_game_over():
        #     env.current_shape = IShape()
        #     print agent._choose_action()
        #
        #     agent._update_perceived_state()
        #
        #     agent._step()
        #
        # agent._choose_action = choose_action
        #
        #
        # state2 = agent.current_state
        #
        # print state1.blocks
        # print state2.blocks
        # self.assertEqual(state2, state1)
        # self.assertTrue(len(agent.Q) != 0)
        #
        # env.current_shape = shape
        #
        # # print agent._find_best_actions()
        #
        # self.assertNotEqual(env.possible_actions(), list(agent._find_best_actions()))

    @unittest.skip("this test is not ready")
    def test_givenLearningRateIs0AndQisEmpty_whenSameState_thenExecuteSameAction(self):
        env = Environment()
        agent = TDLearningAgent()
        agent.alpha = 0.0

        old_action = agent.Q[(agent.current_state, env.current_shape)]

        self.assertEqual(agent._choose_action(), old_action)
