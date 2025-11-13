# Assignment 4: NumPy and Data Analysis
# Student: Test Student

import numpy as np

# Create data array
data_array = list(range(1, 101))

# Calculate statistics using NumPy
mean_value = np.mean(data_array)
std_value = np.std(data_array)
median_value = np.median(data_array)

print(f"Mean: {mean_value}")
print(f"Standard Deviation: {std_value}")
print(f"Median: {median_value}")