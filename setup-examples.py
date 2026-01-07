# -*- coding: utf-8 -*-
"""
Setup Example Files for AutoGrader

This script creates:
1. assignments.xlsx - Example assignment definitions for testing
2. example_submissions/ folder - Sample student submissions
3. solutions/ folder - Solution files for comparison tests

Run this script to set up example files for testing the AutoGrader system.

Usage:
    python setup-examples.py
"""

import os
import sys

def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    try:
        import openpyxl
    except ImportError:
        missing.append('openpyxl')
    
    if missing:
        print("ERROR: Missing required packages:", ', '.join(missing))
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    return True

def create_assignments_excel():
    """Create the assignments.xlsx file with example test definitions."""
    import pandas as pd
    
    # ===== ASSIGNMENT 1: Basic Variables and Math =====
    assignment1_tests = [
        {
            'test_type': 'variable_value',
            'variable_name': 'x',
            'expected_value': 10,
            'tolerance': 0.0,
            'description': 'Variable x should equal 10',
            'pass_feedback': 'Great job setting x to 10!',
            'fail_feedback': 'Make sure x is assigned the value 10'
        },
        {
            'test_type': 'variable_value',
            'variable_name': 'y',
            'expected_value': 20,
            'tolerance': 0.0,
            'description': 'Variable y should equal 20',
        },
        {
            'test_type': 'variable_value',
            'variable_name': 'sum_xy',
            'expected_value': 30,
            'tolerance': 0.0,
            'description': 'sum_xy should equal 30',
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'message',
            'expected_value': 'str',
            'description': 'message should be a string',
        },
        {
            'test_type': 'operator_used',
            'operator': '+',
            'description': 'Should use + operator',
        }
    ]

    # ===== ASSIGNMENT 2: Loops and Control Structures =====
    assignment2_tests = [
        {
            'test_type': 'for_loop_used',
            'description': 'Should use a for loop',
            'pass_feedback': 'Good use of a for loop!',
            'fail_feedback': 'You need to use a for loop for this assignment'
        },
        {
            'test_type': 'if_statement_used',
            'description': 'Should use an if statement',
        },
        {
            'test_type': 'operator_used',
            'operator': '+=',
            'description': 'Should use += operator',
        },
        {
            'test_type': 'loop_iterations',
            'loop_variable': 'count',
            'expected_count': 100,
            'description': 'Loop should run 100 times (count variable)',
            'pass_feedback': 'Your loop correctly ran 100 times!',
            'fail_feedback': 'Your loop should iterate exactly 100 times. Check your range().'
        },
        {
            'test_type': 'variable_value',
            'variable_name': 'total',
            'expected_value': 4950,
            'tolerance': 0.0,
            'description': 'total should equal sum of 0-99',
        }
    ]

    # ===== ASSIGNMENT 3: Functions =====
    assignment3_tests = [
        {
            'test_type': 'function_exists',
            'function_name': 'calculate_average',
            'description': 'Function calculate_average should exist',
        },
        {
            'test_type': 'function_exists',
            'function_name': 'find_maximum',
            'description': 'Function find_maximum should exist',
        },
        {
            'test_type': 'function_called',
            'function_name': 'calculate_average',
            'description': 'calculate_average should be called',
        },
        {
            'test_type': 'variable_value',
            'variable_name': 'avg_result',
            'expected_value': 5.5,
            'tolerance': 0.1,
            'description': 'avg_result should be approximately 5.5',
        }
    ]

    # ===== ASSIGNMENT 4: NumPy and Data Analysis =====
    assignment4_tests = [
        {
            'test_type': 'function_called',
            'function_name': 'np.mean',
            'description': 'Should use np.mean()',
        },
        {
            'test_type': 'function_called',
            'function_name': 'np.std',
            'description': 'Should use np.std()',
        },
        {
            'test_type': 'code_contains',
            'phrase': 'import numpy',
            'case_sensitive': 'false',
            'description': 'Should import numpy',
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'data_array',
            'expected_value': 'list',
            'description': 'data_array should be a list or array',
        },
        {
            'test_type': 'variable_value',
            'variable_name': 'mean_value',
            'expected_value': 50.0,
            'tolerance': 5.0,
            'description': 'mean_value should be around 50',
        }
    ]

    # ===== ASSIGNMENT 5: Plotting with Matplotlib =====
    assignment5_tests = [
        {
            'test_type': 'function_called',
            'function_name': 'plt.plot',
            'description': 'Should use plt.plot()',
        },
        {
            'test_type': 'function_called',
            'function_name': 'plt.xlabel',
            'description': 'Should use plt.xlabel()',
        },
        {
            'test_type': 'function_called',
            'function_name': 'plt.ylabel',
            'description': 'Should use plt.ylabel()',
        },
        {
            'test_type': 'function_called',
            'function_name': 'plt.title',
            'description': 'Should use plt.title()',
        },
        {
            'test_type': 'plot_created',
            'description': 'Should create a plot',
        },
        {
            'test_type': 'plot_properties',
            'title': 'Data Visualization',
            'xlabel': 'X Values',
            'ylabel': 'Y Values',
            'has_legend': 'true',
            'has_grid': 'true',
            'description': 'Plot should have correct labels and properties',
        },
        {
            'test_type': 'plot_data_length',
            'min_length': 50,
            'description': 'Plot should have at least 50 data points',
        }
    ]

    # ===== ASSIGNMENT 6: String Formatting =====
    assignment6_tests = [
        {
            'test_type': 'code_contains',
            'phrase': '.format(',
            'case_sensitive': 'true',
            'description': 'Should use .format() for string formatting',
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'formatted_string',
            'expected_value': 'str',
            'description': 'formatted_string should be a string',
        },
        {
            'test_type': 'code_contains',
            'phrase': '{',
            'case_sensitive': 'true',
            'description': 'Should use {} placeholders',
        }
    ]

    # ===== ASSIGNMENT 7: While Loops =====
    assignment7_tests = [
        {
            'test_type': 'while_loop_used',
            'description': 'Should use a while loop',
        },
        {
            'test_type': 'operator_used',
            'operator': '<',
            'description': 'Should use < comparison operator',
        },
        {
            'test_type': 'loop_iterations',
            'loop_variable': 'iterations',
            'expected_count': 10,
            'description': 'While loop should iterate 10 times',
        },
        {
            'test_type': 'if_statement_used',
            'description': 'Should use an if statement',
        }
    ]

    # ===== ASSIGNMENT 8: Lists and Arrays =====
    assignment8_tests = [
        {
            'test_type': 'list_equals',
            'variable_name': 'my_list',
            'expected_list': '[1, 2, 3, 4, 5]',
            'order_matters': 'true',
            'tolerance': 0.0,
            'description': 'List should equal [1, 2, 3, 4, 5] with order',
        },
        {
            'test_type': 'list_equals',
            'variable_name': 'sorted_numbers',
            'expected_list': '[10, 20, 30, 40]',
            'order_matters': 'false',
            'tolerance': 0.0,
            'description': 'Should contain [10, 20, 30, 40] (order not important)',
        },
        {
            'test_type': 'array_equals',
            'variable_name': 'data_array',
            'expected_array': '[1.5, 2.5, 3.5, 4.5]',
            'tolerance': 0.01,
            'description': 'NumPy array should match expected values',
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'my_list',
            'expected_value': 'list',
            'description': 'my_list should be a list',
        }
    ]

    # ===== ASSIGNMENT 9: Solution Comparison =====
    assignment9_tests = [
        {
            'test_type': 'compare_solution',
            'solution_file': 'solutions/assignment9_solution.py',
            'variables_to_compare': 'result, sum_total, average',
            'tolerance': 0.001,
            'description': 'Compare key variables with solution file',
        },
        {
            'test_type': 'function_exists',
            'function_name': 'process_data',
            'description': 'Function process_data should exist',
        },
        {
            'test_type': 'for_loop_used',
            'description': 'Should use a for loop',
        }
    ]

    # ===== ASSIGNMENT 10: Advanced Function Testing =====
    assignment10_tests = [
        {
            'test_type': 'function_exists',
            'function_name': 'calculate_stats',
            'description': 'Function calculate_stats should exist',
        },
        {
            'test_type': 'function_not_called',
            'function_name': 'mean',
            'match_any_prefix': 'true',
            'description': 'Should NOT use mean() from any module',
            'fail_feedback': 'You must calculate the mean manually - do not use np.mean() or similar'
        },
    ]

    # ===== ASSIGNMENT 11: Variable Relationships =====
    assignment11_tests = [
        {
            'test_type': 'variable_value',
            'variable_name': 'x',
            'expected_value': '[0, 1, 2, 3, 4, 5]',
            'tolerance': 0.0,
            'description': 'x should be array of values',
        },
        {
            'test_type': 'check_relationship',
            'var1_name': 'x',
            'var2_name': 'y',
            'relationship': 'lambda x: [math.cos(math.pi * v) for v in x]',
            'tolerance': 0.001,
            'description': 'y should equal cos(pi * x)',
        },
        {
            'test_type': 'check_relationship',
            'var1_name': 'x',
            'var2_name': 'z',
            'relationship': 'lambda x: [2*v + 1 for v in x]',
            'tolerance': 0.001,
            'description': 'z should equal 2x + 1',
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'y',
            'expected_value': 'list',
            'description': 'y should be a list or array',
        }
    ]

    # ===== ASSIGNMENT 12: Advanced Plotting =====
    assignment12_tests = [
        {
            'test_type': 'plot_created',
            'description': 'Should create a plot',
        },
        {
            'test_type': 'check_multiple_lines',
            'min_lines': 2,
            'description': 'Plot should have at least 2 lines',
        },
        {
            'test_type': 'plot_properties',
            'title': 'Trigonometric Functions',
            'xlabel': 'x',
            'ylabel': 'y',
            'has_legend': 'true',
            'has_grid': 'true',
            'description': 'Plot should have proper labels and legend',
        },
        {
            'test_type': 'function_not_called',
            'function_name': 'linspace',
            'match_any_prefix': 'true',
            'description': 'Should NOT use linspace',
        }
    ]

    # ===== ASSIGNMENT 13: Array Size and Range (NEW) =====
    assignment13_tests = [
        {
            'test_type': 'array_size',
            'variable_name': 'x_values',
            'min_size': 100,
            'description': 'x_values should have at least 100 elements',
            'pass_feedback': 'Good - your array has enough elements!',
            'fail_feedback': 'Your array needs at least 100 elements'
        },
        {
            'test_type': 'array_size',
            'variable_name': 'small_sample',
            'exact_size': 10,
            'description': 'small_sample should have exactly 10 elements',
        },
        {
            'test_type': 'array_values_in_range',
            'variable_name': 'probabilities',
            'min_value': 0,
            'max_value': 1,
            'description': 'Probabilities should be between 0 and 1',
            'fail_feedback': 'Probabilities must be between 0 and 1'
        },
        {
            'test_type': 'function_not_called',
            'function_name': 'linspace',
            'match_any_prefix': 'true',
            'description': 'Should NOT use linspace (any prefix)',
        },
        {
            'test_type': 'function_called',
            'function_name': 'arange',
            'match_any_prefix': 'true',
            'description': 'Should use arange (any prefix like np.arange)',
            'fail_feedback': 'Use np.arange or similar to create your array'
        }
    ]

    # ===== ASSIGNMENT 14: Plot Styling (NEW) =====
    assignment14_tests = [
        {
            'test_type': 'plot_created',
            'description': 'Should create a plot',
        },
        {
            'test_type': 'plot_has_xlabel',
            'description': 'Plot must have an x-axis label (any text)',
            'pass_feedback': 'Good - your plot has an x-axis label!',
            'fail_feedback': 'Add an x-axis label using plt.xlabel()'
        },
        {
            'test_type': 'plot_has_ylabel',
            'description': 'Plot must have a y-axis label (any text)',
        },
        {
            'test_type': 'plot_has_title',
            'description': 'Plot must have a title (any text)',
            'fail_feedback': 'Add a title using plt.title()'
        },
        {
            'test_type': 'plot_line_style',
            'expected_style': 'b-',
            'line_index': 0,
            'description': 'First line should be solid blue (b-)',
            'fail_feedback': 'First line should be solid blue. Use plt.plot(x, y, "b-")'
        },
        {
            'test_type': 'plot_has_line_style',
            'expected_style': 'r--',
            'description': 'Plot should have a red dashed line (r--)',
        },
        {
            'test_type': 'check_exact_lines',
            'exact_lines': 3,
            'description': 'Plot must have exactly 3 data sets',
        }
    ]

    # ===== ASSIGNMENT 15: Type-Strict Comparison (NEW) =====
    assignment15_tests = [
        {
            'test_type': 'compare_solution',
            'solution_file': 'solutions/assignment15_solution.py',
            'variables_to_compare': 'result_list, result_array',
            'tolerance': 0.001,
            'require_same_type': 'true',
            'description': 'Compare with solution - types must match exactly',
            'pass_feedback': 'All variables match with correct types!',
            'fail_feedback': 'Variables must match AND be the same type (list vs numpy array)'
        },
        {
            'test_type': 'variable_type',
            'variable_name': 'result_list',
            'expected_value': 'list',
            'description': 'result_list must be a Python list',
        },
        {
            'test_type': 'array_size',
            'variable_name': 'result_array',
            'min_size': 50,
            'description': 'result_array should have at least 50 elements',
        }
    ]

    # ===== ASSIGNMENT 16: Plot Solution Comparison (NEW) =====
    assignment16_tests = [
        {
            'test_type': 'plot_created',
            'description': 'Should create a plot',
        },
        {
            'test_type': 'compare_plot_solution',
            'solution_file': 'solutions/assignment16_solution.py',
            'line_index': 0,
            'check_color': 'true',
            'check_linestyle': 'true',
            'check_linewidth': 'true',
            'description': 'Line 0 style should match solution',
            'pass_feedback': 'Your plot styling matches the solution!',
            'fail_feedback': 'Your line color, style, or width differs from the solution'
        },
        {
            'test_type': 'check_multiple_lines',
            'min_lines': 2,
            'description': 'Should have at least 2 lines',
        }
    ]

    # Create Excel file with multiple sheets
    with pd.ExcelWriter('assignments.xlsx', engine='openpyxl') as writer:
        pd.DataFrame(assignment1_tests).to_excel(writer, sheet_name='Assignment 1 - Variables', index=False)
        pd.DataFrame(assignment2_tests).to_excel(writer, sheet_name='Assignment 2 - Loops', index=False)
        pd.DataFrame(assignment3_tests).to_excel(writer, sheet_name='Assignment 3 - Functions', index=False)
        pd.DataFrame(assignment4_tests).to_excel(writer, sheet_name='Assignment 4 - NumPy', index=False)
        pd.DataFrame(assignment5_tests).to_excel(writer, sheet_name='Assignment 5 - Plotting', index=False)
        pd.DataFrame(assignment6_tests).to_excel(writer, sheet_name='Assignment 6 - Strings', index=False)
        pd.DataFrame(assignment7_tests).to_excel(writer, sheet_name='Assignment 7 - While Loops', index=False)
        pd.DataFrame(assignment8_tests).to_excel(writer, sheet_name='Assignment 8 - Lists', index=False)
        pd.DataFrame(assignment9_tests).to_excel(writer, sheet_name='Assignment 9 - Solution', index=False)
        pd.DataFrame(assignment10_tests).to_excel(writer, sheet_name='Assignment 10 - Func Test', index=False)
        pd.DataFrame(assignment11_tests).to_excel(writer, sheet_name='Assignment 11 - Relations', index=False)
        pd.DataFrame(assignment12_tests).to_excel(writer, sheet_name='Assignment 12 - Adv Plot', index=False)
        pd.DataFrame(assignment13_tests).to_excel(writer, sheet_name='Assignment 13 - Array Size', index=False)
        pd.DataFrame(assignment14_tests).to_excel(writer, sheet_name='Assignment 14 - Plot Style', index=False)
        pd.DataFrame(assignment15_tests).to_excel(writer, sheet_name='Assignment 15 - Type Match', index=False)
        pd.DataFrame(assignment16_tests).to_excel(writer, sheet_name='Assignment 16 - Plot Soln', index=False)

    print("  ✓ Created assignments.xlsx (16 assignments)")


def create_example_submissions():
    """Create example student submission files in example_submissions/ folder."""
    
    # Create folder
    folder = 'example_submissions'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Define all example submissions
    examples = {
        'assignment1_submission.py': '''# Assignment 1: Basic Variables and Math
# Student: Test Student

x = 10
y = 20
sum_xy = x + y
message = "Hello, World!"

print(f"x = {x}")
print(f"y = {y}")
print(f"sum = {sum_xy}")
print(f"message = {message}")
''',
        
        'assignment2_submission.py': '''# Assignment 2: Loops and Control Structures
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
''',
        
        'assignment3_submission.py': '''# Assignment 3: Functions
# Student: Test Student

def calculate_average(numbers):
    \'\'\'Calculate the average of a list of numbers\'\'\'
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_maximum(numbers):
    \'\'\'Find the maximum value in a list\'\'\'
    if not numbers:
        return None
    return max(numbers)

# Test the functions
test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
avg_result = calculate_average(test_data)
max_result = find_maximum(test_data)

print(f"Average: {avg_result}")
print(f"Maximum: {max_result}")
''',
        
        'assignment4_submission.py': '''# Assignment 4: NumPy and Data Analysis
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
''',
        
        'assignment5_submission.py': '''# Assignment 5: Plotting with Matplotlib
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
''',
        
        'assignment6_submission.py': '''# Assignment 6: String Formatting
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
''',
        
        'assignment7_submission.py': '''# Assignment 7: While Loops
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
''',
        
        'assignment8_submission.py': '''# Assignment 8: Lists and Arrays
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
''',
        
        'assignment9_submission.py': '''# Assignment 9: Solution Comparison
# Student: Test Student

def process_data(data):
    \'\'\'Process a list of numbers\'\'\'
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
''',
        
        'assignment10_submission.py': '''# Assignment 10: Advanced Function Testing
# Student: Test Student
# NOTE: Must calculate mean manually - cannot use np.mean!

import numpy as np

def calculate_stats(data):
    \'\'\'Calculate mean and std manually without using numpy functions\'\'\'
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
''',
        
        'assignment11_submission.py': '''# Assignment 11: Variable Relationships
# Student: Test Student

import math

# Create x values
x = [0, 1, 2, 3, 4, 5]

# Calculate y = cos(pi * x)
y = [math.cos(math.pi * val) for val in x]

# Calculate z = 2x + 1
z = [2 * val + 1 for val in x]

print(f"x = {x}")
print(f"y (cos(pi*x)) = {y}")
print(f"z (2x+1) = {z}")
''',
        
        'assignment12_submission.py': '''# Assignment 12: Advanced Plotting
# Student: Test Student

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
''',
        
        'assignment13_submission.py': '''# Assignment 13: Array Size and Range
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
''',
        
        'assignment14_submission.py': '''# Assignment 14: Plot Styling
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
''',
        
        'assignment15_submission.py': '''# Assignment 15: Type-Strict Comparison
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
''',
        
        'assignment16_submission.py': '''# Assignment 16: Plot Solution Comparison
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
''',
    }
    
    # Write example files
    count = 0
    for filename, content in examples.items():
        filepath = os.path.join(folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    
    print(f"  ✓ Created {count} example submissions in {folder}/")


def create_solution_files():
    """Create solution files in solutions/ folder."""
    
    # Create folder
    folder = 'solutions'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    solutions = {
        'assignment9_solution.py': '''# Solution for Assignment 9

def process_data(data):
    \'\'\'Process a list of numbers\'\'\'
    return sum(data) / len(data)

# Process the data
data = [10, 20, 30, 40, 50]
result = sum(data)
sum_total = result
average = process_data(data)
''',
        
        'assignment10_solution.py': '''# Solution for Assignment 10

import numpy as np

def calculate_stats(data):
    \'\'\'Calculate mean and std manually\'\'\'
    if isinstance(data, np.ndarray):
        data = data.tolist()
    
    mean = sum(data) / len(data)
    variance = sum((x - mean)**2 for x in data) / len(data)
    std = variance ** 0.5
    
    return mean, std
''',
        
        'assignment15_solution.py': '''# Solution for Assignment 15 - Type-Strict Comparison

import numpy as np

# Must be a Python list
result_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Must be a numpy array
result_array = np.arange(0, 5, 0.1)
''',
        
        'assignment16_solution.py': '''# Solution for Assignment 16 - Plot Solution Comparison

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
''',
    }
    
    # Write solution files
    count = 0
    for filename, content in solutions.items():
        filepath = os.path.join(folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    
    print(f"  ✓ Created {count} solution files in {folder}/")


def main():
    """Main entry point."""
    print("")
    print("=" * 60)
    print("  AutoGrader Example Files Setup")
    print("=" * 60)
    print("")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("Creating files...")
    print("")
    
    # Create all files
    create_assignments_excel()
    create_example_submissions()
    create_solution_files()
    
    print("")
    print("=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print("")
    print("Created:")
    print("  • assignments.xlsx          - 16 example assignments")
    print("  • example_submissions/      - 16 student submission files")
    print("  • solutions/                - 4 solution files")
    print("")
    print("Next steps:")
    print("  1. Open Assignment Editor GUI")
    print("  2. Load assignments.xlsx")
    print("  3. Select a student file from example_submissions/")
    print("  4. Click 'Test Current Assignment' to verify tests work")
    print("")


if __name__ == "__main__":
    main()
