'''
Created on 10.05.2012

@author: Mathias
'''
import numpy as np
def append_left_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = np.zeros((matrix.shape[0],diff))
        matrix=np.hstack((matrix,filling))
    elif diff > 0:
        filling = np.zeros(diff)
        row = np.hstack((row,filling))
    matrix = np.vstack((matrix,row))
    return matrix

def append_right_oriented(matrix, row):
    diff = matrix.shape[1] - row.size
    if diff < 0:
        diff = -diff
        filling = np.zeros((matrix.shape[0],diff))
        matrix= np.hstack((filling,matrix))
    elif diff > 0:
        filling = np.zeros(diff)
        row = np.hstack((filling,row))
    matrix = np.vstack((matrix,row))
    return matrix

def listdir_nohidden(path):
    import os
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f
    
