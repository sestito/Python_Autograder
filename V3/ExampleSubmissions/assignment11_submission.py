# Assignment 11: Variable Relationships
# Student: Test Student

import numpy as np

# Create x values
x = [0, 1, 2, 3, 4, 5]

# Calculate y = cos(pi * x)
y = [np.cos(np.pi * val) for val in x]

# Calculate z = 2x + 1
z = [2 * val + 1 for val in x]

print(f"x = {x}")
print(f"y (cos(pi*x)) = {y}")
print(f"z (2x+1) = {z}")