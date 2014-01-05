import math
from BitVector import BitVector
from settings import FIELD_HEIGHT, FIELD_WIDTH
#from environment import Environment

#env = Environment()


def max_height(environment):
    max_height = 0
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0 and (
                    FIELD_HEIGHT - j) > max_height:
                max_height = FIELD_HEIGHT - j
                break
            elif environment.field.blocks[i][j] is not 0:
                break
    return float(max_height)


def min_height(environment):
    #the lowest column
    #return value is the height not the row
    min_height = FIELD_HEIGHT
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0 and (
                    FIELD_HEIGHT - j) < min_height:
                min_height = FIELD_HEIGHT - j
                break
            elif environment.field.blocks[i][j] is not 0:
                break
            elif j == 11:
                min_height = 0
    return min_height


def individual_height(environment):
    #the height of every column
    stack = []
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0:
                stack.append(FIELD_HEIGHT - j)
                break
            elif j == 11:
                stack.append(0)

    return stack


def sum_of_individual_height(environment):
    indi_height = individual_height(environment)
    sum = 0
    for i in range(FIELD_WIDTH):
        sum += indi_height[i]
    return sum


def column_height_differences(environment):
    #Hoehenunterschiede zwischen den Spalten
    indi_height = individual_height(environment)
    stack = []
    for i in range(FIELD_WIDTH - 1):
        stack.append(indi_height[i + 1] - indi_height[i])
    return stack


def sum_of_column_height_differences(environment):
    #Summe der Hoehenunterschiede zwischen den Spalten
    col_height = column_height_differences(environment)
    sum = 0
    for i in range(FIELD_WIDTH - 1):
        sum += math.fabs(col_height[i])
    return sum


def mean_height(environment):
    #durchschnittliche Hoehe der Spalten
    indi_height = individual_height(environment)
    sum = 0.0
    for i in range(FIELD_WIDTH):
        sum += indi_height[i]
    return sum / FIELD_WIDTH


def number_of_holes(environment):
    #Anzahl der Loecher
    holes = 0
    for i in range(FIELD_WIDTH):
        possible_hole = False
        for j in range(FIELD_HEIGHT):
            if possible_hole == True and environment.field.blocks[i][j] is 0:
                holes += 1
            elif environment.field.blocks[i][j] is not 0:
                possible_hole = True
    return holes


def number_of_covers(environment):
    covers = 0
    for i in range(FIELD_WIDTH):
        possible_cover = False
        for j in reversed(range(FIELD_HEIGHT)):
            if possible_cover == True and environment.field.blocks[i][
                j] is not 0:
                covers += 1
            elif environment.field.blocks[i][j] is 0:
                possible_cover = True
    return covers


def number_of_blocks(environment):
    blocks = 0
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0:
                blocks += 1
    return float(blocks)


def weighted_number_of_blocks(environment):
    blocks = 0
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0:
                blocks += (FIELD_HEIGHT - j)
    return float(blocks)


def field_to_bitvector(environment):
    bits = []
    for col in environment.field.blocks:
        for cell in col:
            if cell != 0:
                bits.append(1)
            else:
                bits.append(0)
    return BitVector(bitlist=bits).intValue()