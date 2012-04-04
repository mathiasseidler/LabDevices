'''
Created on Apr 2, 2012

@author: Administrator
'''
import numpy as np

tmp=np.array([2,2,4])

list = [];
list.append([1,23])
list.append('text')
list.append([1,4,55])
list.append(tmp)
print list[:]
list.pop()
print list