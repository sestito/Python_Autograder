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