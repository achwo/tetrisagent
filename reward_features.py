# reward features have to return 1, -1 or 0

def removed_line_reward(environment):
    if environment.number_lines_deleted() > 0:
        return 1
    else:
        return 0

def game_over_reward(environment):
    if environment.is_game_over():
        return -1
    return 0