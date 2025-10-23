import os
import sys

class AutoGraderScript:
    """
    A utility class designed to check the content of an output file 
    for specific variables, values, and existence checks.
    """
    def __init__(self, filepath: str):
        """
        Initializes the checker by opening the file and reading its content 
        into memory for all subsequent checks.
        """
        self.filepath = filepath
        self._content = None
        self.captured_vars = {} # New attribute to store results of execution
        self._open_and_read() 

    def _open_and_read(self) -> bool:
        """
        Internal method to handle opening the file, reading all contents, 
        and closing the file immediately.
        """
        if not os.path.exists(self.filepath):
            print(f"ERROR: File not found at path: {self.filepath}", file=sys.stderr)
            return False
        
        try:
            # Read all content into a single string
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self._content = f.read()
            print(f"INFO: Successfully loaded content from {self.filepath}")
            return True
        except Exception as e:
            print(f"ERROR: Could not read file content: {e}", file=sys.stderr)
            self.close_file() # Ensure file is closed if an error occurred during read
            return False

    def close_file(self):
        """
        A placeholder method to conceptually 'close' the resource. 
        In this design, the file is already closed after reading in init.
        """
        print(f"INFO: File resource for {self.filepath} is closed (content remains loaded).")

    def execute_code_and_capture_vars(self, variables_to_check: list) -> bool:
        """
        Executes the student's Python code (stored in self._content) in an 
        isolated environment and captures the final values of specified variables 
        into self.captured_vars.

        Args:
            variables_to_check: A list of variable names (strings) to extract.

        Returns:
            True if execution was successful, False otherwise.
        """
        if self._content is None:
            print("ERROR: Cannot execute, file content failed to load.", file=sys.stderr)
            return False
        
        # 1. Create a safe, isolated namespace for execution
        execution_namespace = {}
        
        try:
            # 2. Execute the code using exec()
            # The code runs and the resulting variables are stored in execution_namespace
            exec(self._content, {}, execution_namespace)

            # 3. Extract and store the values of the required variables
            self.captured_vars = {}
            for var in variables_to_check:
                if var in execution_namespace:
                    self.captured_vars[var] = execution_namespace[var]
                else:
                    self.captured_vars[var] = None # Variable was not defined
            
            print("INFO: Code execution successful. Variables captured.")
            return True

        except Exception as e:
            print(f"ERROR: Failed to execute student code: {e}", file=sys.stderr)
            self.captured_vars = {}
            return False

    def check_variable_exists(self, var_name: str) -> bool:
        """
        Checks if a variable name string is present anywhere in the file content.
        
        Args:
            var_name: The name of the variable to search for (case sensitive).
            
        Returns:
            True if the variable name is found, False otherwise.
        """
        if self._content is None:
            print("WARNING: Cannot check, file content is empty or failed to load.")
            return False
        
        if var_name in self._content:
            print(f"PASS: Variable name '{var_name}' found.")
            return True
        else:
            print(f"FAIL: Variable name '{var_name}' NOT found.")
            return False

    def check_variable_value(self, var_name: str, expected_value: str, is_approximate: bool = False, tolerance: float = 0.001) -> bool:
        """
        Checks if a variable assignment (like 'var = value') is present with the expected value.
        
        Args:
            var_name: The variable name to look for (e.g., 'final_score').
            expected_value: The exact string or number to expect after the assignment.
            is_approximate: If True, compares numeric values within a tolerance (for floats).
            tolerance: The allowed difference for approximate comparison.

        Returns:
            True if the assignment is found with the expected value, False otherwise.
        """
        if self._content is None:
            return False

        # Create a simple pattern to find the assignment statement (e.g., 'variable = 42')
        # We handle various spacing around the '='
        search_pattern = f"{var_name.strip()}"

        # Find all lines containing the variable name
        for line in self._content.splitlines():
            if search_pattern in line:
                
                # Assume the line is an assignment and try to parse the value part
                try:
                    # Split based on '=' and take the right side, then clean up spaces/quotes
                    value_part = line.split('=', 1)[1].strip().strip("'\"")
                    
                    if is_approximate:
                        actual_float = float(value_part)
                        expected_float = float(expected_value)
                        
                        if abs(actual_float - expected_float) <= tolerance:
                            print(f"PASS: Value of '{var_name}' is approximately {expected_value} (Actual: {actual_float}).")
                            return True
                    else:
                        # Direct string comparison (case-sensitive)
                        if value_part == str(expected_value).strip():
                            print(f"PASS: Value of '{var_name}' equals '{expected_value}'.")
                            return True
                except (IndexError, ValueError):
                    # Line didn't contain an assignment or value wasn't a valid number/string
                    continue
        
        print(f"FAIL: Could not find '{var_name}' assigned to expected value '{expected_value}'.")
        return False  