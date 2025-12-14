# Assignment 15: Type-Strict Comparison
# Student: Test Student
# IMPORTANT: result_list must be a Python list
#            result_array must be a numpy array

import numpy as np

# This MUST be a Python list (not numpy array)
result_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# This MUST be a numpy array (not list)
result_array = np.arange(0, 5, 0.1)  # Creates 50 elements

print(f"result_list type: {type(result_list)}")
print(f"result_array type: {type(result_array)}")
print(f"result_array size: {len(result_array)}")