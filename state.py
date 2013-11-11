import copy

from features import number_of_holes
from features import min_height


class PerceivedState(object):
    def __init__(self, environment, *features):
        self.features = []
        for f in features:
            self.features.append(f(environment))


class SimplePerceivedState(PerceivedState):
    def __init__(self, environment, *features):
        super(SimplePerceivedState, self).__init__(environment, *features)
        self.blocks = copy.deepcopy(environment.blocks)
        self.shape = environment.current_shape


class FirstPerceivedState(PerceivedState):
    def __init__(self, environment, *features):
        super(FirstPerceivedState, self).__init__(environment, number_of_holes,
                                                  min_height, *features)
        self.shape = environment.current_shape