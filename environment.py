import copy
import random
import settings


BOTTOM_INDEX = settings.FIELD_HEIGHT - 1
RIGHTMOST_INDEX = settings.FIELD_WIDTH - 1


class Environment(object):
    def __init__(self, blocks=None):
        self.random = random.Random()
        self.initialize()
        if blocks is not None:
            self.blocks = blocks
        self._choose_next_shape()

    def initialize(self):
        self.highest = BOTTOM_INDEX  # counted backwards because of indexing
        self.blocks = [[0 for _ in range(settings.FIELD_HEIGHT)] for _ in
                       range(settings.FIELD_WIDTH)]
        self._choose_next_shape()

    def possible_actions(self):
        if self.is_game_over():
            return []

        actions = []
        for column in range(0, settings.FIELD_WIDTH):
            if self._column_valid(column):
                actions.append(Action(column))

        return actions

    def _column_valid(self, column):
        return column + self.current_shape.rightmost <= RIGHTMOST_INDEX

    def execute_action(self, action):
        if not self._is_action_valid(action):
            raise InvalidActionError()

        self._place_current_shape_in_column(action.column)
        self._choose_next_shape()
        return self._calculate_reward()

    def _is_action_valid(self, action):
        return action in self.possible_actions()

    def _place_current_shape_in_column(self, column):
        self.current_shape.add_x_offset(column)
        self._drop_shape()
        self._add_shape_to_field()

    def _drop_shape(self):
        while not self._collision():
            for coord in self.current_shape.coords:
                coord[1] += 1

    def _collision(self):
        for coord in self.current_shape.coords:
            if self._touches_ground(coord) or self._touches_block(coord):
                return True
        return False

    def _touches_ground(self, coord):
        return coord[1] + 1 == settings.FIELD_HEIGHT

    def _touches_block(self, coord):
        return self.blocks[coord[0]][coord[1] + 1] is not 0

    def _add_shape_to_field(self):
        for coord in self.current_shape.coords:
            self.blocks[coord[0]][coord[1]] = self.current_shape.__repr__()

    def _choose_next_shape(self):
        # possible_shapes = [OShape]
        possible_shapes = [OShape, JShape, IShape, LShape, ZShape, TShape,
                           SShape]
        self.current_shape = self.random.choice(possible_shapes)()

    def is_game_over(self):
        return self._is_spawn_blocked() or self._is_block_in_vanish_zone()

    def _is_block_in_vanish_zone(self):
        for col in self.blocks:
            for row in range(settings.VANISH_ZONE_HEIGHT):
                if col[row] != 0:
                    return True
        return False

    def _is_spawn_blocked(self):
        for coord in self.current_shape.spawn_position():
            if self.blocks[coord[0]][coord[1]] != 0:
                return True
        return False

    def _highest_block_row(self):
        for row in range(len(self.blocks)):
            for col in self.blocks[row]:
                if col != 0:
                    return row

    def _calculate_reward(self):
        if self.is_game_over():
            return -100
        return self._height_based_reward()

    def _height_based_reward(self):

        new_highest = self._highest_block_row()

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
        for col in self.blocks:
            row.append(col[row_number])
        return row


class Action(object):
    def __init__(self, column):
        self.column = column

    def __eq__(self, other):
        if type(other) is type(self):
            return self.column == other.column
        return False

    def __repr__(self):
        return "Action({0})".format(self.column)


class Shape(object):
    def __init__(self, coords, name, spawn_position):
        self.coords = coords
        self.rightmost = self.__furthest_right()
        self.name = name
        self._spawn_position = spawn_position

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
            coords[0] += self._spawn_position

        return spawn


class OShape(Shape):
    def __init__(self):
        super(OShape, self).__init__([[0, 0], [0, 1], [1, 0], [1, 1]], 'o',
                                     settings.FIELD_WIDTH / 2)


class IShape(Shape):
    def __init__(self):
        super(IShape, self).__init__([[0, 0], [0, 1], [0, 2], [0, 3]], 'i',
                                     settings.FIELD_WIDTH / 2)


class LShape(Shape):
    def __init__(self):
        super(LShape, self).__init__([[0, 0], [0, 1], [0, 2], [1, 2]], 'l',
                                     settings.FIELD_WIDTH / 2 - 1)


class JShape(Shape):
    def __init__(self):
        super(JShape, self).__init__([[0, 2], [1, 0], [1, 1], [1, 2]], 'j',
                                     settings.FIELD_WIDTH / 2 - 1)


class TShape(Shape):
    def __init__(self):
        super(TShape, self).__init__([[0, 1], [1, 0], [1, 1], [2, 1]], 't',
                                     settings.FIELD_WIDTH / 2 - 1)


class SShape(Shape):
    def __init__(self):
        super(SShape, self).__init__([[0, 0], [0, 1], [1, 1], [1, 2]], 's',
                                     settings.FIELD_WIDTH / 2 - 1)


class ZShape(Shape):
    def __init__(self):
        super(ZShape, self).__init__([[0, 1], [0, 2], [1, 0], [1, 1]], 'z',
                                     settings.FIELD_WIDTH / 2 - 1)


class InvalidActionError(RuntimeError):
    pass