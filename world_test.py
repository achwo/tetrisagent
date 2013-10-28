import unittest
from world import World, Action, State
import world

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
        self.world.updated = False

        def update_current_shape():
            self.world.updated = True

        self.world.update_current_shape = update_current_shape
        self.world.execute_action(NEUTRAL_ACTION)
        self.assertTrue(self.world.updated)

    def test_execute_action_updates_state(self):
        self.world.updated = False

        def place_current_shape_on_column(column):
            self.world.updated = True

        self.world.place_current_shape_in_column = place_current_shape_on_column
        self.world.execute_action(NEUTRAL_ACTION)
        self.assertTrue(self.world.updated)


class ActionTest(unittest.TestCase):
    def setUp(self):
        self.a = Action(1)

    def test_eq_false_cases(self):
        other_type = 1
        b = Action(2)
        self.assertFalse(self.a == other_type)
        self.assertFalse(self.a == b)

    def test_eq_true_cases(self):
        self.assertTrue(self.a == self.a)
        b = Action(1)
        self.assertTrue(self.a == b)


class StateTest(unittest.TestCase):
    def setUp(self):
        self.s = State()
        self.empty_state_blocks = [[0 for i in range(world.FIELD_HEIGHT)] for j
                                   in range(world.FIELD_WIDTH)]

    def test_place_shape_adds_o_shape_to_empty_state(self):
        result = self.empty_state_blocks
        result[0][world.FIELD_HEIGHT - 1 - 1] = 'o'
        result[0][world.FIELD_HEIGHT - 1] = 'o'
        result[1][world.FIELD_HEIGHT - 1 - 1] = 'o'
        result[1][world.FIELD_HEIGHT - 1] = 'o'

        new_state = self.s.place_shape(shape=world.OShape(), column=0)
        self.assertEqual(result, new_state.blocks)

    def test_place_shape_throws_exception_on_out_of_bounds_column(self):
        with self.assertRaises(IndexError):
            self.s.place_shape(world.Possible_Shapes.O, 10)

    # @unittest.skip("")
    def test_place_shape_adds_i_shape_to_empty_state(self):
        self.maxDiff = None
        result = self.empty_state_blocks
        result[0][world.FIELD_HEIGHT - 1] = 'i'
        result[0][world.FIELD_HEIGHT - 1 - 1] = 'i'
        result[0][world.FIELD_HEIGHT - 1 - 2] = 'i'
        result[0][world.FIELD_HEIGHT - 1 - 3] = 'i'

        new_state = self.s.place_shape(world.IShape(), 0)
        self.assertEqual(result, new_state.blocks)

# todo execute action changes the state
# todo execute action adds a block to the current state
# todo make_reward actually does something

if __name__ == '__main__':
    unittest.main()