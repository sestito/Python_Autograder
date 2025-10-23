from AutoGraderScript import AutoGraderScript

STUDENT_CODE_FILE = "D:\GitHub_Repositories\Python_Autograder\student_code_example.py"
REQUIRED_VARS = ['x', 'y', 'z', 'greeting', 'area']

# 1. Instantiate the Checker with the student's code file
print("--- Initializing Checker with Student Code ---")
checker = AutoGraderScript(STUDENT_CODE_FILE)

# 2. Execute the code and capture the final variable state
print("\n--- Step 1: Execute Code and Capture Variables ---")
success = checker.execute_code_and_capture_vars(REQUIRED_VARS)

if success:
    print("\n--- Step 2: Verification of Calculated Values ---")
    print(f"Captured variables: {checker.captured_vars}")

    # Check 1: Verify the calculated integer value (z)
    expected_z = 7
    actual_z = checker.captured_vars.get('z')
    if actual_z == expected_z:
        print(f"PASS: Variable 'z' has the correct calculated value: {expected_z}.")
    else:
        print(f"FAIL: Variable 'z' is {actual_z}, expected {expected_z}.")

    # Check 2: Verify the calculated float value (area) with tolerance
    expected_area = 78.5375
    tolerance = 0.01
    actual_area = checker.captured_vars.get('area')

    if actual_area is not None and abs(actual_area - expected_area) <= tolerance:
        print(f"PASS: Variable 'area' is approximately {expected_area} (Actual: {actual_area}).")
    else:
        print(f"FAIL: Variable 'area' is {actual_area}, expected close to {expected_area}.")

    # Check 3: Verify variable existence (checks internal self.captured_vars)
    if 'greeting' in checker.captured_vars and checker.captured_vars['greeting'] is not None:
        print("PASS: Variable 'greeting' was successfully defined and captured.")
    else:
        print("FAIL: Variable 'greeting' was not defined or captured.")

else:
    print("FATAL: Code execution failed. Cannot proceed with variable checks.")