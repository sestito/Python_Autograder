# Assignment 13: Array Size and Range
# Student: Test Student
# NOTE: Must use np.arange, NOT np.linspace!

import numpy as np

# Create x_values with at least 100 elements using arange (not linspace!)
x_values = np.arange(0, 10, 0.1)  # Creates 100 values from 0 to 9.9

# Create small_sample with exactly 10 elements
small_sample = np.arange(0, 10, 1)  # Creates exactly 10 values: 0-9

# Create probabilities between 0 and 1
probabilities = np.arange(0, 1.01, 0.1)  # Values from 0 to 1

print(f"x_values has {len(x_values)} elements")
print(f"x_values range: {x_values.min()} to {x_values.max()}")
print(f"small_sample has {len(small_sample)} elements")
print(f"probabilities range: {probabilities.min()} to {probabilities.max()}")