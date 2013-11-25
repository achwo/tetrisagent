import copy
import random
from settings import FIELD_HEIGHT, FIELD_WIDTH, VANISH_ZONE_HEIGHT

BOTTOM_INDEX = FIELD_HEIGHT - 1
RIGHTMOST_INDEX = FIELD_WIDTH - 1
SPAWN_LOCATION = FIELD_WIDTH / 2 - 1


class Environment(object):
    def __init__(self, blocks=None):
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
        self.lines_deleted = 0

    def possible_actions(self):
        if self.is_game_over():
            return []

        actions = []
        for column in range(0, FIELD_WIDTH):
            if self._column_valid(column):
                actions.append(Action(column))

        return actions

    def _column_valid(self, column):
        return column + self.current_shape.rightmost <= RIGHTMOST_INDEX

    def execute_action(self, action):
        if not self._is_action_valid(action):
            raise InvalidActionError()

        self.field.place(self.current_shape, action.column)
        self._choose_next_shape()
        return self._calculate_reward()

    def _is_action_valid(self, action):
        return action in self.possible_actions()

    def _choose_next_shape(self):
        # possible_shapes = [OShape, JShape, IShape, LShape, ZShape, TShape,
        #                    SShape]
        possible_shapes = [OShape]
        self.current_shape = self.random.choice(possible_shapes)()

    def is_game_over(self):
        return self._is_spawn_blocked() or self._is_block_in_vanish_zone()

    def _is_block_in_vanish_zone(self):
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
        if self.is_game_over():
            return -100
        if self.lines_deleted < self.field.lines_deleted:
            self.lines_deleted = self.field.lines_deleted
            return 100
        return self._height_based_reward()

    def _height_based_reward(self):

        new_highest = self.field.highest_block_row()

        if new_highest < self.highest:
            reward = -10
            self.highest = new_highest
        elif new_highest > self.highest:
            reward = 0
        else:
            reward = 10

        return reward

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

    def place(self, shape, column):
        if not self._is_column_valid(column, shape):
            raise InvalidActionError(
                "Column {0} is not valid for shape {1}".format(column, shape))

        shape.add_x_offset(column)
        self._drop_shape(shape)
        self._add_shape_to_field(shape)
        self._delete_lines(self._find_full_lines())

    def _drop_shape(self, shape):
        while not self._collision(shape):
            for coord in shape.coords:
                coord[1] += 1

    def _collision(self, shape):
        for coord in shape.coords:
            if self._touches_ground(coord) or self._touches_block(coord):
                return True
        return False

    def _touches_ground(self, coord):
        return coord[1] + 1 == FIELD_HEIGHT

    def _touches_block(self, coord):
        return self.blocks[coord[0]][coord[1] + 1] is not 0

    def _add_shape_to_field(self, shape):
        for coord in shape.coords:
            self.blocks[coord[0]][coord[1]] = shape.__repr__()

    def _is_column_valid(self, column, shape):
        return column in self._valid_columns(shape)

    def _valid_columns(self, shape):
        valid = []

        for column in range(FIELD_WIDTH):
            if column + shape.rightmost <= RIGHTMOST_INDEX:
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
    def __init__(self, column):
        self.column = column

    def __eq__(self, other):
        if type(other) is type(self):
            return self.column == other.column
        return False

    def __hash__(self):
        return hash(self.column)

    def __repr__(self):
        return "Action({0})".format(self.column)


class Shape(object):
    def __init__(self, name, coords, spawn_location=SPAWN_LOCATION):
        self.coords = coords
        self.rightmost = self.__furthest_right()
        self.name = name
        self._spawn_location = spawn_location

    def __eq__(self, other):
        if type(self) == type(other):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __furthest_right(self):
        maximum = 0
        for coord in self.coords:
            if coord[0] > maximum:
                maximum = coord[0]
        return maximum

    def add_x_offset(self, offset):
        for coord in self.coords:
            coord[0] += offset

    def spawn_position(self):
        spawn = copy.deepcopy(self.coords)

        for coords in spawn:
            coords[0] += self._spawn_location

        return spawn


class OShape(Shape):
    def __init__(self):
        super(OShape, self).__init__('o', [[0, 0], [0, 1], [1, 0], [1, 1]],
                                     SPAWN_LOCATION + 1)


class IShape(Shape):
    def __init__(self):
        super(IShape, self).__init__('i', [[0, 0], [0, 1], [0, 2], [0, 3]])


class LShape(Shape):
    def __init__(self):
        super(LShape, self).__init__('l', [[0, 0], [0, 1], [0, 2], [1, 2]])


class JShape(Shape):
    def __init__(self):
        super(JShape, self).__init__('j', [[0, 2], [1, 0], [1, 1], [1, 2]])


class TShape(Shape):
    def __init__(self):
        super(TShape, self).__init__('t', [[0, 1], [1, 0], [1, 1], [2, 1]])


class SShape(Shape):
    def __init__(self):
        super(SShape, self).__init__('s', [[0, 0], [0, 1], [1, 1], [1, 2]])


class ZShape(Shape):
    def __init__(self):
        super(ZShape, self).__init__('z', [[0, 1], [0, 2], [1, 0], [1, 1]])


class InvalidActionError(RuntimeError):
    pass