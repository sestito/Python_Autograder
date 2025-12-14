# Solution for Assignment 16 - Plot Solution Comparison

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