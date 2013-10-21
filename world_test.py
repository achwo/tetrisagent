import unittest
import shapes
from world import World, Action, State

NEUTRAL_REWARD = 0
NEGATIVE_REWARD = -10
POSITIVE_REWARD = 10
NEUTRAL_ACTION = Action(2)
NEGATIVE_ACTION = Action(1)
POSITIVE_ACTION = Action(0)


class WorldTest(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_execute_action_returns_a_reward(self):
        self.assertEqual(0, self.world.execute_action(Action(0)))

    def test_execute_action_returns_positive_reward_on_well_rated_action(self):
        def make_reward(action):
            if action == POSITIVE_ACTION:
                return POSITIVE_REWARD
            elif action == NEGATIVE_ACTION:
                return NEGATIVE_REWARD
            else:
                return NEUTRAL_REWARD

        self.world.make_reward = make_reward
        self.reward_on_action(POSITIVE_ACTION, POSITIVE_REWARD)
        self.reward_on_action(NEUTRAL_ACTION, NEUTRAL_REWARD)
        self.reward_on_action(NEGATIVE_ACTION, NEGATIVE_REWARD)

    def reward_on_action(self, action, reward):
        self.assertEqual(reward, self.world.execute_action(action))

    def test_state_returns_the_current_state(self):
        state = State()
        self.world.current_state = state
        self.assertEqual(state, self.world.current_state)

    def test_execute_action_updates_current_shape(self):
        old_shape = self.world.current_shape
        self.world.execute_action(NEUTRAL_ACTION)
        new_shape = self.world.current_shape
        self.assertIsNot(old_shape, new_shape)


class ActionTest(unittest.TestCase):

    def setUp(self):
        self.a = Action(1)
        self.a = Action(1)

    def test_eq_false_cases(self):
        other_type = 1
        self.assertFalse(self.a == other_type)
        b = Action(2)
        self.assertFalse(self.a == b)

    def test_eq_true_cases(self):
        self.assertTrue(self.a == self.a)
        b = Action(1)
        self.assertTrue(self.a == b)


# todo execute action changes the state
# todo execute action adds a block to the current state
# todo make_reward actually does something

if __name__ == '__main__':
    unittest.main()