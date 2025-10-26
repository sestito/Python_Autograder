"""
Script to create an example assignments.xlsx file with sample assignments and tests.
Run this script once to generate the Excel file.
"""

import pandas as pd

# ===== ASSIGNMENT 1: Basic Variables and Math =====
assignment1_tests = [
    {
        'test_type': 'variable_value',
        'variable_name': 'x',
        'expected_value': 10,
        'tolerance': 0.0,
        'description': 'Variable x should equal 10'
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'y',
        'expected_value': 20,
        'tolerance': 0.0,
        'description': 'Variable y should equal 20'
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'sum_xy',
        'expected_value': 30,
        'tolerance': 0.0,
        'description': 'sum_xy should equal 30'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'message',
        'expected_value': 'str',
        'description': 'message should be a string'
    },
    {
        'test_type': 'operator_used',
        'operator': '+',
        'description': 'Should use + operator'
    }
]

# ===== ASSIGNMENT 2: Loops and Control Structures =====
assignment2_tests = [
    {
        'test_type': 'for_loop_used',
        'description': 'Should use a for loop'
    },
    {
        'test_type': 'if_statement_used',
        'description': 'Should use an if statement'
    },
    {
        'test_type': 'operator_used',
        'operator': '+=',
        'description': 'Should use += operator'
    },
    {
        'test_type': 'loop_iterations',
        'loop_variable': 'count',
        'expected_count': 100,
        'description': 'Loop should run 100 times (count variable)'
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'total',
        'expected_value': 4950,
        'tolerance': 0.0,
        'description': 'total should equal sum of 0-99'
    }
]

# ===== ASSIGNMENT 3: Functions =====
assignment3_tests = [
    {
        'test_type': 'function_exists',
        'function_name': 'calculate_average',
        'description': 'Function calculate_average should exist'
    },
    {
        'test_type': 'function_exists',
        'function_name': 'find_maximum',
        'description': 'Function find_maximum should exist'
    },
    {
        'test_type': 'function_called',
        'function_name': 'calculate_average',
        'description': 'calculate_average should be called'
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'avg_result',
        'expected_value': 5.5,
        'tolerance': 0.1,
        'description': 'avg_result should be approximately 5.5'
    }
]

# ===== ASSIGNMENT 4: NumPy and Data Analysis =====
assignment4_tests = [
    {
        'test_type': 'function_called',
        'function_name': 'np.mean',
        'description': 'Should use np.mean()'
    },
    {
        'test_type': 'function_called',
        'function_name': 'np.std',
        'description': 'Should use np.std()'
    },
    {
        'test_type': 'code_contains',
        'phrase': 'import numpy',
        'case_sensitive': 'false',
        'description': 'Should import numpy'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'data_array',
        'expected_value': 'list',
        'description': 'data_array should be a list or array'
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'mean_value',
        'expected_value': 50.0,
        'tolerance': 5.0,
        'description': 'mean_value should be around 50'
    }
]

# ===== ASSIGNMENT 5: Plotting with Matplotlib =====
assignment5_tests = [
    {
        'test_type': 'function_called',
        'function_name': 'plt.plot',
        'description': 'Should use plt.plot()'
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.xlabel',
        'description': 'Should use plt.xlabel()'
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.ylabel',
        'description': 'Should use plt.ylabel()'
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.title',
        'description': 'Should use plt.title()'
    },
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot'
    },
    {
        'test_type': 'plot_properties',
        'title': 'Data Visualization',
        'xlabel': 'X Values',
        'ylabel': 'Y Values',
        'has_legend': 'true',
        'has_grid': 'true',
        'description': 'Plot should have correct labels and properties'
    },
    {
        'test_type': 'plot_data_length',
        'min_length': 50,
        'description': 'Plot should have at least 50 data points'
    }
]

# ===== ASSIGNMENT 6: String Formatting =====
assignment6_tests = [
    {
        'test_type': 'code_contains',
        'phrase': '.format(',
        'case_sensitive': 'true',
        'description': 'Should use .format() for string formatting'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'formatted_string',
        'expected_value': 'str',
        'description': 'formatted_string should be a string'
    },
    {
        'test_type': 'code_contains',
        'phrase': '{',
        'case_sensitive': 'true',
        'description': 'Should use {} placeholders'
    }
]

# ===== ASSIGNMENT 7: While Loops =====
assignment7_tests = [
    {
        'test_type': 'while_loop_used',
        'description': 'Should use a while loop'
    },
    {
        'test_type': 'operator_used',
        'operator': '<',
        'description': 'Should use < comparison operator'
    },
    {
        'test_type': 'loop_iterations',
        'loop_variable': 'iterations',
        'expected_count': 10,
        'description': 'While loop should iterate 10 times'
    },
    {
        'test_type': 'if_statement_used',
        'description': 'Should use an if statement'
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

print("✓ assignments.xlsx created successfully!")
print("\nCreated assignments:")
print("  - Assignment 1 - Variables")
print("  - Assignment 2 - Loops")
print("  - Assignment 3 - Functions")
print("  - Assignment 4 - NumPy")
print("  - Assignment 5 - Plotting")
print("  - Assignment 6 - Strings")
print("  - Assignment 7 - While Loops")
print("\nYou can now use this file with the AutoGrader GUI application.")
print("\nTo add more assignments:")
print("  1. Open assignments.xlsx in Excel")
print("  2. Add a new sheet (tab) with the assignment name")
print("  3. Add test rows with the appropriate test_type and parameters")
print("\nSupported test types:")
print("  - variable_value: Check variable value")
print("  - variable_type: Check variable type")
print("  - function_exists: Check if function is defined")
print("  - function_called: Check if function is called")
print("  - for_loop_used: Check for 'for' loop")
print("  - while_loop_used: Check for 'while' loop")
print("  - if_statement_used: Check for 'if' statement")
print("  - operator_used: Check if operator is used")
print("  - code_contains: Check if code contains phrase")
print("  - plot_created: Check if plot was created")
print("  - plot_properties: Check plot title, labels, legend, grid")
print("  - plot_data_length: Check number of data points in plot")
print("  - loop_iterations: Check loop iteration count")