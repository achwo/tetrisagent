import copy
import random
import reward_features
from settings import FIELD_HEIGHT, FIELD_WIDTH, VANISH_ZONE_HEIGHT

BOTTOM_INDEX = FIELD_HEIGHT - 1
RIGHTMOST_INDEX = FIELD_WIDTH - 1
SPAWN_LOCATION = FIELD_WIDTH / 2 - 1
BASE_SCORE_MULTIPLIER = 10


class Environment(object):
    def __init__(self, blocks=None):

        # can be set from gui, therefore maybe default is not used
        self.possible_shapes = [OShape, JShape, IShape, LShape, ZShape, TShape,
                           SShape]

        # can be set from gui, therefore maybe default is not used
        self.rewards = {reward_features.game_over_reward: 25,
                        reward_features.removed_line_reward: 10,
                        reward_features.number_of_holes_reward: 1,
                        reward_features.number_of_covers_reward: 1,
                        reward_features.max_height_reward: 0.5,
                        reward_features.sum_of_column_height_differences_reward: 0.7,
                        reward_features.number_of_blocks_reward: 0.5}
        self.random = random.Random()
        self.field = Field()
        self.initialize()
        self.field.initialize(blocks)
        self._choose_next_shape()

    def __eq__(self, other):
        if type(self) == type(other):
            return self.field == other.field and \
                   self.current_shape == other.current_shape
        return False

    def __hash__(self):
        return hash((self.field, self.current_shape))

    def initialize(self):
        self.highest = BOTTOM_INDEX  # counted backwards because of indexing
        self.field.initialize()
        self._choose_next_shape()
        self.deleted_lines_last_round = 0

    def choose_next_shape(self):
        self._choose_next_shape()

    def possible_actions(self):
        """
        Calculates which actions are possible for the current shape.
        Since some shapes are very wide in certain rotations, the last few
        columns would often be out of bounds otherwise.

        :return: list of possible actions
        """
        if self.is_game_over():
            return []

        actions = []
        for rotation in range(len(self.current_shape.rotations)):
            for column in range(0, FIELD_WIDTH):
                if self._column_valid(column, rotation):
                    actions.append(Action(column, rotation))

        return actions

    def _column_valid(self, column, rotation):
        return column + self.current_shape.rightmost(rotation) <= RIGHTMOST_INDEX

    def execute_action(self, action):
        """
        Executes the given action, if valid and calculates the reward for this action.
        :param action: Action object
        :return: the reward for the action
        :raise: InvalidActionError if action is invalid
        """
        if not self._is_action_valid(action):
            raise InvalidActionError()

        self.field.place(self.current_shape, action)
        self._choose_next_shape()
        return self._calculate_reward()

    def _is_action_valid(self, action):
        return action in self.possible_actions()

    def _choose_next_shape(self):
        self.current_shape = self.random.choice(self.possible_shapes)()

    def is_game_over(self):
        return self._is_spawn_blocked() or self._is_block_in_vanish_zone()

    def _is_block_in_vanish_zone(self):
        """
        Vanish zone is the invisible zone of the field above the screen.
        According to the official Tetris standard, there may be no block placed
        inside of the vanish zone.
        """
        for col in self.field.blocks:
            for row in range(VANISH_ZONE_HEIGHT):
                if col[row] != 0:
                    return True
        return False

    def _is_spawn_blocked(self):
        for coord in self.current_shape.spawn_position():
            if self.field.blocks[coord[0]][coord[1]] != 0:
                return True
        return False

    def _calculate_reward(self):
        reward = 0

        for feature, weighting in self.rewards.iteritems():
            reward += BASE_SCORE_MULTIPLIER * weighting * feature(self)

        return reward

    def number_lines_deleted(self):
        deleted_previously = self.deleted_lines_last_round
        self.deleted_lines_last_round = self.field.lines_deleted

        return self.field.lines_deleted - deleted_previously

    def row(self, row_number):
        row = []
        for col in self.field.blocks:
            row.append(col[row_number])
        return row


class Field(object):
    def __init__(self):
        self.initialize()

    def __eq__(self, other):
        if (type(self) == type(other)):
            return self.blocks == other.blocks
        return False

    def __hash__(self):
        return hash(tuple(self.blocks))

    def initialize(self, blocks=None):
        self.lines_deleted = 0
        if blocks is None:
            self.blocks = [[0 for _ in range(FIELD_HEIGHT)] for _ in
                           range(FIELD_WIDTH)]
        else:
            self.blocks = blocks

    def place(self, shape, action):
        if not self._is_action_valid(action, shape):
            raise InvalidActionError(
                "{0} is not valid for shape {1}".format(action, shape))

        shape.set_drop_rotation(action.rotation)
        shape.add_x_offset(action.column)
        self._drop_shape(shape)
        self._add_shape_to_field(shape)
        self._delete_lines(self._find_full_lines())

    def _drop_shape(self, shape):
        while not self._collision(shape):
            for coord in shape.dropping_coords:
                coord[1] += 1

    def _collision(self, shape):
        for coord in shape.dropping_coords:
            if self._touches_ground(coord) or self._touches_block(coord):
                return True
        return False

    def _touches_ground(self, coord):
        return coord[1] + 1 == FIELD_HEIGHT

    def _touches_block(self, coord):
        return self.blocks[coord[0]][coord[1] + 1] is not 0

    def _add_shape_to_field(self, shape):
        for coord in shape.dropping_coords:
            self.blocks[coord[0]][coord[1]] = shape.__repr__()

    def _is_action_valid(self, action, shape):
        return action.column in self._valid_columns(shape, action.rotation)

    def _valid_columns(self, shape, rotation):
        valid = []

        for column in range(FIELD_WIDTH):
            if column + shape.rightmost(rotation) <= RIGHTMOST_INDEX:
                valid.append(column)

        return valid

    def highest_block_row(self):
        for row in range(FIELD_HEIGHT):
            for col in self.blocks:
                if col[row] != 0:
                    return row
        return -1

    def _find_full_lines(self):
        full_lines = []
        for row in range(FIELD_HEIGHT):
            holes = False
            for col in range(FIELD_WIDTH):
                if self.blocks[col][row] == 0:
                    holes = True
                    break
            if not holes:
                full_lines.append(row)

        return full_lines

    def _delete_lines(self, lines):
        for line in lines:
            self._delete_line(line)

        self.lines_deleted += len(lines)

    def _delete_line(self, line):
        for col in range(FIELD_WIDTH):
            del self.blocks[col][line]
            self.blocks[col].insert(0, 0)


class Action(object):
    def __init__(self, column, rotation):
        self.column = column
        self.rotation = rotation

    def __eq__(self, other):
        if type(other) is type(self):
            return self.column == other.column and self.rotation == other.rotation
        return False

    def __hash__(self):
        return hash(self.column)

    def __repr__(self):
        return "Action({0}, {1})".format(self.column, self.rotation)


class Shape(object):
    def __init__(self, name, spawn_column=SPAWN_LOCATION):
        self.name = name
        self._spawn_column = spawn_column

    def __eq__(self, other):
        if type(self) == type(other):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def rightmost(self, rotation):
        """
        The rightmost position in which the shape can be placed in the given
        rotation.
        :return: column number
        """
        maximum = 0
        for coord in self.rotations[rotation]:
            if coord[0] > maximum:
                maximum = coord[0]
        return maximum

    def add_x_offset(self, offset):
        for coord in self.dropping_coords:
            coord[0] += offset

    def spawn_position(self):
        spawn = copy.deepcopy(self.rotations[0])

        for coords in spawn:
            coords[0] += self._spawn_column

        return spawn

    def set_drop_rotation(self, rotation):
        self.dropping_coords = self.rotations[rotation]


class OShape(Shape):
    def __init__(self):
        super(OShape, self).__init__('o', SPAWN_LOCATION + 1)
        self.rotations = [[[0, 0], [0, 1], [1, 0], [1, 1]]]


class IShape(Shape):
    def __init__(self):
        super(IShape, self).__init__('i')
        self.rotations = [
            [[0, 0], [1, 0], [2, 0], [3, 0]],
            [[0, 0], [0, 1], [0, 2], [0, 3]]
        ]


class LShape(Shape):
    def __init__(self):
        super(LShape, self).__init__('l')
        self.rotations = [
            [[0, 1], [1, 1], [2, 0], [2, 1]],
            [[0, 0], [0, 1], [0, 2], [1, 2]], 
            [[0, 0], [0, 1], [1, 0], [2, 0]],
            [[0, 0], [1, 0], [1, 1], [1, 2]]
        ]


class JShape(Shape):
    def __init__(self):
        super(JShape, self).__init__('j')
        self.rotations = [
            [[0, 0], [0, 1], [1, 1], [2, 1]],
            [[0, 2], [1, 0], [1, 1], [1, 2]],
            [[0, 0], [0, 1], [0, 2], [1, 0]],
            [[0, 0], [1, 0], [2, 0], [2, 1]]
        ]


class TShape(Shape):
    def __init__(self):
        super(TShape, self).__init__('t')
        self.rotations = [
            [[0, 1], [1, 0], [1, 1], [2, 1]],
            [[0, 1], [1, 0], [1, 1], [1, 2]],
            [[0, 0], [1, 0], [1, 1], [2, 0]],
            [[0, 0], [0, 1], [0, 2], [1, 1]]
        ]


class SShape(Shape):
    def __init__(self):
        super(SShape, self).__init__('s')
        self.rotations = [
            [[0, 1], [1, 0], [1, 1], [2, 0]],
            [[0, 0], [0, 1], [1, 1], [1, 2]]
        ]


class ZShape(Shape):
    def __init__(self):
        super(ZShape, self).__init__('z')
        self.rotations = [
            [[0, 0], [1, 0], [1, 1], [2, 1]],
            [[0, 1], [0, 2], [1, 0], [1, 1]]
        ]

class InvalidActionError(RuntimeError):
    pass
