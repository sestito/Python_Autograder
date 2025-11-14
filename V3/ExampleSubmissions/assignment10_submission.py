# Assignment 10: Advanced Function Testing
# Student: Test Student

import numpy as np

def calculate_stats(data):
    '''Calculate mean and std manually without using numpy functions'''
    # Convert to list if numpy array
    if isinstance(data, np.ndarray):
        data = data.tolist()
    
    # Calculate mean manually
    mean = sum(data) / len(data)
    
    # Calculate standard deviation manually
    variance = sum((x - mean)**2 for x in data) / len(data)
    std = variance ** 0.5
    
    return mean, std

# Test with different input types
result1 = calculate_stats([1, 2, 3, 4, 5])
result2 = calculate_stats([10, 20, 30])
result3 = calculate_stats(np.array([5, 10, 15]))

print(f"Result 1: {result1}")
print(f"Result 2: {result2}")
print(f"Result 3: {result3}")