import math
from BitVector import BitVector
from settings import FIELD_HEIGHT, FIELD_WIDTH
from environment import Environment

env = Environment()


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
    return max_height

#the lowest column
#return value is the height not the row
def min_height(environment):
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


#the height of every column     
def individual_height(environment):
    stack = []
    for i in range(FIELD_WIDTH):
        for j in range(FIELD_HEIGHT):
            if environment.field.blocks[i][j] is not 0:
                stack.append(FIELD_HEIGHT - j)
                break
            elif j == 11:
                stack.append(0)

    return stack

#Hoehenunterschiede zwischen den Spalten
def column_height_differences(environment):
    ind_height = individual_height(environment)
    stack = []
    for i in range(FIELD_WIDTH - 1):
        stack.append(ind_height[i + 1] - ind_height[i])
    return stack

#Summe der Hoehenunterschiede zwischen den Spalten
def sum_of_column_height_differences(environment, column_height_differences):
    sum = 0
    for i in range(FIELD_WIDTH - 1):
        sum += math.fabs(column_height_differences[i])
    return sum

#durchschnittliche Hoehe der Spalten    
def mean_height(environment, individual_height):
    sum = 0.0
    for i in range(FIELD_WIDTH):
        sum += individual_height[i]
    return sum / FIELD_WIDTH

#Anzahl der Loecher
def number_of_holes(environment):
    holes = 0
    for i in range(FIELD_WIDTH):
        possible_hole = False
    for j in range(FIELD_HEIGHT):
        if possible_hole == True and environment.field.blocks[i][j] is 0:
            holes += 1
        elif environment.field.blocks[i][j] is not 0:
            possible_hole = True
    return holes


def field_to_bitvector(environment):
    bits = []
    for col in environment.field.blocks:
        for cell in col:
            if cell != 0:
                bits.append(1)
            else:
                bits.append(0)
    return BitVector(bitlist=bits).intValue()