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