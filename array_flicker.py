'''
Created on 03.04.2012

@author: Mathias
'''

from numpy import *

a= array([[1,2,3],[1,1,1]])
row1=array([4,4,4,4])
row2=array([5])
row3=array([6,6,6,6,6])


def append_left_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    print diff
    if diff < 0:
        diff = -diff
        filling = zeros((matrix.shape[0],diff))
        matrix=hstack((matrix,filling))
    elif diff > 0:
        filling = zeros(diff)
        row = hstack((row,filling))
    matrix=vstack((row,matrix))
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
    matrix=vstack((row,matrix))
    return matrix

a=append_right_oriented(a,row1)
print a
a=append_right_oriented(a,row2)
print a
a=append_right_oriented(a,row3)
print a