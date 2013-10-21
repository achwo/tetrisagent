
def enum(**enums):
    return type('Enum', (), enums)

FIELD_WIDTH = 10
FIELD_HEIGHT = 12
Possible_Shapes = enum(T='T', L='L', S='S', Z='Z', O='O', I='I', J='J')


S0 = tuple(
    [tuple(0 for i in range(0, FIELD_WIDTH)) for i in
     range(0, FIELD_HEIGHT)])


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

        ret = tuple(state_new)
        return ret

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
    def __init__(self, arrstate=S0):
        self.arrstate = arrstate
        self.board = None




class Action(object):
    def __init__(self, column):
        self.column = column

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        if other is self:
            return True
        return other.column == self.column
