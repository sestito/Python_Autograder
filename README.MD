# Python_Autograder
 
For function grading, I want the ability to be able to call a function with different values for the inputs where the values can be numbers, strings, lists, or even numpy arrays; then I want to be able to compare the output or outputs to a solution file.

When comparing a variable a student coded, I want the ability to do the following. Let's say students have two varaibles called x and y. I want to check if y = np.cos(np.pi * x).

For plot grading, I want to be able to see if they plotted the correct function; for example, cos(2x); for this, there may be two sets of data on the plot. I also want to see if the data length is greater than a certain value. I also want to see if they have a legend.

I also want to be able to check and see if a student used a specific function in their code, and fail them if they did. For example, if they used np.linspace or numpy.linspace the check fails.

For the successful email text, I want this to only display if the code is in debug mode.