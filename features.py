import math
from environment import FIELD_HEIGHT, FIELD_WIDTH, Environment

environment = Environment()


def max_height(self):
    max_height = 0
    count_i = 0
    count_j = 0
    for i in self.state.blocks:
        for j in self.state.blocks[count_i]:
            if self.state.blocks[count_i][count_j] is not 0 and (
                FIELD_HEIGHT - count_j) > max_height:
                max_height = FIELD_HEIGHT - count_j
                break
            elif self.state.blocks[count_i][count_j] is not 0:
                break
            count_j += 1
        count_i += 1
    return max_height
    #the lowest column
    #return value is the height not the row


def min_height(self):
    min_height = FIELD_HEIGHT
    count_i = 0
    count_j = 0
    for i in self.state.blocks:
        for j in self.state.blocks[count_i]:
            if self.state.blocks[count_i][count_j] is not 0 and (
                FIELD_HEIGHT - count_j) < min_height:
                min_height = FIELD_HEIGHT - count_j
                break
            elif self.state.blocks[count_i][count_j] is not 0:
                break
            count_j += 1
        count_i += 1
    return min_height
    #the height of every column     


def individual_height(self):
    stack = []
    count_i = 0
    count_j = 0
    for i in self.state.blocks:
        for j in self.state.blocks[count_i]:
            if self.state.blocks[count_i][count_j] is not 0:
                stack.append(FIELD_HEIGHT - count_j)
                break
            count_j += 1
        count_i += 1
    return stack
    #Hoehenunterschiede zwischen den Spalten


def column_height_differences(self, individual_height):
    stack = []
    for i in range(FIELD_WIDTH - 1):
        stack.append(individual_height[i + 1] - individual_height[i])
    return stack

    #Summe der Hoehenunterschiede zwischen den Spalten


def sum_of_column_height_differences(self, column_height_differences):
    sum = 0
    for i in range(FIELD_WIDTH - 1):
        sum += math.fabs(column_height_differences[i])
    return sum

    #durchschnittliche Hoehe der Spalten    


def mean_height(self, individual_height):
    sum = 0
    for i in range(FIELD_WIDTH):
        sum += individual_height[i]
    return sum / FIELD_WIDTH

    #Anzahl der Loecher


def number_of_holes(environment):
    holes = 0
    for i in environment.blocks:
        possible_hole = False
        for j in environment.blocks[i]:
            if possible_hole == True and environment.blocks[i][j] is 0:
                holes += 1
            elif environment.blocks[i][j] is not 0:
                possible_hole = True
    return holes