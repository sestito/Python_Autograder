# -*- coding: utf-8 -*-
"""
Assignment Editor GUI for AutoGrader
Provides an easy interface to create and edit assignments and tests.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
import subprocess
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import configparser

# List of bundled resource files that ship with the executable
BUNDLED_FILES = ['autograder.py', 'autograder-gui-app.py']

# Temporary directory for extracted files (cleaned up on exit)
_temp_extract_dir = None

def get_temp_extract_dir():
    """
    Get or create a temporary directory for extracting bundled files.
    This directory is cleaned up when the application exits.
    """
    global _temp_extract_dir
    if _temp_extract_dir is None or not os.path.exists(_temp_extract_dir):
        import tempfile
        import atexit
        _temp_extract_dir = tempfile.mkdtemp(prefix='autograder_editor_')
        atexit.register(cleanup_temp_extract_dir)
    return _temp_extract_dir

def cleanup_temp_extract_dir():
    """Clean up the temporary extraction directory."""
    global _temp_extract_dir
    if _temp_extract_dir and os.path.exists(_temp_extract_dir):
        try:
            shutil.rmtree(_temp_extract_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {e}")

def get_subprocess_flags():
    """Get platform-specific subprocess flags to hide console windows."""
    if sys.platform == 'win32':
        # On Windows, prevent console window from appearing
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}

def get_python_executable():
    """
    Get the path to the Python interpreter.
    When running as a PyInstaller bundle, sys.executable points to the bundled exe,
    so we need to find the actual Python interpreter on the system.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - need to find Python
        import shutil
        
        # Try common Python executable names
        for python_name in ['python3', 'python', 'python.exe']:
            python_path = shutil.which(python_name)
            if python_path:
                return python_path
        
        # Fallback: try some common locations
        common_paths = [
            '/usr/bin/python3',
            '/usr/bin/python',
            '/usr/local/bin/python3',
            '/usr/local/bin/python',
        ]
        if sys.platform == 'win32':
            common_paths = [
                os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python312\python.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python311\python.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python310\python.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python39\python.exe'),
                r'C:\Python312\python.exe',
                r'C:\Python311\python.exe',
                r'C:\Python310\python.exe',
                r'C:\Python39\python.exe',
            ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None  # Python not found
    else:
        # Running as script - use the current interpreter
        return sys.executable

def get_bundled_resource_path(filename):
    """
    Get the path to a bundled resource file.
    When running as a PyInstaller bundle, files are in sys._MEIPASS.
    When running as a script, files are in the script directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        bundle_dir = sys._MEIPASS
    else:
        # Running as script
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(bundle_dir, 'bundled_files', filename)

def extract_bundled_file(filename, target_dir=None):
    """
    Extract a bundled file to the target directory.
    When running as frozen executable and no target_dir specified, uses temp directory.
    Returns the path to the extracted file, or None if extraction failed.
    """
    if target_dir is None:
        if getattr(sys, 'frozen', False):
            # Use temp directory when running as executable
            target_dir = get_temp_extract_dir()
        else:
            # Use current directory when running as script
            target_dir = os.getcwd()
    
    target_path = os.path.join(target_dir, filename)
    
    # If file already exists in target, return it
    if os.path.exists(target_path):
        return target_path
    
    # Get path to bundled file
    bundled_path = get_bundled_resource_path(filename)
    
    if os.path.exists(bundled_path):
        try:
            shutil.copy2(bundled_path, target_path)
            return target_path
        except Exception as e:
            print(f"Error extracting {filename}: {e}")
            return None
    
    return None

def ensure_bundled_files_available(filenames, target_dir=None):
    """
    Ensure that the specified bundled files are available in the target directory.
    Returns a tuple of (success, missing_files).
    """
    if target_dir is None:
        target_dir = os.getcwd()
    
    missing = []
    for filename in filenames:
        target_path = os.path.join(target_dir, filename)
        
        # Already exists in target directory
        if os.path.exists(target_path):
            continue
        
        # Try to extract from bundle
        extracted = extract_bundled_file(filename, target_dir)
        if not extracted:
            missing.append(filename)
    
    return (len(missing) == 0, missing)

SETTINGS_FILE = 'assignment_editor_settings.json'

def friendly_name(s):
    """Convert snake_case to Title Case."""
    if not s:
        return ''
    return s.replace('_', ' ').title()

def clean_value(value):
    """Clean a value, converting nan to empty string."""
    if pd.isna(value):
        return ''
    s = str(value)
    if s.lower() == 'nan':
        return ''
    return s

def make_relative_path(filepath, base_dir=None):
    """Convert absolute path to relative, always using forward slashes."""
    if not filepath:
        return filepath
    if base_dir is None:
        base_dir = os.getcwd()
    try:
        rel = os.path.relpath(filepath, base_dir)
        # Always use forward slashes for cross-platform compatibility
        return rel.replace('\\', '/')
    except ValueError:
        return filepath.replace('\\', '/')

BOOLEAN_FIELDS = {'match_any_prefix', 'case_sensitive', 'order_matters', 'require_same_type',
                  'has_legend', 'has_grid', 'check_color', 'check_linestyle', 
                  'check_linewidth', 'check_marker', 'check_markersize'}

TEST_TYPE_DEFINITIONS = {
    'variable_value': {
        'display_name': 'Check Variable Value',
        'required': ['variable_name', 'expected_value'],
        'optional': ['description', 'tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Verifies that a variable in the student code equals an expected value. For numeric values, uses tolerance for comparison. Works with numbers, strings, lists, and other Python types.',
        'example': "variable_name: total\nexpected_value: 42\ntolerance: 0.01",
        'key_param': 'variable_name'
    },
    'variable_type': {
        'display_name': 'Check Variable Type',
        'required': ['variable_name', 'expected_value'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that a variable has the correct Python type. Useful for ensuring students use the right data structures. Valid types: int, float, str, list, dict, tuple, set, bool.',
        'example': "variable_name: my_data\nexpected_value: list",
        'key_param': 'variable_name'
    },
    'function_exists': {
        'display_name': 'Check Function Exists',
        'required': ['function_name'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that a function with the specified name is defined in the student code. Checks the AST (code structure), so works even if code has runtime errors.',
        'example': "function_name: calculate_average",
        'key_param': 'function_name'
    },
    'function_called': {
        'display_name': 'Check Function Called',
        'required': ['function_name'],
        'optional': ['description', 'match_any_prefix'],
        'defaults': {'match_any_prefix': ''},
        'help': 'Verifies that a function is called somewhere in the student code. Use match_any_prefix=true to match any module prefix (e.g., "mean" matches np.mean, numpy.mean, statistics.mean).',
        'example': "function_name: np.mean\nmatch_any_prefix: false",
        'key_param': 'function_name'
    },
    'function_not_called': {
        'display_name': 'Check Function NOT Called',
        'required': ['function_name'],
        'optional': ['description', 'match_any_prefix'],
        'defaults': {'match_any_prefix': ''},
        'help': 'Verifies that a function is NOT used in the student code. Useful for ensuring students implement algorithms manually instead of using built-in functions.',
        'example': "function_name: sorted\nmatch_any_prefix: true",
        'key_param': 'function_name'
    },
    'compare_solution': {
        'display_name': 'Compare with Solution File',
        'required': ['solution_file', 'variables_to_compare'],
        'optional': ['description', 'tolerance', 'require_same_type'],
        'defaults': {'tolerance': '1e-6', 'require_same_type': ''},
        'help': 'Executes a solution file and compares specified variables between student and solution. Most versatile test - handles any variable types including arrays and plots.',
        'example': "solution_file: solutions/hw1_sol.py\nvariables_to_compare: x, y, result",
        'file_field': 'solution_file',
        'key_param': 'solution_file'
    },
    'test_function_solution': {
        'display_name': 'Test Function with Solution',
        'required': ['function_name', 'solution_file'],
        'optional': ['description', 'tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Tests a student function by calling it with specified inputs and comparing results to the same function in a solution file. Click "Edit Test Inputs" to define test cases.',
        'example': "function_name: add_numbers\nsolution_file: solutions/math_sol.py",
        'file_field': 'solution_file',
        'key_param': 'function_name',
        'has_test_inputs': True
    },
    'test_function_solution_advanced': {
        'display_name': 'Test Function (with Kwargs)',
        'required': ['function_name', 'solution_file'],
        'optional': ['description', 'tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Like "Test Function with Solution" but also supports keyword arguments. Use this when the function has optional parameters that need testing.',
        'example': "function_name: format_data\nsolution_file: solutions/utils_sol.py",
        'file_field': 'solution_file',
        'key_param': 'function_name',
        'has_test_inputs': True,
        'has_kwargs': True
    },
    'for_loop_used': {
        'display_name': 'Check For Loop Used',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the student code contains at least one "for" loop. Checks the code structure, not execution.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'while_loop_used': {
        'display_name': 'Check While Loop Used',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the student code contains at least one "while" loop. Checks the code structure, not execution.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'if_statement_used': {
        'display_name': 'Check If Statement Used',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the student code contains at least one "if" statement. Checks the code structure, not execution.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'operator_used': {
        'display_name': 'Check Operator Used',
        'required': ['operator'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that a specific operator is used in the code. Supports: +, -, *, /, //, %, **, +=, -=, *=, /=, ==, !=, <, <=, >, >=, and, or, not.',
        'example': "operator: +=",
        'key_param': 'operator'
    },
    'code_contains': {
        'display_name': 'Check Code Contains Text',
        'required': ['phrase'],
        'optional': ['description', 'case_sensitive'],
        'defaults': {'case_sensitive': ''},
        'help': 'Searches the student code for a specific text phrase. Useful for checking imports, comments, or specific syntax patterns.',
        'example': "phrase: import numpy\ncase_sensitive: false",
        'key_param': 'phrase'
    },
    'loop_iterations': {
        'display_name': 'Check Loop Iterations',
        'required': ['loop_variable'],
        'optional': ['description', 'expected_count', 'tolerance'],
        'defaults': {'tolerance': '0'},
        'help': 'Checks the value of a counter variable after code execution. Students must define a variable that tracks iteration count. If expected_count is set, verifies it matches.',
        'example': "loop_variable: iteration_count\nexpected_count: 100",
        'key_param': 'loop_variable'
    },
    'list_equals': {
        'display_name': 'Check List Equals',
        'required': ['variable_name', 'expected_list'],
        'optional': ['description', 'order_matters', 'tolerance'],
        'defaults': {'order_matters': '', 'tolerance': '1e-6'},
        'help': 'Verifies that a list variable matches expected values. Set order_matters=false to ignore element order (compares as sets).',
        'example': "variable_name: results\nexpected_list: [1, 2, 3, 4, 5]\norder_matters: true",
        'key_param': 'variable_name'
    },
    'array_equals': {
        'display_name': 'Check Array Equals',
        'required': ['variable_name', 'expected_array'],
        'optional': ['description', 'tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Verifies that a NumPy array matches expected values within tolerance. Automatically converts lists to arrays for comparison. Checks both shape and values.',
        'example': "variable_name: data\nexpected_array: [1.0, 2.0, 3.0]\ntolerance: 0.001",
        'key_param': 'variable_name'
    },
    'array_size': {
        'display_name': 'Check Array/List Size',
        'required': ['variable_name'],
        'optional': ['description', 'min_size', 'max_size', 'exact_size'],
        'defaults': {},
        'help': 'Verifies the size/length of an array or list. Can check for minimum size, maximum size, exact size, or any combination.',
        'example': "variable_name: x_values\nmin_size: 100\nmax_size: 1000",
        'key_param': 'variable_name'
    },
    'array_values_in_range': {
        'display_name': 'Check Array Values in Range',
        'required': ['variable_name'],
        'optional': ['description', 'min_value', 'max_value'],
        'defaults': {},
        'help': 'Verifies that ALL values in an array/list fall within a specified range. Useful for checking normalized data, probabilities, or bounded values.',
        'example': "variable_name: probabilities\nmin_value: 0\nmax_value: 1",
        'key_param': 'variable_name'
    },
    'check_relationship': {
        'display_name': 'Check Variable Relationship',
        'required': ['var1_name', 'var2_name', 'relationship'],
        'optional': ['description', 'tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Verifies that var2 equals a mathematical function of var1. The relationship is a lambda function. Example: check if y = sin(x).',
        'example': "var1_name: x\nvar2_name: y\nrelationship: lambda x: np.sin(x)\ntolerance: 0.001",
        'key_param': 'var1_name'
    },
    'plot_created': {
        'display_name': 'Check Plot Created',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the student code created at least one matplotlib figure. Basic check before testing plot properties.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'plot_properties': {
        'display_name': 'Check Plot Properties',
        'required': [],
        'optional': ['description', 'title', 'xlabel', 'ylabel', 'has_legend', 'has_grid'],
        'defaults': {},
        'help': 'Verifies plot labels, title, legend, and grid settings. Leave fields blank to skip checking them. String comparisons are exact matches.',
        'example': "title: Sales Data\nxlabel: Month\nylabel: Revenue ($)\nhas_legend: true\nhas_grid: true",
        'key_param': 'title'
    },
    'plot_has_xlabel': {
        'display_name': 'Check Plot Has X Label',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the plot has ANY x-axis label set (does not check the specific text). Use plot_properties to check exact label text.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'plot_has_ylabel': {
        'display_name': 'Check Plot Has Y Label',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the plot has ANY y-axis label set (does not check the specific text). Use plot_properties to check exact label text.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'plot_has_title': {
        'display_name': 'Check Plot Has Title',
        'required': [],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the plot has ANY title set (does not check the specific text). Use plot_properties to check exact title text.',
        'example': "(no parameters needed)",
        'key_param': None
    },
    'plot_data_length': {
        'display_name': 'Check Plot Data Length',
        'required': [],
        'optional': ['description', 'min_length', 'max_length', 'exact_length', 'line_index'],
        'defaults': {'line_index': '0'},
        'help': 'Verifies the number of data points in a plot line. line_index specifies which line (0=first). Can check min, max, or exact count.',
        'example': "min_length: 50\nline_index: 0",
        'key_param': 'min_length'
    },
    'plot_line_style': {
        'display_name': 'Check Plot Line Style',
        'required': ['expected_style'],
        'optional': ['description', 'line_index'],
        'defaults': {'line_index': '0'},
        'help': 'Verifies the line style of a specific line in the plot. Common styles: "-" (solid), "--" (dashed), ":" (dotted), "-." (dash-dot).',
        'example': "expected_style: --\nline_index: 0",
        'key_param': 'expected_style'
    },
    'plot_has_line_style': {
        'display_name': 'Check Any Line Has Style',
        'required': ['expected_style'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that ANY line in the plot has the specified style. Useful when you do not care which line has the style.',
        'example': "expected_style: --",
        'key_param': 'expected_style'
    },
    'check_multiple_lines': {
        'display_name': 'Check Minimum Lines in Plot',
        'required': ['min_lines'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the plot contains at least the specified number of lines. Useful for multi-line plots.',
        'example': "min_lines: 3",
        'key_param': 'min_lines'
    },
    'check_exact_lines': {
        'display_name': 'Check Exact Lines in Plot',
        'required': ['exact_lines'],
        'optional': ['description'],
        'defaults': {},
        'help': 'Verifies that the plot contains exactly the specified number of lines.',
        'example': "exact_lines: 2",
        'key_param': 'exact_lines'
    },
    'compare_plot_solution': {
        'display_name': 'Compare Plot with Solution',
        'required': ['solution_file'],
        'optional': ['description', 'line_index', 'tolerance', 'check_color', 'check_linestyle', 'check_linewidth', 'check_marker', 'check_markersize'],
        'defaults': {'line_index': '0', 'tolerance': '1e-6'},
        'help': 'Compares plot data (x, y values) with a solution file. Optionally checks visual properties like color, line style, width, and markers.',
        'example': "solution_file: solutions/plot_sol.py\nline_index: 0\ncheck_color: true",
        'file_field': 'solution_file',
        'key_param': 'solution_file'
    },
    'check_function_any_line': {
        'display_name': 'Check Plot Matches Function',
        'required': ['function'],
        'optional': ['description', 'min_length', 'tolerance'],
        'defaults': {'min_length': '1', 'tolerance': '1e-6'},
        'help': 'Verifies that ANY line in the plot matches y = f(x) for the given function. The function should be a lambda that takes x values and returns expected y values.',
        'example': "function: lambda x: np.sin(2*x)\nmin_length: 50\ntolerance: 0.01",
        'key_param': 'function'
    },
}

DISPLAY_TO_INTERNAL = {v['display_name']: k for k, v in TEST_TYPE_DEFINITIONS.items()}

def get_display_names_sorted():
    return sorted([v['display_name'] for v in TEST_TYPE_DEFINITIONS.values()])


class TestInputsDialog(tk.Toplevel):
    def __init__(self, parent, test_inputs_str='', has_kwargs=False):
        super().__init__(parent)
        self.title("Edit Test Inputs")
        self.geometry("850x650")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.has_kwargs = has_kwargs
        self.input_sets = []
        self.parse_existing_inputs(test_inputs_str)
        self.create_widgets()
        self.refresh_display()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def parse_existing_inputs(self, s):
        if not s or s.lower() == 'nan' or not s.strip():
            self.input_sets = [{'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}}]
            return
        try:
            import ast
            inputs_list = ast.literal_eval(s)
            for inp in inputs_list:
                args_list = []
                for arg in inp.get('args', []):
                    is_numpy = isinstance(arg, str) and arg.startswith('np.array(')
                    if is_numpy:
                        arg = arg[9:-1]
                    args_list.append({'value': str(arg), 'is_numpy': is_numpy})
                kwargs_dict = {}
                for k, v in inp.get('kwargs', {}).items():
                    is_numpy = isinstance(v, str) and v.startswith('np.array(')
                    if is_numpy:
                        v = v[9:-1]
                    kwargs_dict[k] = {'value': str(v), 'is_numpy': is_numpy}
                if not args_list:
                    args_list = [{'value': '', 'is_numpy': False}]
                self.input_sets.append({'args': args_list, 'kwargs': kwargs_dict})
            if not self.input_sets:
                self.input_sets = [{'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}}]
        except:
            self.input_sets = [{'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}}]

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        info = ttk.LabelFrame(main, text="Instructions & Examples", padding="5")
        info.pack(fill=tk.X, pady=5)
        txt = """Each input set calls the function once. Examples:
  Numbers: 5, 3.14    Strings: 'hello' (with quotes)    Lists: [1, 2, 3]
  Check 'numpy array' to wrap value as np.array([1, 2, 3])"""
        ttk.Label(info, text=txt, justify=tk.LEFT).pack(anchor=tk.W)
        
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.canvas = tk.Canvas(canvas_frame)
        sb = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.inputs_frame = ttk.Frame(self.canvas)
        self.inputs_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inputs_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(main, text="+ Add Input Set", command=self.add_input_set).pack(pady=10)
        
        bf = ttk.Frame(main)
        bf.pack(fill=tk.X, pady=10)
        ttk.Button(bf, text="OK", command=self.ok, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text="Cancel", command=self.cancel, width=10).pack(side=tk.RIGHT, padx=5)

    def refresh_display(self):
        for w in self.inputs_frame.winfo_children():
            w.destroy()
        for i, inp_set in enumerate(self.input_sets):
            self.create_input_set_widget(i, inp_set)

    def create_input_set_widget(self, idx, inp_set):
        frame = ttk.LabelFrame(self.inputs_frame, text=f"Input Set {idx+1}", padding="5")
        frame.pack(fill=tk.X, pady=5, padx=5)
        if len(self.input_sets) > 1:
            ttk.Button(frame, text="Remove Set", command=lambda: self.remove_input_set(idx)).pack(anchor=tk.E)
        
        args_f = ttk.LabelFrame(frame, text="Arguments", padding="5")
        args_f.pack(fill=tk.X, pady=5)
        for j, arg in enumerate(inp_set['args']):
            self.create_arg_widget(args_f, idx, j, arg)
        ttk.Button(args_f, text="+ Add Argument", command=lambda i=idx: self.add_argument(i)).pack(pady=5)
        
        if self.has_kwargs:
            kw_f = ttk.LabelFrame(frame, text="Keyword Arguments", padding="5")
            kw_f.pack(fill=tk.X, pady=5)
            for name, kwarg in inp_set['kwargs'].items():
                self.create_kwarg_widget(kw_f, idx, name, kwarg)
            add_f = ttk.Frame(kw_f)
            add_f.pack(fill=tk.X, pady=5)
            kw_var = tk.StringVar()
            ttk.Label(add_f, text="Name:").pack(side=tk.LEFT)
            ttk.Entry(add_f, textvariable=kw_var, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(add_f, text="+ Add Kwarg", command=lambda i=idx, v=kw_var: self.add_kwarg(i, v)).pack(side=tk.LEFT)

    def create_arg_widget(self, parent, si, ai, arg):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text=f"Arg {ai+1}:", width=8).pack(side=tk.LEFT)
        var = tk.StringVar(value=arg['value'])
        ttk.Entry(f, textvariable=var, width=40).pack(side=tk.LEFT, padx=5)
        var.trace_add('write', lambda *a, s=si, i=ai, v=var: self.update_arg_value(s, i, v.get()))
        np_var = tk.BooleanVar(value=arg['is_numpy'])
        ttk.Checkbutton(f, text="numpy array", variable=np_var, 
                       command=lambda s=si, i=ai, v=np_var: self.update_arg_numpy(s, i, v.get())).pack(side=tk.LEFT, padx=5)
        if len(self.input_sets[si]['args']) > 1:
            ttk.Button(f, text="X", width=3, command=lambda s=si, i=ai: self.remove_argument(s, i)).pack(side=tk.LEFT)

    def create_kwarg_widget(self, parent, si, name, kwarg):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text=f"{name}=", width=12).pack(side=tk.LEFT)
        var = tk.StringVar(value=kwarg['value'])
        ttk.Entry(f, textvariable=var, width=35).pack(side=tk.LEFT, padx=5)
        var.trace_add('write', lambda *a, s=si, n=name, v=var: self.update_kwarg_value(s, n, v.get()))
        np_var = tk.BooleanVar(value=kwarg['is_numpy'])
        ttk.Checkbutton(f, text="numpy array", variable=np_var,
                       command=lambda s=si, n=name, v=np_var: self.update_kwarg_numpy(s, n, v.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(f, text="X", width=3, command=lambda s=si, n=name: self.remove_kwarg(s, n)).pack(side=tk.LEFT)

    def add_input_set(self):
        self.input_sets.append({'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}})
        self.refresh_display()

    def remove_input_set(self, idx):
        if len(self.input_sets) > 1:
            del self.input_sets[idx]
            self.refresh_display()

    def add_argument(self, si):
        self.input_sets[si]['args'].append({'value': '', 'is_numpy': False})
        self.refresh_display()

    def remove_argument(self, si, ai):
        if len(self.input_sets[si]['args']) > 1:
            del self.input_sets[si]['args'][ai]
            self.refresh_display()

    def add_kwarg(self, si, name_var):
        name = name_var.get().strip()
        if name and name not in self.input_sets[si]['kwargs']:
            self.input_sets[si]['kwargs'][name] = {'value': '', 'is_numpy': False}
            self.refresh_display()

    def remove_kwarg(self, si, name):
        if name in self.input_sets[si]['kwargs']:
            del self.input_sets[si]['kwargs'][name]
            self.refresh_display()

    def update_arg_value(self, si, ai, val):
        if si < len(self.input_sets) and ai < len(self.input_sets[si]['args']):
            self.input_sets[si]['args'][ai]['value'] = val

    def update_arg_numpy(self, si, ai, is_np):
        if si < len(self.input_sets) and ai < len(self.input_sets[si]['args']):
            self.input_sets[si]['args'][ai]['is_numpy'] = is_np

    def update_kwarg_value(self, si, name, val):
        if si < len(self.input_sets) and name in self.input_sets[si]['kwargs']:
            self.input_sets[si]['kwargs'][name]['value'] = val

    def update_kwarg_numpy(self, si, name, is_np):
        if si < len(self.input_sets) and name in self.input_sets[si]['kwargs']:
            self.input_sets[si]['kwargs'][name]['is_numpy'] = is_np

    def build_test_inputs_string(self):
        result = []
        for inp_set in self.input_sets:
            args = []
            for arg in inp_set['args']:
                val = arg['value'].strip()
                if not val:
                    continue
                if arg['is_numpy']:
                    args.append(f"np.array({val})")
                else:
                    try:
                        import ast
                        args.append(ast.literal_eval(val))
                    except:
                        args.append(val)
            kwargs = {}
            for name, kwarg in inp_set['kwargs'].items():
                val = kwarg['value'].strip()
                if not val:
                    continue
                if kwarg['is_numpy']:
                    kwargs[name] = f"np.array({val})"
                else:
                    try:
                        import ast
                        kwargs[name] = ast.literal_eval(val)
                    except:
                        kwargs[name] = val
            if args or kwargs:
                entry = {'args': args}
                if kwargs:
                    entry['kwargs'] = kwargs
                result.append(entry)
        return str(result) if result else ''

    def ok(self):
        self.result = self.build_test_inputs_string()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class TestEditorDialog(tk.Toplevel):
    def __init__(self, parent, test_data=None, title="Edit Test"):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x750")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.test_data = test_data or {}
        self.field_widgets = {}
        self.test_inputs_str = ''
        self.create_widgets()
        self.load_test_data()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        tf = ttk.LabelFrame(main, text="Test Type", padding="5")
        tf.pack(fill=tk.X, pady=5)
        self.test_type_var = tk.StringVar()
        self.test_type_combo = ttk.Combobox(tf, textvariable=self.test_type_var, 
                                            values=get_display_names_sorted(), state='readonly', width=55)
        self.test_type_combo.pack(side=tk.LEFT, padx=5)
        self.test_type_combo.bind('<<ComboboxSelected>>', self.on_test_type_changed)
        
        hf = ttk.LabelFrame(main, text="Help", padding="5")
        hf.pack(fill=tk.X, pady=5)
        self.help_text = tk.Text(hf, height=4, wrap=tk.WORD, state='disabled')
        self.help_text.pack(fill=tk.X)
        
        fc = ttk.LabelFrame(main, text="Parameters", padding="5")
        fc.pack(fill=tk.BOTH, expand=True, pady=5)
        canvas = tk.Canvas(fc, height=250)
        sb = ttk.Scrollbar(fc, orient="vertical", command=canvas.yview)
        self.fields_frame = ttk.Frame(canvas)
        self.fields_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ti_frame = ttk.Frame(main)
        self.ti_frame.pack(fill=tk.X, pady=5)
        self.ti_btn = ttk.Button(self.ti_frame, text="Edit Test Inputs...", command=self.edit_test_inputs)
        self.ti_label = ttk.Label(self.ti_frame, text="")
        
        ff = ttk.LabelFrame(main, text="Custom Feedback (Optional)", padding="5")
        ff.pack(fill=tk.X, pady=5)
        ttk.Label(ff, text="Pass:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.pass_fb = tk.StringVar()
        ttk.Entry(ff, textvariable=self.pass_fb, width=70).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(ff, text="Fail:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.fail_fb = tk.StringVar()
        ttk.Entry(ff, textvariable=self.fail_fb, width=70).grid(row=1, column=1, padx=5, pady=2)
        
        bf = ttk.Frame(main)
        bf.pack(fill=tk.X, pady=10)
        ttk.Button(bf, text="Save", command=self.save, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text="Cancel", command=self.cancel, width=10).pack(side=tk.RIGHT, padx=5)

    def on_test_type_changed(self, event=None):
        dn = self.test_type_var.get()
        if not dn:
            return
        internal = DISPLAY_TO_INTERNAL.get(dn)
        if not internal:
            return
        defn = TEST_TYPE_DEFINITIONS.get(internal, {})
        
        self.help_text.config(state='normal')
        self.help_text.delete(1.0, tk.END)
        self.help_text.insert(tk.END, f"{defn.get('help', '')}\n\nExample:\n{defn.get('example', '')}")
        self.help_text.config(state='disabled')
        
        for w in self.fields_frame.winfo_children():
            w.destroy()
        self.field_widgets.clear()
        self.ti_btn.pack_forget()
        self.ti_label.pack_forget()
        
        row = 0
        req = defn.get('required', [])
        opt = defn.get('optional', [])
        defaults = defn.get('defaults', {})
        file_f = defn.get('file_field')
        
        if req:
            ttk.Label(self.fields_frame, text="Required Fields:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 2))
            row += 1
        for f in req:
            row = self.create_field_widget(f, row, defaults.get(f, ''), f == file_f)
        
        if opt:
            ttk.Label(self.fields_frame, text="Optional Fields:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 2))
            row += 1
        for f in opt:
            row = self.create_field_widget(f, row, defaults.get(f, ''), f == file_f)
        
        if defn.get('has_test_inputs'):
            self.ti_btn.pack(side=tk.LEFT, padx=5)
            self.ti_label.pack(side=tk.LEFT, padx=5)
            self.update_ti_label()

    def create_field_widget(self, field, row, default, is_file):
        display_label = friendly_name(field) + ":"
        ttk.Label(self.fields_frame, text=display_label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        
        if field in BOOLEAN_FIELDS:
            var = tk.StringVar(value=default if default else '')
            frame = ttk.Frame(self.fields_frame)
            frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Radiobutton(frame, text="True", variable=var, value="true").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(frame, text="False", variable=var, value="false").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(frame, text="(Not Used)", variable=var, value="").pack(side=tk.LEFT, padx=5)
            self.field_widgets[field] = (var, 'boolean')
        elif is_file:
            var = tk.StringVar(value=default)
            frame = ttk.Frame(self.fields_frame)
            frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(frame, textvariable=var, width=48).pack(side=tk.LEFT)
            ttk.Button(frame, text="Browse...", command=lambda v=var: self.browse_file(v)).pack(side=tk.LEFT, padx=5)
            self.field_widgets[field] = (var, 'file')
        else:
            var = tk.StringVar(value=default)
            ttk.Entry(self.fields_frame, textvariable=var, width=55).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            self.field_widgets[field] = (var, 'entry')
        
        return row + 1

    def browse_file(self, var):
        fn = filedialog.askopenfilename(title="Select Solution File", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if fn:
            var.set(make_relative_path(fn))

    def edit_test_inputs(self):
        dn = self.test_type_var.get()
        internal = DISPLAY_TO_INTERNAL.get(dn, '')
        defn = TEST_TYPE_DEFINITIONS.get(internal, {})
        dialog = TestInputsDialog(self, self.test_inputs_str, defn.get('has_kwargs', False))
        self.wait_window(dialog)
        if dialog.result is not None:
            self.test_inputs_str = dialog.result
            self.update_ti_label()

    def update_ti_label(self):
        if self.test_inputs_str:
            try:
                import ast
                inp = ast.literal_eval(self.test_inputs_str)
                self.ti_label.config(text=f"({len(inp)} input set(s) defined)")
            except:
                self.ti_label.config(text="(inputs defined)")
        else:
            self.ti_label.config(text="(no inputs defined)")

    def load_test_data(self):
        if not self.test_data:
            self.test_type_var.set('Compare with Solution File')
            self.on_test_type_changed()
            return
        tt = self.test_data.get('test_type', '')
        if tt:
            defn = TEST_TYPE_DEFINITIONS.get(tt, {})
            dn = defn.get('display_name', tt)
            self.test_type_var.set(dn)
            self.on_test_type_changed()
        self.test_inputs_str = clean_value(self.test_data.get('test_inputs', ''))
        self.update_ti_label()
        for f, (var, wtype) in self.field_widgets.items():
            val = clean_value(self.test_data.get(f, ''))
            var.set(val)
        self.pass_fb.set(clean_value(self.test_data.get('pass_feedback', '')))
        self.fail_fb.set(clean_value(self.test_data.get('fail_feedback', '')))

    def validate(self):
        dn = self.test_type_var.get()
        if not dn:
            messagebox.showerror("Error", "Please select a test type.")
            return False
        internal = DISPLAY_TO_INTERNAL.get(dn)
        defn = TEST_TYPE_DEFINITIONS.get(internal, {})
        for f in defn.get('required', []):
            if f in self.field_widgets:
                var, wtype = self.field_widgets[f]
                if not var.get().strip():
                    messagebox.showerror("Error", f"'{friendly_name(f)}' is required.")
                    return False
        return True

    def save(self):
        if not self.validate():
            return
        dn = self.test_type_var.get()
        internal = DISPLAY_TO_INTERNAL.get(dn, dn)
        self.result = {'test_type': internal}
        for f, (var, wtype) in self.field_widgets.items():
            v = var.get().strip()
            if v:
                self.result[f] = v
        if self.test_inputs_str:
            self.result['test_inputs'] = self.test_inputs_str
        if self.pass_fb.get().strip():
            self.result['pass_feedback'] = self.pass_fb.get().strip()
        if self.fail_fb.get().strip():
            self.result['fail_feedback'] = self.fail_fb.get().strip()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class ConfigEditorDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Edit Configuration")
        self.geometry("550x350")
        self.transient(parent)
        self.grab_set()
        self.config_file = 'config.ini'
        self.config = configparser.ConfigParser()
        self.create_widgets()
        self.load_config()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        ef = ttk.LabelFrame(main, text="Email Settings", padding="10")
        ef.pack(fill=tk.X, pady=5)
        
        self.smtp_srv = tk.StringVar()
        self.smtp_port = tk.StringVar()
        self.sender_email = tk.StringVar()
        self.sender_pwd = tk.StringVar()
        self.instr_email = tk.StringVar()
        
        fields = [("SMTP Server:", self.smtp_srv), ("SMTP Port:", self.smtp_port),
                  ("Sender Email:", self.sender_email), ("Sender Password:", self.sender_pwd),
                  ("Instructor Email:", self.instr_email)]
        for r, (lbl, var) in enumerate(fields):
            ttk.Label(ef, text=lbl).grid(row=r, column=0, sticky=tk.W, pady=2)
            ttk.Entry(ef, textvariable=var, width=45).grid(row=r, column=1, pady=2, padx=5)
        
        sf = ttk.LabelFrame(main, text="Settings", padding="10")
        sf.pack(fill=tk.X, pady=5)
        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(sf, text="Debug Mode", variable=self.debug_var).pack(anchor=tk.W)
        
        bf = ttk.Frame(main)
        bf.pack(fill=tk.X, pady=10)
        ttk.Button(bf, text="Save", command=self.save, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text="Cancel", command=self.destroy, width=10).pack(side=tk.RIGHT, padx=5)

    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        if 'email' not in self.config:
            self.config['email'] = {}
        if 'settings' not in self.config:
            self.config['settings'] = {}
        self.smtp_srv.set(self.config.get('email', 'smtp_server', fallback='smtp.gmail.com'))
        self.smtp_port.set(self.config.get('email', 'smtp_port', fallback='587'))
        self.sender_email.set(self.config.get('email', 'sender_email', fallback=''))
        self.sender_pwd.set(self.config.get('email', 'sender_password', fallback=''))
        self.instr_email.set(self.config.get('email', 'instructor_email', fallback=''))
        self.debug_var.set(self.config.getboolean('settings', 'debug', fallback=False))

    def save(self):
        self.config['email'] = {'smtp_server': self.smtp_srv.get(), 'smtp_port': self.smtp_port.get(),
                                'sender_email': self.sender_email.get(), 'sender_password': self.sender_pwd.get(),
                                'instructor_email': self.instr_email.get()}
        self.config['settings'] = {'debug': str(self.debug_var.get()).lower()}
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        messagebox.showinfo("Saved", "Configuration saved!")
        self.destroy()


class ExtraFilesDialog(tk.Toplevel):
    def __init__(self, parent, extra_files, solution_files):
        super().__init__(parent)
        self.title("Extra Files for Build")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.extra_files = list(extra_files)
        self.solution_files = solution_files
        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        info_text = "Files listed below will be included in the executable build.\nSolution files are auto-detected from your tests AND the 'solutions' folder."
        ttk.Label(main, text=info_text, foreground='gray').pack(anchor=tk.W, pady=(0, 5))
        
        sf = ttk.LabelFrame(main, text=f"Auto-detected Solution Files ({len(self.solution_files)} files)", padding="5")
        sf.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add scrollbar for solution files
        sol_frame = ttk.Frame(sf)
        sol_frame.pack(fill=tk.BOTH, expand=True)
        sol_scroll = ttk.Scrollbar(sol_frame)
        sol_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        sol_list = tk.Listbox(sol_frame, height=6, yscrollcommand=sol_scroll.set)
        sol_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sol_scroll.config(command=sol_list.yview)
        
        for f in sorted(self.solution_files):
            sol_list.insert(tk.END, f)
        if not self.solution_files:
            sol_list.insert(tk.END, "(none detected - add files to 'solutions' folder)")
        
        ef = ttk.LabelFrame(main, text="Additional Files (manually added)", padding="5")
        ef.pack(fill=tk.BOTH, expand=True, pady=5)
        
        extra_frame = ttk.Frame(ef)
        extra_frame.pack(fill=tk.BOTH, expand=True)
        extra_scroll = ttk.Scrollbar(extra_frame)
        extra_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.extra_lb = tk.Listbox(extra_frame, height=6, yscrollcommand=extra_scroll.set)
        self.extra_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        extra_scroll.config(command=self.extra_lb.yview)
        
        for f in self.extra_files:
            self.extra_lb.insert(tk.END, f)
        
        bf = ttk.Frame(ef)
        bf.pack(fill=tk.X, pady=5)
        ttk.Button(bf, text="Add File...", command=self.add_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Add Folder...", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Remove Selected", command=self.remove_file).pack(side=tk.LEFT, padx=2)
        
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=10)
        ttk.Button(bottom, text="OK", command=self.ok, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom, text="Cancel", command=self.cancel, width=10).pack(side=tk.RIGHT, padx=5)

    def add_file(self):
        files = filedialog.askopenfilenames(title="Select Files")
        for f in files:
            rel = make_relative_path(f)
            if rel not in self.extra_files:
                self.extra_files.append(rel)
                self.extra_lb.insert(tk.END, rel)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            rel = make_relative_path(folder)
            if rel not in self.extra_files:
                self.extra_files.append(rel)
                self.extra_lb.insert(tk.END, rel)

    def remove_file(self):
        sel = self.extra_lb.curselection()
        if sel:
            del self.extra_files[sel[0]]
            self.extra_lb.delete(sel[0])

    def ok(self):
        self.result = self.extra_files
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class HelpDialog(tk.Toplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x450")
        self.transient(parent)
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        txt = scrolledtext.ScrolledText(main, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, content)
        txt.config(state='disabled')
        ttk.Button(main, text="Close", command=self.destroy).pack(pady=10)


class AssignmentEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrader Assignment Editor")
        self.root.geometry("1250x900")
        self.assignments = {}
        self.current_assignment = None
        self.excel_file = "assignments.xlsx"
        self.solution_files = set()
        self.extra_files = []
        self.sample_file = ""
        self.icon_file = ""
        self.modified = False
        self.load_settings()
        self.create_widgets()
        self.load_assignments()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    self.extra_files = s.get('extra_files', [])
                    self.sample_file = s.get('sample_file', '')
                    self.icon_file = s.get('icon_file', '')
            except:
                pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({
                    'extra_files': self.extra_files, 
                    'sample_file': self.sample_file,
                    'icon_file': self.icon_file
                }, f)
        except:
            pass

    def create_widgets(self):
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel
        left = ttk.Frame(self.paned, width=300)
        self.paned.add(left, weight=1)
        ttk.Label(left, text="Assignments", font=('TkDefaultFont', 11, 'bold')).pack(pady=5)
        
        lf = ttk.Frame(left)
        lf.pack(fill=tk.BOTH, expand=True, padx=5)
        sb = ttk.Scrollbar(lf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.assign_lb = tk.Listbox(lf, yscrollcommand=sb.set, width=38)
        self.assign_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.assign_lb.yview)
        self.assign_lb.bind('<<ListboxSelect>>', self.on_assignment_selected)
        
        abf = ttk.Frame(left)
        abf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(abf, text="New", command=self.new_assignment, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Rename", command=self.rename_assignment, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Duplicate", command=self.duplicate_assignment, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Delete", command=self.delete_assignment, width=9).pack(side=tk.LEFT, padx=2)
        
        rf = ttk.Frame(left)
        rf.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(rf, text="Move Up", command=self.move_assignment_up, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(rf, text="Move Down", command=self.move_assignment_down, width=12).pack(side=tk.LEFT, padx=2)
        
        # Right panel
        right = ttk.Frame(self.paned)
        self.paned.add(right, weight=3)
        self.tests_label = ttk.Label(right, text="Tests", font=('TkDefaultFont', 11, 'bold'))
        self.tests_label.pack(pady=5)
        
        tf = ttk.Frame(right)
        tf.pack(fill=tk.BOTH, expand=True, padx=5)
        cols = ('type', 'description', 'key_param')
        self.tests_tree = ttk.Treeview(tf, columns=cols, show='headings', height=12)
        self.tests_tree.heading('type', text='Test Type')
        self.tests_tree.heading('description', text='Description')
        self.tests_tree.heading('key_param', text='Key Parameter')
        self.tests_tree.column('type', width=220)
        self.tests_tree.column('description', width=250)
        self.tests_tree.column('key_param', width=220)
        ts = ttk.Scrollbar(tf, orient="vertical", command=self.tests_tree.yview)
        self.tests_tree.configure(yscrollcommand=ts.set)
        self.tests_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.tests_tree.bind('<Double-1>', self.edit_test)
        
        tbf = ttk.Frame(right)
        tbf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(tbf, text="Add", command=self.add_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Edit", command=self.edit_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Duplicate", command=self.duplicate_test, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Delete", command=self.delete_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Separator(tbf, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(tbf, text="Move Up", command=self.move_test_up, width=9).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Move Down", command=self.move_test_down, width=10).pack(side=tk.LEFT, padx=2)
        
        qf = ttk.LabelFrame(right, text="Quick Add Common Tests", padding="5")
        qf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(qf, text="+ Compare Solution", command=self.quick_add_compare_solution, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(qf, text="+ Variable Value", command=self.quick_add_variable_value, width=17).pack(side=tk.LEFT, padx=5)
        ttk.Button(qf, text="+ Test Function", command=self.quick_add_test_function, width=16).pack(side=tk.LEFT, padx=5)
        
        tsf = ttk.LabelFrame(right, text="Test Current Assignment", padding="5")
        tsf.pack(fill=tk.X, padx=5, pady=5)
        tr = ttk.Frame(tsf)
        tr.pack(fill=tk.X)
        ttk.Button(tr, text="Select Student File...", command=self.browse_sample_file, width=20).pack(side=tk.LEFT, padx=5)
        self.sample_lbl = ttk.Label(tr, text="No file selected", foreground='gray')
        self.sample_lbl.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.update_sample_label()
        ttk.Button(tr, text="Run Tests", command=self.test_current_assignment, width=12).pack(side=tk.RIGHT, padx=5)
        
        # Bottom
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=5, pady=5)
        
        ff = ttk.LabelFrame(bottom, text="File Operations", padding="5")
        ff.pack(side=tk.LEFT, padx=5)
        ttk.Button(ff, text="Save Assignments", command=self.save_assignments, width=17).pack(side=tk.LEFT, padx=2)
        ttk.Button(ff, text="Reload Assignments", command=self.load_assignments, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(ff, text="Edit Config...", command=self.edit_config, width=13).pack(side=tk.LEFT, padx=2)
        
        bf = ttk.LabelFrame(bottom, text="Build Tools", padding="5")
        bf.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(bf, text="Encode Resources", command=self.encode_resources, width=17).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Launch AutoGrader", command=self.launch_autograder_gui, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Extra Files...", command=self.manage_extra_files, width=13).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Set Icon...", command=self.select_icon, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Build Executable", command=self.build_executable, width=16).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="?", command=self.show_build_help, width=3).pack(side=tk.LEFT, padx=2)
        
        logf = ttk.LabelFrame(self.root, text="Log", padding="5")
        logf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(logf, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config('pass', foreground='green')
        self.log_text.tag_config('fail', foreground='red')
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('header', foreground='black', font=('TkDefaultFont', 10, 'bold'))

    def update_sample_label(self):
        if self.sample_file and os.path.exists(self.sample_file):
            self.sample_lbl.config(text=os.path.basename(self.sample_file), foreground='black')
        else:
            self.sample_lbl.config(text="No file selected", foreground='gray')

    def log(self, msg, tag=None):
        ts = datetime.now().strftime("%H:%M:%S")
        if tag:
            self.log_text.insert(tk.END, f"[{ts}] ", None)
            self.log_text.insert(tk.END, f"{msg}\n", tag)
        else:
            self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def show_build_help(self):
        txt = """BUILD PROCESS HELP

=== Testing the AutoGrader ===
1. Click "Encode Resources" to embed config.ini and assignments.xlsx
2. Click "Launch AutoGrader" to test the GUI application
3. Verify everything works correctly before building

=== Building the Executable ===
1. Save your assignments (if modified)
2. Click "Encode Resources" to embed the latest files
3. Click "Extra Files..." to review/add additional files
4. Click "Set Icon..." to choose a custom application icon (optional)
5. Click "Build Executable" to create the standalone application

=== Solution Files ===
Solution files are automatically included from:
- Any solution_file referenced in your tests
- ALL files in the 'solutions' folder (and subfolders)
This ensures all solution files are bundled with the executable.

=== Custom Icon ===
- Windows: Use .ico files
- Mac: Use .icns files
- The icon setting is saved and remembered

=== Required Files ===
- config.ini, assignments.xlsx (created by this editor)
- autograder.py, autograder-gui-app.py
  (bundled with editor - extracted temporarily when needed)
- encode_resources functionality is built into the editor

=== Notes ===
- Output will be in the 'dist' folder
- Requires: pip install pyinstaller"""
        HelpDialog(self.root, "Build Process Help", txt)


    def load_assignments(self):
        self.assignments.clear()
        self.assign_lb.delete(0, tk.END)
        self.solution_files.clear()
        if not os.path.exists(self.excel_file):
            self.log(f"No {self.excel_file} found. Starting fresh.", 'info')
            return
        try:
            xl = pd.ExcelFile(self.excel_file)
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                self.assignments[sheet] = df.to_dict('records')
                self.assign_lb.insert(tk.END, sheet)
                for t in self.assignments[sheet]:
                    sf = t.get('solution_file')
                    if sf and pd.notna(sf):
                        self.solution_files.add(str(sf))
            self.log(f"Loaded {len(self.assignments)} assignments", 'info')
            self.modified = False
        except Exception as e:
            self.log(f"Error loading: {e}", 'fail')

    def save_assignments(self):
        try:
            order = list(self.assign_lb.get(0, tk.END))
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as w:
                for name in order:
                    if name in self.assignments:
                        pd.DataFrame(self.assignments[name]).to_excel(w, sheet_name=name, index=False)
            self.log(f"Saved {len(self.assignments)} assignments", 'pass')
            self.modified = False
            messagebox.showinfo("Saved", f"Saved to {self.excel_file}")
        except Exception as e:
            self.log(f"Error saving: {e}", 'fail')
            messagebox.showerror("Error", str(e))

    def on_assignment_selected(self, event):
        sel = self.assign_lb.curselection()
        if not sel:
            return
        name = self.assign_lb.get(sel[0])
        self.current_assignment = name
        self.tests_label.config(text=f"Tests - {name}")
        self.refresh_tests_tree()

    def refresh_tests_tree(self):
        self.tests_tree.delete(*self.tests_tree.get_children())
        if not self.current_assignment:
            return
        tests = self.assignments.get(self.current_assignment, [])
        for t in tests:
            tt = clean_value(t.get('test_type', 'unknown'))
            defn = TEST_TYPE_DEFINITIONS.get(tt, {})
            dn = defn.get('display_name', tt)
            desc = clean_value(t.get('description', ''))
            kpf = defn.get('key_param')
            kp = ''
            if kpf and kpf in t:
                v = clean_value(t.get(kpf, ''))
                if v:
                    if 'file' in kpf.lower():
                        v = os.path.basename(v)
                    kp = v[:40] + ('...' if len(v) > 40 else '')
            self.tests_tree.insert('', tk.END, values=(dn, desc[:50], kp))

    def new_assignment(self):
        name = self.prompt_string("New Assignment", "Enter assignment name:")
        if not name:
            return
        if name in self.assignments:
            messagebox.showerror("Error", "Name already exists.")
            return
        self.assignments[name] = []
        self.assign_lb.insert(tk.END, name)
        self.assign_lb.selection_clear(0, tk.END)
        self.assign_lb.selection_set(tk.END)
        self.on_assignment_selected(None)
        self.modified = True
        self.log(f"Created: {name}", 'info')

    def rename_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an assignment first.")
            return
        old = self.assign_lb.get(sel[0])
        new = self.prompt_string("Rename", "Enter new name:", old)
        if not new or new == old:
            return
        if new in self.assignments:
            messagebox.showerror("Error", "Name already exists.")
            return
        self.assignments[new] = self.assignments.pop(old)
        self.assign_lb.delete(sel[0])
        self.assign_lb.insert(sel[0], new)
        self.assign_lb.selection_set(sel[0])
        self.current_assignment = new
        self.tests_label.config(text=f"Tests - {new}")
        self.modified = True
        self.log(f"Renamed: {old} -> {new}", 'info')

    def duplicate_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an assignment first.")
            return
        old = self.assign_lb.get(sel[0])
        new = self.prompt_string("Duplicate", "Enter name for copy:", f"{old} (Copy)")
        if not new:
            return
        if new in self.assignments:
            messagebox.showerror("Error", "Name already exists.")
            return
        import copy
        self.assignments[new] = copy.deepcopy(self.assignments[old])
        self.assign_lb.insert(tk.END, new)
        self.modified = True
        self.log(f"Duplicated: {old} -> {new}", 'info')

    def delete_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an assignment first.")
            return
        name = self.assign_lb.get(sel[0])
        if not messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            return
        del self.assignments[name]
        self.assign_lb.delete(sel[0])
        self.tests_tree.delete(*self.tests_tree.get_children())
        self.current_assignment = None
        self.tests_label.config(text="Tests")
        self.modified = True
        self.log(f"Deleted: {name}", 'info')

    def move_assignment_up(self):
        sel = self.assign_lb.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        name = self.assign_lb.get(idx)
        self.assign_lb.delete(idx)
        self.assign_lb.insert(idx - 1, name)
        self.assign_lb.selection_set(idx - 1)
        self.modified = True

    def move_assignment_down(self):
        sel = self.assign_lb.curselection()
        if not sel or sel[0] >= self.assign_lb.size() - 1:
            return
        idx = sel[0]
        name = self.assign_lb.get(idx)
        self.assign_lb.delete(idx)
        self.assign_lb.insert(idx + 1, name)
        self.assign_lb.selection_set(idx + 1)
        self.modified = True

    def get_selected_test_idx(self):
        sel = self.tests_tree.selection()
        if not sel:
            return None
        return self.tests_tree.index(sel[0])

    def add_test(self):
        if not self.current_assignment:
            messagebox.showwarning("No Assignment", "Select an assignment first.")
            return
        dlg = TestEditorDialog(self.root, title="Add Test")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment].append(dlg.result)
            self.refresh_tests_tree()
            self.modified = True
            sf = dlg.result.get('solution_file')
            if sf:
                self.solution_files.add(sf)
            self.log(f"Added test", 'info')

    def edit_test(self, event=None):
        idx = self.get_selected_test_idx()
        if idx is None:
            if event is None:
                messagebox.showwarning("No Selection", "Select a test first.")
            return
        data = self.assignments[self.current_assignment][idx]
        dlg = TestEditorDialog(self.root, test_data=data, title="Edit Test")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment][idx] = dlg.result
            self.refresh_tests_tree()
            self.modified = True
            sf = dlg.result.get('solution_file')
            if sf:
                self.solution_files.add(sf)
            self.log(f"Updated test", 'info')

    def duplicate_test(self):
        idx = self.get_selected_test_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a test first.")
            return
        import copy
        cp = copy.deepcopy(self.assignments[self.current_assignment][idx])
        self.assignments[self.current_assignment].insert(idx + 1, cp)
        self.refresh_tests_tree()
        self.modified = True
        self.log("Duplicated test", 'info')

    def delete_test(self):
        idx = self.get_selected_test_idx()
        if idx is None:
            messagebox.showwarning("No Selection", "Select a test first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this test?"):
            return
        del self.assignments[self.current_assignment][idx]
        self.refresh_tests_tree()
        self.modified = True
        self.log("Deleted test", 'info')

    def move_test_up(self):
        idx = self.get_selected_test_idx()
        if idx is None or idx == 0:
            return
        tests = self.assignments[self.current_assignment]
        tests[idx], tests[idx - 1] = tests[idx - 1], tests[idx]
        self.refresh_tests_tree()
        ch = self.tests_tree.get_children()
        self.tests_tree.selection_set(ch[idx - 1])
        self.modified = True

    def move_test_down(self):
        idx = self.get_selected_test_idx()
        tests = self.assignments[self.current_assignment]
        if idx is None or idx >= len(tests) - 1:
            return
        tests[idx], tests[idx + 1] = tests[idx + 1], tests[idx]
        self.refresh_tests_tree()
        ch = self.tests_tree.get_children()
        self.tests_tree.selection_set(ch[idx + 1])
        self.modified = True

    def quick_add_compare_solution(self):
        if not self.current_assignment:
            messagebox.showwarning("No Assignment", "Select an assignment first.")
            return
        dlg = TestEditorDialog(self.root, test_data={'test_type': 'compare_solution'}, title="Add Compare Solution")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment].append(dlg.result)
            self.refresh_tests_tree()
            self.modified = True
            sf = dlg.result.get('solution_file')
            if sf:
                self.solution_files.add(sf)
            self.log("Added Compare Solution test", 'info')

    def quick_add_variable_value(self):
        if not self.current_assignment:
            messagebox.showwarning("No Assignment", "Select an assignment first.")
            return
        dlg = TestEditorDialog(self.root, test_data={'test_type': 'variable_value'}, title="Add Variable Value")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment].append(dlg.result)
            self.refresh_tests_tree()
            self.modified = True
            self.log("Added Variable Value test", 'info')

    def quick_add_test_function(self):
        if not self.current_assignment:
            messagebox.showwarning("No Assignment", "Select an assignment first.")
            return
        dlg = TestEditorDialog(self.root, test_data={'test_type': 'test_function_solution'}, title="Add Test Function")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment].append(dlg.result)
            self.refresh_tests_tree()
            self.modified = True
            sf = dlg.result.get('solution_file')
            if sf:
                self.solution_files.add(sf)
            self.log("Added Test Function test", 'info')

    def browse_sample_file(self):
        fn = filedialog.askopenfilename(title="Select Student File", filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if fn:
            self.sample_file = make_relative_path(fn)
            self.update_sample_label()
            self.save_settings()

    def test_current_assignment(self):
        if not self.current_assignment:
            messagebox.showwarning("No Assignment", "Select an assignment first.")
            return
        if not self.sample_file or not os.path.exists(self.sample_file):
            messagebox.showwarning("No File", "Select a valid student file first.")
            return
        
        self.log("=" * 60, 'header')
        self.log(f"TESTING: {self.current_assignment}", 'header')
        self.log(f"File: {self.sample_file}", 'info')
        self.log("=" * 60, 'header')
        
        try:
            # IMPORTANT: Import matplotlib and numpy FIRST, before importing autograder
            # This ensures they're in sys.modules when autograder.py tries to import them
            self.log("Loading required libraries...", 'info')
            try:
                import matplotlib
                matplotlib.use('Agg')  # Non-interactive backend
                import matplotlib.pyplot as plt
                plt.close('all')
                import numpy as np
                self.log("  âœ“ Libraries loaded successfully", 'pass')
            except ImportError as e:
                self.log(f"ERROR: Required library not available: {e}", 'fail')
                self.log("Make sure matplotlib and numpy are installed.", 'fail')
                if getattr(sys, 'frozen', False):
                    self.log("Note: When running as executable, libraries must be bundled.", 'info')
                    self.log("Rebuild with: pyinstaller --clean assignment-editor.spec", 'info')
                else:
                    self.log("Install with: pip install matplotlib numpy", 'info')
                return
            
            # Extract autograder.py to temp directory and add to path
            temp_dir = get_temp_extract_dir()
            autograder_path = extract_bundled_file('autograder.py', temp_dir)
            
            if not autograder_path:
                # Fallback: try current directory
                if not os.path.exists('autograder.py'):
                    self.log("ERROR: autograder.py not found!", 'fail')
                    return
                temp_dir = os.getcwd()
            
            # Add temp directory to path for import
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)
            
            # Force reimport in case it was cached
            if 'autograder' in sys.modules:
                del sys.modules['autograder']
            
            self.log("Loading autograder module...", 'info')
            from autograder import AutoGrader
            self.log("  âœ“ AutoGrader loaded successfully", 'pass')
            
            grader = AutoGrader(self.sample_file)
            self.log("\n[1] EXECUTING STUDENT SCRIPT...", 'header')
            success = grader.execute_script()
            if success:
                self.log("    Script executed successfully", 'pass')
                if grader.captured_vars:
                    var_count = len(grader.captured_vars)
                    vars_preview = list(grader.captured_vars.keys())[:5]
                    self.log(f"    Captured {var_count} variables: {', '.join(vars_preview)}{'...' if var_count > 5 else ''}")
            else:
                self.log("    Script execution FAILED!", 'fail')
                self.log("    Check for syntax errors or runtime exceptions.")
                return
            
            tests = self.assignments[self.current_assignment]
            total_tests = len(tests)
            self.log(f"\n[2] RUNNING {total_tests} TESTS...", 'header')
            self.log("-" * 50)
            
            passed_count = 0
            failed_count = 0
            
            for i, t in enumerate(tests):
                tt = clean_value(t.get('test_type', '')).lower()
                defn = TEST_TYPE_DEFINITIONS.get(tt, {})
                display = defn.get('display_name', tt)
                desc = clean_value(t.get('description', ''))
                
                test_label = f"Test {i+1}/{total_tests}: {display}"
                if desc:
                    test_label += f" - {desc}"
                self.log(f"\n  {test_label}")
                
                try:
                    # Pass current working directory as base_dir for resolving solution file paths
                    result = self.run_single_test(grader, t, tt, base_dir=os.getcwd())
                    if result:
                        self.log(f"    >>> PASSED", 'pass')
                        passed_count += 1
                    else:
                        self.log(f"    >>> FAILED", 'fail')
                        failed_count += 1
                except Exception as e:
                    self.log(f"    >>> ERROR: {e}", 'fail')
                    failed_count += 1
            
            self.log("\n" + "=" * 60, 'header')
            self.log(f"SUMMARY: {passed_count}/{total_tests} tests passed", 'header')
            self.log("=" * 60, 'header')
            
            if passed_count == total_tests:
                self.log("All tests passed!", 'pass')
            elif passed_count == 0:
                self.log("All tests failed.", 'fail')
            else:
                self.log(f"{failed_count} test(s) need attention.", 'info')
                
        except ImportError as e:
            self.log(f"Import error: {e}", 'fail')
            self.log("Could not load autograder module.", 'fail')
        except Exception as e:
            self.log(f"Unexpected error: {e}", 'fail')
            import traceback
            self.log(traceback.format_exc())

    def run_single_test(self, grader, t, tt, base_dir=None):
        """Run a single test. base_dir is used to resolve relative paths for solution files."""
        if base_dir is None:
            base_dir = os.getcwd()
        
        def resolve_path(path):
            """Resolve a relative path against base_dir."""
            if path and not os.path.isabs(path):
                return os.path.join(base_dir, path)
            return path
        
        if tt == 'variable_value':
            var = t['variable_name']
            exp = eval(str(t['expected_value']))
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Checking: {var} == {exp} (tol: {tol})")
            result = grader.check_variable_value(var, exp, tol)
            if not result and var in grader.captured_vars:
                self.log(f"    Actual: {grader.captured_vars[var]}")
            return result
        elif tt == 'variable_type':
            var = t['variable_name']
            exp_type = t['expected_value']
            tm = {'int': int, 'float': float, 'str': str, 'list': list, 'dict': dict, 'tuple': tuple}
            self.log(f"    Checking: type({var}) == {exp_type}")
            result = grader.check_variable_type(var, tm.get(exp_type, str))
            if not result and var in grader.captured_vars:
                self.log(f"    Actual type: {type(grader.captured_vars[var]).__name__}")
            return result
        elif tt == 'function_exists':
            func = t['function_name']
            self.log(f"    Checking: '{func}' is defined")
            return grader.check_function_exists(func)
        elif tt == 'function_called':
            func = t['function_name']
            mp = str(t.get('match_any_prefix', '')).lower() == 'true'
            self.log(f"    Checking: '{func}' is called")
            return grader.check_function_called(func, mp)
        elif tt == 'function_not_called':
            func = t['function_name']
            mp = str(t.get('match_any_prefix', '')).lower() == 'true'
            self.log(f"    Checking: '{func}' is NOT called")
            return grader.check_function_not_called(func, mp)
        elif tt == 'compare_solution':
            sol = resolve_path(t['solution_file'])
            vs = [v.strip() for v in str(t['variables_to_compare']).split(',')]
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Solution: {sol}")
            self.log(f"    Variables: {', '.join(vs)}")
            return grader.compare_with_solution(sol, vs, tol)
        elif tt == 'for_loop_used':
            self.log(f"    Checking: for loop used")
            return grader.check_for_loop_used()
        elif tt == 'while_loop_used':
            self.log(f"    Checking: while loop used")
            return grader.check_while_loop_used()
        elif tt == 'if_statement_used':
            self.log(f"    Checking: if statement used")
            return grader.check_if_statement_used()
        elif tt == 'operator_used':
            op = t['operator']
            self.log(f"    Checking: operator '{op}' used")
            return grader.check_operator_used(op)
        elif tt == 'code_contains':
            phrase = t['phrase']
            cs = str(t.get('case_sensitive', '')).lower() != 'false'
            self.log(f"    Checking: code contains '{phrase}'")
            return grader.check_code_contains(phrase, cs)
        elif tt == 'loop_iterations':
            var = t['loop_variable']
            exp = t.get('expected_count')
            self.log(f"    Checking: loop counter '{var}'")
            result = grader.count_loop_iterations(var, int(exp) if exp else None)
            if var in grader.captured_vars:
                self.log(f"    Actual: {grader.captured_vars[var]}")
            return result is not None
        elif tt == 'list_equals':
            var = t['variable_name']
            exp = eval(str(t['expected_list']))
            order = str(t.get('order_matters', '')).lower() != 'false'
            self.log(f"    Checking: {var} == {exp}")
            result = grader.check_list_equals(var, exp, order)
            if not result and var in grader.captured_vars:
                self.log(f"    Actual: {grader.captured_vars[var]}")
            return result
        elif tt == 'array_equals':
            var = t['variable_name']
            exp = eval(str(t['expected_array']))
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Checking: {var} array equals expected")
            result = grader.check_array_equals(var, exp, tol)
            if not result and var in grader.captured_vars:
                self.log(f"    Actual: {grader.captured_vars[var]}")
            return result
        elif tt == 'array_size':
            var = t['variable_name']
            min_s = t.get('min_size')
            max_s = t.get('max_size')
            exact_s = t.get('exact_size')
            self.log(f"    Checking size of '{var}'")
            return grader.check_array_size(var, 
                min_size=int(min_s) if min_s else None,
                max_size=int(max_s) if max_s else None,
                exact_size=int(exact_s) if exact_s else None)
        elif tt == 'array_values_in_range':
            var = t['variable_name']
            min_v = t.get('min_value')
            max_v = t.get('max_value')
            self.log(f"    Checking: values in '{var}' in range [{min_v}, {max_v}]")
            return grader.check_array_values_in_range(var,
                min_value=float(min_v) if min_v else None,
                max_value=float(max_v) if max_v else None)
        elif tt == 'check_relationship':
            v1 = t['var1_name']
            v2 = t['var2_name']
            rel = t['relationship']
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Checking: {v2} = f({v1})")
            return grader.check_variable_relationship(v1, v2, eval(rel), tol)
        elif tt == 'plot_created':
            self.log(f"    Checking: plot created")
            return grader.check_plot_created()
        elif tt == 'plot_properties':
            title = t.get('title')
            xlabel = t.get('xlabel')
            ylabel = t.get('ylabel')
            has_legend = t.get('has_legend')
            has_grid = t.get('has_grid')
            self.log(f"    Checking plot properties")
            return grader.check_plot_properties(
                title=title if title else None,
                xlabel=xlabel if xlabel else None,
                ylabel=ylabel if ylabel else None,
                has_legend=str(has_legend).lower() == 'true' if has_legend else None,
                has_grid=str(has_grid).lower() == 'true' if has_grid else None)
        elif tt == 'plot_has_xlabel':
            self.log(f"    Checking: plot has x label")
            return grader.check_plot_has_xlabel()
        elif tt == 'plot_has_ylabel':
            self.log(f"    Checking: plot has y label")
            return grader.check_plot_has_ylabel()
        elif tt == 'plot_has_title':
            self.log(f"    Checking: plot has title")
            return grader.check_plot_has_title()
        elif tt == 'plot_data_length':
            line_idx = int(t.get('line_index', 0))
            min_len = t.get('min_length')
            max_len = t.get('max_length')
            exact_len = t.get('exact_length')
            self.log(f"    Checking plot data length (line {line_idx})")
            return grader.check_plot_data_length(
                min_length=int(min_len) if min_len else None,
                max_length=int(max_len) if max_len else None,
                exact_length=int(exact_len) if exact_len else None,
                line_index=line_idx)
        elif tt == 'plot_line_style':
            style = t['expected_style']
            line_idx = int(t.get('line_index', 0))
            self.log(f"    Checking: line {line_idx} style == '{style}'")
            return grader.check_plot_line_style(style, line_idx)
        elif tt == 'plot_has_line_style':
            style = t['expected_style']
            self.log(f"    Checking: any line has style '{style}'")
            return grader.check_plot_has_line_style(style)
        elif tt == 'check_multiple_lines':
            min_lines = int(t['min_lines'])
            self.log(f"    Checking: >= {min_lines} lines")
            return grader.check_multiple_lines(min_lines)
        elif tt == 'check_exact_lines':
            exact = int(t['exact_lines'])
            self.log(f"    Checking: exactly {exact} lines")
            return grader.check_exact_lines(exact)
        elif tt == 'compare_plot_solution':
            sol = resolve_path(t['solution_file'])
            line_idx = int(t.get('line_index', 0))
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Comparing plot with solution: {sol}")
            return grader.compare_plot_with_solution(sol, line_idx, tol,
                check_color=str(t.get('check_color', '')).lower() == 'true',
                check_linestyle=str(t.get('check_linestyle', '')).lower() == 'true')
        elif tt == 'check_function_any_line':
            func = t['function']
            min_len = int(t.get('min_length', 1))
            tol = float(t.get('tolerance', 1e-6))
            self.log(f"    Checking: plot matches {func}")
            return grader.check_function_any_line(eval(func), min_len, tol)
        else:
            self.log(f"    Unknown test type: {tt}", 'info')
            return False

    def launch_autograder_gui(self):
        self.log("Launching AutoGrader GUI...", 'info')
        
        # Get Python interpreter path
        python_exe = get_python_executable()
        if not python_exe:
            self.log("ERROR: Python interpreter not found!", 'fail')
            messagebox.showerror("Error", "Python interpreter not found on system.\n\n"
                               "Please ensure Python is installed and in your PATH.")
            return
        
        self.log(f"Found Python: {python_exe}", 'info')
        
        # Check if required libraries are available in system Python
        self.log("Checking required libraries...", 'info')
        check_script = """
import sys
missing = []
for lib in ['pandas', 'numpy', 'matplotlib', 'openpyxl']:
    try:
        __import__(lib)
    except ImportError:
        missing.append(lib)
if missing:
    print("MISSING:" + ",".join(missing))
    sys.exit(1)
else:
    print("OK")
    sys.exit(0)
"""
        try:
            result = subprocess.run(
                [python_exe, '-c', check_script],
                capture_output=True,
                text=True,
                timeout=30,
                **get_subprocess_flags()
            )
            if result.returncode != 0:
                output = result.stdout.strip()
                if output.startswith("MISSING:"):
                    missing_libs = output.replace("MISSING:", "")
                    self.log(f"ERROR: System Python missing libraries: {missing_libs}", 'fail')
                    messagebox.showerror("Missing Libraries", 
                        f"Your system Python is missing required libraries:\n\n{missing_libs}\n\n"
                        f"Install them with:\npip install {missing_libs.replace(',', ' ')}")
                    return
                else:
                    self.log(f"Library check failed: {result.stderr}", 'fail')
        except subprocess.TimeoutExpired:
            self.log("WARNING: Library check timed out, proceeding anyway...", 'info')
        except Exception as e:
            self.log(f"WARNING: Could not check libraries: {e}", 'info')
        
        # Check for embedded_resources.py first
        if not os.path.exists('embedded_resources.py'):
            self.log("WARNING: embedded_resources.py not found", 'fail')
            if not messagebox.askyesno("Warning", "embedded_resources.py not found.\n\n"
                                      "The AutoGrader needs this file to load assignments.\n\n"
                                      "Launch anyway?"):
                return
        
        # Get temp directory for extracted files
        temp_dir = get_temp_extract_dir()
        self.log(f"Using temp directory: {temp_dir}", 'info')
        
        # Extract required files to temp directory
        required_files = ['autograder-gui-app.py', 'autograder.py']
        for filename in required_files:
            extracted = extract_bundled_file(filename, temp_dir)
            if not extracted:
                # Try from current directory as fallback
                src = os.path.join(os.getcwd(), filename)
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(temp_dir, filename))
                    self.log(f"Copied {filename} from current directory", 'info')
                else:
                    self.log(f"ERROR: {filename} not found!", 'fail')
                    messagebox.showerror("Error", f"{filename} not found!")
                    return
            else:
                self.log(f"Extracted {filename}", 'info')
        
        # Copy embedded_resources.py to temp directory if it exists
        if os.path.exists('embedded_resources.py'):
            shutil.copy2('embedded_resources.py', os.path.join(temp_dir, 'embedded_resources.py'))
            self.log("Copied embedded_resources.py", 'info')
        
        # Copy solution files to temp directory
        solution_files_copied = 0
        for sol_file in self.solution_files:
            if sol_file and os.path.exists(sol_file):
                # Create directory structure if needed
                dest_path = os.path.join(temp_dir, sol_file)
                dest_dir = os.path.dirname(dest_path)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                try:
                    shutil.copy2(sol_file, dest_path)
                    solution_files_copied += 1
                except Exception as e:
                    self.log(f"Warning: Could not copy {sol_file}: {e}", 'info')
        
        # Also copy any solutions/ directory if it exists
        if os.path.exists('solutions') and os.path.isdir('solutions'):
            dest_solutions = os.path.join(temp_dir, 'solutions')
            if not os.path.exists(dest_solutions):
                try:
                    shutil.copytree('solutions', dest_solutions)
                    self.log("Copied solutions/ directory", 'info')
                except Exception as e:
                    self.log(f"Warning: Could not copy solutions directory: {e}", 'info')
        elif solution_files_copied > 0:
            self.log(f"Copied {solution_files_copied} solution file(s)", 'info')
        
        gui_file = os.path.join(temp_dir, 'autograder-gui-app.py')
        
        try:
            self.log(f"Launching: {python_exe} {gui_file}", 'info')
            process = subprocess.Popen(
                [python_exe, gui_file], 
                cwd=temp_dir,
                **get_subprocess_flags()
            )
            self.log(f"Launched successfully (PID: {process.pid})", 'pass')
            self.log("Note: The AutoGrader window should open shortly.", 'info')
        except Exception as e:
            self.log(f"Error launching: {e}", 'fail')
            messagebox.showerror("Error", f"Failed to launch AutoGrader:\n\n{str(e)}")

    def edit_config(self):
        ConfigEditorDialog(self.root)

    def encode_resources(self):
        """Encode config.ini and assignments.xlsx directly into embedded_resources.py"""
        self.log("Encoding resources...", 'info')
        
        # Create default config.ini if it doesn't exist
        if not os.path.exists('config.ini'):
            self.log("Creating default config.ini...", 'info')
            self.create_default_config()
        
        # Check for assignments.xlsx
        if not os.path.exists('assignments.xlsx'):
            if self.modified or self.assignments:
                if messagebox.askyesno("Save Assignments", "assignments.xlsx not found.\n\nSave current assignments?"):
                    self.save_assignments()
            if not os.path.exists('assignments.xlsx'):
                self.log("ERROR: assignments.xlsx not found", 'fail')
                messagebox.showerror("Error", "assignments.xlsx not found.\n\nPlease create and save assignments first.")
                return
        
        # Save changes first if needed
        if self.modified:
            if messagebox.askyesno("Save First?", "Save changes before encoding?"):
                self.save_assignments()
        
        try:
            import base64
            
            # Encode config.ini
            with open('config.ini', 'rb') as f:
                config_data = base64.b64encode(f.read()).decode('utf-8')
            self.log(f"  âœ“ Encoded config.ini ({len(config_data)} characters)")
            
            # Encode assignments.xlsx
            with open('assignments.xlsx', 'rb') as f:
                excel_data = base64.b64encode(f.read()).decode('utf-8')
            self.log(f"  âœ“ Encoded assignments.xlsx ({len(excel_data)} characters)")
            
            # Generate the embedded_resources.py module
            output = f'''"""
Auto-generated embedded resources.
DO NOT EDIT MANUALLY!
Generated by Assignment Editor GUI

This module contains config.ini and assignments.xlsx embedded as base64 strings.
Files are decoded at runtime and never extracted to disk in a visible location.
"""

import base64
import io
import tempfile
import os

# Embedded config.ini (base64 encoded)
CONFIG_DATA = """{config_data}"""

# Embedded assignments.xlsx (base64 encoded)
EXCEL_DATA = """{excel_data}"""

def get_config_string():
    """Return decoded config.ini content as string"""
    return base64.b64decode(CONFIG_DATA).decode('utf-8')

def get_excel_bytes():
    """Return decoded assignments.xlsx as bytes"""
    return base64.b64decode(EXCEL_DATA)

def get_excel_file():
    """Return path to temporary Excel file"""
    data = get_excel_bytes()
    
    # Create temporary file that will be cleaned up
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', mode='wb')
    temp_file.write(data)
    temp_file.close()
    
    return temp_file.name

def get_config_parser():
    """Return ConfigParser object with embedded config"""
    import configparser
    config = configparser.ConfigParser()
    config.read_string(get_config_string())
    return config

def cleanup_temp_file(filepath):
    """Delete temporary file"""
    try:
        if filepath and os.path.exists(filepath):
            os.unlink(filepath)
    except:
        pass
'''
            
            # Write the embedded_resources.py file
            with open('embedded_resources.py', 'w', encoding='utf-8') as f:
                f.write(output)
            
            self.log("  âœ“ Generated embedded_resources.py", 'pass')
            self.log("Resources encoded successfully!", 'pass')
            messagebox.showinfo("Success", "Resources encoded!\n\nGenerated: embedded_resources.py")
            
        except Exception as e:
            self.log(f"Error encoding resources: {e}", 'fail')
            messagebox.showerror("Error", f"Encoding failed:\n{str(e)}")

    def manage_extra_files(self):
        # Get all solution files for display
        all_solution_files = self.get_all_solution_files()
        dlg = ExtraFilesDialog(self.root, self.extra_files, all_solution_files)
        self.root.wait_window(dlg)
        if dlg.result is not None:
            self.extra_files = dlg.result
            self.save_settings()

    def create_default_config(self):
        """Create a default config.ini file if it doesn't exist."""
        if os.path.exists('config.ini'):
            return True
        
        default_config = """[email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = your_email@gmail.com
sender_password = your_app_password
instructor_email = instructor@university.edu

[settings]
# Set to true to show email error messages, false to hide them
debug = false
"""
        try:
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.write(default_config)
            self.log("Created default config.ini", 'info')
            return True
        except Exception as e:
            self.log(f"Error creating config.ini: {e}", 'fail')
            return False

    def build_executable(self):
        """Start the build process."""
        self.log("Preparing build...", 'info')
        
        # Track files we extract so we can clean them up later
        extracted_files = []
        
        # Extract required files from bundle to current directory (temporary)
        required_files = ['autograder-gui-app.py', 'autograder.py']
        for filename in required_files:
            if not os.path.exists(filename):
                self.log(f"Extracting {filename} from bundle...", 'info')
                # Extract directly to current directory for PyInstaller
                extracted = extract_bundled_file(filename, os.getcwd())
                if extracted:
                    extracted_files.append(filename)
        
        # Check if required files exist
        missing = []
        for filename in required_files:
            if not os.path.exists(filename):
                missing.append(filename)
        
        if missing:
            # Clean up any files we extracted before returning
            for f in extracted_files:
                try:
                    os.remove(f)
                except:
                    pass
            messagebox.showerror("Error", f"Missing required files:\n" + "\n".join(missing))
            return
        
        # Create default config.ini if it doesn't exist
        if not os.path.exists('config.ini'):
            self.log("Creating default config.ini...", 'info')
            if not self.create_default_config():
                for f in extracted_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                return
        
        # Check for assignments.xlsx
        if not os.path.exists('assignments.xlsx'):
            if self.modified or self.assignments:
                if messagebox.askyesno("Save Assignments", "Save assignments.xlsx first?"):
                    self.save_assignments()
            if not os.path.exists('assignments.xlsx'):
                messagebox.showerror("Error", "assignments.xlsx not found.\n\nPlease create and save assignments first.")
                for f in extracted_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                return
        
        # Check for embedded_resources.py
        if not os.path.exists('embedded_resources.py'):
            if messagebox.askyesno("Missing", "embedded_resources.py not found.\n\nEncode resources now?"):
                self.encode_resources()
                if not os.path.exists('embedded_resources.py'):
                    # Clean up extracted files
                    for f in extracted_files:
                        try:
                            os.remove(f)
                        except:
                            pass
                    return
            else:
                # Clean up extracted files
                for f in extracted_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                return
        
        if not messagebox.askyesno("Build", "Build executable?\n\nThis may take a few minutes."):
            # Clean up extracted files
            for f in extracted_files:
                try:
                    os.remove(f)
                except:
                    pass
            return
        
        # Create the spec file
        self.create_build_spec()
        
        # Start build in background thread
        self._start_build_thread(extracted_files)
    
    def _start_build_thread(self, extracted_files):
        """Run PyInstaller in a background thread to prevent UI freezing."""
        import threading
        
        # Disable build button during build
        self._set_build_buttons_state('disabled')
        
        # Create progress indicator
        self.log("\n" + "=" * 50, 'header')
        self.log("BUILD IN PROGRESS - Please wait...", 'header')
        self.log("=" * 50, 'header')
        
        def build_thread():
            try:
                # Get platform-specific flags to hide console window
                popen_kwargs = {
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.STDOUT,
                    'text': True,
                    'cwd': os.getcwd(),
                    'bufsize': 1,  # Line buffered
                    **get_subprocess_flags()  # Add Windows-specific flags
                }
                
                proc = subprocess.Popen(
                    ['pyinstaller', 'autograder_build.spec', '--clean'],
                    **popen_kwargs
                )
                
                # Read output line by line
                for line in iter(proc.stdout.readline, ''):
                    if line.strip():
                        # Schedule log update on main thread
                        self.root.after(0, lambda l=line.strip(): self.log(f"  {l}"))
                
                proc.wait()
                
                # Schedule completion on main thread
                self.root.after(0, lambda: self._build_complete(proc.returncode, extracted_files))
                
            except FileNotFoundError:
                self.root.after(0, lambda: self._build_error("PyInstaller not found.\n\nInstall with: pip install pyinstaller", extracted_files))
            except Exception as e:
                self.root.after(0, lambda: self._build_error(str(e), extracted_files))
        
        # Start the thread
        thread = threading.Thread(target=build_thread, daemon=True)
        thread.start()
    
    def _build_complete(self, return_code, extracted_files):
        """Called when build completes (on main thread)."""
        # Re-enable build buttons
        self._set_build_buttons_state('normal')
        
        # Clean up extracted files
        for f in extracted_files:
            try:
                os.remove(f)
                self.log(f"Cleaned up: {f}", 'info')
            except Exception as e:
                self.log(f"Could not remove {f}: {e}", 'info')
        
        if return_code == 0:
            self.log("\n" + "=" * 50, 'header')
            self.log("BUILD COMPLETE!", 'pass')
            self.log("=" * 50, 'header')
            self.log("Executable is in the 'dist' folder.", 'info')
            messagebox.showinfo("Success", "Build complete!\n\nCheck the 'dist' folder for your executable.")
        else:
            self.log("\n" + "=" * 50, 'header')
            self.log("BUILD FAILED!", 'fail')
            self.log("=" * 50, 'header')
            self.log("Check the log above for errors.", 'info')
            messagebox.showerror("Build Failed", "Build failed. Check the log for details.")
    
    def _build_error(self, error_msg, extracted_files):
        """Called when build encounters an error (on main thread)."""
        # Re-enable build buttons
        self._set_build_buttons_state('normal')
        
        # Clean up extracted files
        for f in extracted_files:
            try:
                os.remove(f)
            except:
                pass
        
        self.log(f"Build error: {error_msg}", 'fail')
        messagebox.showerror("Error", error_msg)
    
    def _set_build_buttons_state(self, state):
        """Enable or disable build-related buttons."""
        # Find and update build buttons
        # This searches through all widgets to find buttons with build-related text
        try:
            for widget in self.root.winfo_children():
                self._set_button_state_recursive(widget, state)
        except:
            pass
    
    def _set_button_state_recursive(self, widget, state):
        """Recursively find and update button states."""
        try:
            if isinstance(widget, ttk.Button):
                text = str(widget.cget('text')).lower()
                if any(word in text for word in ['build', 'encode', 'launch']):
                    widget.configure(state=state)
            for child in widget.winfo_children():
                self._set_button_state_recursive(child, state)
        except:
            pass

    def select_icon(self):
        """Select an icon file for the executable."""
        filetypes = [("Icon Files", "*.ico"), ("All Files", "*.*")]
        if sys.platform == 'darwin':
            filetypes = [("Icon Files", "*.icns"), ("Icon Files", "*.ico"), ("All Files", "*.*")]
        
        fn = filedialog.askopenfilename(
            title="Select Application Icon",
            filetypes=filetypes
        )
        if fn:
            self.icon_file = make_relative_path(fn)
            self.save_settings()
            self.log(f"Icon set: {self.icon_file}", 'info')
            messagebox.showinfo("Icon Set", f"Icon will be used for build:\n{os.path.basename(self.icon_file)}")

    def get_all_solution_files(self):
        """Get all files from solutions folder and any solution files referenced in tests."""
        all_solution_files = set()
        
        # Add all files referenced in tests
        for sf in self.solution_files:
            if os.path.exists(sf):
                all_solution_files.add(sf)
        
        # Also add entire solutions folder if it exists
        solutions_folder = 'solutions'
        if os.path.exists(solutions_folder) and os.path.isdir(solutions_folder):
            for root, dirs, files in os.walk(solutions_folder):
                for file in files:
                    filepath = os.path.join(root, file).replace('\\', '/')
                    all_solution_files.add(filepath)
        
        return all_solution_files

    def create_build_spec(self):
        # Collect all files to include
        all_files = set(self.extra_files)
        
        # Add all solution files (from tests AND solutions folder)
        solution_files = self.get_all_solution_files()
        all_files.update(solution_files)
        
        # Build datas list - preserve directory structure
        datas = []
        folders_added = set()
        
        for f in all_files:
            f = f.replace('\\', '/')  # Normalize path
            if os.path.exists(f):
                if os.path.isdir(f):
                    # For directories, include the whole directory
                    datas.append(f"        ('{f}', '{f}'),")
                    folders_added.add(f)
                else:
                    # For files, preserve the directory structure
                    dirname = os.path.dirname(f)
                    if dirname:
                        datas.append(f"        ('{f}', '{dirname}'),")
                    else:
                        datas.append(f"        ('{f}', '.'),")
        
        # Also add the solutions folder as a whole if it exists and wasn't already added
        if os.path.exists('solutions') and 'solutions' not in folders_added:
            datas.append("        ('solutions', 'solutions'),")
        
        datas_str = '\n'.join(sorted(set(datas)))  # Remove duplicates
        
        # Handle icon
        icon_line = ""
        if self.icon_file and os.path.exists(self.icon_file):
            icon_path = self.icon_file.replace('\\', '/')
            icon_line = f", icon='{icon_path}'"
            self.log(f"Including icon: {icon_path}", 'info')
        
        # Detect platform for appropriate build mode
        is_mac = sys.platform == 'darwin'
        
        if is_mac:
            # macOS: Use onedir mode for .app bundle (required for PyInstaller 7.0+)
            spec = f"""# -*- mode: python ; coding: utf-8 -*-
# Auto-generated by Assignment Editor (macOS onedir mode)

block_cipher = None

a = Analysis(
    ['autograder-gui-app.py'],
    pathex=[],
    binaries=[],
    datas=[
{datas_str}
    ],
    hiddenimports=[
        'autograder', 'embedded_resources', 'pandas', 'openpyxl', 'numpy',
        'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_tkagg',
        'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles',
        'reportlab.lib.units', 'reportlab.platypus', 'reportlab.lib.enums',
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        'tkinter.scrolledtext', 'configparser', 'smtplib', 'email',
        'email.mime.text', 'email.mime.multipart', 'email.mime.base',
        'socket', 'getpass', 'base64', 'tempfile',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['test', 'pdb', 'doctest', 'IPython', 'jupyter', 'pytest', 'sphinx'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# macOS: Use onedir mode (not onefile) for .app bundle
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoGrader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None{icon_line},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoGrader',
)

app = BUNDLE(
    coll,
    name='AutoGrader.app',
    bundle_identifier='com.autograder.app'{icon_line},
)
"""
        else:
            # Windows/Linux: Use onefile mode for single executable
            spec = f"""# -*- mode: python ; coding: utf-8 -*-
# Auto-generated by Assignment Editor (Windows/Linux onefile mode)

block_cipher = None

a = Analysis(
    ['autograder-gui-app.py'],
    pathex=[],
    binaries=[],
    datas=[
{datas_str}
    ],
    hiddenimports=[
        'autograder', 'embedded_resources', 'pandas', 'openpyxl', 'numpy',
        'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_tkagg',
        'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles',
        'reportlab.lib.units', 'reportlab.platypus', 'reportlab.lib.enums',
        'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        'tkinter.scrolledtext', 'configparser', 'smtplib', 'email',
        'email.mime.text', 'email.mime.multipart', 'email.mime.base',
        'socket', 'getpass', 'base64', 'tempfile',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['test', 'pdb', 'doctest', 'IPython', 'jupyter', 'pytest', 'sphinx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoGrader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None{icon_line},
)
"""
        with open('autograder_build.spec', 'w') as f:
            f.write(spec)
        
        self.log(f"Created build spec:", 'info')
        self.log(f"  - {len(all_files)} data files/folders", 'info')
        self.log(f"  - {len(solution_files)} solution files", 'info')
        if self.icon_file:
            self.log(f"  - Icon: {self.icon_file}", 'info')

    def prompt_string(self, title, prompt, initial=""):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("450x130")
        dlg.transient(self.root)
        dlg.grab_set()
        ttk.Label(dlg, text=prompt).pack(pady=10)
        var = tk.StringVar(value=initial)
        ent = ttk.Entry(dlg, textvariable=var, width=55)
        ent.pack(pady=5)
        ent.select_range(0, tk.END)
        ent.focus()
        result = [None]
        def ok():
            result[0] = var.get().strip()
            dlg.destroy()
        def cancel():
            dlg.destroy()
        ent.bind('<Return>', lambda e: ok())
        ent.bind('<Escape>', lambda e: cancel())
        bf = ttk.Frame(dlg)
        bf.pack(pady=10)
        ttk.Button(bf, text="OK", command=ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Cancel", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        self.root.wait_window(dlg)
        return result[0]


def main():
    root = tk.Tk()
    app = AssignmentEditorGUI(root)
    def on_closing():
        if app.modified:
            r = messagebox.askyesnocancel("Unsaved Changes", "Save changes before closing?")
            if r is True:
                app.save_assignments()
                app.save_settings()
                root.destroy()
            elif r is False:
                app.save_settings()
                root.destroy()
        else:
            app.save_settings()
            root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()