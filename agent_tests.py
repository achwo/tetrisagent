import unittest
import environment
from agent import PerceivedState
from environment import Environment

from mock import MagicMock



class PerceivedStateTest(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        self.env.current_shape = environment.OShape()
        self.feature1 = MagicMock(return_value=1)

    def test_eq_true_cases(self):
        state1 = PerceivedState(self.env, self.feature1)
        state2 = PerceivedState(self.env, self.feature1)

        self.assertEqual(state1, state2)
        self.assertEqual(state1, state1)

    def test_eq_false_on_different_feature(self):
        feature2 = MagicMock(return_value=2)

        state1 = PerceivedState(self.env, self.feature1)
        state2 = PerceivedState(self.env, feature2)

        self.assertNotEqual(state1, state2)

    def test_eq_false_on_different_shape(self):
        state1 = PerceivedState(self.env, self.feature1)
        self.env.current_shape = environment.IShape()
        state2 = PerceivedState(self.env, self.feature1)

        self.assertNotEqual(state1, state2)


if __name__ == '__main__':
    unittest.main()