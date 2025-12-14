import os
import sys
import ast
import threading
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from typing import Any, List, Dict, Optional, Callable, Union


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
    
    def _log_result(self, passed: bool, message: str, 
                    custom_pass_feedback: Optional[str] = None,
                    custom_fail_feedback: Optional[str] = None):
        """Log a test result with optional custom feedback."""
        status = "PASS" if passed else "FAIL"
        checkmark = "\u2713" if passed else "\u2717"
        
        if passed and custom_pass_feedback:
            display_message = custom_pass_feedback
        elif not passed and custom_fail_feedback:
            display_message = custom_fail_feedback
        else:
            display_message = message
        
        print(f"{checkmark} {status}: {display_message}")
        self.test_results.append({
            "passed": passed, 
            "message": display_message,
            "default_message": message
        })
    
    def execute_script(self, variables_to_capture: Optional[List[str]] = None,
                       custom_pass_feedback: Optional[str] = None,
                       custom_fail_feedback: Optional[str] = None) -> bool:
        """Execute the student's entire script and capture variables."""
        if self._content is None:
            self._log_result(False, "No code to execute", 
                           custom_fail_feedback=custom_fail_feedback)
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
            self._log_result(True, f"Script executed successfully",
                           custom_pass_feedback=custom_pass_feedback)
            return True
            
        except TimeoutException as e:
            self._log_result(False, str(e), custom_fail_feedback=custom_fail_feedback)
            return False
        except Exception as e:
            self._log_result(False, f"Execution failed: {type(e).__name__}: {e}",
                           custom_fail_feedback=custom_fail_feedback)
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
    
    def check_variable_value(self, var_name: str, expected_value: Any, tolerance: float = 1e-6,
                             custom_pass_feedback: Optional[str] = None,
                             custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a variable has the expected value."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_value = self.captured_vars[var_name]
        
        if actual_value is None and expected_value is None:
            self._log_result(True, f"'{var_name}' is None as expected",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        
        import numpy as np
        
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            if abs(actual_value - expected_value) <= tolerance:
                self._log_result(True, f"'{var_name}' = {actual_value}",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            else:
                self._log_result(False, f"'{var_name}' = {actual_value}, expected {expected_value}",
                               custom_fail_feedback=custom_fail_feedback)
                return False
        
        if isinstance(expected_value, (list, tuple, np.ndarray)) and isinstance(actual_value, (list, tuple, np.ndarray)):
            try:
                if np.allclose(actual_value, expected_value, atol=tolerance):
                    self._log_result(True, f"'{var_name}' matches expected",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
                else:
                    self._log_result(False, f"'{var_name}' does not match expected",
                                   custom_fail_feedback=custom_fail_feedback)
                    return False
            except:
                pass
        
        if actual_value == expected_value:
            self._log_result(True, f"'{var_name}' = {repr(actual_value)}",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        else:
            self._log_result(False, f"'{var_name}' = {repr(actual_value)}, expected {repr(expected_value)}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def check_variable_type(self, var_name: str, expected_type: type,
                            custom_pass_feedback: Optional[str] = None,
                            custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a variable has the expected type."""
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if isinstance(self.captured_vars[var_name], expected_type):
            self._log_result(True, f"'{var_name}' is of type {expected_type.__name__}",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        else:
            actual_type = type(self.captured_vars[var_name])
            self._log_result(False, f"'{var_name}' is {actual_type.__name__}, expected {expected_type.__name__}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def check_array_size(self, var_name: str, min_size: Optional[int] = None, 
                         max_size: Optional[int] = None, exact_size: Optional[int] = None,
                         custom_pass_feedback: Optional[str] = None,
                         custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a numpy array or list has the required size."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_value = self.captured_vars[var_name]
        
        import numpy as np
        if isinstance(actual_value, np.ndarray):
            actual_size = actual_value.size
        elif isinstance(actual_value, (list, tuple)):
            actual_size = len(actual_value)
        else:
            self._log_result(False, f"'{var_name}' is not an array or list",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if exact_size is not None:
            if actual_size != exact_size:
                self._log_result(False, f"'{var_name}' has {actual_size} elements, expected exactly {exact_size}",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            self._log_result(True, f"'{var_name}' has exactly {exact_size} elements",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        
        all_passed = True
        if min_size is not None:
            if actual_size < min_size:
                self._log_result(False, f"'{var_name}' has {actual_size} elements, expected at least {min_size}",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"'{var_name}' has at least {min_size} elements ({actual_size})",
                               custom_pass_feedback=custom_pass_feedback)
        
        if max_size is not None:
            if actual_size > max_size:
                self._log_result(False, f"'{var_name}' has {actual_size} elements, expected at most {max_size}",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"'{var_name}' has at most {max_size} elements ({actual_size})",
                               custom_pass_feedback=custom_pass_feedback)
        
        return all_passed
    
    def check_array_values_in_range(self, var_name: str, min_value: Optional[float] = None,
                                    max_value: Optional[float] = None,
                                    custom_pass_feedback: Optional[str] = None,
                                    custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if all values in an array/list are within a specified range."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_value = self.captured_vars[var_name]
        
        import numpy as np
        if isinstance(actual_value, np.ndarray):
            values = actual_value.flatten()
        elif isinstance(actual_value, (list, tuple)):
            values = np.array(actual_value).flatten()
        else:
            self._log_result(False, f"'{var_name}' is not an array or list",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_min = np.min(values)
        actual_max = np.max(values)
        
        all_passed = True
        if min_value is not None:
            if actual_min < min_value:
                self._log_result(False, f"'{var_name}' has values below {min_value} (min: {actual_min})",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"'{var_name}' values >= {min_value}",
                               custom_pass_feedback=custom_pass_feedback)
        
        if max_value is not None:
            if actual_max > max_value:
                self._log_result(False, f"'{var_name}' has values above {max_value} (max: {actual_max})",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"'{var_name}' values <= {max_value}",
                               custom_pass_feedback=custom_pass_feedback)
        
        return all_passed
    
    def check_list_equals(self, var_name: str, expected_list: list, order_matters: bool = True, 
                          tolerance: float = 1e-6,
                          custom_pass_feedback: Optional[str] = None,
                          custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a variable contains a list equal to the expected list."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_value = self.captured_vars[var_name]
        import numpy as np
        
        if not isinstance(actual_value, (list, tuple, np.ndarray)):
            self._log_result(False, f"'{var_name}' is not a list/array",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if order_matters:
            try:
                if np.allclose(actual_value, expected_list, atol=tolerance):
                    self._log_result(True, f"'{var_name}' equals expected list",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
            except:
                if list(actual_value) == list(expected_list):
                    self._log_result(True, f"'{var_name}' equals expected list",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
            self._log_result(False, f"'{var_name}' does not equal expected list",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        else:
            if sorted(list(actual_value)) == sorted(list(expected_list)):
                self._log_result(True, f"'{var_name}' contains expected elements",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            self._log_result(False, f"'{var_name}' does not contain expected elements",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def check_array_equals(self, var_name: str, expected_array, tolerance: float = 1e-6,
                           custom_pass_feedback: Optional[str] = None,
                           custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a variable contains an array equal to the expected array."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot check '{var_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_value = self.captured_vars[var_name]
        import numpy as np
        
        if isinstance(actual_value, (list, tuple)):
            actual_value = np.array(actual_value)
        elif not isinstance(actual_value, np.ndarray):
            self._log_result(False, f"'{var_name}' is not a list or array",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if not isinstance(expected_array, np.ndarray):
            expected_array = np.array(expected_array)
        
        if actual_value.shape != expected_array.shape:
            self._log_result(False, f"'{var_name}' shape {actual_value.shape} != expected {expected_array.shape}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if np.allclose(actual_value, expected_array, atol=tolerance):
            self._log_result(True, f"'{var_name}' array equals expected",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"'{var_name}' array does not equal expected",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def compare_with_solution(self, solution_file: str, variables_to_compare: list, 
                              tolerance: float = 1e-6, require_same_type: bool = False,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Execute a solution file and compare variables with element-wise checking."""
        if not self._execution_successful:
            self._log_result(False, "Cannot compare: student script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if not os.path.exists(solution_file):
            self._log_result(False, f"Solution file not found: {solution_file}",
                           custom_fail_feedback=custom_fail_feedback)
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
                    self._log_result(False, f"Variable '{var_name}' not found in student code",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_match = False
                    continue
                
                if var_name not in solution_namespace:
                    self._log_result(False, f"Variable '{var_name}' not found in solution",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_match = False
                    continue
                
                student_value = self.captured_vars[var_name]
                solution_value = solution_namespace[var_name]
                
                match = self._compare_values_detailed(var_name, student_value, solution_value, 
                                                     tolerance, require_same_type,
                                                     custom_pass_feedback, custom_fail_feedback)
                if not match:
                    all_match = False
            
            return all_match
            
        except TimeoutException:
            self._log_result(False, "Solution execution timed out",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        except Exception as e:
            self._log_result(False, f"Error executing solution: {str(e)}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def _compare_values_detailed(self, var_name: str, student_value: Any, solution_value: Any, 
                                 tolerance: float, require_same_type: bool = False,
                                 custom_pass_feedback: Optional[str] = None,
                                 custom_fail_feedback: Optional[str] = None) -> bool:
        """Detailed comparison with element-wise checking for arrays/lists."""
        import numpy as np
        
        student_is_array = isinstance(student_value, np.ndarray)
        student_is_list = isinstance(student_value, (list, tuple))
        solution_is_array = isinstance(solution_value, np.ndarray)
        solution_is_list = isinstance(solution_value, (list, tuple))
        
        student_is_arraylike = student_is_array or student_is_list
        solution_is_arraylike = solution_is_array or solution_is_list
        
        if student_is_arraylike and solution_is_arraylike:
            if require_same_type:
                if student_is_array != solution_is_array:
                    student_type = "numpy array" if student_is_array else "list"
                    solution_type = "numpy array" if solution_is_array else "list"
                    self._log_result(False, f"'{var_name}' is {student_type}, expected {solution_type}",
                                   custom_fail_feedback=custom_fail_feedback)
                    return False
            
            try:
                student_arr = np.array(student_value)
                solution_arr = np.array(solution_value)
            except:
                self._log_result(False, f"'{var_name}' could not be converted for comparison",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            
            if student_arr.shape != solution_arr.shape:
                self._log_result(False, f"'{var_name}' shape {student_arr.shape} != expected {solution_arr.shape}",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            
            try:
                differences = np.abs(student_arr - solution_arr)
                max_diff = np.max(differences)
                
                if max_diff <= tolerance:
                    self._log_result(True, f"'{var_name}' matches solution (max diff: {max_diff:.2e})",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
                else:
                    diff_indices = np.where(differences > tolerance)
                    if len(diff_indices[0]) > 0:
                        first_idx = tuple(idx[0] for idx in diff_indices)
                        self._log_result(False, 
                            f"'{var_name}' differs at index {first_idx}: got {student_arr[first_idx]}, expected {solution_arr[first_idx]}",
                            custom_fail_feedback=custom_fail_feedback)
                    return False
            except:
                if np.allclose(student_arr, solution_arr, atol=tolerance):
                    self._log_result(True, f"'{var_name}' matches solution",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
                self._log_result(False, f"'{var_name}' does not match solution",
                               custom_fail_feedback=custom_fail_feedback)
                return False
        
        if isinstance(solution_value, (int, float)) and isinstance(student_value, (int, float)):
            if abs(student_value - solution_value) <= tolerance:
                self._log_result(True, f"'{var_name}' matches solution",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            self._log_result(False, f"'{var_name}' = {student_value}, expected {solution_value}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if student_value == solution_value:
            self._log_result(True, f"'{var_name}' matches solution",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"'{var_name}' = {repr(student_value)}, expected {repr(solution_value)}",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    # ======================== FUNCTION CHECKING ========================
    
    def check_function_exists(self, func_name: str,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a function is defined."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                self._log_result(True, f"Function '{func_name}' is defined",
                               custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, f"Function '{func_name}' not found",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def _get_function_name_from_call(self, node: ast.Call) -> Optional[str]:
        """Extract function name from a Call node, returning only the final attribute."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None
    
    def _get_full_function_name_from_call(self, node: ast.Call) -> Optional[str]:
        """Extract full function name (with prefix) from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return '.'.join(parts)
        return None
    
    def check_function_called(self, func_name: str, match_any_prefix: bool = False,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a function is called. If match_any_prefix=True, matches any prefix."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        func_parts = func_name.split('.')
        final_name = func_parts[-1]
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.Call):
                if match_any_prefix:
                    call_name = self._get_function_name_from_call(node)
                    if call_name == final_name:
                        full_name = self._get_full_function_name_from_call(node)
                        self._log_result(True, f"Function '{full_name}' is called",
                                       custom_pass_feedback=custom_pass_feedback)
                        return True
                else:
                    full_call_name = self._get_full_function_name_from_call(node)
                    if full_call_name == func_name:
                        self._log_result(True, f"Function '{func_name}' is called",
                                       custom_pass_feedback=custom_pass_feedback)
                        return True
                    if isinstance(node.func, ast.Name) and node.func.id == func_name:
                        self._log_result(True, f"Function '{func_name}' is called",
                                       custom_pass_feedback=custom_pass_feedback)
                        return True
        
        self._log_result(False, f"Function '{func_name}' is not called",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_function_not_called(self, func_name: str, match_any_prefix: bool = False,
                                  custom_pass_feedback: Optional[str] = None,
                                  custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a function is NOT called. If match_any_prefix=True, catches any prefix."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        func_parts = func_name.split('.')
        final_name = func_parts[-1]
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.Call):
                if match_any_prefix:
                    call_name = self._get_function_name_from_call(node)
                    if call_name == final_name:
                        full_name = self._get_full_function_name_from_call(node)
                        self._log_result(False, f"Function '{full_name}' should NOT be called",
                                       custom_fail_feedback=custom_fail_feedback)
                        return False
                else:
                    full_call_name = self._get_full_function_name_from_call(node)
                    if full_call_name == func_name:
                        self._log_result(False, f"Function '{func_name}' should NOT be called",
                                       custom_fail_feedback=custom_fail_feedback)
                        return False
                    if isinstance(node.func, ast.Name) and node.func.id == func_name:
                        self._log_result(False, f"Function '{func_name}' should NOT be called",
                                       custom_fail_feedback=custom_fail_feedback)
                        return False
        
        self._log_result(True, f"Function '{func_name}' is correctly not used",
                       custom_pass_feedback=custom_pass_feedback)
        return True
    
    def test_function(self, func_name: str, test_cases: List[Dict[str, Any]],
                      custom_pass_feedback: Optional[str] = None,
                      custom_fail_feedback: Optional[str] = None) -> bool:
        """Test a function with multiple test cases."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot test '{func_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if func_name not in self.execution_namespace:
            self._log_result(False, f"Function '{func_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        func = self.execution_namespace[func_name]
        if not callable(func):
            self._log_result(False, f"'{func_name}' is not a function",
                           custom_fail_feedback=custom_fail_feedback)
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
                    self._log_result(True, f"{func_name}{args} = {result}",
                                   custom_pass_feedback=custom_pass_feedback)
                else:
                    self._log_result(False, f"{func_name}{args} = {result}, expected {expected}",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_passed = False
            except Exception as e:
                self._log_result(False, f"{func_name}{args} raised {type(e).__name__}: {e}",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        return all_passed
    
    def test_function_with_solution(self, func_name: str, solution_file: str, 
                                    test_inputs: List[Dict[str, Any]], tolerance: float = 1e-6,
                                    custom_pass_feedback: Optional[str] = None,
                                    custom_fail_feedback: Optional[str] = None) -> bool:
        """Test a function against a solution file."""
        if not self._execution_successful:
            self._log_result(False, f"Cannot test '{func_name}': script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if func_name not in self.execution_namespace:
            self._log_result(False, f"Function '{func_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        student_func = self.execution_namespace[func_name]
        if not callable(student_func):
            self._log_result(False, f"'{func_name}' is not a function",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if not os.path.exists(solution_file):
            self._log_result(False, f"Solution file not found: {solution_file}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        try:
            with open(solution_file, 'r', encoding='utf-8') as f:
                solution_content = f.read()
            
            safe_builtins = self._get_safe_builtins()
            solution_namespace = {'__builtins__': safe_builtins}
            
            def execute_solution():
                exec(solution_content, solution_namespace, solution_namespace)
            
            run_with_timeout(execute_solution, timeout=self.timeout)
            
            if func_name not in solution_namespace:
                self._log_result(False, f"Function '{func_name}' not found in solution",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            
            solution_func = solution_namespace[func_name]
            all_passed = True
            
            for i, test_input in enumerate(test_inputs):
                args = test_input.get('args', [])
                kwargs = test_input.get('kwargs', {})
                
                try:
                    student_result = student_func(*args, **kwargs)
                    solution_result = solution_func(*args, **kwargs)
                    
                    match = self._compare_values_detailed(f"{func_name}_output_{i}", 
                                                        student_result, solution_result, tolerance,
                                                        custom_pass_feedback=custom_pass_feedback,
                                                        custom_fail_feedback=custom_fail_feedback)
                    if not match:
                        all_passed = False
                except Exception as e:
                    self._log_result(False, f"{func_name} test {i} raised {type(e).__name__}: {e}",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_passed = False
            
            return all_passed
            
        except TimeoutException:
            self._log_result(False, "Solution execution timed out",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        except Exception as e:
            self._log_result(False, f"Error executing solution: {str(e)}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def check_variable_relationship(self, var1_name: str, var2_name: str, relationship: Callable, 
                                    tolerance: float = 1e-6, description: str = None,
                                    custom_pass_feedback: Optional[str] = None,
                                    custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if two variables have a specific mathematical relationship."""
        if not self._execution_successful:
            self._log_result(False, "Cannot check relationship: script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var1_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var1_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        if var2_name not in self.captured_vars:
            self._log_result(False, f"Variable '{var2_name}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return False
        
        var1_value = self.captured_vars[var1_name]
        var2_value = self.captured_vars[var2_name]
        
        import numpy as np
        try:
            expected_var2 = relationship(var1_value)
            
            if isinstance(expected_var2, np.ndarray) or isinstance(var2_value, np.ndarray):
                match = np.allclose(var2_value, expected_var2, atol=tolerance)
            elif isinstance(expected_var2, (list, tuple)) or isinstance(var2_value, (list, tuple)):
                match = np.allclose(var2_value, expected_var2, atol=tolerance)
            elif isinstance(expected_var2, (int, float)) and isinstance(var2_value, (int, float)):
                match = abs(var2_value - expected_var2) <= tolerance
            else:
                match = var2_value == expected_var2
            
            desc = description or f"{var2_name} = f({var1_name})"
            if match:
                self._log_result(True, f"Relationship verified: {desc}",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            else:
                self._log_result(False, f"Relationship failed: {desc}",
                               custom_fail_feedback=custom_fail_feedback)
                return False
        except Exception as e:
            self._log_result(False, f"Error checking relationship: {str(e)}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    # ======================== PLOT CHECKING ========================
    
    def check_plot_created(self, custom_pass_feedback: Optional[str] = None,
                           custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if any plot was created."""
        figs = plt.get_fignums()
        if len(figs) > 0:
            self._log_result(True, f"Plot created", custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, "No plot created", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_has_xlabel(self, fig_num: int = 1,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if plot has an x-axis label (any text)."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        xlabel = ax.get_xlabel()
        
        if xlabel and xlabel.strip():
            self._log_result(True, f"Plot has x-axis label: '{xlabel}'",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, "Plot is missing x-axis label", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_has_ylabel(self, fig_num: int = 1,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if plot has a y-axis label (any text)."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        ylabel = ax.get_ylabel()
        
        if ylabel and ylabel.strip():
            self._log_result(True, f"Plot has y-axis label: '{ylabel}'",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, "Plot is missing y-axis label", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_has_title(self, fig_num: int = 1,
                             custom_pass_feedback: Optional[str] = None,
                             custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if plot has a title (any text)."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        title = ax.get_title()
        
        if title and title.strip():
            self._log_result(True, f"Plot has title: '{title}'",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, "Plot is missing title", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_properties(self, title: Optional[str] = None, xlabel: Optional[str] = None, 
                              ylabel: Optional[str] = None, has_legend: Optional[bool] = None,
                              has_grid: Optional[bool] = None, fig_num: int = 1,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check specific plot properties."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        all_passed = True
        
        if title is not None:
            if ax.get_title() == title:
                self._log_result(True, f"Plot title: '{title}'", custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"Plot title is '{ax.get_title()}', expected '{title}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if xlabel is not None:
            if ax.get_xlabel() == xlabel:
                self._log_result(True, f"X-axis label: '{xlabel}'", custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"X-axis label is '{ax.get_xlabel()}', expected '{xlabel}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if ylabel is not None:
            if ax.get_ylabel() == ylabel:
                self._log_result(True, f"Y-axis label: '{ylabel}'", custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"Y-axis label is '{ax.get_ylabel()}', expected '{ylabel}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if has_legend is not None:
            legend_exists = ax.get_legend() is not None
            if legend_exists == has_legend:
                self._log_result(True, f"Plot {'has' if has_legend else 'does not have'} legend",
                               custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"Plot {'should have' if has_legend else 'should not have'} legend",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if has_grid is not None:
            try:
                grid_on = ax.xaxis._major_tick_kw.get('gridOn', False) or ax.yaxis._major_tick_kw.get('gridOn', False)
            except:
                grid_on = any(line.get_visible() for line in ax.xaxis.get_gridlines())
            
            if grid_on == has_grid:
                self._log_result(True, f"Plot {'has' if has_grid else 'does not have'} grid",
                               custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"Plot {'should have' if has_grid else 'should not have'} grid",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        return all_passed
    
    def check_plot_line_style(self, expected_style: str, line_index: int = 0, fig_num: int = 1,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a line has the expected style (e.g., 'b-', 'r--', 'g:', 'b*', 'ro')."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        line = lines[line_index]
        
        color_codes = {'b': 'blue', 'g': 'green', 'r': 'red', 'c': 'cyan', 
                       'm': 'magenta', 'y': 'yellow', 'k': 'black', 'w': 'white'}
        linestyle_codes = {'-': '-', '--': '--', '-.': '-.', ':': ':'}
        marker_codes = {'.': '.', ',': ',', 'o': 'o', 'v': 'v', '^': '^', 
                       '<': '<', '>': '>', 's': 's', 'p': 'p', '*': '*', 
                       'h': 'h', '+': '+', 'x': 'x', 'D': 'D', 'd': 'd'}
        
        actual_color = line.get_color()
        actual_linestyle = line.get_linestyle()
        actual_marker = line.get_marker()
        
        remaining = expected_style
        expected_color = expected_linestyle = expected_marker = None
        
        if remaining and remaining[0] in color_codes:
            expected_color = color_codes[remaining[0]]
            remaining = remaining[1:]
        
        if remaining:
            if len(remaining) >= 2 and remaining[:2] in linestyle_codes:
                expected_linestyle = linestyle_codes[remaining[:2]]
                remaining = remaining[2:]
            elif remaining[0] in linestyle_codes:
                expected_linestyle = linestyle_codes[remaining[0]]
                remaining = remaining[1:]
            elif remaining[0] in marker_codes:
                expected_marker = marker_codes[remaining[0]]
                remaining = remaining[1:]
        
        if remaining and remaining[0] in marker_codes:
            expected_marker = marker_codes[remaining[0]]
        
        all_passed = True
        
        if expected_color:
            from matplotlib.colors import to_rgb, CSS4_COLORS
            try:
                if expected_color in CSS4_COLORS:
                    expected_rgb = to_rgb(CSS4_COLORS[expected_color])
                else:
                    expected_rgb = to_rgb(expected_color)
                actual_rgb = to_rgb(actual_color)
                
                if not all(abs(a - e) < 0.01 for a, e in zip(actual_rgb, expected_rgb)):
                    self._log_result(False, f"Line {line_index} color mismatch",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_passed = False
            except:
                pass
        
        if expected_linestyle:
            linestyle_names = {'-': 'solid', '--': 'dashed', '-.': 'dashdot', ':': 'dotted',
                             'solid': 'solid', 'dashed': 'dashed', 'dashdot': 'dashdot', 'dotted': 'dotted'}
            expected_ls_norm = linestyle_names.get(expected_linestyle, expected_linestyle)
            actual_ls_norm = linestyle_names.get(actual_linestyle, actual_linestyle)
            
            if expected_ls_norm != actual_ls_norm:
                self._log_result(False, f"Line {line_index} style is '{actual_linestyle}', expected '{expected_linestyle}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if expected_marker:
            if actual_marker != expected_marker and actual_marker not in ('None', None, ''):
                self._log_result(False, f"Line {line_index} marker is '{actual_marker}', expected '{expected_marker}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            elif actual_marker in ('None', None, ''):
                self._log_result(False, f"Line {line_index} has no marker, expected '{expected_marker}'",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
        
        if all_passed:
            self._log_result(True, f"Line {line_index} has correct style '{expected_style}'",
                           custom_pass_feedback=custom_pass_feedback)
        
        return all_passed
    
    def check_plot_has_line_style(self, expected_style: str, fig_num: int = 1,
                                  custom_pass_feedback: Optional[str] = None,
                                  custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if ANY line in the plot has the expected style."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if len(lines) == 0:
            self._log_result(False, "No lines found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        for i in range(len(lines)):
            old_results = self.test_results.copy()
            result = self.check_plot_line_style(expected_style, line_index=i, fig_num=fig_num)
            self.test_results = old_results
            
            if result:
                self._log_result(True, f"Found line with style '{expected_style}'",
                               custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, f"No line found with style '{expected_style}'",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_line_width(self, expected_width: float, line_index: int = 0, 
                              tolerance: float = 0.1, fig_num: int = 1,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a line has the expected line width."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_width = lines[line_index].get_linewidth()
        
        if abs(actual_width - expected_width) <= tolerance:
            self._log_result(True, f"Line {line_index} width is {actual_width}",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"Line {line_index} width is {actual_width}, expected {expected_width}",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_marker_size(self, expected_size: float, line_index: int = 0,
                               tolerance: float = 0.5, fig_num: int = 1,
                               custom_pass_feedback: Optional[str] = None,
                               custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a line's markers have the expected size."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        lines = ax.get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_size = lines[line_index].get_markersize()
        
        if abs(actual_size - expected_size) <= tolerance:
            self._log_result(True, f"Line {line_index} marker size is {actual_size}",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"Line {line_index} marker size is {actual_size}, expected {expected_size}",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def compare_plot_with_solution(self, solution_file: str, line_index: int = 0,
                                   check_color: bool = True, check_linestyle: bool = True,
                                   check_linewidth: bool = True, check_marker: bool = True,
                                   check_markersize: bool = True,
                                   linewidth_tolerance: float = 0.1,
                                   markersize_tolerance: float = 0.5, fig_num: int = 1,
                                   custom_pass_feedback: Optional[str] = None,
                                   custom_fail_feedback: Optional[str] = None) -> bool:
        """Compare plot line properties with a solution file."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        ax = fig.gca()
        student_lines = ax.get_lines()
        
        if line_index >= len(student_lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        student_line = student_lines[line_index]
        
        if not os.path.exists(solution_file):
            self._log_result(False, f"Solution file not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        try:
            plt.close('all')
            
            with open(solution_file, 'r', encoding='utf-8') as f:
                solution_content = f.read()
            
            safe_builtins = self._get_safe_builtins()
            solution_namespace = {'__builtins__': safe_builtins}
            
            def execute_solution():
                exec(solution_content, solution_namespace, solution_namespace)
            
            run_with_timeout(execute_solution, timeout=self.timeout)
            
            sol_figs = plt.get_fignums()
            if not sol_figs:
                self._log_result(False, "Solution did not create a plot",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            
            sol_fig = plt.figure(sol_figs[0])
            sol_lines = sol_fig.gca().get_lines()
            
            if line_index >= len(sol_lines):
                self._log_result(False, f"Line {line_index} not found in solution",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            
            sol_line = sol_lines[line_index]
            all_passed = True
            
            if check_color:
                from matplotlib.colors import to_rgb
                try:
                    student_rgb = to_rgb(student_line.get_color())
                    sol_rgb = to_rgb(sol_line.get_color())
                    if not all(abs(s - e) < 0.01 for s, e in zip(student_rgb, sol_rgb)):
                        self._log_result(False, "Line color differs from solution",
                                       custom_fail_feedback=custom_fail_feedback)
                        all_passed = False
                except:
                    pass
            
            if check_linestyle and student_line.get_linestyle() != sol_line.get_linestyle():
                self._log_result(False, "Line style differs from solution",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            
            if check_linewidth:
                if abs(student_line.get_linewidth() - sol_line.get_linewidth()) > linewidth_tolerance:
                    self._log_result(False, f"Line width differs from solution",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_passed = False
            
            if check_marker and student_line.get_marker() != sol_line.get_marker():
                self._log_result(False, "Marker style differs from solution",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            
            if check_markersize:
                if abs(student_line.get_markersize() - sol_line.get_markersize()) > markersize_tolerance:
                    self._log_result(False, "Marker size differs from solution",
                                   custom_fail_feedback=custom_fail_feedback)
                    all_passed = False
            
            if all_passed:
                self._log_result(True, f"Line {line_index} properties match solution",
                               custom_pass_feedback=custom_pass_feedback)
            
            return all_passed
            
        except Exception as e:
            self._log_result(False, f"Error comparing with solution: {str(e)}",
                           custom_fail_feedback=custom_fail_feedback)
            return False
    
    def check_plot_data_length(self, min_length: Optional[int] = None, max_length: Optional[int] = None,
                                exact_length: Optional[int] = None, line_index: int = 0, fig_num: int = 1,
                                custom_pass_feedback: Optional[str] = None,
                                custom_fail_feedback: Optional[str] = None) -> bool:
        """Check plot data length."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        fig = plt.figure(fig_num)
        lines = fig.gca().get_lines()
        
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        actual_length = len(lines[line_index].get_xdata())
        all_passed = True
        
        if exact_length is not None:
            if actual_length != exact_length:
                self._log_result(False, f"Line has {actual_length} points, expected {exact_length}",
                               custom_fail_feedback=custom_fail_feedback)
                return False
            self._log_result(True, f"Line has exactly {exact_length} data points",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        
        if min_length is not None:
            if actual_length < min_length:
                self._log_result(False, f"Line has {actual_length} points, minimum is {min_length}",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"Line has at least {min_length} data points",
                               custom_pass_feedback=custom_pass_feedback)
        
        if max_length is not None:
            if actual_length > max_length:
                self._log_result(False, f"Line has {actual_length} points, maximum is {max_length}",
                               custom_fail_feedback=custom_fail_feedback)
                all_passed = False
            else:
                self._log_result(True, f"Line has at most {max_length} data points",
                               custom_pass_feedback=custom_pass_feedback)
        
        return all_passed
    
    def check_multiple_lines(self, min_lines: int = 1, fig_num: int = 1,
                             custom_pass_feedback: Optional[str] = None,
                             custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if plot has at least min_lines lines."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        lines = plt.figure(fig_num).gca().get_lines()
        
        if len(lines) >= min_lines:
            self._log_result(True, f"Plot has {len(lines)} lines (minimum: {min_lines})",
                           custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"Plot has {len(lines)} lines, expected at least {min_lines}",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_function_any_line(self, function: Callable, min_length: int = 1, 
                                tolerance: float = 1e-6, fig_num: int = 1,
                                custom_pass_feedback: Optional[str] = None,
                                custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if any line in the plot matches a function."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        import numpy as np
        lines = plt.figure(fig_num).gca().get_lines()
        
        for i, line in enumerate(lines):
            x, y = line.get_xdata(), line.get_ydata()
            if len(x) < min_length:
                continue
            try:
                expected_y = function(np.array(x))
                if np.allclose(y, expected_y, atol=tolerance):
                    self._log_result(True, f"Line {i} matches expected function",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
            except:
                continue
        
        self._log_result(False, f"No line matches expected function",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_plot_color(self, expected_color: str, line_index: int = 0, fig_num: int = 1,
                         custom_pass_feedback: Optional[str] = None,
                         custom_fail_feedback: Optional[str] = None) -> bool:
        """Check plot color."""
        if fig_num not in plt.get_fignums():
            self._log_result(False, f"Figure {fig_num} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        lines = plt.figure(fig_num).gca().get_lines()
        if line_index >= len(lines):
            self._log_result(False, f"Line {line_index} not found", custom_fail_feedback=custom_fail_feedback)
            return False
        
        from matplotlib.colors import to_rgb
        try:
            expected_rgb = to_rgb(expected_color)
            actual_rgb = to_rgb(lines[line_index].get_color())
            
            if all(abs(a - e) < 0.01 for a, e in zip(actual_rgb, expected_rgb)):
                self._log_result(True, f"Line color is {expected_color}",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            self._log_result(False, f"Line color mismatch", custom_fail_feedback=custom_fail_feedback)
            return False
        except:
            self._log_result(False, "Could not compare colors", custom_fail_feedback=custom_fail_feedback)
            return False
    
    def get_plot_data(self, line_index: int = 0, fig_num: int = 1) -> Optional[Dict[str, Any]]:
        """Get plot data."""
        if fig_num not in plt.get_fignums():
            return None
        lines = plt.figure(fig_num).gca().get_lines()
        if line_index >= len(lines):
            return None
        line = lines[line_index]
        return {
            'x': line.get_xdata(), 'y': line.get_ydata(),
            'color': line.get_color(), 'linestyle': line.get_linestyle(),
            'linewidth': line.get_linewidth(), 'marker': line.get_marker(),
            'markersize': line.get_markersize(), 'label': line.get_label()
        }
    
    # ======================== CODE PATTERN CHECKING ========================
    
    def check_code_contains(self, phrase: str, case_sensitive: bool = True,
                            custom_pass_feedback: Optional[str] = None,
                            custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if code contains a phrase."""
        if self._content is None:
            self._log_result(False, "No code content available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        search_content = self._content
        search_phrase = phrase
        
        if not case_sensitive:
            search_content = search_content.lower()
            search_phrase = search_phrase.lower()
        
        if search_phrase in search_content:
            self._log_result(True, f"Code contains '{phrase}'", custom_pass_feedback=custom_pass_feedback)
            return True
        self._log_result(False, f"Code does not contain '{phrase}'", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_operator_used(self, operator: str,
                            custom_pass_feedback: Optional[str] = None,
                            custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if an operator is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        operator_map = {
            '+=': ast.Add, '-=': ast.Sub, '*=': ast.Mult, '/=': ast.Div,
            '//=': ast.FloorDiv, '%=': ast.Mod, '**=': ast.Pow,
            '+': ast.Add, '-': ast.Sub, '*': ast.Mult, '/': ast.Div,
            '//': ast.FloorDiv, '%': ast.Mod, '**': ast.Pow,
            '==': ast.Eq, '!=': ast.NotEq, '<': ast.Lt, '<=': ast.LtE,
            '>': ast.Gt, '>=': ast.GtE, 'and': ast.And, 'or': ast.Or, 'not': ast.Not,
        }
        
        if operator not in operator_map:
            return self.check_code_contains(operator, custom_pass_feedback=custom_pass_feedback,
                                           custom_fail_feedback=custom_fail_feedback)
        
        target_op = operator_map[operator]
        
        for node in ast.walk(self._ast_tree):
            if operator in ['+=', '-=', '*=', '/=', '//=', '%=', '**=']:
                if isinstance(node, ast.AugAssign) and isinstance(node.op, target_op):
                    self._log_result(True, f"Operator '{operator}' is used",
                                   custom_pass_feedback=custom_pass_feedback)
                    return True
            elif isinstance(node, ast.BinOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, target_op):
                        self._log_result(True, f"Operator '{operator}' is used",
                                       custom_pass_feedback=custom_pass_feedback)
                        return True
            elif isinstance(node, ast.BoolOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used",
                               custom_pass_feedback=custom_pass_feedback)
                return True
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, target_op):
                self._log_result(True, f"Operator '{operator}' is used",
                               custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, f"Operator '{operator}' is not used",
                       custom_fail_feedback=custom_fail_feedback)
        return False
    
    # ======================== CONTROL STRUCTURE CHECKING ========================
    
    def check_for_loop_used(self, custom_pass_feedback: Optional[str] = None,
                            custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a for loop is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.For):
                self._log_result(True, "For loop is used", custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, "For loop is not used", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_while_loop_used(self, custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if a while loop is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.While):
                self._log_result(True, "While loop is used", custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, "While loop is not used", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def check_if_statement_used(self, custom_pass_feedback: Optional[str] = None,
                                custom_fail_feedback: Optional[str] = None) -> bool:
        """Check if an if statement is used."""
        if self._ast_tree is None:
            self._log_result(False, "AST not available", custom_fail_feedback=custom_fail_feedback)
            return False
        
        for node in ast.walk(self._ast_tree):
            if isinstance(node, ast.If):
                self._log_result(True, "If statement is used", custom_pass_feedback=custom_pass_feedback)
                return True
        
        self._log_result(False, "If statement is not used", custom_fail_feedback=custom_fail_feedback)
        return False
    
    def count_loop_iterations(self, loop_variable: str, expected_count: Optional[int] = None, 
                              tolerance: int = 0,
                              custom_pass_feedback: Optional[str] = None,
                              custom_fail_feedback: Optional[str] = None) -> Optional[int]:
        """Count loop iterations by checking a counter variable."""
        if not self._execution_successful:
            self._log_result(False, "Cannot count iterations: script not executed",
                           custom_fail_feedback=custom_fail_feedback)
            return None
        
        if loop_variable not in self.captured_vars:
            self._log_result(False, f"Loop counter '{loop_variable}' not found",
                           custom_fail_feedback=custom_fail_feedback)
            return None
        
        actual_count = self.captured_vars[loop_variable]
        
        if not isinstance(actual_count, (int, float)):
            self._log_result(False, f"Variable '{loop_variable}' is not a number",
                           custom_fail_feedback=custom_fail_feedback)
            return None
        
        actual_count = int(actual_count)
        
        if expected_count is not None:
            if abs(actual_count - expected_count) <= tolerance:
                self._log_result(True, f"Loop ran {actual_count} times",
                               custom_pass_feedback=custom_pass_feedback)
            else:
                self._log_result(False, f"Loop ran {actual_count} times, expected {expected_count}",
                               custom_fail_feedback=custom_fail_feedback)
        else:
            self._log_result(True, f"Loop counter '{loop_variable}' = {actual_count}",
                           custom_pass_feedback=custom_pass_feedback)
        
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