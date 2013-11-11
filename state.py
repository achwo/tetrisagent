import copy
import features


class PerceivedState(object):
    pass


class SimplePerceivedState(PerceivedState):
    def __init__(self, environment):
        self.blocks = copy.deepcopy(environment.blocks)
        self.shape = environment.current_shape


class HolePerceivedState(PerceivedState):
    def __init__(self, environment):
        self.number_holes = features.number_of_holes(environment)


class MinHeightPerceivedState(PerceivedState):
    def __init__(self, environment):
        self.min_height = features.min_height(environment)