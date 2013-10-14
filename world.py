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