import copy
import random

FIELD_WIDTH = 10
FIELD_HEIGHT = 12

S0 = [[0 for i in range(FIELD_HEIGHT)] for j in
      range(FIELD_WIDTH)]


class World(object):
    def __init__(self):
        self.current_state = State()
        self.random = random.Random()
        self.update_current_shape()

    def actions(self):
        return self.current_state.possible_actions(self.current_shape)

    def execute_action(self, action):
        self.place_current_shape_in_column(action.column)
        self.update_current_shape()

        return self.current_state, self.make_reward(action)

    def make_reward(self, action):
        return self.evaluate_features()

    def update_current_shape(self):
        possible_shapes = [OShape, JShape, IShape, LShape, ZShape, TShape,
                           SShape]
        self.current_shape = self.random.choice(possible_shapes)()

    def place_current_shape_in_column(self, column):
        self.current_state = self.current_state.place_shape(self.current_shape,
                                                            column)

    def init_state(self):
        self.current_state = State()

    def current_state_terminal(self):
        return self.current_state.terminal

    def evaluate_features(self):
        # todo evaluate and include features
        return 10


class State(object):
    def __init__(self, blocks=S0):
        self.blocks = blocks
        self.max_index_width = FIELD_WIDTH - 1
        self.bottom_index = FIELD_HEIGHT - 1
        self.terminal = False

    def drop_shape(self, shape):
        while not self.collision(shape):
            for coord in shape.coords:
                coord[1] += 1

    def add_shape_to_field(self, shape):
        new_blocks = copy.deepcopy(self.blocks)
        for coord in shape.coords:
            new_blocks[coord[0]][coord[1]] = shape.__repr__()
        return new_blocks

    def place_shape(self, shape, column):
        self.check_column_in_bounds(column, shape)
        shape.add_x_offset(column)
        self.drop_shape(shape)
        new_blocks = self.add_shape_to_field(shape)

        new_state = State(new_blocks)
        new_state.check_terminal()

        return new_state

    def collision(self, shape):
        for coord in shape.coords:
            if coord[1] + 1 == FIELD_HEIGHT:
                return True
            if self.blocks[coord[0]][coord[1] + 1] is not 0:
                return True
        return False

    def check_column_in_bounds(self, column, shape):
        if not self.column_valid_for_given_shape(column, shape):
            raise IndexError(
                '{0} + {2} <= {1}'.format(column, self.max_index_width,
                                          shape.rightmost))

    def column_valid_for_given_shape(self, column, shape):
        return column + shape.rightmost <= self.max_index_width

    def possible_actions(self, shape):
        actions = []

        for column in range(0, FIELD_WIDTH):
            if self.column_valid_for_given_shape(column, shape):
                actions.append(Action(column))

        return set(actions)

    def check_terminal(self):
        if self.collision(OShape()):
            self.terminal = True


class Action(object):
    def __init__(self, column):
        self.column = column

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        if other is self:
            return True
        return other.column == self.column


class Shape(object):
    def __init__(self, coords, name):
        self.coords = coords
        self.rightmost = self.__furthest_right()
        self.name = name

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


class OShape(Shape):
    def __init__(self):
        super(OShape, self).__init__([[0, 0], [0, 1], [1, 0], [1, 1]], 'o')


class IShape(Shape):
    def __init__(self):
        super(IShape, self).__init__([[0, 0], [0, 1], [0, 2], [0, 3]], 'i')


class LShape(Shape):
    def __init__(self):
        super(LShape, self).__init__([[0, 0], [0, 1], [0, 2], [1, 2]], 'l')


class JShape(Shape):
    def __init__(self):
        super(JShape, self).__init__([[0, 2], [1, 0], [1, 1], [1, 2]], 'j')


class TShape(Shape):
    def __init__(self):
        super(TShape, self).__init__([[0, 1], [1, 0], [1, 1], [2, 1]], 't')


class SShape(Shape):
    def __init__(self):
        super(SShape, self).__init__([[0, 0], [0, 1], [1, 1], [1, 2]], 's')


class ZShape(Shape):
    def __init__(self):
        super(ZShape, self).__init__([[0, 1], [0, 2], [1, 0], [1, 1]], 'z')


class CollisionShape(Shape):
    def __init__(self):
        super(CollisionShape, self).__init__([[0, 0], [0, 1], [0, 2], [1, 0],
                                              [1, 1], [1, 2], [2, 0], [2, 1],
                                              [2, 2]], 'COLLISION ATTACK')
