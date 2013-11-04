import copy


def enum(**enums):
    return type('Enum', (), enums)


FIELD_WIDTH = 10
FIELD_HEIGHT = 12
Possible_Shapes = enum(T='t', L='l', S='s', Z='z', O='o', I='i', J='j')

old_S0 = tuple(
    [tuple(0 for i in range(0, FIELD_WIDTH)) for i in
     range(0, FIELD_HEIGHT)])

S0 = [[0 for i in range(FIELD_HEIGHT)] for j in
      range(FIELD_WIDTH)]


class World(object):
    def __init__(self):
        self.game_controller = None
        self.current_state = State()
        self.update_current_shape()

    def actions(self):
        return self.current_state.possible_actions()

    def execute_action(self, action):
        self.place_current_shape_in_column(action.column)
        self.update_current_shape()

        return self.current_state, self.make_reward(action)

    def make_reward(self, action):

        return self.evaluate_features()

    def update_current_shape(self):
        self.current_shape = OShape()

    def place_current_shape_in_column(self, column):
        self.current_state = self.current_state.place_shape(self.current_shape, column)

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

        return State(new_blocks)

    def collision(self, shape):
        for coord in shape.coords:
            if coord[1] + 1 == FIELD_HEIGHT:
                return True
            if self.blocks[coord[0]][coord[1] + 1] is not 0:
                return True
        return False

    def check_column_in_bounds(self, column, shape):
        if column > self.max_index_width or \
                self.is_column_valid_for_given_shape(column, shape):
            raise IndexError()

    def is_column_valid_for_given_shape(self, column, shape):
        return self.max_index_width - shape.furthest_right() < column


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
    def __init__(self):
        self.coords = None

    def furthest_right(self):
        max = 0
        for coord in self.coords:
            if coord[0] > max:
                max = coord[0]
        return max

    def add_x_offset(self, offset):
       for coord in self.coords:
           coord[0] += offset



class OShape(Shape):
    def __init__(self):
        self.coords = [[0, 0], [0, 1], [1, 0], [1, 1]]

    def __repr__(self):
        return 'o'


class IShape(Shape):
    def __init__(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [0, 3]]

    def __repr__(self):
        return 'i'


class LShape(Shape):
    def __init__(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 2]]

    def __repr__(self):
        return 'l'


class JShape(Shape):
    def __init__(self):
        self.coords = [[0, 2], [1, 0], [1, 1], [1, 2]]

    def __repr__(self):
        return 'j'


class TShape(Shape):
    def __init__(self):
        self.coords = [[0, 1], [1, 0], [1, 1], [2, 1]]

    def __repr__(self):
        return 't'


class SShape(Shape):
    def __init__(self):
        self.coords = [[0, 0], [0, 1], [1, 1], [1, 2]]

    def __repr__(self):
        return 's'


class ZShape(Shape):
    def __init__(self):
        self.coords = [[0, 1], [0, 2], [1, 0], [1, 1]]

    def __repr__(self):
        return 'z'