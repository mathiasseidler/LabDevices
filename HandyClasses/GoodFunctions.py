'''
Created on 10.05.2012

@author: Mathias
'''

def append_left_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((matrix,filling))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((row,filling))
    matrix=vstack((matrix,row))
    return matrix

def append_right_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((filling,matrix))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((filling,row))
    matrix=vstack((matrix,row))
    return matrix