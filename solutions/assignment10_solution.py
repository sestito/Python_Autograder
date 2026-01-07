# Solution for Assignment 10

import numpy as np

def calculate_stats(data):
    '''Calculate mean and std manually'''
    if isinstance(data, np.ndarray):
        data = data.tolist()
    
    mean = sum(data) / len(data)
    variance = sum((x - mean)**2 for x in data) / len(data)
    std = variance ** 0.5
    
    return mean, std