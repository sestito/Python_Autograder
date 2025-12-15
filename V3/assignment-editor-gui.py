# -*- coding: utf-8 -*-
"""
Assignment Editor GUI for AutoGrader
Provides an easy interface to create and edit assignments and tests.
Also includes tools to encode resources, test the autograder, and build executables.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import os
import sys
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import configparser

SETTINGS_FILE = 'assignment_editor_settings.json'

TEST_TYPE_DEFINITIONS = {
    'variable_value': {
        'display_name': 'Check Variable Value',
        'required': ['variable_name', 'expected_value'],
        'optional': ['tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Checks if a variable equals an expected value.',
        'example': "variable_name: result\nexpected_value: 42",
        'key_param': 'variable_name'
    },
    'variable_type': {
        'display_name': 'Check Variable Type',
        'required': ['variable_name', 'expected_value'],
        'optional': [],
        'defaults': {},
        'help': 'Checks variable type. Use: int, float, str, list, dict, tuple',
        'example': "variable_name: my_list\nexpected_value: list",
        'key_param': 'variable_name'
    },
    'function_exists': {
        'display_name': 'Check Function Exists',
        'required': ['function_name'],
        'optional': [],
        'defaults': {},
        'help': 'Checks if a function is defined.',
        'example': "function_name: calculate_average",
        'key_param': 'function_name'
    },
    'function_called': {
        'display_name': 'Check Function Called',
        'required': ['function_name'],
        'optional': ['match_any_prefix'],
        'defaults': {'match_any_prefix': 'false'},
        'help': 'Checks if a function is called.',
        'example': "function_name: np.mean",
        'key_param': 'function_name'
    },
    'function_not_called': {
        'display_name': 'Check Function NOT Called',
        'required': ['function_name'],
        'optional': ['match_any_prefix'],
        'defaults': {'match_any_prefix': 'false'},
        'help': 'Checks that a function is NOT used.',
        'example': "function_name: linspace\nmatch_any_prefix: true",
        'key_param': 'function_name'
    },
    'compare_solution': {
        'display_name': 'Compare with Solution File',
        'required': ['solution_file', 'variables_to_compare'],
        'optional': ['tolerance', 'require_same_type'],
        'defaults': {'tolerance': '1e-6', 'require_same_type': 'false'},
        'help': 'Compares variables with a solution file. Most common test.',
        'example': "solution_file: solutions/sol.py\nvariables_to_compare: x, y, result",
        'file_field': 'solution_file',
        'key_param': 'solution_file'
    },
    'test_function_solution': {
        'display_name': 'Test Function with Solution',
        'required': ['function_name', 'solution_file'],
        'optional': ['tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Tests function with inputs and compares to solution.',
        'example': "function_name: add\nsolution_file: solutions/sol.py",
        'file_field': 'solution_file',
        'key_param': 'function_name',
        'has_test_inputs': True
    },
    'test_function_solution_advanced': {
        'display_name': 'Test Function with Solution (Advanced)',
        'required': ['function_name', 'solution_file'],
        'optional': ['tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Tests function with args and kwargs.',
        'example': "function_name: process\nsolution_file: solutions/sol.py",
        'file_field': 'solution_file',
        'key_param': 'function_name',
        'has_test_inputs': True,
        'has_kwargs': True
    },
    'for_loop_used': {
        'display_name': 'Check For Loop Used',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if code contains a for loop.',
        'example': '(no parameters)', 'key_param': None
    },
    'while_loop_used': {
        'display_name': 'Check While Loop Used',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if code contains a while loop.',
        'example': '(no parameters)', 'key_param': None
    },
    'if_statement_used': {
        'display_name': 'Check If Statement Used',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if code contains an if statement.',
        'example': '(no parameters)', 'key_param': None
    },
    'operator_used': {
        'display_name': 'Check Operator Used',
        'required': ['operator'],
        'optional': [], 'defaults': {},
        'help': 'Checks if operator is used (+, -, *, /, +=, etc).',
        'example': "operator: +=",
        'key_param': 'operator'
    },
    'code_contains': {
        'display_name': 'Check Code Contains Text',
        'required': ['phrase'],
        'optional': ['case_sensitive'],
        'defaults': {'case_sensitive': 'true'},
        'help': 'Checks if code contains a phrase.',
        'example': "phrase: import numpy",
        'key_param': 'phrase'
    },
    'loop_iterations': {
        'display_name': 'Check Loop Iterations',
        'required': ['loop_variable'],
        'optional': ['expected_count'],
        'defaults': {},
        'help': 'Checks loop counter variable value.',
        'example': "loop_variable: count\nexpected_count: 100",
        'key_param': 'loop_variable'
    },
    'list_equals': {
        'display_name': 'Check List Equals',
        'required': ['variable_name', 'expected_list'],
        'optional': ['order_matters', 'tolerance'],
        'defaults': {'order_matters': 'true', 'tolerance': '1e-6'},
        'help': 'Checks if list equals expected values.',
        'example': "variable_name: my_list\nexpected_list: [1, 2, 3]",
        'key_param': 'variable_name'
    },
    'array_equals': {
        'display_name': 'Check Array Equals',
        'required': ['variable_name', 'expected_array'],
        'optional': ['tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Checks if numpy array equals expected.',
        'example': "variable_name: data\nexpected_array: [1.0, 2.0]",
        'key_param': 'variable_name'
    },
    'array_size': {
        'display_name': 'Check Array Size',
        'required': ['variable_name'],
        'optional': ['min_size', 'max_size', 'exact_size'],
        'defaults': {},
        'help': 'Checks array/list size.',
        'example': "variable_name: x_values\nmin_size: 100",
        'key_param': 'variable_name'
    },
    'array_values_in_range': {
        'display_name': 'Check Array Values in Range',
        'required': ['variable_name'],
        'optional': ['min_value', 'max_value'],
        'defaults': {},
        'help': 'Checks array values are within bounds.',
        'example': "variable_name: probs\nmin_value: 0\nmax_value: 1",
        'key_param': 'variable_name'
    },
    'check_relationship': {
        'display_name': 'Check Variable Relationship',
        'required': ['var1_name', 'var2_name', 'relationship'],
        'optional': ['tolerance'],
        'defaults': {'tolerance': '1e-6'},
        'help': 'Checks if var2 = f(var1).',
        'example': "var1_name: x\nvar2_name: y\nrelationship: lambda x: np.sin(x)",
        'key_param': 'var1_name'
    },
    'plot_created': {
        'display_name': 'Check Plot Created',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if matplotlib plot was created.',
        'example': '(no parameters)', 'key_param': None
    },
    'plot_properties': {
        'display_name': 'Check Plot Properties',
        'required': [],
        'optional': ['title', 'xlabel', 'ylabel', 'has_legend', 'has_grid'],
        'defaults': {},
        'help': 'Checks plot title, labels, legend, grid.',
        'example': "title: My Plot\nxlabel: X\nylabel: Y",
        'key_param': 'title'
    },
    'plot_has_xlabel': {
        'display_name': 'Check Plot Has X-Label',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if plot has x-axis label.',
        'example': '(no parameters)', 'key_param': None
    },
    'plot_has_ylabel': {
        'display_name': 'Check Plot Has Y-Label',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if plot has y-axis label.',
        'example': '(no parameters)', 'key_param': None
    },
    'plot_has_title': {
        'display_name': 'Check Plot Has Title',
        'required': [], 'optional': [], 'defaults': {},
        'help': 'Checks if plot has title.',
        'example': '(no parameters)', 'key_param': None
    },
    'plot_data_length': {
        'display_name': 'Check Plot Data Length',
        'required': [],
        'optional': ['min_length', 'max_length', 'exact_length', 'line_index'],
        'defaults': {'line_index': '0'},
        'help': 'Checks number of data points.',
        'example': "min_length: 50",
        'key_param': 'min_length'
    },
    'plot_line_style': {
        'display_name': 'Check Plot Line Style',
        'required': ['expected_style'],
        'optional': ['line_index'],
        'defaults': {'line_index': '0'},
        'help': "Checks line style (e.g., 'b-', 'r--').",
        'example': "expected_style: b-",
        'key_param': 'expected_style'
    },
    'plot_has_line_style': {
        'display_name': 'Check Plot Has Line Style',
        'required': ['expected_style'],
        'optional': [], 'defaults': {},
        'help': 'Checks if ANY line has style.',
        'example': "expected_style: r--",
        'key_param': 'expected_style'
    },
    'plot_line_width': {
        'display_name': 'Check Plot Line Width',
        'required': ['expected_width'],
        'optional': ['line_index', 'tolerance'],
        'defaults': {'line_index': '0', 'tolerance': '0.1'},
        'help': 'Checks line width.',
        'example': "expected_width: 2.0",
        'key_param': 'expected_width'
    },
    'plot_marker_size': {
        'display_name': 'Check Plot Marker Size',
        'required': ['expected_size'],
        'optional': ['line_index', 'tolerance'],
        'defaults': {'line_index': '0', 'tolerance': '0.5'},
        'help': 'Checks marker size.',
        'example': "expected_size: 10",
        'key_param': 'expected_size'
    },
    'check_multiple_lines': {
        'display_name': 'Check Minimum Lines in Plot',
        'required': ['min_lines'],
        'optional': [], 'defaults': {},
        'help': 'Checks minimum number of lines.',
        'example': "min_lines: 2",
        'key_param': 'min_lines'
    },
    'check_exact_lines': {
        'display_name': 'Check Exact Lines in Plot',
        'required': ['exact_lines'],
        'optional': [], 'defaults': {},
        'help': 'Checks exact number of lines.',
        'example': "exact_lines: 3",
        'key_param': 'exact_lines'
    },
    'compare_plot_solution': {
        'display_name': 'Compare Plot with Solution',
        'required': ['solution_file'],
        'optional': ['line_index', 'check_color', 'check_linestyle', 'check_linewidth', 'check_marker', 'check_markersize'],
        'defaults': {'line_index': '0', 'check_color': 'true', 'check_linestyle': 'true'},
        'help': 'Compares plot with solution file.',
        'example': "solution_file: solutions/plot_sol.py",
        'file_field': 'solution_file',
        'key_param': 'solution_file'
    },
    'check_function_any_line': {
        'display_name': 'Check Plot Matches Function',
        'required': ['function'],
        'optional': ['min_length', 'tolerance'],
        'defaults': {'min_length': '1', 'tolerance': '1e-6'},
        'help': 'Checks if line matches y = f(x).',
        'example': "function: lambda x: np.sin(x)",
        'key_param': 'function'
    },
}

DISPLAY_TO_INTERNAL = {v['display_name']: k for k, v in TEST_TYPE_DEFINITIONS.items()}

def get_display_names_sorted():
    return sorted([v['display_name'] for v in TEST_TYPE_DEFINITIONS.values()])

def clean_value(value):
    if pd.isna(value):
        return ''
    s = str(value)
    if s.lower() == 'nan':
        return ''
    return s


class TestInputsDialog(tk.Toplevel):
    def __init__(self, parent, test_inputs_str='', has_kwargs=False):
        super().__init__(parent)
        self.title("Edit Test Inputs")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.has_kwargs = has_kwargs
        self.input_sets = []
        self.parse_existing_inputs(test_inputs_str)
        self.create_widgets()
        self.refresh_display()
        self.update_idletasks()
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
                self.input_sets.append({'args': args_list if args_list else [{'value': '', 'is_numpy': False}], 'kwargs': kwargs_dict})
            if not self.input_sets:
                self.input_sets = [{'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}}]
        except:
            self.input_sets = [{'args': [{'value': '', 'is_numpy': False}], 'kwargs': {}}]

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text="Each input set calls the function once.", wraplength=750).pack(pady=5)
        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
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
        hdr = ttk.Frame(frame)
        hdr.pack(fill=tk.X)
        if len(self.input_sets) > 1:
            ttk.Button(hdr, text="Remove Set", command=lambda: self.remove_input_set(idx)).pack(side=tk.RIGHT)
        args_f = ttk.LabelFrame(frame, text="Arguments", padding="5")
        args_f.pack(fill=tk.X, pady=5)
        for j, arg in enumerate(inp_set['args']):
            self.create_arg_widget(args_f, idx, j, arg)
        ttk.Button(args_f, text="+ Add Arg", command=lambda i=idx: self.add_argument(i)).pack(pady=5)
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
            ttk.Button(add_f, text="+ Add", command=lambda i=idx, v=kw_var: self.add_kwarg(i, v)).pack(side=tk.LEFT)

    def create_arg_widget(self, parent, si, ai, arg):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text=f"Arg {ai+1}:", width=8).pack(side=tk.LEFT)
        var = tk.StringVar(value=arg['value'])
        ttk.Entry(f, textvariable=var, width=40).pack(side=tk.LEFT, padx=5)
        var.trace_add('write', lambda *a, s=si, i=ai, v=var: self.update_arg_value(s, i, v.get()))
        np_var = tk.BooleanVar(value=arg['is_numpy'])
        ttk.Checkbutton(f, text="numpy", variable=np_var, command=lambda s=si, i=ai, v=np_var: self.update_arg_numpy(s, i, v.get())).pack(side=tk.LEFT, padx=5)
        if len(self.input_sets[si]['args']) > 1:
            ttk.Button(f, text="X", width=2, command=lambda s=si, i=ai: self.remove_argument(s, i)).pack(side=tk.LEFT)

    def create_kwarg_widget(self, parent, si, name, kwarg):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=2)
        ttk.Label(f, text=f"{name}=", width=12).pack(side=tk.LEFT)
        var = tk.StringVar(value=kwarg['value'])
        ttk.Entry(f, textvariable=var, width=35).pack(side=tk.LEFT, padx=5)
        var.trace_add('write', lambda *a, s=si, n=name, v=var: self.update_kwarg_value(s, n, v.get()))
        np_var = tk.BooleanVar(value=kwarg['is_numpy'])
        ttk.Checkbutton(f, text="numpy", variable=np_var, command=lambda s=si, n=name, v=np_var: self.update_kwarg_numpy(s, n, v.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(f, text="X", width=2, command=lambda s=si, n=name: self.remove_kwarg(s, n)).pack(side=tk.LEFT)

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
        self.geometry("750x650")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.test_data = test_data or {}
        self.field_widgets = {}
        self.test_inputs_str = ''
        self.create_widgets()
        self.load_test_data()
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        tf = ttk.LabelFrame(main, text="Test Type", padding="5")
        tf.pack(fill=tk.X, pady=5)
        self.test_type_var = tk.StringVar()
        self.test_type_combo = ttk.Combobox(tf, textvariable=self.test_type_var, values=get_display_names_sorted(), state='readonly', width=50)
        self.test_type_combo.pack(side=tk.LEFT, padx=5)
        self.test_type_combo.bind('<<ComboboxSelected>>', self.on_test_type_changed)
        hf = ttk.LabelFrame(main, text="Help", padding="5")
        hf.pack(fill=tk.X, pady=5)
        self.help_text = tk.Text(hf, height=3, wrap=tk.WORD, state='disabled')
        self.help_text.pack(fill=tk.X)
        fc = ttk.LabelFrame(main, text="Parameters", padding="5")
        fc.pack(fill=tk.BOTH, expand=True, pady=5)
        canvas = tk.Canvas(fc, height=180)
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
        ttk.Entry(ff, textvariable=self.pass_fb, width=65).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(ff, text="Fail:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.fail_fb = tk.StringVar()
        ttk.Entry(ff, textvariable=self.fail_fb, width=65).grid(row=1, column=1, padx=5, pady=2)
        bf = ttk.Frame(main)
        bf.pack(fill=tk.X, pady=10)
        ttk.Button(bf, text="Save", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=5)

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
        self.help_text.insert(tk.END, f"{defn.get('help', '')}\nExample: {defn.get('example', '')}")
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
            ttk.Label(self.fields_frame, text="Required:", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))
            row += 1
        for f in req:
            self.create_field_widget(f, row, True, '', f == file_f)
            row += 1
        if opt:
            ttk.Label(self.fields_frame, text="Optional:", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
            row += 1
        for f in opt:
            self.create_field_widget(f, row, False, defaults.get(f, ''), f == file_f)
            row += 1
        if defn.get('has_test_inputs'):
            self.ti_btn.pack(side=tk.LEFT, padx=5)
            self.ti_label.pack(side=tk.LEFT, padx=5)
            self.update_ti_label()

    def create_field_widget(self, field, row, req, default, is_file):
        lbl = f"{field}{'*' if req else ''}:"
        ttk.Label(self.fields_frame, text=lbl).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.StringVar(value=default)
        if is_file:
            fr = ttk.Frame(self.fields_frame)
            fr.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(fr, textvariable=var, width=42).pack(side=tk.LEFT)
            ttk.Button(fr, text="Browse...", command=lambda v=var: self.browse_file(v)).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Entry(self.fields_frame, textvariable=var, width=52).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        self.field_widgets[field] = var

    def browse_file(self, var):
        fn = filedialog.askopenfilename(title="Select Solution File", filetypes=[("Python", "*.py"), ("All", "*.*")])
        if fn:
            var.set(fn)

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
                self.ti_label.config(text=f"({len(inp)} input set(s))")
            except:
                self.ti_label.config(text="(inputs defined)")
        else:
            self.ti_label.config(text="(no inputs)")

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
        for f, var in self.field_widgets.items():
            var.set(clean_value(self.test_data.get(f, '')))
        self.pass_fb.set(clean_value(self.test_data.get('pass_feedback', '')))
        self.fail_fb.set(clean_value(self.test_data.get('fail_feedback', '')))

    def validate(self):
        dn = self.test_type_var.get()
        if not dn:
            messagebox.showerror("Error", "Select a test type.")
            return False
        internal = DISPLAY_TO_INTERNAL.get(dn)
        defn = TEST_TYPE_DEFINITIONS.get(internal, {})
        for f in defn.get('required', []):
            if f in self.field_widgets and not self.field_widgets[f].get().strip():
                messagebox.showerror("Error", f"'{f}' is required.")
                return False
        return True

    def save(self):
        if not self.validate():
            return
        dn = self.test_type_var.get()
        internal = DISPLAY_TO_INTERNAL.get(dn, dn)
        self.result = {'test_type': internal}
        for f, var in self.field_widgets.items():
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
        self.geometry("500x320")
        self.transient(parent)
        self.grab_set()
        self.config_file = 'config.ini'
        self.config = configparser.ConfigParser()
        self.create_widgets()
        self.load_config()
        self.update_idletasks()
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
        r = 0
        for lbl, var in [("SMTP Server:", self.smtp_srv), ("SMTP Port:", self.smtp_port), ("Sender Email:", self.sender_email), ("Sender Password:", self.sender_pwd), ("Instructor Email:", self.instr_email)]:
            ttk.Label(ef, text=lbl).grid(row=r, column=0, sticky=tk.W, pady=2)
            ttk.Entry(ef, textvariable=var, width=40).grid(row=r, column=1, pady=2)
            r += 1
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
        self.config['email'] = {'smtp_server': self.smtp_srv.get(), 'smtp_port': self.smtp_port.get(), 'sender_email': self.sender_email.get(), 'sender_password': self.sender_pwd.get(), 'instructor_email': self.instr_email.get()}
        self.config['settings'] = {'debug': str(self.debug_var.get()).lower()}
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        messagebox.showinfo("Saved", "Configuration saved!")
        self.destroy()


class ExtraFilesDialog(tk.Toplevel):
    def __init__(self, parent, extra_files, solution_files):
        super().__init__(parent)
        self.title("Extra Files for Build")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.extra_files = list(extra_files)
        self.solution_files = solution_files
        self.create_widgets()
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        sf = ttk.LabelFrame(main, text="Auto-detected Solution Files", padding="5")
        sf.pack(fill=tk.X, pady=5)
        sol_list = tk.Listbox(sf, height=4)
        sol_list.pack(fill=tk.X)
        for f in sorted(self.solution_files):
            sol_list.insert(tk.END, f)
        if not self.solution_files:
            sol_list.insert(tk.END, "(none)")
        ef = ttk.LabelFrame(main, text="Additional Files", padding="5")
        ef.pack(fill=tk.BOTH, expand=True, pady=5)
        self.extra_lb = tk.Listbox(ef, height=8)
        self.extra_lb.pack(fill=tk.BOTH, expand=True)
        for f in self.extra_files:
            self.extra_lb.insert(tk.END, f)
        bf = ttk.Frame(ef)
        bf.pack(fill=tk.X, pady=5)
        ttk.Button(bf, text="Add File...", command=self.add_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Add Folder...", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Remove", command=self.remove_file).pack(side=tk.LEFT, padx=2)
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=10)
        ttk.Button(bottom, text="OK", command=self.ok, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom, text="Cancel", command=self.cancel, width=10).pack(side=tk.RIGHT, padx=5)

    def add_file(self):
        files = filedialog.askopenfilenames(title="Select Files")
        for f in files:
            if f not in self.extra_files:
                self.extra_files.append(f)
                self.extra_lb.insert(tk.END, f)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder and folder not in self.extra_files:
            self.extra_files.append(folder)
            self.extra_lb.insert(tk.END, folder)

    def remove_file(self):
        sel = self.extra_lb.curselection()
        if sel:
            idx = sel[0]
            self.extra_lb.delete(idx)
            del self.extra_files[idx]

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
        self.geometry("550x400")
        self.transient(parent)
        main = ttk.Frame(self, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        txt = scrolledtext.ScrolledText(main, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, content)
        txt.config(state='disabled')
        ttk.Button(main, text="Close", command=self.destroy).pack(pady=10)
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


class AssignmentEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrader Assignment Editor")
        self.root.geometry("1200x850")
        self.assignments = {}
        self.current_assignment = None
        self.excel_file = "assignments.xlsx"
        self.solution_files = set()
        self.extra_files = []
        self.sample_file = ""
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
            except:
                pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump({'extra_files': self.extra_files, 'sample_file': self.sample_file}, f)
        except:
            pass

    def create_widgets(self):
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left = ttk.Frame(self.paned, width=280)
        self.paned.add(left, weight=1)
        ttk.Label(left, text="Assignments", font=('TkDefaultFont', 11, 'bold')).pack(pady=5)
        lf = ttk.Frame(left)
        lf.pack(fill=tk.BOTH, expand=True, padx=5)
        sb = ttk.Scrollbar(lf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.assign_lb = tk.Listbox(lf, yscrollcommand=sb.set, width=35)
        self.assign_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.assign_lb.yview)
        self.assign_lb.bind('<<ListboxSelect>>', self.on_assignment_selected)
        abf = ttk.Frame(left)
        abf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(abf, text="New", command=self.new_assignment, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Rename", command=self.rename_assignment, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Duplicate", command=self.duplicate_assignment, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(abf, text="Delete", command=self.delete_assignment, width=8).pack(side=tk.LEFT, padx=2)
        rf = ttk.Frame(left)
        rf.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(rf, text="Move Up", command=self.move_assignment_up, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(rf, text="Move Down", command=self.move_assignment_down, width=10).pack(side=tk.LEFT, padx=2)
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
        self.tests_tree.column('type', width=200)
        self.tests_tree.column('description', width=230)
        self.tests_tree.column('key_param', width=200)
        ts = ttk.Scrollbar(tf, orient="vertical", command=self.tests_tree.yview)
        self.tests_tree.configure(yscrollcommand=ts.set)
        self.tests_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.tests_tree.bind('<Double-1>', self.edit_test)
        tbf = ttk.Frame(right)
        tbf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(tbf, text="Add", command=self.add_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Edit", command=self.edit_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Duplicate", command=self.duplicate_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Delete", command=self.delete_test, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Separator(tbf, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(tbf, text="Up", command=self.move_test_up, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(tbf, text="Down", command=self.move_test_down, width=6).pack(side=tk.LEFT, padx=2)
        qf = ttk.LabelFrame(right, text="Quick Add", padding="5")
        qf.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(qf, text="+ Compare Solution", command=self.quick_add_compare_solution, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(qf, text="+ Variable Value", command=self.quick_add_variable_value, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(qf, text="+ Test Function", command=self.quick_add_test_function, width=14).pack(side=tk.LEFT, padx=5)
        tsf = ttk.LabelFrame(right, text="Test Current Assignment", padding="5")
        tsf.pack(fill=tk.X, padx=5, pady=5)
        tr = ttk.Frame(tsf)
        tr.pack(fill=tk.X)
        ttk.Button(tr, text="Select Student File...", command=self.browse_sample_file, width=18).pack(side=tk.LEFT, padx=5)
        self.sample_lbl = ttk.Label(tr, text="No file selected", foreground='gray')
        self.sample_lbl.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.update_sample_label()
        ttk.Button(tr, text="Run Tests", command=self.test_current_assignment, width=12).pack(side=tk.RIGHT, padx=5)
        bottom = ttk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=5, pady=5)
        ff = ttk.LabelFrame(bottom, text="File", padding="5")
        ff.pack(side=tk.LEFT, padx=5)
        ttk.Button(ff, text="Save Assignments", command=self.save_assignments, width=16).pack(side=tk.LEFT, padx=2)
        ttk.Button(ff, text="Reload", command=self.load_assignments, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(ff, text="Edit Config...", command=self.edit_config, width=12).pack(side=tk.LEFT, padx=2)
        bf = ttk.LabelFrame(bottom, text="Build", padding="5")
        bf.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(bf, text="Encode Resources", command=self.encode_resources, width=14).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Launch AutoGrader", command=self.launch_autograder_gui, width=16).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Extra Files...", command=self.manage_extra_files, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Build Executable", command=self.build_executable, width=14).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="?", command=self.show_build_help, width=3).pack(side=tk.LEFT, padx=2)
        logf = ttk.LabelFrame(self.root, text="Log", padding="5")
        logf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(logf, height=5, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def update_sample_label(self):
        if self.sample_file and os.path.exists(self.sample_file):
            self.sample_lbl.config(text=os.path.basename(self.sample_file), foreground='black')
        else:
            self.sample_lbl.config(text="No file selected", foreground='gray')

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def show_build_help(self):
        txt = """BUILD HELP

Testing:
1. Encode Resources
2. Launch AutoGrader
3. Verify it works

Building:
1. Save assignments
2. Encode Resources
3. Extra Files (optional)
4. Build Executable

Notes:
- Solution files auto-included
- Output in dist/ folder
- Need PyInstaller installed"""
        HelpDialog(self.root, "Build Help", txt)

    def load_assignments(self):
        self.assignments.clear()
        self.assign_lb.delete(0, tk.END)
        self.solution_files.clear()
        if not os.path.exists(self.excel_file):
            self.log(f"No {self.excel_file} found.")
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
            self.log(f"Loaded {len(self.assignments)} assignments")
            self.modified = False
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to load: {e}")

    def save_assignments(self):
        try:
            order = list(self.assign_lb.get(0, tk.END))
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as w:
                for name in order:
                    if name in self.assignments:
                        pd.DataFrame(self.assignments[name]).to_excel(w, sheet_name=name, index=False)
            self.log(f"Saved {len(self.assignments)} assignments")
            self.modified = False
            messagebox.showinfo("Saved", f"Saved to {self.excel_file}")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Failed: {e}")

    def new_assignment(self):
        name = self.prompt_string("New Assignment", "Name:")
        if not name:
            return
        if name in self.assignments:
            messagebox.showerror("Error", "Name exists.")
            return
        self.assignments[name] = []
        self.assign_lb.insert(tk.END, name)
        self.assign_lb.selection_clear(0, tk.END)
        self.assign_lb.selection_set(tk.END)
        self.on_assignment_selected(None)
        self.modified = True
        self.log(f"Created: {name}")

    def rename_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select an assignment.")
            return
        old = self.assign_lb.get(sel[0])
        new = self.prompt_string("Rename", "New name:", old)
        if not new or new == old:
            return
        if new in self.assignments:
            messagebox.showerror("Error", "Name exists.")
            return
        self.assignments[new] = self.assignments.pop(old)
        self.assign_lb.delete(sel[0])
        self.assign_lb.insert(sel[0], new)
        self.assign_lb.selection_set(sel[0])
        self.current_assignment = new
        self.tests_label.config(text=f"Tests - {new}")
        self.modified = True
        self.log(f"Renamed: {old} -> {new}")

    def duplicate_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select an assignment.")
            return
        old = self.assign_lb.get(sel[0])
        new = self.prompt_string("Duplicate", "Name:", f"{old} (Copy)")
        if not new:
            return
        if new in self.assignments:
            messagebox.showerror("Error", "Name exists.")
            return
        import copy
        self.assignments[new] = copy.deepcopy(self.assignments[old])
        self.assign_lb.insert(tk.END, new)
        self.modified = True
        self.log(f"Duplicated: {old} -> {new}")

    def delete_assignment(self):
        sel = self.assign_lb.curselection()
        if not sel:
            messagebox.showwarning("Select", "Select an assignment.")
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
        self.log(f"Deleted: {name}")

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
                    kp = v[:35] + ('...' if len(v) > 35 else '')
            self.tests_tree.insert('', tk.END, values=(dn, desc[:45], kp))

    def get_selected_test_idx(self):
        sel = self.tests_tree.selection()
        if not sel:
            return None
        return self.tests_tree.index(sel[0])

    def add_test(self):
        if not self.current_assignment:
            messagebox.showwarning("Select", "Select an assignment first.")
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
            self.log(f"Added: {dlg.result.get('test_type')}")

    def edit_test(self, event=None):
        idx = self.get_selected_test_idx()
        if idx is None:
            if event is None:
                messagebox.showwarning("Select", "Select a test.")
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
            self.log(f"Updated: {dlg.result.get('test_type')}")

    def duplicate_test(self):
        idx = self.get_selected_test_idx()
        if idx is None:
            messagebox.showwarning("Select", "Select a test.")
            return
        import copy
        cp = copy.deepcopy(self.assignments[self.current_assignment][idx])
        self.assignments[self.current_assignment].insert(idx + 1, cp)
        self.refresh_tests_tree()
        self.modified = True
        self.log("Duplicated test")

    def delete_test(self):
        idx = self.get_selected_test_idx()
        if idx is None:
            messagebox.showwarning("Select", "Select a test.")
            return
        if not messagebox.askyesno("Confirm", "Delete test?"):
            return
        del self.assignments[self.current_assignment][idx]
        self.refresh_tests_tree()
        self.modified = True
        self.log("Deleted test")

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
            messagebox.showwarning("Select", "Select an assignment.")
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
            self.log("Added Compare Solution")

    def quick_add_variable_value(self):
        if not self.current_assignment:
            messagebox.showwarning("Select", "Select an assignment.")
            return
        dlg = TestEditorDialog(self.root, test_data={'test_type': 'variable_value'}, title="Add Variable Value")
        self.root.wait_window(dlg)
        if dlg.result:
            self.assignments[self.current_assignment].append(dlg.result)
            self.refresh_tests_tree()
            self.modified = True
            self.log("Added Variable Value")

    def quick_add_test_function(self):
        if not self.current_assignment:
            messagebox.showwarning("Select", "Select an assignment.")
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
            self.log("Added Test Function")


    def browse_sample_file(self):
        fn = filedialog.askopenfilename(title="Select Student File", filetypes=[("Python", "*.py"), ("All", "*.*")])
        if fn:
            self.sample_file = fn
            self.update_sample_label()
            self.save_settings()

    def test_current_assignment(self):
        if not self.current_assignment:
            messagebox.showwarning("Select", "Select an assignment.")
            return
        if not self.sample_file or not os.path.exists(self.sample_file):
            messagebox.showwarning("File", "Select a valid student file.")
            return
        self.log(f"Testing {self.current_assignment} with {os.path.basename(self.sample_file)}")
        try:
            from autograder import AutoGrader
            import matplotlib.pyplot as plt
            plt.close('all')
            grader = AutoGrader(self.sample_file)
            grader.execute_script()
            tests = self.assignments[self.current_assignment]
            self.run_tests_on_grader(grader, tests)
            s = grader.get_summary()
            self.log(f"Results: {s['passed']}/{s['total_tests']} ({s['success_rate']:.1f}%)")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_tests_on_grader(self, grader, tests):
        for t in tests:
            tt = clean_value(t.get('test_type', '')).lower()
            try:
                if tt == 'variable_value':
                    grader.check_variable_value(t['variable_name'], eval(str(t['expected_value'])), float(t.get('tolerance', 1e-6)))
                elif tt == 'variable_type':
                    tm = {'int': int, 'float': float, 'str': str, 'list': list, 'dict': dict, 'tuple': tuple}
                    grader.check_variable_type(t['variable_name'], tm.get(t['expected_value'], str))
                elif tt == 'function_exists':
                    grader.check_function_exists(t['function_name'])
                elif tt == 'function_called':
                    grader.check_function_called(t['function_name'], str(t.get('match_any_prefix', 'false')).lower() == 'true')
                elif tt == 'function_not_called':
                    grader.check_function_not_called(t['function_name'], str(t.get('match_any_prefix', 'false')).lower() == 'true')
                elif tt == 'compare_solution':
                    vs = [v.strip() for v in str(t['variables_to_compare']).split(',')]
                    grader.compare_with_solution(t['solution_file'], vs, float(t.get('tolerance', 1e-6)))
                elif tt == 'for_loop_used':
                    grader.check_for_loop_used()
                elif tt == 'while_loop_used':
                    grader.check_while_loop_used()
                elif tt == 'if_statement_used':
                    grader.check_if_statement_used()
                elif tt == 'operator_used':
                    grader.check_operator_used(t['operator'])
                elif tt == 'code_contains':
                    grader.check_code_contains(t['phrase'], str(t.get('case_sensitive', 'true')).lower() == 'true')
                elif tt == 'plot_created':
                    grader.check_plot_created()
                elif tt == 'list_equals':
                    grader.check_list_equals(t['variable_name'], eval(str(t['expected_list'])), str(t.get('order_matters', 'true')).lower() == 'true')
                elif tt == 'array_equals':
                    grader.check_array_equals(t['variable_name'], eval(str(t['expected_array'])), float(t.get('tolerance', 1e-6)))
                else:
                    self.log(f"  Unknown: {tt}")
            except Exception as e:
                self.log(f"  Error in {tt}: {e}")

    def launch_autograder_gui(self):
        self.log("Launching AutoGrader GUI...")
        try:
            subprocess.Popen([sys.executable, 'autograder-gui-app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.log("Launched")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Launch failed: {e}")

    def edit_config(self):
        ConfigEditorDialog(self.root)

    def encode_resources(self):
        self.log("Encoding resources...")
        if self.modified and messagebox.askyesno("Save?", "Save first?"):
            self.save_assignments()
        try:
            r = subprocess.run([sys.executable, 'encode_resources.py'], capture_output=True, text=True, cwd=os.getcwd())
            if r.stdout:
                for line in r.stdout.strip().split('\n'):
                    self.log(line)
            if r.returncode == 0:
                self.log("Encoded successfully!")
                messagebox.showinfo("Success", "Resources encoded!")
            else:
                messagebox.showerror("Error", "Encoding failed.")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Failed: {e}")

    def manage_extra_files(self):
        dlg = ExtraFilesDialog(self.root, self.extra_files, self.solution_files)
        self.root.wait_window(dlg)
        if dlg.result is not None:
            self.extra_files = dlg.result
            self.save_settings()
            self.log(f"Extra files: {len(self.extra_files)}")

    def build_executable(self):
        self.log("Starting build...")
        if not os.path.exists('autograder-gui-app.py'):
            messagebox.showerror("Error", "autograder-gui-app.py not found!")
            return
        if not os.path.exists('embedded_resources.py'):
            if messagebox.askyesno("Missing", "Encode resources now?"):
                self.encode_resources()
                if not os.path.exists('embedded_resources.py'):
                    return
            else:
                return
        if not messagebox.askyesno("Build", "Build the executable?"):
            return
        self.create_build_spec()
        self.log("Running PyInstaller...")
        try:
            proc = subprocess.Popen(['pyinstaller', 'autograder_build.spec', '--clean'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in iter(proc.stdout.readline, ''):
                line = line.strip()
                if line:
                    self.log(line)
                self.root.update_idletasks()
            proc.wait()
            if proc.returncode == 0:
                self.log("Build complete!")
                messagebox.showinfo("Done", "Built! Check dist/")
            else:
                self.log("Build failed!")
                messagebox.showerror("Failed", "Build failed.")
        except FileNotFoundError:
            self.log("PyInstaller not found.")
            messagebox.showerror("Error", "Install PyInstaller: pip install pyinstaller")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Build failed: {e}")

    def create_build_spec(self):
        all_files = set(self.extra_files)
        for sf in self.solution_files:
            if os.path.exists(sf):
                all_files.add(sf)
        datas = []
        for f in all_files:
            if os.path.exists(f):
                if os.path.isdir(f):
                    datas.append(f"        ('{f}', '{f}'),")
                else:
                    d = os.path.dirname(f) or '.'
                    datas.append(f"        ('{f}', '{d}'),")
        datas_str = '\n'.join(datas) if datas else ''
        spec = f"""# Auto-generated spec
block_cipher = None
a = Analysis(['autograder-gui-app.py'], pathex=[], binaries=[], datas=[
{datas_str}
], hiddenimports=['autograder', 'embedded_resources', 'pandas', 'openpyxl', 'numpy', 'matplotlib', 'matplotlib.pyplot', 'matplotlib.backends.backend_tkagg', 'reportlab', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles', 'reportlab.lib.units', 'reportlab.platypus', 'reportlab.lib.enums', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.scrolledtext', 'configparser', 'smtplib', 'email', 'email.mime.text', 'email.mime.multipart', 'email.mime.base', 'socket', 'getpass', 'base64', 'tempfile'], hookspath=[], runtime_hooks=[], excludes=['test', 'unittest', 'pdb', 'doctest', 'IPython', 'jupyter', 'pytest', 'sphinx'], cipher=block_cipher, noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='AutoGrader', debug=False, strip=False, upx=True, runtime_tmpdir=None, console=False)
app = BUNDLE(exe, name='AutoGrader.app', bundle_identifier='com.autograder.app')
"""
        with open('autograder_build.spec', 'w') as f:
            f.write(spec)
        self.log(f"Created spec with {len(all_files)} files")

    def prompt_string(self, title, prompt, initial=""):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("400x120")
        dlg.transient(self.root)
        dlg.grab_set()
        ttk.Label(dlg, text=prompt).pack(pady=10)
        var = tk.StringVar(value=initial)
        ent = ttk.Entry(dlg, textvariable=var, width=50)
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
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dlg.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{x}+{y}")
        self.root.wait_window(dlg)
        return result[0]


def main():
    root = tk.Tk()
    app = AssignmentEditorGUI(root)
    def on_closing():
        if app.modified:
            r = messagebox.askyesnocancel("Unsaved", "Save before closing?")
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