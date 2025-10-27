import os
import sys
import ast
import threading
import inspect
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from contextlib import contextmanager
from typing import Any, List, Dict, Optional, Union, Callable
from io import StringIO


class TimeoutException(Exception):
    """Raised when code execution times out."""
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout=10):
    """
    Run a function with a timeout (cross-platform).
    
    Args:
        func: Function to run
        args: Positional arguments
        kwargs: Keyword arguments
        timeout: Timeout in seconds
        
    Returns:
        Result of the function
        
    Raises:
        TimeoutException: If execution exceeds timeout
    """
    if kwargs is None:
        kwargs = {}
    
    result = [TimeoutException("Code execution timed out")]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            result[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        # Thread is still running, timeout occurred
        raise TimeoutException(f"Code execution timed out after {timeout} seconds")
    
    # Check if an exception was raised
    if isinstance(result[0], Exception):
        raise result[0]
    
    return result[0]


class AutoGrader:
    """
    Comprehensive autograder for Python scripts and functions.
    Supports checking variable values, function usage, plot validation, and more.
    """
    
    def __init__(self, filepath: str = None, timeout: int = 10):
        """
        Initialize the AutoGrader.
        
        Args:
            filepath: Path to the student's Python file (optional if grading functions directly)
            timeout: Maximum seconds allowed for code execution (default: 10)
        """
        self.filepath = filepath
        self.timeout = timeout
        self._content = None
        self._ast_tree = None
        self.captured_vars: Dict[str, Any] = {}
        self.execution_namespace: Dict[str, Any] = {}
        self._execution_successful = False
        self.test_results = []
        
        if filepath:
            self._load_file()
    
    def _load_file(self) -> bool:
        """Load and parse the student's code file."""
        if not os.path.exists(self.filepath):
            self._log_result(False, f"File not found: {self.filepath}")
            return False
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self._content = f.read()
            
            # Parse AST for static analysis
            try:
                self._ast_tree = ast.parse(self._content)
            except SyntaxError as e:
                self._log_result(False, f"Syntax error in code: {e}")
                return False
            
            return True
        except Exception as e:
            self._log_result(False, f"Could not read file: {e}")
            return False
    
    def _log_result(self, passed: bool, message: str):
        """Log a test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {message}")
        self.test_results.append({"passed": passed, "message": message})
    
    def execute_script(self, variables_to_capture: Optional[List[str]] = None) -> bool:
        """
        Execute the student's entire script and capture specified variables.
        
        Args:
            variables_to_capture: List of variable names to capture (None = capture all)
            
        Returns:
            True if execution was successful, False otherwise.
        """
        if self._content is None:
            self._log_result(False, "No code to execute")
            return False
        
        # Create restricted namespace
        safe_builtins = self._get_safe_builtins()
        self.execution_namespace = {'__builtins__': safe_builtins}
        
        def execute_code():
            exec(self._content, self.execution_namespace, self.execution_namespace)
        
        try:
            run_with_timeout(execute_code, timeout=self.timeout)
            
            # Capture variables
            if variables_to_capture is None:
                # Capture all user-defined variables
                self.captured_vars = {
                    k: v for k, v in self.execution_namespace.items() 
                    if not k.startswith('_') and k != '__builtins__'
                }
            else:
                self.captured_vars = {
                    var: self.execution_namespace.get(var, None) 
                    for var in variables_to_capture
                }
            
            self._execution_successful = True
            self._log_result(True, f"Script executed successfully")
            return True
            
        except TimeoutException as e:
            self._log_result(False, str(e))
            return False
        except Exception as e:
            self._log_result(False, f"Execution failed: {type(e).__name__}: {e}")
            return False
    
    def _get_safe_builtins(self) -> Dict[str, Any]:
        """Return a dictionary of safe built-in functions."""
        import math
        import random
        import numpy as np
        import matplotlib.pyplot as plt
        
        safe = {
            # Import functionality
            '__import__': __import__,
            '__name__': '__main__',
            '__file__': self.filepath if self.filepath else '<string>',
            
            # Basic builtins
            'print': print, 'len': len, 'range': range, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
            'sum': sum, 'min': min, 'max': max, 'abs': abs, 'round': round,
            'pow': pow, 'divmod': divmod, 'all': all, 'any': any,
            
            # Types
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'frozenset': frozenset,
            
            # Type checking
            'isinstance': isinstance, 'type': type, 'hasattr': hasattr,
            'getattr': getattr, 'setattr': setattr,
            
            # String/list operations
            'reversed': reversed, 'slice': slice,
            
            # Common modules (pre-imported for convenience)
            'math': math,
            'random': random,
            'np': np,
            'plt': plt,
            
            # Exceptions
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'IndexError': IndexError,
            'KeyError': KeyError,
            'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
        }
        return safe
    
    # ======================== VARIABLE CHECKING ========================
    
    def check_variable_value(
        self, 
        var_name: str, 
        expected_value: Any, 
        tolerance: float = 1e-6
    ) -> bool:
        """
        Check if a variable has the expected value after execution.
        
        Args:
            var_name: Name of the variable to check
            expected_value: Expected value
            tolerance: Tolerance for floating point comparison
            
        Returns:
            True if the check passes, False otherwise.
        """
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        # Handle None
        if actual_value is None and expected_value is None:
            self._log_result(True, f"'{var_name}' is None as expected")
            return True
        
        # Numeric comparison with tolerance
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            if abs(actual_value - expected_value) <= tolerance:
                self._log_result(True, f"'{var_name}' = {actual_value} (expected {expected_value})")
                return True
            else:
                self._log_result(False, f"'{var_name}' = {actual_value}, expected {expected_value}")
                return False
        
        # List/tuple comparison with tolerance
        if isinstance(expected_value, (list, tuple)) and isinstance(actual_value, (list, tuple)):
            try:
                import numpy as np
                if np.allclose(actual_value, expected_value, atol=tolerance):
                    self._log_result(True, f"'{var_name}' matches expected list/array")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected list/array")
                    return False
            except:
                # Fallback to exact comparison if numpy comparison fails
                if actual_value == expected_value:
                    self._log_result(True, f"'{var_name}' matches expected list")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected list")
                    return False
        
        # NumPy array comparison
        try:
            import numpy as np
            if isinstance(expected_value, np.ndarray) or isinstance(actual_value, np.ndarray):
                if np.allclose(actual_value, expected_value, atol=tolerance):
                    self._log_result(True, f"'{var_name}' matches expected array")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected array")
                    return False
        except:
            pass
        
        # Exact comparison
        if actual_value == expected_value:
            self._log_result(True, f"'{var_name}' = {repr(actual_value)}")
            return True
        else:
            self._log_result(False, f"'{var_name}' = {repr(actual_value)}, expected {repr(expected_value)}")
            return False
    
    def check_variable_type(self, var_name: str, expected_type: type) -> bool:
        """
        Check if a variable has the expected type.
        
        Args:
            var_name: Name of the variable
            expected_type: Expected type (e.g., int, str, list)
            
        Returns:
            True if the check passes, False otherwise.
        """
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_type = type(self.captured_vars[var_name])
        if isinstance(self.captured_vars[var_name], expected_type):
            self._log_result(True, f"'{var_name}' is of type {expected_type.__name__}")
            return True
        else:
            self._log_result(False, f"'{var_name}' is {actual_type.__name__}, expected {expected_type.__name__}")
            return False
    
    def check_list_equals(
        self,
        var_name: str,
        expected_list: list,
        order_matters: bool = True,
        tolerance: float = 1e-6
    ) -> bool:
        """
        Check if a variable contains a list equal to the expected list.
        
        Args:
            var_name: Name of the variable
            expected_list: Expected list
            order_matters: If True, order must match. If False, only elements need to match.
            tolerance: Tolerance for numeric comparisons
            
        Returns:
            True if the check passes, False otherwise.
        """
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        # Check if it's a list, tuple, or numpy array
        try:
            import numpy as np
            is_array_like = isinstance(actual_value, (list, tuple, np.ndarray))
        except ImportError:
            is_array_like = isinstance(actual_value, (list, tuple))
        
        if not is_array_like:
            self._log_result(False, f"'{var_name}' is not a list/array (type: {type(actual_value).__name__})")
            return False
        
        if order_matters:
            # Check with order
            try:
                import numpy as np
                if np.allclose(actual_value, expected_list, atol=tolerance):
                    self._log_result(True, f"'{var_name}' equals expected list")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not equal expected list")
                    return False
            except:
                if list(actual_value) == list(expected_list):
                    self._log_result(True, f"'{var_name}' equals expected list")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not equal expected list")
                    return False
        else:
            # Check without order (set comparison)
            if sorted(list(actual_value)) == sorted(list(expected_list)):
                self._log_result(True, f"'{var_name}' contains expected elements (order not checked)")
                return True
            else:
                self._log_result(False, f"'{var_name}' does not contain expected elements")
                return False
    
    def check_array_equals(
        self,
        var_name: str,
        expected_array,
        tolerance: float = 1e-6
    ) -> bool:
        """
        Check if a variable contains a NumPy array equal to the expected array.
        
        Args:
            var_name: Name of the variable
            expected_array: Expected array (can be list or numpy array)
            tolerance: Tolerance for numeric comparisons
            
        Returns:
            True if the check passes, False otherwise.
        """
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        try:
            import numpy as np
            
            # Convert to numpy arrays if needed
            if isinstance(actual_value, (list, tuple)):
                try:
                    actual_value = np.array(actual_value)
                except:
                    self._log_result(False, f"'{var_name}' cannot be converted to array")
                    return False
            elif not isinstance(actual_value, np.ndarray):
                self._log_result(False, f"'{var_name}' is not a list or array (type: {type(actual_value).__name__})")
                return False
            
            if not isinstance(expected_array, np.ndarray):
                expected_array = np.array(expected_array)
            
            # Check shape
            if actual_value.shape != expected_array.shape:
                self._log_result(False, 
                    f"'{var_name}' shape {actual_value.shape} != expected shape {expected_array.shape}")
                return False
            
            # Check values
            if np.allclose(actual_value, expected_array, atol=tolerance):
                self._log_result(True, f"'{var_name}' array equals expected array")
                return True
            else:
                self._log_result(False, f"'{var_name}' array does not equal expected array")
                return False
                
        except ImportError:
            self._log_result(False, "NumPy not available for array comparison")
            return False
        except Exception as e:
            self._log_result(False, f"Error comparing arrays: {str(e)}")
            return False
    
    def compare_with_solution(
        self,
        solution_file: str,
        variables_to_compare: list,
        tolerance: float = 1e-6
    ) -> bool:
        """
        Execute a solution file and compare specified variables with student's values.
        
        Args:
            solution_file: Path to the solution Python file
            variables_to_compare: List of variable names to compare
            tolerance: Tolerance for numeric comparisons
            
        Returns:
            True if all variables match, False otherwise.
        """
        if not self._execution_successful:
            self._log_result(False, "Cannot compare: student script not executed")
            return False
        
        if not os.path.exists(solution_file):
            self._log_result(False, f"Solution file not found: {solution_file}")
            return False
        
        try:
            # Read solution file
            with open(solution_file, 'r', encoding='utf-8') as f:
                solution_content = f.read()
            
            # Execute solution
            safe_builtins = self._get_safe_builtins()
            solution_namespace = {'__builtins__': safe_builtins}
            
            def execute_solution():
                exec(solution_content, solution_namespace, solution_namespace)
            
            run_with_timeout(execute_solution, timeout=self.timeout)
            
            # Compare variables
            all_match = True
            for var_name in variables_to_compare:
                # Check if variable exists in both
                if var_name not in self.captured_vars:
                    self._log_result(False, f"Variable '{var_name}' not found in student code")
                    all_match = False
                    continue
                
                if var_name not in solution_namespace:
                    self._log_result(False, f"Variable '{var_name}' not found in solution")
                    all_match = False
                    continue
                
                student_value = self.captured_vars[var_name]
                solution_value = solution_namespace[var_name]
                
                # Compare values
                match = self._compare_values(var_name, student_value, solution_value, tolerance)
                if not match:
                    all_match = False
            
            return all_match
            
        except TimeoutException:
            self._log_result(False, "Solution execution timed out")
            return False
        except Exception as e:
            self._log_result(False, f"Error executing solution: {str(e)}")
            return False
    
    def _compare_values(self, var_name: str, student_value: Any, solution_value: Any, tolerance: float) -> bool:
        """
        Internal method to compare two values with appropriate logic.
        
        Args:
            var_name: Variable name (for logging)
            student_value: Student's value
            solution_value: Solution value
            tolerance: Tolerance for numeric comparisons
            
        Returns:
            True if values match, False otherwise.
        """
        try:
            import numpy as np
            
            # NumPy array comparison
            if isinstance(solution_value, np.ndarray) or isinstance(student_value, np.ndarray):
                try:
                    if np.allclose(student_value, solution_value, atol=tolerance):
                        self._log_result(True, f"'{var_name}' matches solution")
                        return True
                    else:
                        self._log_result(False, f"'{var_name}' does not match solution")
                        return False
                except:
                    pass
        except ImportError:
            pass
        
        # Numeric comparison
        if isinstance(solution_value, (int, float)) and isinstance(student_value, (int, float)):
            if abs(student_value - solution_value) <= tolerance:
                self._log_result(True, f"'{var_name}' = {student_value} (matches solution)")
                return True
            else:
                self._log_result(False, 
                    f"'{var_name}' = {student_value}, expected {solution_value}")
                return False
        
        # List/tuple comparison
        if isinstance(solution_value, (list, tuple)) and isinstance(student_value, (list, tuple)):
            try:
                import numpy as np
                if np.allclose(student_value, solution_value, atol=tolerance):
                    self._log_result(True, f"'{var_name}' list matches solution")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' list does not match solution")
                    return False
            except:
                if student_value == solution_value:
                    self._log_result(True, f"'{var_name}' list matches solution")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' list does not match solution")
                    return False
        
        # Exact comparison
        if student_value == solution_value:
            self._log_result(True, f"'{var_name}' matches solution")
            return True
        else:
            self._log_result(False, 
                f"'{var_name}' = {repr(student_value)}, expected {repr(solution_value)}")
            return False
    
    # ======================== FUNCTION CHECKING ========================
    
    def check_function_exists(self, func_name: str) -> bool:
        """
        Check if a function is defined in the code (static analysis).
        
        Args:
            func_name: Name of the function
            
        Returns:
            True if the function exists, False otherwise.
        """
        if self._ast_tree is None:
            self._log_result(False, "AST not available for static analysis")
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                self._log_result(True, f"Function '{func_name}' is defined")
                return True
        
        self._log_result(False, f"Function '{func_name}' not found")
        return False
    
    def check_function_called(self, func_name: str) -> bool:
        """
        Check if a function is called in the code (static analysis).
        
        Args:
            func_name: Name of the function (can include module, e.g., 'np.mean', 'plt.plot')
            
        Returns:
            True if the function is called, False otherwise.
        """
        if self._ast_tree is None:
            self._log_result(False, "AST not available for static analysis")
            return False
        
        # Split function name to handle module.function notation
        parts = func_name.split('.')
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.Call):
                # Handle simple function calls: func()
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    self._log_result(True, f"Function '{func_name}' is called")
                    return True
                
                # Handle attribute calls: module.func() or obj.method()
                if isinstance(node.func, ast.Attribute):
                    if len(parts) == 2:
                        # Check for module.function pattern (e.g., np.mean)
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == parts[0] and node.func.attr == parts[1]:
                                self._log_result(True, f"Function '{func_name}' is called")
                                return True
                    elif len(parts) == 1:
                        # Just check the method/attribute name
                        if node.func.attr == parts[0]:
                            self._log_result(True, f"Function/method '{func_name}' is called")
                            return True
                
                # Handle nested attributes: numpy.random.randint()
                if len(parts) > 2 and isinstance(node.func, ast.Attribute):
                    # Reconstruct the full call path
                    call_parts = []
                    current = node.func
                    while isinstance(current, ast.Attribute):
                        call_parts.insert(0, current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        call_parts.insert(0, current.id)
                    
                    if '.'.join(call_parts) == func_name:
                        self._log_result(True, f"Function '{func_name}' is called")
                        return True
        
        self._log_result(False, f"Function '{func_name}' is not called")
        return False
    
    def test_function(
        self, 
        func_name: str, 
        test_cases: List[Dict[str, Any]]
    ) -> bool:
        """
        Test a function with multiple test cases.
        
        Args:
            func_name: Name of the function to test
            test_cases: List of test case dictionaries with 'args', 'kwargs', 'expected'
                       Example: [{'args': [5, 3], 'expected': 8}, 
                                {'args': [10], 'kwargs': {'y': 2}, 'expected': 12}]
            
        Returns:
            True if all test cases pass, False otherwise.
        """
        if not self._execution_successful:
            self._log_result(False, f"Cannot test '{func_name}': script not executed")
            return False
        
        if func_name not in self.execution_namespace:
            self._log_result(False, f"Function '{func_name}' not found in namespace")
            return False
        
        func = self.execution_namespace[func_name]
        if not callable(func):
            self._log_result(False, f"'{func_name}' is not a function")
            return False
        
        all_passed = True
        for i, test_case in enumerate(test_cases):
            args = test_case.get('args', [])
            kwargs = test_case.get('kwargs', {})
            expected = test_case.get('expected')
            tolerance = test_case.get('tolerance', 1e-6)
            
            try:
                result = func(*args, **kwargs)
                
                # Compare result with expected
                if isinstance(expected, (int, float)) and isinstance(result, (int, float)):
                    passed = abs(result - expected) <= tolerance
                else:
                    passed = result == expected
                
                if passed:
                    self._log_result(True, f"{func_name}{args} = {result}")
                else:
                    self._log_result(False, f"{func_name}{args} = {result}, expected {expected}")
                    all_passed = False
                    
            except Exception as e:
                self._log_result(False, f"{func_name}{args} raised {type(e).__name__}: {e}")
                all_passed = False
        
        return all_passed
    
    # ======================== PLOT CHECKING ========================
    
    def check_plot_created(self) -> bool:
        """
        Check if any plot was created.
        
        Returns:
            True if a plot exists, False otherwise.
        """
        figs = plt.get_fignums()
        if len(figs) > 0:
            self._log_result(True, f"Plot created ({len(figs)} figure(s))")
            return True
        else:
            self._log_result(False, "No plot created")
            return False
    
    def check_plot_properties(
        self,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        has_legend: Optional[bool] = None,
        has_grid: Optional[bool] = None,
        fig_num: int = 1
    ) -> bool:
        """
        Check various properties of a matplotlib plot.
        
        Args:
            title: Expected plot title (None to skip check)
            xlabel: Expected x-axis label (None to skip check)
            ylabel: Expected y-axis label (None to skip check)
            has_legend: Whether plot should have a legend (None to skip check)
            has_grid: Whether plot should have grid (None to skip check)
            fig_num: Figure number to check (default: 1)
            
        Returns:
            True if all specified checks pass, False otherwise.
        """
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found")
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        
        all_passed = True
        
        # Check title
        if title is not None:
            actual_title = ax.get_title()
            if actual_title == title:
                self._log_result(True, f"Plot title: '{title}'")
            else:
                self._log_result(False, f"Plot title is '{actual_title}', expected '{title}'")
                all_passed = False
        
        # Check xlabel
        if xlabel is not None:
            actual_xlabel = ax.get_xlabel()
            if actual_xlabel == xlabel:
                self._log_result(True, f"X-axis label: '{xlabel}'")
            else:
                self._log_result(False, f"X-axis label is '{actual_xlabel}', expected '{xlabel}'")
                all_passed = False
        
        # Check ylabel
        if ylabel is not None:
            actual_ylabel = ax.get_ylabel()
            if actual_ylabel == ylabel:
                self._log_result(True, f"Y-axis label: '{ylabel}'")
            else:
                self._log_result(False, f"Y-axis label is '{actual_ylabel}', expected '{ylabel}'")
                all_passed = False
        
        # Check legend
        if has_legend is not None:
            legend_exists = ax.get_legend() is not None
            if legend_exists == has_legend:
                status = "has" if has_legend else "does not have"
                self._log_result(True, f"Plot {status} legend")
            else:
                status = "should have" if has_legend else "should not have"
                self._log_result(False, f"Plot {status} legend")
                all_passed = False
        
        # Check grid
        if has_grid is not None:
            # Modern matplotlib versions
            try:
                grid_on = ax.xaxis._major_tick_kw.get('gridOn', False) or \
                          ax.yaxis._major_tick_kw.get('gridOn', False)
            except (AttributeError, KeyError):
                # Fallback: check if gridlines are visible
                grid_on = False
                for line in ax.xaxis.get_gridlines():
                    if line.get_visible():
                        grid_on = True
                        break
                if not grid_on:
                    for line in ax.yaxis.get_gridlines():
                        if line.get_visible():
                            grid_on = True
                            break
            
            if grid_on == has_grid:
                status = "has" if has_grid else "does not have"
                self._log_result(True, f"Plot {status} grid")
            else:
                status = "should have" if has_grid else "should not have"
                self._log_result(False, f"Plot {status} grid")
                all_passed = False
        
        return all_passed
    
    def check_plot_data(
        self,
        expected_x: Optional[List] = None,
        expected_y: Optional[List] = None,
        line_index: int = 0,
        tolerance: float = 1e-6,
        fig_num: int = 1
    ) -> bool:
        """
        Check the data plotted in a line plot.
        
        Args:
            expected_x: Expected x-axis data (None to skip check)
            expected_y: Expected y-axis data (None to skip check)
            line_index: Which line to check if multiple lines (default: 0)
            tolerance: Tolerance for numerical comparison
            fig_num: Figure number to check (default: 1)
            
        Returns:
            True if data matches, False otherwise.
        """
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found")
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found (only {len(lines)} lines)")
            return False
        
        line = lines[line_index]
        actual_x = line.get_xdata()
        actual_y = line.get_ydata()
        
        all_passed = True
        
        # Check x data
        if expected_x is not None:
            import numpy as np
            if np.allclose(actual_x, expected_x, atol=tolerance):
                self._log_result(True, f"X-axis data matches (line {line_index})")
            else:
                self._log_result(False, f"X-axis data does not match (line {line_index})")
                all_passed = False
        
        # Check y data
        if expected_y is not None:
            import numpy as np
            if np.allclose(actual_y, expected_y, atol=tolerance):
                self._log_result(True, f"Y-axis data matches (line {line_index})")
            else:
                self._log_result(False, f"Y-axis data does not match (line {line_index})")
                all_passed = False
        
        return all_passed
    
    def check_plot_color(
        self,
        expected_color: str,
        line_index: int = 0,
        fig_num: int = 1
    ) -> bool:
        """
        Check the color of a plotted line.
        
        Args:
            expected_color: Expected color (e.g., 'red', 'r', '#FF0000')
            line_index: Which line to check (default: 0)
            fig_num: Figure number to check (default: 1)
            
        Returns:
            True if color matches, False otherwise.
        """
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found")
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found")
            return False
        
        line = lines[line_index]
        actual_color = line.get_color()
        
        # Normalize colors for comparison
        from matplotlib.colors import to_rgb
        try:
            expected_rgb = to_rgb(expected_color)
            actual_rgb = to_rgb(actual_color)
            
            if expected_rgb == actual_rgb:
                self._log_result(True, f"Line {line_index} color is {expected_color}")
                return True
            else:
                self._log_result(False, f"Line {line_index} color is {actual_color}, expected {expected_color}")
                return False
        except:
            self._log_result(False, f"Could not compare colors")
            return False
    
    # ======================== REPORTING ========================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all test results.
        
        Returns:
            Dictionary with test statistics and results.
        """
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'results': self.test_results
        }
    
    def print_summary(self):
        """Print a formatted summary of all test results."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("AUTOGRADER SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print("="*60)


# ======================== EXAMPLE USAGE ========================

if __name__ == "__main__":
    # Example 1: Grade a script
    print("EXAMPLE 1: Grading a Script")
    print("-" * 60)
    
    # Create a sample student submission
    with open("student_script.py", "w") as f:
        f.write("""
import matplotlib.pyplot as plt
import numpy as np

# Variables
x = 10
y = 20
sum_xy = x + y
product = x * y
message = "Hello, World!"

# Create a plot
data_x = [1, 2, 3, 4, 5]
data_y = [2, 4, 6, 8, 10]
plt.plot(data_x, data_y, 'r-', label='Linear')
plt.xlabel('X Values')
plt.ylabel('Y Values')
plt.title('My Plot')
plt.legend()
plt.grid(True)
""")
    
    # Initialize grader and execute script
    grader = AutoGrader("student_script.py")
    grader.execute_script()
    
    # Check variables
    grader.check_variable_value('x', 10)
    grader.check_variable_value('sum_xy', 30)
    grader.check_variable_value('product', 200)
    grader.check_variable_type('message', str)
    
    # Check plot
    grader.check_plot_created()
    grader.check_plot_properties(
        title='My Plot',
        xlabel='X Values',
        ylabel='Y Values',
        has_legend=True,
        has_grid=True
    )
    grader.check_plot_data(
        expected_x=[1, 2, 3, 4, 5],
        expected_y=[2, 4, 6, 8, 10]
    )
    grader.check_plot_color('red')
    
    grader.print_summary()
    
    # Clean up
    os.remove("student_script.py")
    plt.close('all')
    
    # Example 2: Grade a function
    print("\n\nEXAMPLE 2: Grading a Function")
    print("-" * 60)
    
    with open("student_function.py", "w") as f:
        f.write("""
def calculate_average(numbers):
    '''Calculate the average of a list of numbers'''
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def multiply_by_two(x):
    '''Multiply a number by 2'''
    return x * 2
""")
    
    grader2 = AutoGrader("student_function.py")
    grader2.execute_script()
    
    # Check if functions exist
    grader2.check_function_exists('calculate_average')
    grader2.check_function_exists('multiply_by_two')
    
    # Test the functions
    grader2.test_function('calculate_average', [
        {'args': [[1, 2, 3, 4, 5]], 'expected': 3.0},
        {'args': [[10, 20, 30]], 'expected': 20.0},
        {'args': [[]], 'expected': 0}
    ])
    
    grader2.test_function('multiply_by_two', [
        {'args': [5], 'expected': 10},
        {'args': [0], 'expected': 0},
        {'args': [-3], 'expected': -6}
    ])
    
    grader2.print_summary()
    
    # Clean up
    os.remove("student_function.py")