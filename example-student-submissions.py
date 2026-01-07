# -*- coding: utf-8 -*-
"""
Example student submissions for testing the AutoGrader GUI.
Save each submission as a separate .py file to test with the application.

Includes examples for new assignments:
- Assignment 13: Array Size and Range
- Assignment 14: Plot Styling
- Assignment 15: Type-Strict Comparison
- Assignment 16: Plot Solution Comparison
"""

# ============================================================
# EXAMPLE 1: assignment1_submission.py
# For "Assignment 1 - Variables"
# ============================================================
example1 = """
# Assignment 1: Basic Variables and Math
# Student: Test Student

x = 10
y = 20
sum_xy = x + y
message = "Hello, World!"

print(f"x = {x}")
print(f"y = {y}")
print(f"sum = {sum_xy}")
print(f"message = {message}")
"""

# ============================================================
# EXAMPLE 2: assignment2_submission.py
# For "Assignment 2 - Loops"
# ============================================================
example2 = """
# Assignment 2: Loops and Control Structures
# Student: Test Student

count = 0
total = 0

for i in range(100):
    count += 1
    total += i
    
    if i == 50:
        print("Halfway there!")

print(f"Loop ran {count} times")
print(f"Total sum: {total}")
"""

# ============================================================
# EXAMPLE 3: assignment3_submission.py
# For "Assignment 3 - Functions"
# ============================================================
example3 = """
# Assignment 3: Functions
# Student: Test Student

def calculate_average(numbers):
    '''Calculate the average of a list of numbers'''
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_maximum(numbers):
    '''Find the maximum value in a list'''
    if not numbers:
        return None
    return max(numbers)

# Test the functions
test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
avg_result = calculate_average(test_data)
max_result = find_maximum(test_data)

print(f"Average: {avg_result}")
print(f"Maximum: {max_result}")
"""

# ============================================================
# EXAMPLE 4: assignment4_submission.py
# For "Assignment 4 - NumPy"
# ============================================================
example4 = """
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
"""

# ============================================================
# EXAMPLE 5: assignment5_submission.py
# For "Assignment 5 - Plotting"
# ============================================================
example5 = """
# Assignment 5: Plotting with Matplotlib
# Student: Test Student

import matplotlib.pyplot as plt
import numpy as np

# Generate data
x_data = np.linspace(0, 10, 100)
y_data = np.sin(x_data)

# Create plot
plt.plot(x_data, y_data, 'b-', label='Sine Wave')
plt.xlabel('X Values')
plt.ylabel('Y Values')
plt.title('Data Visualization')
plt.legend()
plt.grid(True)
"""

# ============================================================
# EXAMPLE 6: assignment6_submission.py
# For "Assignment 6 - Strings"
# ============================================================
example6 = """
# Assignment 6: String Formatting
# Student: Test Student

name = "Alice"
age = 25
height = 5.6

# Use .format() method
formatted_string = "Name: {}, Age: {}, Height: {} ft".format(name, age, height)

print(formatted_string)

# More formatting examples
message = "Hello, {}! You are {} years old.".format(name, age)
print(message)
"""

# ============================================================
# EXAMPLE 7: assignment7_submission.py
# For "Assignment 7 - While Loops"
# ============================================================
example7 = """
# Assignment 7: While Loops
# Student: Test Student

iterations = 0
counter = 0

while counter < 10:
    iterations += 1
    counter += 1
    
    if counter == 5:
        print("Halfway through the loop!")
    
    print(f"Iteration {iterations}: counter = {counter}")

print(f"Total iterations: {iterations}")
"""

# ============================================================
# EXAMPLE 8: assignment8_submission.py
# For "Assignment 8 - Lists"
# ============================================================
example8 = """
# Assignment 8: Lists and Arrays
# Student: Test Student

import numpy as np

# Create a list with specific order
my_list = [1, 2, 3, 4, 5]

# Create a list where order doesn't matter
sorted_numbers = [30, 10, 40, 20]  # Will be checked without order

# Create a numpy array
data_array = np.array([1.5, 2.5, 3.5, 4.5])

# Print results
print(f"my_list: {my_list}")
print(f"sorted_numbers: {sorted_numbers}")
print(f"data_array: {data_array}")
print(f"Type of my_list: {type(my_list)}")
"""

# ============================================================
# EXAMPLE 9: assignment9_submission.py
# For "Assignment 9 - Solution"
# ============================================================
example9 = """
# Assignment 9: Solution Comparison
# Student: Test Student

def process_data(data):
    '''Process a list of numbers'''
    return sum(data) / len(data)

# Process the data
data = [10, 20, 30, 40, 50]
result = sum(data)
sum_total = result
average = process_data(data)

for item in data:
    print(f"Processing: {item}")

print(f"Data: {data}")
print(f"Result (sum): {result}")
print(f"Sum total: {sum_total}")
print(f"Average: {average}")
"""

# ============================================================
# EXAMPLE 10: assignment10_submission.py
# For "Assignment 10 - Func Test"
# ============================================================
example10 = """
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
"""

# ============================================================
# EXAMPLE 11: assignment11_submission.py
# For "Assignment 11 - Relations"
# ============================================================
example11 = """
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
"""

# ============================================================
# EXAMPLE 12: assignment12_submission.py
# For "Assignment 12 - Adv Plot"
# NOTE: Must NOT use np.linspace!
# ============================================================
example12 = """
# Assignment 12: Advanced Plotting
# Student: Test Student
# NOTE: Must create x values WITHOUT using np.linspace!

import numpy as np
import matplotlib.pyplot as plt

# Create x values using range (not np.linspace)
x = [i * 0.1 for i in range(100)]  # 0 to 9.9 with 100 points

# Calculate y values for two functions
y1 = [np.cos(2 * val) for val in x]
y2 = [np.sin(2 * val) for val in x]

# Create plot with two lines
plt.plot(x, y1, 'b-', label='cos(2x)')
plt.plot(x, y2, 'r-', label='sin(2x)')

plt.xlabel('x')
plt.ylabel('y')
plt.title('Trigonometric Functions')
plt.legend()
plt.grid(True)

print(f"Created plot with {len(x)} data points per line")
"""

# ============================================================
# EXAMPLE 13: assignment13_submission.py
# For "Assignment 13 - Array Size" (NEW)
# Tests: array_size, array_values_in_range, match_any_prefix
# ============================================================
example13 = """
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
"""

# ============================================================
# EXAMPLE 14: assignment14_submission.py
# For "Assignment 14 - Plot Style" (NEW)
# Tests: plot_has_xlabel/ylabel/title, plot_line_style, 
#        plot_has_line_style, plot_line_width, plot_marker_size
# ============================================================
example14 = """
# Assignment 14: Plot Styling
# Student: Test Student
# Requirements:
#   - First line: solid blue (b-) with linewidth 2.0
#   - Second line: red dashed (r--)
#   - Third line: green stars (g*) with markersize 10

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 50)

# First line: solid blue with specific line width
plt.plot(x, np.sin(x), 'b-', linewidth=2.0, label='sin(x)')

# Second line: red dashed
plt.plot(x, np.cos(x), 'r--', label='cos(x)')

# Third line: green stars with specific marker size
plt.plot(x[::5], np.sin(x[::5]) * 0.5, 'g*', markersize=10, label='markers')

# Labels (any text is fine)
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.title('My Styled Plot')
plt.legend()
plt.grid(True)

print("Plot created with proper styling!")
"""

# ============================================================
# EXAMPLE 15: assignment15_submission.py
# For "Assignment 15 - Type Match" (NEW)
# Tests: require_same_type in compare_solution
# ============================================================
example15 = """
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
"""

# ============================================================
# EXAMPLE 16: assignment16_submission.py
# For "Assignment 16 - Plot Soln" (NEW)
# Tests: compare_plot_solution
# ============================================================
example16 = """
# Assignment 16: Plot Solution Comparison
# Student: Test Student
# Plot properties should match the solution file

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)

# Line 0 - should match solution's color, style, and width
plt.plot(x, np.sin(x), 'b-', linewidth=2.0, label='sin(x)')

# Line 1 - additional line
plt.plot(x, np.cos(x), 'r--', linewidth=1.5, label='cos(x)')

plt.xlabel('x')
plt.ylabel('y')
plt.title('Solution Comparison Plot')
plt.legend()
plt.grid(True)

print("Plot created - should match solution!")
"""

# ============================================================
# SOLUTION FILES
# ============================================================

solution9 = """
# Solution for Assignment 9

def process_data(data):
    '''Process a list of numbers'''
    return sum(data) / len(data)

# Process the data
data = [10, 20, 30, 40, 50]
result = sum(data)
sum_total = result
average = process_data(data)
"""

solution10 = """
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
"""

solution15 = """
# Solution for Assignment 15 - Type-Strict Comparison

import numpy as np

# Must be a Python list
result_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Must be a numpy array
result_array = np.arange(0, 5, 0.1)
"""

solution16 = """
# Solution for Assignment 16 - Plot Solution Comparison

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)

# Line 0 - this defines the expected style
plt.plot(x, np.sin(x), 'b-', linewidth=2.0, label='sin(x)')

# Line 1
plt.plot(x, np.cos(x), 'r--', linewidth=1.5, label='cos(x)')

plt.xlabel('x')
plt.ylabel('y')
plt.title('Solution Plot')
plt.legend()
"""

# ============================================================
# Save all examples to files
# ============================================================

if __name__ == "__main__":
    import os
    
    examples = {
        'assignment1_submission.py': example1,
        'assignment2_submission.py': example2,
        'assignment3_submission.py': example3,
        'assignment4_submission.py': example4,
        'assignment5_submission.py': example5,
        'assignment6_submission.py': example6,
        'assignment7_submission.py': example7,
        'assignment8_submission.py': example8,
        'assignment9_submission.py': example9,
        'assignment10_submission.py': example10,
        'assignment11_submission.py': example11,
        'assignment12_submission.py': example12,
        'assignment13_submission.py': example13,
        'assignment14_submission.py': example14,
        'assignment15_submission.py': example15,
        'assignment16_submission.py': example16,
    }
    
    solutions = {
        'assignment9_solution.py': solution9,
        'assignment10_solution.py': solution10,
        'assignment15_solution.py': solution15,
        'assignment16_solution.py': solution16,
    }
    
    # Create solutions folder if it doesn't exist
    if not os.path.exists('solutions'):
        os.makedirs('solutions')
        print("Created solutions/ folder")
    
    # Create example submissions
    for filename, content in examples.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created {filename}")
    
    # Create solution files
    for filename, content in solutions.items():
        filepath = os.path.join('solutions', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created solutions/{filename}")
    
    print("\n" + "="*60)
    print("Example student submissions created successfully!")
    print("="*60)
    print("\nSubmission files created:")
    for i, filename in enumerate(examples.keys(), 1):
        print(f"  {i:2}. {filename}")
    
    print("\nSolution files created:")
    for filename in solutions.keys():
        print(f"      solutions/{filename}")
    
    print("\n" + "="*60)
    print("NEW ASSIGNMENTS (13-16) demonstrate these features:")
    print("="*60)
    print("  Assignment 13 - Array Size/Range:")
    print("    - array_size (min_size, exact_size)")
    print("    - array_values_in_range (min_value, max_value)")
    print("    - match_any_prefix for function_called/not_called")
    print("")
    print("  Assignment 14 - Plot Styling:")
    print("    - plot_has_xlabel, plot_has_ylabel, plot_has_title")
    print("    - plot_line_style ('b-', 'r--', 'g*', etc.)")
    print("    - plot_has_line_style (check if ANY line has style)")
    print("    - plot_line_width, plot_marker_size")
    print("")
    print("  Assignment 15 - Type-Strict Comparison:")
    print("    - compare_solution with require_same_type=true")
    print("    - list and numpy array must match exactly")
    print("")
    print("  Assignment 16 - Plot Solution Comparison:")
    print("    - compare_plot_solution (compare line properties)")
    print("    - check_color, check_linestyle, check_linewidth")