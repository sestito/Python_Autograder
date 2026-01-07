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