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
        self.board = None
        self.state = [[0 for i in range(FIELD_HEIGHT)] for j in
                       range(FIELD_WIDTH)]
        self.max_index_width = FIELD_WIDTH - 1
        self.bottom_index = FIELD_HEIGHT - 1

    def place_shape(self, shape, column):
        if(column > self.max_index_width):
            raise IndexError("Given column %i greater than max index %i",
                             column, self.max_index_width)
        new_blocks = copy.deepcopy(self.blocks)
        if(type(shape) is OShape):
            new_blocks[0][self.bottom_index -1] = shape.__repr__()
            new_blocks[0][self.bottom_index] = shape.__repr__()
            new_blocks[1][self.bottom_index -1] = shape.__repr__()
            new_blocks[1][self.bottom_index] = shape.__repr__()
        elif(type(shape) is IShape):
            new_blocks[0][self.bottom_index] = shape.__repr__()
            new_blocks[0][self.bottom_index -1] = shape.__repr__()
            new_blocks[0][self.bottom_index -2] = shape.__repr__()
            new_blocks[0][self.bottom_index -3] = shape.__repr__()

        return State(new_blocks)


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
    pass

class OShape(Shape):
    def __init__(self):
        self.coords = ((0, 0), (0, 1), (1, 0), (1, 1))

    def __repr__(self):
        return 'o'

class IShape(Shape):
    def __init__(self):
        self.coords = ((0, 0), (0, 1), (0, 2), (0, 3))

    def __repr__(self):
        return 'i'