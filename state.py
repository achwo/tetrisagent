import copy
from BitVector import BitVector

from features import number_of_holes
from features import min_height
import environment as e


class PerceivedState(object):
    def __init__(self, environment, *features):
        self.shape = environment.current_shape
        self.features = []
        for f in features:
            self.features.append(f(environment))


    def __eq__(self, other):
        if type(other) is type(self):
            self_props = vars(self)
            other_props = vars(other)

            for self_p, other_p in zip(self_props, other_props):
                if self_p != other_p:
                    return False
        return True


class WorkingAreaPerceivedState(PerceivedState):
    def __init__(self, environment, *features):
        super(WorkingAreaPerceivedState, self).__init__(environment)
        highest = environment.highest
        if highest == e.BOTTOM_INDEX:
            highest -= 1

        self.area = [environment.row(highest), environment.row(highest+1)]

    def __eq__(self, other):
        return super.__eq__(other) and self.area == other.area


class BlockPerceivedState(PerceivedState):
    def __init__(self, environment, *features):
        super(BlockPerceivedState, self).__init__(environment, *features)
        self.blocks = field_to_bitvector(environment.blocks)

    def __eq__(self, other):
        # return super.__eq__(other) and self.blocks == other.blocks
        return self.blocks == other.blocks


class FirstPerceivedState(PerceivedState):
    def __init__(self, environment, *features):
        super(FirstPerceivedState, self).__init__(environment, number_of_holes,
                                                  min_height, *features)

    def __eq__(self, other):
        super.__eq__(other)


def field_to_bitvector(field):
    bits = []
    for col in field:
        for cell in col:
            if cell != 0:
                bits.append(1)
            else:
                bits.append(0)

    return BitVector(bitlist=bits)