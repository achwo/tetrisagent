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

    def calculate_reward(self, consecutive_zeros):
        """
        alter kram
        """
        if len(consecutive_zeros) > 0 and max(consecutive_zeros) < 2:
            score_i = -10
        elif len(consecutive_zeros) == 0:
            score_i = 10
        else:
            score_i = 0
        return score_i

    def create_new_state(self, state, row, action):
        """
        alter kram
        Creates a new state based on the previous state and the action

        :param state:
        :param row:
        :param action:
        :return:
        """
        state_new = []
        for i in state:
            state_new.append(tuple(i))
        state_new[row] = list(state_new[row])            # convert last 2 rows
        state_new[row + 1] = list(state_new[row + 1])    # to lists

        # todo this part is block-shape specific
        # add the new block into the game matrix -> new state
        state_new[row][action] = 1
        state_new[row][action + 1] = 1
        state_new[row + 1][action] = 1
        state_new[row + 1][action + 1] = 1

        state_new[row] = tuple(state_new[row])           # convert last 2 rows
        state_new[row + 1] = tuple(state_new[row + 1])   # back to tuples

        return tuple(state_new)

    def execute_action(self, action):
        self.place_current_shape_in_column(action.column)
        self.update_current_shape()
        return self.make_reward(action)

    def make_reward(self, action):
        return 0

    def update_current_shape(self):
        self.current_shape = Possible_Shapes.O

    def place_current_shape_in_column(self, column):
        pass


class State(object):
    def __init__(self, blocks=S0):
        self.blocks = blocks
        self.max_index_width = FIELD_WIDTH - 1
        self.bottom_index = FIELD_HEIGHT - 1

    def place_shape(self, shape, column):
        self.check_column_in_bounds(column, shape)
        new_blocks = copy.deepcopy(self.blocks)
        shape.add_x_offset(column)

        while not self.collision(shape):
            for coord in shape.coords:
                coord[1] += 1

        for coord in shape.coords:
            new_blocks[coord[0]][coord[1]] = shape.__repr__()

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