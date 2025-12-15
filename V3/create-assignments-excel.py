# -*- coding: utf-8 -*-
"""
Script to create an example assignments.xlsx file with sample assignments and tests.
Run this script once to generate the Excel file.

Includes examples for all test types including new features:
- array_size: Check array/list size
- array_values_in_range: Check values are within bounds
- match_any_prefix: Catch function calls with any prefix
- plot_has_xlabel/ylabel/title: Check for any label (not specific text)
- plot_line_style, plot_has_line_style: Check line styles like 'b-', 'r--', 'g*'
- plot_line_width, plot_marker_size: Check line/marker sizes
- compare_plot_solution: Compare plot properties with solution
- require_same_type: Require list vs numpy array match in comparisons
"""

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
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'sum_xy',
        'expected_value': 30,
        'tolerance': 0.0,
        'description': 'sum_xy should equal 30',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'message',
        'expected_value': 'str',
        'description': 'message should be a string',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'operator_used',
        'operator': '+',
        'description': 'Should use + operator',
        'pass_feedback': '',
        'fail_feedback': ''
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
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'operator_used',
        'operator': '+=',
        'description': 'Should use += operator',
        'pass_feedback': '',
        'fail_feedback': ''
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
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 3: Functions =====
assignment3_tests = [
    {
        'test_type': 'function_exists',
        'function_name': 'calculate_average',
        'description': 'Function calculate_average should exist',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_exists',
        'function_name': 'find_maximum',
        'description': 'Function find_maximum should exist',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'calculate_average',
        'description': 'calculate_average should be called',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'avg_result',
        'expected_value': 5.5,
        'tolerance': 0.1,
        'description': 'avg_result should be approximately 5.5',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 4: NumPy and Data Analysis =====
assignment4_tests = [
    {
        'test_type': 'function_called',
        'function_name': 'np.mean',
        'description': 'Should use np.mean()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'np.std',
        'description': 'Should use np.std()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'code_contains',
        'phrase': 'import numpy',
        'case_sensitive': 'false',
        'description': 'Should import numpy',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'data_array',
        'expected_value': 'list',
        'description': 'data_array should be a list or array',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_value',
        'variable_name': 'mean_value',
        'expected_value': 50.0,
        'tolerance': 5.0,
        'description': 'mean_value should be around 50',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 5: Plotting with Matplotlib =====
assignment5_tests = [
    {
        'test_type': 'function_called',
        'function_name': 'plt.plot',
        'description': 'Should use plt.plot()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.xlabel',
        'description': 'Should use plt.xlabel()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.ylabel',
        'description': 'Should use plt.ylabel()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'plt.title',
        'description': 'Should use plt.title()',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'plot_properties',
        'title': 'Data Visualization',
        'xlabel': 'X Values',
        'ylabel': 'Y Values',
        'has_legend': 'true',
        'has_grid': 'true',
        'description': 'Plot should have correct labels and properties',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'plot_data_length',
        'min_length': 50,
        'description': 'Plot should have at least 50 data points',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 6: String Formatting =====
assignment6_tests = [
    {
        'test_type': 'code_contains',
        'phrase': '.format(',
        'case_sensitive': 'true',
        'description': 'Should use .format() for string formatting',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'formatted_string',
        'expected_value': 'str',
        'description': 'formatted_string should be a string',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'code_contains',
        'phrase': '{',
        'case_sensitive': 'true',
        'description': 'Should use {} placeholders',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 7: While Loops =====
assignment7_tests = [
    {
        'test_type': 'while_loop_used',
        'description': 'Should use a while loop',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'operator_used',
        'operator': '<',
        'description': 'Should use < comparison operator',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'loop_iterations',
        'loop_variable': 'iterations',
        'expected_count': 10,
        'description': 'While loop should iterate 10 times',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'if_statement_used',
        'description': 'Should use an if statement',
        'pass_feedback': '',
        'fail_feedback': ''
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
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'list_equals',
        'variable_name': 'sorted_numbers',
        'expected_list': '[10, 20, 30, 40]',
        'order_matters': 'false',
        'tolerance': 0.0,
        'description': 'Should contain [10, 20, 30, 40] (order not important)',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'array_equals',
        'variable_name': 'data_array',
        'expected_array': '[1.5, 2.5, 3.5, 4.5]',
        'tolerance': 0.01,
        'description': 'NumPy array should match expected values',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'my_list',
        'expected_value': 'list',
        'description': 'my_list should be a list',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 9: Solution Comparison =====
assignment9_tests = [
    {
        'test_type': 'compare_solution',
        'solution_file': 'solutions/assignment9_solution.py',
        'variables_to_compare': 'result, sum_total, average',
        'tolerance': 0.001,
        'require_same_type': 'false',
        'description': 'Compare key variables with solution file',
        'pass_feedback': 'Your solution matches the expected output!',
        'fail_feedback': 'Your variable values differ from the expected solution'
    },
    {
        'test_type': 'function_exists',
        'function_name': 'process_data',
        'description': 'Function process_data should exist',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'for_loop_used',
        'description': 'Should use a for loop',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 10: Advanced Function Testing =====
assignment10_tests = [
    {
        'test_type': 'function_exists',
        'function_name': 'calculate_stats',
        'description': 'Function calculate_stats should exist',
        'pass_feedback': '',
        'fail_feedback': 'Define a function named calculate_stats'
    },
    {
        'test_type': 'test_function_solution',
        'function_name': 'calculate_stats',
        'solution_file': 'solutions/assignment10_solution.py',
        'test_inputs': "[{'args': [[1, 2, 3, 4, 5]]}, {'args': [[10, 20, 30]]}, {'args': [np.array([5, 10, 15])]}]",
        'tolerance': 0.01,
        'description': 'Test function with lists and arrays against solution',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'mean',
        'match_any_prefix': 'true',
        'description': 'Should NOT use mean() with any prefix (np.mean, numpy.mean, etc.)',
        'pass_feedback': 'Good - you calculated the mean manually!',
        'fail_feedback': 'Do not use np.mean or any mean() function - calculate it manually'
    }
]

# ===== ASSIGNMENT 11: Variable Relationships =====
assignment11_tests = [
    {
        'test_type': 'variable_value',
        'variable_name': 'x',
        'expected_value': '[0, 1, 2, 3, 4, 5]',
        'tolerance': 0.0,
        'description': 'x should be array of values',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'check_relationship',
        'var1_name': 'x',
        'var2_name': 'y',
        'relationship': 'lambda x: np.cos(np.pi * x)',
        'tolerance': 0.001,
        'description': 'y should equal cos(pi * x)',
        'pass_feedback': '',
        'fail_feedback': 'y should be calculated as cos(pi * x) for each value in x'
    },
    {
        'test_type': 'check_relationship',
        'var1_name': 'x',
        'var2_name': 'z',
        'relationship': 'lambda x: 2*x + 1',
        'tolerance': 0.001,
        'description': 'z should equal 2x + 1',
        'pass_feedback': '',
        'fail_feedback': 'z should be calculated as 2*x + 1 for each value in x'
    },
    {
        'test_type': 'variable_type',
        'variable_name': 'y',
        'expected_value': 'list',
        'description': 'y should be a list or array',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 12: Advanced Plotting =====
assignment12_tests = [
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'check_multiple_lines',
        'min_lines': 2,
        'description': 'Plot should have at least 2 lines',
        'pass_feedback': '',
        'fail_feedback': 'Your plot should have at least 2 different lines'
    },
    {
        'test_type': 'check_function_any_line',
        'function': 'lambda x: np.cos(2*x)',
        'min_length': 50,
        'tolerance': 0.01,
        'description': 'One line should be cos(2x) with at least 50 points',
        'pass_feedback': '',
        'fail_feedback': 'One of your lines should plot cos(2x) with at least 50 points'
    },
    {
        'test_type': 'plot_properties',
        'title': 'Trigonometric Functions',
        'xlabel': 'x',
        'ylabel': 'y',
        'has_legend': 'true',
        'has_grid': 'true',
        'description': 'Plot should have proper labels and legend',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'linspace',
        'match_any_prefix': 'true',
        'description': 'Should NOT use linspace with any prefix',
        'pass_feedback': 'Good - you created x values without linspace!',
        'fail_feedback': 'Do not use np.linspace or any linspace() - create x values another way'
    }
]

# ===== ASSIGNMENT 13: Array Size and Range (NEW) =====
assignment13_tests = [
    {
        'test_type': 'array_size',
        'variable_name': 'x_values',
        'min_size': 100,
        'description': 'x_values should have at least 100 elements',
        'pass_feedback': 'Good - your array has enough data points!',
        'fail_feedback': 'Your x_values array needs at least 100 elements'
    },
    {
        'test_type': 'array_size',
        'variable_name': 'small_sample',
        'exact_size': 10,
        'description': 'small_sample should have exactly 10 elements',
        'pass_feedback': '',
        'fail_feedback': 'small_sample must have exactly 10 elements'
    },
    {
        'test_type': 'array_values_in_range',
        'variable_name': 'x_values',
        'min_value': 0,
        'max_value': 10,
        'description': 'All x_values should be between 0 and 10',
        'pass_feedback': 'All values are within the expected range!',
        'fail_feedback': 'Some values in x_values are outside the range [0, 10]'
    },
    {
        'test_type': 'array_values_in_range',
        'variable_name': 'probabilities',
        'min_value': 0,
        'max_value': 1,
        'description': 'Probabilities should be between 0 and 1',
        'pass_feedback': '',
        'fail_feedback': 'Probabilities must be between 0 and 1'
    },
    {
        'test_type': 'function_not_called',
        'function_name': 'linspace',
        'match_any_prefix': 'true',
        'description': 'Should NOT use linspace (any prefix)',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'function_called',
        'function_name': 'arange',
        'match_any_prefix': 'true',
        'description': 'Should use arange (any prefix like np.arange)',
        'pass_feedback': '',
        'fail_feedback': 'Use np.arange or similar to create your array'
    }
]

# ===== ASSIGNMENT 14: Plot Styling (NEW) =====
assignment14_tests = [
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot',
        'pass_feedback': '',
        'fail_feedback': ''
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
        'pass_feedback': 'Good - your plot has a y-axis label!',
        'fail_feedback': 'Add a y-axis label using plt.ylabel()'
    },
    {
        'test_type': 'plot_has_title',
        'description': 'Plot must have a title (any text)',
        'pass_feedback': '',
        'fail_feedback': 'Add a title using plt.title()'
    },
    {
        'test_type': 'plot_line_style',
        'expected_style': 'b-',
        'line_index': 0,
        'description': 'First line should be solid blue (b-)',
        'pass_feedback': 'Correct - first line is solid blue!',
        'fail_feedback': 'First line should be solid blue. Use plt.plot(x, y, "b-")'
    },
    {
        'test_type': 'plot_has_line_style',
        'expected_style': 'r--',
        'description': 'Plot should have a red dashed line (r--)',
        'pass_feedback': '',
        'fail_feedback': 'Add a red dashed line using "r--" style'
    },
    {
        'test_type': 'plot_has_line_style',
        'expected_style': 'g*',
        'description': 'Plot should have green star markers (g*)',
        'pass_feedback': '',
        'fail_feedback': 'Add a line with green star markers using "g*" style'
    },
    {
        'test_type': 'plot_line_width',
        'expected_width': 2.0,
        'line_index': 0,
        'tolerance': 0.1,
        'description': 'First line should have width 2.0',
        'pass_feedback': '',
        'fail_feedback': 'Set the first line width to 2.0 using linewidth=2.0'
    },
    {
        'test_type': 'plot_marker_size',
        'expected_size': 10,
        'line_index': 2,
        'tolerance': 1.0,
        'description': 'Third line markers should be size 10',
        'pass_feedback': '',
        'fail_feedback': 'Set marker size to 10 using markersize=10'
    },
    {
        'test_type': 'check_exact_lines',
        'exact_lines': 3,
        'description': 'Plot must have exactly 3 data sets',
        'pass_feedback': 'Correct - your plot has exactly 3 lines!',
        'fail_feedback': 'Your plot should have exactly 3 lines/data sets'
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
        'pass_feedback': '',
        'fail_feedback': 'result_list should be a Python list, not a numpy array'
    },
    {
        'test_type': 'array_size',
        'variable_name': 'result_array',
        'min_size': 50,
        'description': 'result_array should have at least 50 elements',
        'pass_feedback': '',
        'fail_feedback': ''
    }
]

# ===== ASSIGNMENT 16: Plot Solution Comparison (NEW) =====
assignment16_tests = [
    {
        'test_type': 'plot_created',
        'description': 'Should create a plot',
        'pass_feedback': '',
        'fail_feedback': ''
    },
    {
        'test_type': 'compare_plot_solution',
        'solution_file': 'solutions/assignment16_solution.py',
        'line_index': 0,
        'check_color': 'true',
        'check_linestyle': 'true',
        'check_linewidth': 'true',
        'check_marker': 'false',
        'check_markersize': 'false',
        'description': 'Line 0 style should match solution',
        'pass_feedback': 'Your plot styling matches the solution!',
        'fail_feedback': 'Your line color, style, or width differs from the solution'
    },
    {
        'test_type': 'check_multiple_lines',
        'min_lines': 2,
        'description': 'Should have at least 2 lines',
        'pass_feedback': '',
        'fail_feedback': ''
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

print("Created assignments.xlsx successfully!")
print("\nAssignments included:")
print("  1.  Assignment 1 - Variables")
print("  2.  Assignment 2 - Loops")
print("  3.  Assignment 3 - Functions")
print("  4.  Assignment 4 - NumPy")
print("  5.  Assignment 5 - Plotting")
print("  6.  Assignment 6 - Strings")
print("  7.  Assignment 7 - While Loops")
print("  8.  Assignment 8 - Lists")
print("  9.  Assignment 9 - Solution Comparison")
print("  10. Assignment 10 - Function Testing")
print("  11. Assignment 11 - Variable Relations")
print("  12. Assignment 12 - Advanced Plotting")
print("  13. Assignment 13 - Array Size/Range (NEW)")
print("  14. Assignment 14 - Plot Styling (NEW)")
print("  15. Assignment 15 - Type-Strict Comparison (NEW)")
print("  16. Assignment 16 - Plot Solution Comparison (NEW)")
print("\n" + "="*60)
print("NEW TEST TYPES DEMONSTRATED:")
print("="*60)
print("  array_size          - Assignment 13: Check array length")
print("  array_values_in_range - Assignment 13: Check value bounds")
print("  match_any_prefix    - Assignments 10, 12, 13: Catch any.linspace")
print("  plot_has_xlabel     - Assignment 14: Check for any x label")
print("  plot_has_ylabel     - Assignment 14: Check for any y label")
print("  plot_has_title      - Assignment 14: Check for any title")
print("  plot_line_style     - Assignment 14: Check specific line style")
print("  plot_has_line_style - Assignment 14: Check if any line has style")
print("  plot_line_width     - Assignment 14: Check line width")
print("  plot_marker_size    - Assignment 14: Check marker size")
print("  check_exact_lines   - Assignment 14: Require exact number of lines")
print("  require_same_type   - Assignment 15: list vs array must match")
print("  compare_plot_solution - Assignment 16: Compare plot properties")