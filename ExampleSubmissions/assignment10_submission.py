# Assignment 10: Advanced Function Testing
# Student: Test Student
# NOTE: Must calculate mean manually - cannot use np.mean!

import numpy as np

def calculate_stats(data):
    '''Calculate mean and std manually without using numpy functions'''
    # Convert to list if numpy array
    if isinstance(data, np.ndarray):
        data = data.tolist()
    
    # Calculate mean manually
    total = 0
    for val in data:
        total += val
    mean = total / len(data)
    
    # Calculate standard deviation manually
    variance_sum = 0
    for val in data:
        variance_sum += (val - mean)**2
    variance = variance_sum / len(data)
    std = variance ** 0.5
    
    return mean, std

# Test with different input types
result1 = calculate_stats([1, 2, 3, 4, 5])
result2 = calculate_stats([10, 20, 30])
result3 = calculate_stats(np.array([5, 10, 15]))

print(f"Result 1: {result1}")
print(f"Result 2: {result2}")
print(f"Result 3: {result3}")