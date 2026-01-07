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