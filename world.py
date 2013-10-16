from itertools import groupby

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

    def is_final_state(self, state):
        """

        :param state:
        :return:
        """
        if state is None:
            return True

        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(state[len(state) - 1], lambda x: x == 0) if
                             g]
        return len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2

    def final_score(self, state):
        """
        Returns the score once the episode is finished

        :param state:
        :return:
        """
        # todo  could be abstracted, since it would be great as a parameter
        #       or maybe changed entirely
        if state is None:
            return 0
        for row in state:
            # when at least one unfilled field, score is -100
            if len(row) != reduce(lambda x, y: x + y, row):
                return -100
        return 100

    def execute_action(self, state, action):
        row = len(state) - 1
        # find row where the piece will land on
        while row >= 0 and state[row][action] == 0 and state[row][
                    action + 1] == 0:
            row -= 1
        row += 1
        # piece hit the roof => gameover
        if row > len(state) - 2:
            return self.final_score(state), None

        new_state = self.create_new_state(state, row, action)

        # looks for more zero groups in a row
        # (ex. (0, 0, 1, 1, 0, 0, 1, 1, 0) result: (2, 2, 1))
        consecutive_zeros = [len(list(v)) for g, v in
                             groupby(new_state[row], lambda x: x == 0) if g]

        # possibilities depleted => calculate final score
        if row == len(new_state) - 2:
            if len(consecutive_zeros) <= 0 or max(consecutive_zeros) < 2:
                return self.final_score(new_state), new_state

        # otherwise, calculate current reward
        score_i = self.calculate_reward(consecutive_zeros)

        return score_i, new_state

    def current_state(self):
        return self.state