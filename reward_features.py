# reward features have to return 1, -1 or 0
import features

from features import *

def removed_line_reward(environment):
    if environment.number_lines_deleted() > 0:
        return 1
    else:
        return 0

def game_over_reward(environment):
    if environment.is_game_over():
        return -1
    return 0

def max_height_reward(environment):
	return -(features.max_height(environment) / FIELD_HEIGHT)

#def min_height_reward(environment):
#	return features.min_height(environment) / FIELD_HEIGHT

def number_of_holes_reward(environment):
    if number_of_holes(environment) > 0:
        return -(number_of_holes(environment))
    return 0

def number_of_blocks_reward(environment):
    if number_of_blocks(environment) > 0:
        return -(number_of_blocks(environment)/4)
    return 0

def weighted_number_of_blocks_reward(environment):
    res = 0
    for i in range(FIELD_HEIGHT+1):
        res += i
    return -(weighted_number_of_blocks(environment)/res/FIELD_WIDTH)

def number_of_covers_reward(environment):
	if number_of_covers(environment) > 0:
		return -(number_of_covers(environment))
	return 0

def sum_of_column_height_differences_reward(environment):
    return -(sum_of_column_height_differences(environment))

