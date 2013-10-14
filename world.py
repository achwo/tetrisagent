FIELD_WIDTH = 10
FIELD_HEIGHT = 12

S0 = tuple(
    [tuple(0 for i in range(0, FIELD_WIDTH)) for i in
     range(0, FIELD_HEIGHT)])


class World(object):

    def reward(self, state, action):
        pass

    def calculate_reward(self, consecutive_zeros):
        if len(consecutive_zeros) > 0 and max(consecutive_zeros) < 2:
            score_i = -10
        elif len(consecutive_zeros) == 0:
            score_i = 10
        else:
            score_i = 0
        return score_i

    def create_new_state(self, state, row, action):
        """
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
