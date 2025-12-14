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