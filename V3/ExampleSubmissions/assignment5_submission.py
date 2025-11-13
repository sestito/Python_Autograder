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