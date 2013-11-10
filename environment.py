import copy
import random

FIELD_WIDTH = 10
FIELD_HEIGHT = 12
VANISH_ZONE = 11

S0 = [[0 for i in range(FIELD_HEIGHT)] for j in
      range(FIELD_WIDTH)]


class InvalidActionError(RuntimeError):
    pass


class Environment(object):
    def __init__(self, blocks=S0):
        self.blocks = blocks
        self.random = random.Random()
        self._choose_next_shape()
        self.max_index_width = FIELD_WIDTH - 1
        self.bottom_index = FIELD_HEIGHT - 1

    def possible_actions(self):
        if self.is_game_over():
            return []

        actions = []
        for column in range(0, FIELD_WIDTH):
            if self._column_valid(column):
                actions.append(Action(column))

        return actions

    def _column_valid(self, column):
        return column + self.current_shape.rightmost <= self.max_index_width

    def execute_action(self, action):
        if not self._is_action_valid(action):
            raise InvalidActionError()

        self._place_current_shape_in_column(action.column)
        self._choose_next_shape()

        return self._make_reward(action) # todo reward has to go

    def _is_action_valid(self, action):
        return action in self.possible_actions()

    def _place_current_shape_in_column(self, column):
        self.current_shape.add_x_offset(column)
        self._drop_shape()
        self._add_shape_to_field()
        # todo agent has to update his perceived state

    def _drop_shape(self):
        while not self._collision():
            for coord in self.current_shape.coords:
                coord[1] += 1

    def _collision(self):
        for coord in self.current_shape.coords:
            if coord[1] + 1 == FIELD_HEIGHT:
                return True
            if self.blocks[coord[0]][coord[1] + 1] is not 0:
                return True
        return False

    def _add_shape_to_field(self):
        for coord in self.current_shape.coords:
            self.blocks[coord[0]][coord[1]] = self.current_shape.__repr__()
    #todo add shape to field


    def _choose_next_shape(self):
        possible_shapes = [OShape, JShape, IShape, LShape, ZShape, TShape,
                           SShape]
        self.current_shape = self.random.choice(possible_shapes)()

    def _make_reward(self, action):
        #todo aufgabe des agents, anhand perceived state
        return 10

    def is_game_over(self):
        return self._is_spawn_blocked() or self._is_block_in_vanish_zone()

    def _is_block_in_vanish_zone(self):
        for col in self.blocks:
            if col[1] != 0 or col[0] != 0:
                return True
        return False

    def _is_spawn_blocked(self):
        for coord in self.current_shape.spawn_position():
            if self.blocks[coord[0]][coord[1]] != 0:
                return True
        return False


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
        super(OShape, self).__init__([[0, 0], [0, 1], [1, 0], [1, 1]], 'o', FIELD_WIDTH / 2)


class IShape(Shape):
    def __init__(self):
        super(IShape, self).__init__([[0, 0], [0, 1], [0, 2], [0, 3]], 'i', FIELD_WIDTH / 2)


class LShape(Shape):
    def __init__(self):
        super(LShape, self).__init__([[0, 0], [0, 1], [0, 2], [1, 2]], 'l', FIELD_WIDTH / 2 - 1)


class JShape(Shape):
    def __init__(self):
        super(JShape, self).__init__([[0, 2], [1, 0], [1, 1], [1, 2]], 'j', FIELD_WIDTH / 2 - 1)


class TShape(Shape):
    def __init__(self):
        super(TShape, self).__init__([[0, 1], [1, 0], [1, 1], [2, 1]], 't', FIELD_WIDTH / 2 - 1)


class SShape(Shape):
    def __init__(self):
        super(SShape, self).__init__([[0, 0], [0, 1], [1, 1], [1, 2]], 's', FIELD_WIDTH / 2 - 1)


class ZShape(Shape):
    def __init__(self):
        super(ZShape, self).__init__([[0, 1], [0, 2], [1, 0], [1, 1]], 'z', FIELD_WIDTH / 2 - 1)
