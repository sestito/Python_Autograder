import os
import sys
import ast
import threading
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from typing import Any, List, Dict, Optional, Callable


class TimeoutException(Exception):
    """Raised when code execution times out."""
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout=10):
    """Run a function with a timeout (cross-platform)."""
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
        raise TimeoutException(f"Code execution timed out after {timeout} seconds")
    
    if isinstance(result[0], Exception):
        raise result[0]
    
    return result[0]


class AutoGrader:
    """Comprehensive autograder for Python scripts and functions."""
    
    def __init__(self, filepath: str = None, timeout: int = 10):
        """Initialize the AutoGrader."""
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
        """Execute the student's entire script and capture variables."""
        if self._content is None:
            self._log_result(False, "No code to execute")
            return False
        
        safe_builtins = self._get_safe_builtins()
        self.execution_namespace = {'__builtins__': safe_builtins}
        
        def execute_code():
            exec(self._content, self.execution_namespace, self.execution_namespace)
        
        try:
            run_with_timeout(execute_code, timeout=self.timeout)
            
            if variables_to_capture is None:
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
        
        return {
            '__import__': __import__,
            '__name__': '__main__',
            '__file__': self.filepath if self.filepath else '<string>',
            'print': print, 'len': len, 'range': range, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter, 'sorted': sorted,
            'sum': sum, 'min': min, 'max': max, 'abs': abs, 'round': round,
            'pow': pow, 'divmod': divmod, 'all': all, 'any': any,
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'frozenset': frozenset,
            'isinstance': isinstance, 'type': type, 'hasattr': hasattr,
            'getattr': getattr, 'setattr': setattr,
            'reversed': reversed, 'slice': slice,
            'math': math, 'random': random, 'np': np, 'plt': plt,
            'Exception': Exception, 'ValueError': ValueError,
            'TypeError': TypeError, 'IndexError': IndexError,
            'KeyError': KeyError, 'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
        }
    
    # ======================== VARIABLE CHECKING ========================
    
    def check_variable_value(self, var_name: str, expected_value: Any, tolerance: float = 1e-6) -> bool:
        """Check if a variable has the expected value."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        if actual_value is None and expected_value is None:
            self._log_result(True, f"'{var_name}' is None as expected")
            return True
        
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            if abs(actual_value - expected_value) <= tolerance:
                self._log_result(True, f"'{var_name}' = {actual_value}")
                return True
            else:
                self._log_result(False, f"'{var_name}' = {actual_value}, expected {expected_value}")
                return False
        
        if isinstance(expected_value, (list, tuple)) and isinstance(actual_value, (list, tuple)):
            try:
                import numpy as np
                if np.allclose(actual_value, expected_value, atol=tolerance):
                    self._log_result(True, f"'{var_name}' matches expected list")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected list")
                    return False
            except:
                if actual_value == expected_value:
                    self._log_result(True, f"'{var_name}' matches expected list")
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected list")
                    return False
        
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
        
        if actual_value == expected_value:
            self._log_result(True, f"'{var_name}' = {repr(actual_value)}")
            return True
        else:
            self._log_result(False, f"'{var_name}' = {repr(actual_value)}, expected {repr(expected_value)}")
            return False
    
    def check_variable_type(self, var_name: str, expected_type: type) -> bool:
        """Check if a variable has the expected type."""
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        if isinstance(self.captured_vars[var_name], expected_type):
            self._log_result(True, f"'{var_name}' is of type {expected_type.__name__}")
            return True
        else:
            actual_type = type(self.captured_vars[var_name])
            self._log_result(False, f"'{var_name}' is {actual_type.__name__}, expected {expected_type.__name__}")
            return False
    
    def check_list_equals(self, var_name: str, expected_list: list, order_matters: bool = True, tolerance: float = 1e-6) -> bool:
        """Check if a variable contains a list equal to the expected list."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        try:
            import numpy as np
            is_array_like = isinstance(actual_value, (list, tuple, np.ndarray))
        except ImportError:
            is_array_like = isinstance(actual_value, (list, tuple))
        
        if not is_array_like:
            self._log_result(False, f"'{var_name}' is not a list/array (type: {type(actual_value).__name__})")
            return False
        
        if order_matters:
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
            if sorted(list(actual_value)) == sorted(list(expected_list)):
                self._log_result(True, f"'{var_name}' contains expected elements")
                return True
            else:
                self._log_result(False, f"'{var_name}' does not contain expected elements")
                return False
    
    def check_array_equals(self, var_name: str, expected_array, tolerance: float = 1e-6) -> bool:
        """Check if a variable contains an array equal to the expected array."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed")
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found")
            return False
        
        actual_value = self.captured_vars[var_name]
        
        try:
            import numpy as np
            
            if isinstance(actual_value, (list, tuple)):
                try:
                    actual_value = np.array(actual_value)
                except:
                    self._log_result(False, f"'{var_name}' cannot be converted to array")
                    return False
            elif not isinstance(actual_value, np.ndarray):
                self._log_result(False, f"'{var_name}' is not a list or array")
                return False
            
            if not isinstance(expected_array, np.ndarray):
                expected_array = np.array(expected_array)
            
            if actual_value.shape != expected_array.shape:
                self._log_result(False, f"'{var_name}' shape {actual_value.shape} != expected {expected_array.shape}")
                return False
            
            if np.allclose(actual_value, expected_array, atol=tolerance):
                self._log_result(True, f"'{var_name}' array equals expected")
                return True
            else:
                self._log_result(False, f"'{var_name}' array does not equal expected")
                return False
                
        except ImportError:
            self._log_result(False, "NumPy not available")
            return False
        except Exception as e:
            self._log_result(False, f"Error comparing arrays: {str(e)}")
            return False
    
    def compare_with_solution(self, solution_file: str, variables_to_compare: list, tolerance: float = 1e-6) -> bool:
        """Execute a solution file and compare variables."""
        if not self._execution_successful:
            self._log_result(False, "Cannot compare: student script not executed")
            return False
        
        if not os.path.exists(solution_file):
            self._log_result(False, f"Solution file not found: {solution_file}")
            return False
        
        try:
            with open(solution_file, 'r', encoding='utf-8') as f:
                solution_content = f.read()
            
            safe_builtins = self._get_safe_builtins()
            solution_namespace = {'__builtins__': safe_builtins}
            
            def execute_solution():
                exec(solution_content, solution_namespace, solution_namespace)
            
            run_with_timeout(execute_solution, timeout=self.timeout)
            
            all_match = True
            for var_name in variables_to_compare:
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
        """Internal method to compare two values."""
        try:
            import numpy as np
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
        
        if isinstance(solution_value, (int, float)) and isinstance(student_value, (int, float)):
            if abs(student_value - solution_value) <= tolerance:
                self._log_result(True, f"'{var_name}' matches solution")
                return True
            else:
                self._log_result(False, f"'{var_name}' = {student_value}, expected {solution_value}")
                return False
        
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
        
        if student_value == solution_value:
            self._log_result(True, f"'{var_name}' matches solution")
            return True
        else:
            self._log_result(False, f"'{var_name}' = {repr(student_value)}, expected {repr(solution_value)}")
            return False
    
    # ======================== FUNCTION CHECKING ========================
    
    def check_function_exists(self, func_name: str) -> bool:
        """Check if a function is defined."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                self._log_result(True, f"Function '{func_name}' is defined")
                return True
        
        self._log_result(False, f"Function '{func_name}' not found")
        return False
    
    def check_function_called(self, func_name: str) -> bool:
        """Check if a function is called."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        parts = func_name.split('.')
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    self._log_result(True, f"Function '{func_name}' is called")
                    return True
                
                if isinstance(node.func, ast.Attribute):
                    if len(parts) == 2:
                        if isinstance(node.func.value, ast.Name):
                            if node.func.value.id == parts[0] and node.func.attr == parts[1]:
                                self._log_result(True, f"Function '{func_name}' is called")
                                return True
                    elif len(parts) == 1:
                        if node.func.attr == parts[0]:
                            self._log_result(True, f"Function '{func_name}' is called")
                            return True
                
                if len(parts) > 2 and isinstance(node.func, ast.Attribute):
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
    
    def test_function(self, func_name: str, test_cases: List[Dict[str, Any]]) -> bool:
        """Test a function with multiple test cases."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot test '{func_name}': script not executed")
            return False
        
        if func_name not in self.execution_namespace:
            self._log_result(False, f"Function '{func_name}' not found")
            return False
        
        func = self.execution_namespace[func_name]
        if not callable(func):
            self._log_result(False, f"'{func_name}' is not a function")
            return False
        
        all_passed = True
        for test_case in test_cases:
            args = test_case.get('args', [])
            kwargs = test_case.get('kwargs', {})
            expected = test_case.get('expected')
            tolerance = test_case.get('tolerance', 1e-6)
            
            try:
                result = func(*args, **kwargs)
                
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
        """Check if any plot was created."""
        figs = plt.get_fignums()
        if len(figs) > 0:
            self._log_result(True, f"Plot created")
            return True
        else:
            self._log_result(False, "No plot created")
            return False
    
    def check_plot_properties(self, title: Optional[str] = None, xlabel: Optional[str] = None, 
                              ylabel: Optional[str] = None, has_legend: Optional[bool] = None,
                              has_grid: Optional[bool] = None, fig_num: int = 1) -> bool:
        """Check plot properties."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found")
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        all_passed = True
        
        if title is not None:
            if ax.get_title() == title:
                self._log_result(True, f"Plot title: '{title}'")
            else:
                self._log_result(False, f"Plot title is '{ax.get_title()}', expected '{title}'")
                all_passed = False
        
        if xlabel is not None:
            if ax.get_xlabel() == xlabel:
                self._log_result(True, f"X-axis label: '{xlabel}'")
            else:
                self._log_result(False, f"X-axis label is '{ax.get_xlabel()}', expected '{xlabel}'")
                all_passed = False
        
        if ylabel is not None:
            if ax.get_ylabel() == ylabel:
                self._log_result(True, f"Y-axis label: '{ylabel}'")
            else:
                self._log_result(False, f"Y-axis label is '{ax.get_ylabel()}', expected '{ylabel}'")
                all_passed = False
        
        if has_legend is not None:
            legend_exists = ax.get_legend() is not None
            if legend_exists == has_legend:
                self._log_result(True, f"Plot {'has' if has_legend else 'does not have'} legend")
            else:
                self._log_result(False, f"Plot {'should have' if has_legend else 'should not have'} legend")
                all_passed = False
        
        if has_grid is not None:
            try:
                grid_on = ax.xaxis._major_tick_kw.get('gridOn', False) or ax.yaxis._major_tick_kw.get('gridOn', False)
            except:
                grid_on = False
                for line in ax.xaxis.get_gridlines():
                    if line.get_visible():
                        grid_on = True
                        break
            
            if grid_on == has_grid:
                self._log_result(True, f"Plot {'has' if has_grid else 'does not have'} grid")
            else:
                self._log_result(False, f"Plot {'should have' if has_grid else 'should not have'} grid")
                all_passed = False
        
        return all_passed
    
    def check_plot_data(self, expected_x: Optional[List] = None, expected_y: Optional[List] = None,
                        line_index: int = 0, tolerance: float = 1e-6, fig_num: int = 1) -> bool:
        """Check plot data."""
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
        actual_x = line.get_xdata()
        actual_y = line.get_ydata()
        all_passed = True
        
        if expected_x is not None:
            import numpy as np
            if np.allclose(actual_x, expected_x, atol=tolerance):
                self._log_result(True, f"X-axis data matches")
            else:
                self._log_result(False, f"X-axis data does not match")
                all_passed = False
        
        if expected_y is not None:
            import numpy as np
            if np.allclose(actual_y, expected_y, atol=tolerance):
                self._log_result(True, f"Y-axis data matches")
            else:
                self._log_result(False, f"Y-axis data does not match")
                all_passed = False
        
        return all_passed
    
    def check_plot_data_length(self, min_length: Optional[int] = None, max_length: Optional[int] = None,
                                exact_length: Optional[int] = None, line_index: int = 0, fig_num: int = 1) -> bool:
        """Check plot data length."""
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
        actual_length = len(line.get_xdata())
        all_passed = True
        
        if exact_length is not None:
            if actual_length == exact_length:
                self._log_result(True, f"Line has exactly {exact_length} data points")
            else:
                self._log_result(False, f"Line has {actual_length} data points, expected {exact_length}")
                all_passed = False
        
        if min_length is not None:
            if actual_length >= min_length:
                self._log_result(True, f"Line has at least {min_length} data points")
            else:
                self._log_result(False, f"Line has {actual_length} data points, minimum is {min_length}")
                all_passed = False
        
        if max_length is not None:
            if actual_length <= max_length:
                self._log_result(True, f"Line has at most {max_length} data points")
            else:
                self._log_result(False, f"Line has {actual_length} data points, maximum is {max_length}")
                all_passed = False
        
        return all_passed
    
    def check_plot_function(self, function: Callable, line_index: int = 0, tolerance: float = 1e-6, fig_num: int = 1) -> bool:
        """Check if Y data matches a function of X data."""
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
        actual_x = line.get_xdata()
        actual_y = line.get_ydata()
        
        try:
            import numpy as np
            expected_y = function(actual_x)
            
            if np.allclose(actual_y, expected_y, atol=tolerance):
                self._log_result(True, f"Y data matches expected function")
                return True
            else:
                self._log_result(False, f"Y data does not match expected function")
                return False
        except Exception as e:
            self._log_result(False, f"Error evaluating function: {str(e)}")
            return False
    
    def get_plot_data(self, line_index: int = 0, fig_num: int = 1) -> Optional[Dict[str, Any]]:
        """Get plot data."""
        if fig_num not in plt.get_fignums():
            return None
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            return None
        
        line = lines[line_index]
        return {
            'x': line.get_xdata(),
            'y': line.get_ydata(),
            'color': line.get_color(),
            'linestyle': line.get_linestyle(),
            'linewidth': line.get_linewidth(),
            'label': line.get_label()
        }
    
    def check_plot_color(self, expected_color: str, line_index: int = 0, fig_num: int = 1) -> bool:
        """Check plot color."""
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
        
        from matplotlib.colors import to_rgb
        try:
            expected_rgb = to_rgb(expected_color)
            actual_rgb = to_rgb(actual_color)
            
            if expected_rgb == actual_rgb:
                self._log_result(True, f"Line color is {expected_color}")
                return True
            else:
                self._log_result(False, f"Line color is {actual_color}, expected {expected_color}")
                return False
        except:
            self._log_result(False, f"Could not compare colors")
            return False
    
    # ======================== CODE PATTERN CHECKING ========================
    
    def check_code_contains(self, phrase: str, case_sensitive: bool = True) -> bool:
        """Check if code contains a phrase."""
        if self._content is None:
            self._log_result(False, "No code content available")
            return False
        
        search_content = self._content
        search_phrase = phrase
        
        if not case_sensitive:
            search_content = search_content.lower()
            search_phrase = search_phrase.lower()
        
        if search_phrase in search_content:
            self._log_result(True, f"Code contains '{phrase}'")
            return True
        else:
            self._log_result(False, f"Code does not contain '{phrase}'")
            return False
    
    def check_operator_used(self, operator: str) -> bool:
        """Check if an operator is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        operator_map = {
            '+=': ast.Add, '-=': ast.Sub, '*=': ast.Mult, '/=': ast.Div,
            '//=': ast.FloorDiv, '%=': ast.Mod, '**=': ast.Pow,
            '+': ast.Add, '-': ast.Sub, '*': ast.Mult, '/': ast.Div,
            '//': ast.FloorDiv, '%': ast.Mod, '**': ast.Pow,
            '==': ast.Eq, '!=': ast.NotEq, '<': ast.Lt, '<=': ast.LtE,
            '>': ast.Gt, '>=': ast.GtE, 'and': ast.And, 'or': ast.Or,
            'not': ast.Not,
        }
        
        if operator not in operator_map:
            return self.check_code_contains(operator)
        
        target_op = operator_map[operator]
        
        for node in ast.walk(self._ast_tree):
            if operator in ['+=', '-=', '*=', '/=', '//=', '%=', '**=']:
                if isinstance(node, ast.AugAssign) and isinstance(node.op, target_op):
                    self._log_result(True, f"Operator '{operator}' is used")
                    return True
            elif isinstance(node, ast.BinOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used")
                return True
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, target_op):
                        self._log_result(True, f"Operator '{operator}' is used")
                        return True
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used")
                return True
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used")
                return True
        
        self._log_result(False, f"Operator '{operator}' is not used")
        return False
    
    # ======================== CONTROL STRUCTURE CHECKING ========================
    
    def check_for_loop_used(self) -> bool:
        """Check if a for loop is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.For):
                self._log_result(True, "For loop is used")
                return True
        
        self._log_result(False, "For loop is not used")
        return False
    
    def check_while_loop_used(self) -> bool:
        """Check if a while loop is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.While):
                self._log_result(True, "While loop is used")
                return True
        
        self._log_result(False, "While loop is not used")
        return False
    
    def check_if_statement_used(self) -> bool:
        """Check if an if statement is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available")
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.If):
                self._log_result(True, "If statement is used")
                return True
        
        self._log_result(False, "If statement is not used")
        return False
    
    def count_loop_iterations(self, loop_variable: str, expected_count: Optional[int] = None, tolerance: int = 0) -> Optional[int]:
        """Count loop iterations by checking a counter variable."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot count iterations: script not executed")
            return None
        
        if loop_variable not in self.captured_vars:
            self._log_result(False, f"Loop counter variable '{loop_variable}' not found")
            return None
        
        actual_count = self.captured_vars[loop_variable]
        
        if not isinstance(actual_count, (int, float)):
            self._log_result(False, f"Variable '{loop_variable}' is not a number")
            return None
        
        actual_count = int(actual_count)
        
        if expected_count is not None:
            if abs(actual_count - expected_count) <= tolerance:
                self._log_result(True, f"Loop ran {actual_count} times")
            else:
                self._log_result(False, f"Loop ran {actual_count} times, expected {expected_count}")
        else:
            self._log_result(True, f"Loop counter '{loop_variable}' = {actual_count}")
        
        return actual_count
    
    # ======================== REPORTING ========================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'score': f"{passed}/{total}",
            'results': self.test_results
        }
    
    def print_summary(self):
        """Print formatted summary."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("AUTOGRADER SUMMARY")
        print("="*60)
        print(f"Score: {summary['score']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print("="*60)