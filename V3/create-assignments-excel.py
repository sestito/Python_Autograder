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

# ===== ASSIGNMENT 8: Lists and Arrays =====
assignment8_tests = [
    {
        'test_type': 'list_equals',
        'variable_name': 'my_list',
        'expected_list': '[1, 2, 3, 4, 5]',
        'order_matters': 'true',
        'tolerance': 0.0,
        'description': 'List should equal [1, 2, 3, 4, 5] with order'
    },
    {
        'test_type': 'list_equals',
        'variable_name': 'sorted_numbers',
        'expected_list': '[10, 20, 30, 40]',
        'order_matters': 'false',
        'tolerance': 0.0,
        'description': 'Should contain [10, 20, 30, 40] (order not important)'
    },
    {
        'test_type': 'array_equals',
        'variable_name': 'data_array',
        'expected_array': '[1.5, 2.5, 3.5, 4.5]',
        'tolerance': 0.01,
        'description': 'NumPy array should match expected values'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'my_list',
        'expected_value': 'list',
        'description': 'my_list should be a list'
    }
]

# ===== ASSIGNMENT 9: Solution Comparison =====
assignment9_tests = [
    {
        'test_type': 'compare_solution',
        'solution_file': 'solutions/assignment9_solution.py',
        'variables_to_compare': 'result, sum_total, average',
        'tolerance': 0.001,
        'description': 'Compare key variables with solution file'
    },
    {
        'test_type': 'function_exists',
        'function_name': 'process_data',
        'description': 'Function process_data should exist'
    },
    {
        'test_type': 'for_loop_used',
        'description': 'Should use a for loop'
    }
]

# ===== ASSIGNMENT 10: Advanced Function Testing =====
assignment10_tests = [
    {
        'test_type': 'function_exists',
        'function_name': 'calculate_stats',
        'description': 'Function calculate_stats should exist'
    },
    {
        'test_type': 'test_function_solution',
        'function_name': 'calculate_stats',
        'solution_file': 'solutions/assignment10_solution.py',
        'test_inputs': "[{'args': [[1, 2, 3, 4, 5]]}, {'args': [[10, 20, 30]]}, {'args': [np.array([5, 10, 15])]}]",
        'tolerance': 0.01,
        'description': 'Test function with lists and arrays against solution'
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'np.mean',
        'description': 'Should NOT use np.mean - must calculate manually'
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'numpy.mean',
        'description': 'Should NOT use numpy.mean'
    }
]

# ===== ASSIGNMENT 11: Variable Relationships =====
assignment11_tests = [
    {
        'test_type': 'variable_value',
        'variable_name': 'x',
        'expected_value': '[0, 1, 2, 3, 4, 5]',
        'tolerance': 0.0,
        'description': 'x should be array of values'
    },
    {
        'test_type': 'check_relationship',
        'var1_name': 'x',
        'var2_name': 'y',
        'relationship': 'lambda x: np.cos(np.pi * x)',
        'tolerance': 0.001,
        'description': 'y should equal cos(π * x)'
    },
    {
        'test_type': 'check_relationship',
        'var1_name': 'x',
        'var2_name': 'z',
        'relationship': 'lambda x: 2*x + 1',
        'tolerance': 0.001,
        'description': 'z should equal 2x + 1'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'y',
        'expected_value': 'list',
        'description': 'y should be a list or array'
    }
]

# ===== ASSIGNMENT 12: Advanced Plotting =====
assignment12_tests = [
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot'
    },
    {
        'test_type': 'check_multiple_lines',
        'min_lines': 2,
        'description': 'Plot should have at least 2 lines'
    },
    {
        'test_type': 'check_function_any_line',
        'function': 'lambda x: np.cos(2*x)',
        'min_length': 50,
        'tolerance': 0.01,
        'description': 'One line should be cos(2x) with at least 50 points'
    },
    {
        'test_type': 'plot_properties',
        'title': 'Trigonometric Functions',
        'xlabel': 'x',
        'ylabel': 'y',
        'has_legend': 'true',
        'has_grid': 'true',
        'description': 'Plot should have proper labels and legend'
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'np.linspace',
        'description': 'Should NOT use np.linspace'
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'numpy.linspace',
        'description': 'Should NOT use numpy.linspace'
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

print("✓ assignments.xlsx created successfully!")
print("\nCreated assignments:")
print("  - Assignment 1 - Variables")
print("  - Assignment 2 - Loops")
print("  - Assignment 3 - Functions")
print("  - Assignment 4 - NumPy")
print("  - Assignment 5 - Plotting")
print("  - Assignment 6 - Strings")
print("  - Assignment 7 - While Loops")
print("  - Assignment 8 - Lists")
print("  - Assignment 9 - Solution")
print("\nYou can now use this file with the AutoGrader GUI application.")