"""
Example student submissions for testing the AutoGrader GUI.
Save each submission as a separate .py file to test with the application.
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

print(f"Data: {data}")
print(f"Result (sum): {result}")
print(f"Sum total: {sum_total}")
print(f"Average: {average}")
"""

# ============================================================
# SOLUTION 9: assignment9_solution.py (for solutions folder)
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

# ============================================================
# EXAMPLE 10: assignment10_submission.py
# For "Assignment 10 - Func Test"
# ============================================================
example10 = """
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
"""

# ============================================================
# SOLUTION 10: assignment10_solution.py (for solutions folder)
# ============================================================
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

# Calculate y = cos(π * x)
y = [np.cos(np.pi * val) for val in x]

# Calculate z = 2x + 1
z = [2 * val + 1 for val in x]

print(f"x = {x}")
print(f"y (cos(π*x)) = {y}")
print(f"z (2x+1) = {z}")
"""

# ============================================================
# EXAMPLE 12: assignment12_submission.py
# For "Assignment 12 - Adv Plot"
# ============================================================
example12 = """
# Assignment 12: Advanced Plotting
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
    }
    
    # Create solutions folder if it doesn't exist
    if not os.path.exists('solutions'):
        os.makedirs('solutions')
        print("✓ Created solutions/ folder")
    
    # Create example submissions
    for filename, content in examples.items():
        with open(filename, 'w') as f:
            f.write(content.strip())
        print(f"✓ Created {filename}")
    
    # Create solution file for assignment 9
    with open('solutions/assignment9_solution.py', 'w') as f:
        f.write(solution9.strip())
    print(f"✓ Created solutions/assignment9_solution.py")
    
    print("\n" + "="*60)
    print("Example student submissions created successfully!")
    print("="*60)
    print("\nYou can now use these files to test the AutoGrader GUI:")
    print("1. Run the GUI application")
    print("2. Enter student name")
    print("3. Select an assignment from the dropdown")
    print("4. Browse and select the corresponding submission file")
    print("5. Click 'Check Code' to see the results")
    print("\nFiles created:")
    for filename in examples.keys():
        print(f"  - {filename}")
    print(f"  - solutions/assignment9_solution.py")
