import unittest
import copy

from mock import MagicMock

from environment import Environment, Action, OShape, IShape, SShape, ZShape, Field
from environment import InvalidActionError


FIELD_WIDTH = 10
FIELD_HEIGHT = 12
BOTTOM_LINE = FIELD_HEIGHT - 1
VANISH_ZONE_HEIGHT = 2


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.empty_blocks = [[0 for i in range(FIELD_HEIGHT)]
                             for j in range(FIELD_WIDTH)]
        self.env = Environment(copy.deepcopy(self.empty_blocks))

    def fill_row(self, field, row, letter):
        for col in field:
            col[row] = letter

    def test_initially_game_is_not_over(self):
        self.assertFalse(self.env.is_game_over())

    def test_when_game_over_possible_actions_are_empty(self):
        self.env.is_game_over = MagicMock(return_value=True)
        self.assertEqual([], self.env.possible_actions())

    def test_block_out(self):
        self.env.field.blocks = self.empty_blocks
        self.fill_row(self.env.field.blocks, 0, 'l')

        self.assertTrue(self.env.is_game_over())

    def test_lock_out(self):
        self.env.blocks = self.empty_blocks
        self.fill_row(self.env.field.blocks, 0 + VANISH_ZONE_HEIGHT + 1, 'l')

        self.env.current_shape = OShape()
        self.assertFalse(self.env.is_game_over())
        self.env.execute_action(Action(0))

        self.assertTrue(self.env.is_game_over())

    def test_execute_action_changes_field(self):
        self.assertEqual(self.empty_blocks, self.env.field.blocks)

        self.env.execute_action(Action(1))
        self.assertNotEqual(self.empty_blocks, self.env.field.blocks)


class FieldTest(unittest.TestCase):
    def setUp(self):
        self.empty_blocks = [[0 for i in range(FIELD_HEIGHT)]
                             for j in range(FIELD_WIDTH)]

        self.field = Field()

    def assert_placed(self, shape, column, result):
        self.field.place(shape, column)
        self.assertEqual(result, self.field.blocks)


    def fill_row(self, field, row, letter='p'):
        for col in field:
            col[row] = letter

    def fill_field_row(self, row):
        self.fill_row(self.field.blocks, row)

    def test_invalid_action_throws_exception(self):
        with self.assertRaises(InvalidActionError):
            self.field.place(IShape(), 10)

    def test_invalid_action_on_wide_shape_throws_exception(self):
        with self.assertRaises(InvalidActionError):
            self.field.place(OShape(), 9)

    def test_o_shape_is_added_to_empty_state(self):
        result = copy.deepcopy(self.empty_blocks)
        result[0][BOTTOM_LINE - 1] = 'o'
        result[0][BOTTOM_LINE] = 'o'
        result[1][BOTTOM_LINE - 1] = 'o'
        result[1][BOTTOM_LINE] = 'o'

        self.assert_placed(OShape(), 0, result)

    def test_i_shape_is_added_to_empty_state(self):
        result = self.empty_blocks
        result[0][BOTTOM_LINE] = 'i'
        result[0][BOTTOM_LINE - 1] = 'i'
        result[0][BOTTOM_LINE - 2] = 'i'
        result[0][BOTTOM_LINE - 3] = 'i'

        self.assert_placed(IShape(), 0, result)

    def test_shape_is_placed_with_column_offset(self):
        result = self.empty_blocks
        result[3][BOTTOM_LINE] = 's'
        result[3][BOTTOM_LINE - 1] = 's'
        result[2][BOTTOM_LINE - 1] = 's'
        result[2][BOTTOM_LINE - 2] = 's'

        self.assert_placed(SShape(), 2, result)

    def test_shape_is_placed_above_existing_blocks(self):
        result = self.empty_blocks
        self.fill_row(result, BOTTOM_LINE, 'l')

        self.field.blocks = copy.deepcopy(result)

        result[0][BOTTOM_LINE - 1] = 'o'
        result[0][BOTTOM_LINE - 2] = 'o'
        result[1][BOTTOM_LINE - 1] = 'o'
        result[1][BOTTOM_LINE - 2] = 'o'

        self.assert_placed(OShape(), 0, result)

    def test_shape_is_placed_partially_floating(self):
        result = self.empty_blocks
        self.fill_row(result, BOTTOM_LINE, 'l')
        result[0][BOTTOM_LINE - 1] = 'l'

        self.field.blocks = copy.deepcopy(result)

        result[0][BOTTOM_LINE - 2] = 'z'
        result[0][BOTTOM_LINE - 3] = 'z'
        result[1][BOTTOM_LINE - 3] = 'z'
        result[1][BOTTOM_LINE - 4] = 'z'

        self.assert_placed(ZShape(), 0, result)

    def test_shape_is_placed_fitting_with_terrain(self):
        result = self.empty_blocks
        self.fill_row(result, BOTTOM_LINE, 'l')
        result[1][BOTTOM_LINE - 1] = 'l'

        self.field.blocks = copy.deepcopy(result)

        result[0][BOTTOM_LINE - 1] = 'z'
        result[0][BOTTOM_LINE - 2] = 'z'
        result[1][BOTTOM_LINE - 2] = 'z'
        result[1][BOTTOM_LINE - 3] = 'z'

        self.assert_placed(ZShape(), 0, result)

    def test_highest_block_row_is_zero_on_empty_field(self):
        self.assertEqual(-1, self.field.highest_block_row())

    def test_highest_block_on_even_floor(self):
        self.fill_field_row(BOTTOM_LINE)
        self.assertEqual(BOTTOM_LINE, self.field.highest_block_row())

    def test_highest_block_on_uneven_floor(self):
        self.field.blocks[5][3] = 'l'
        self.assertEqual(3, self.field.highest_block_row())

    def test_find_no_full_line_on_field_with_holes(self):
        self.assertEqual([], self.field._find_full_lines())
        self.fill_field_row(BOTTOM_LINE)
        self.fill_field_row(BOTTOM_LINE-1)
        self.field.blocks[3][BOTTOM_LINE] = 0
        self.field.blocks[FIELD_WIDTH-1][BOTTOM_LINE-1] = 0

        self.assertEqual([], self.field._find_full_lines())

    def test_find_full_lines(self):
        self.fill_field_row(BOTTOM_LINE)
        self.fill_field_row(BOTTOM_LINE-1)
        self.assertEqual([BOTTOM_LINE-1, BOTTOM_LINE], self.field._find_full_lines())

    def test_delete_no_lines_on_empty_list(self):
        result = self.empty_blocks

        self.fill_row(result, BOTTOM_LINE)
        self.fill_field_row(BOTTOM_LINE)
        self.field._delete_lines([])

        self.assertEqual(result, self.field.blocks)

    def test_delete_every_line_in_list(self):
        result = self.empty_blocks
        self.fill_row(result, BOTTOM_LINE)
        self.fill_row(result, BOTTOM_LINE-1)

        self.fill_field_row(BOTTOM_LINE)
        self.fill_field_row(BOTTOM_LINE-1)
        self.fill_field_row(BOTTOM_LINE-2)
        self.fill_field_row(BOTTOM_LINE-3)

        self.field._delete_lines([BOTTOM_LINE-2, BOTTOM_LINE-1])

        self.assertEqual(result, self.field.blocks)

    def test_delete_line_drops_a_line(self):
        result = self.empty_blocks
        self.fill_row(result, BOTTOM_LINE)
        self.fill_row(result, BOTTOM_LINE-1)
        self.fill_field_row(BOTTOM_LINE)
        self.fill_field_row(BOTTOM_LINE-1)
        self.fill_field_row(BOTTOM_LINE-2)

        self.field._delete_lines([BOTTOM_LINE-1])

        self.assertEqual(result, self.field.blocks)


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


if __name__ == '__main__':
    unittest.main()