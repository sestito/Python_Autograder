import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from pathlib import Path
import sys

# Import the AutoGrader class (assumes it's in the same directory)
# from AutoGrader import AutoGrader


class AutoGraderGUI:
    """GUI Application for the AutoGrader system."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrader - Student Code Checker")
        self.root.geometry("900x700")
        
        # Student info
        self.student_name = tk.StringVar()
        self.student_email = tk.StringVar()
        self.selected_file = tk.StringVar()
        self.selected_assignment = tk.StringVar()
        
        # Data storage
        self.assignments = {}
        self.config = {}
        self.grader = None
        
        # Load configuration and assignments
        self.load_config()
        self.load_assignments()
        
        # Build UI
        self.create_widgets()
        
    def load_config(self):
        """Load email configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Config Error", 
                "config.json not found. Please create it with email settings.")
            self.config = {
                'email': {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': '',
                    'sender_password': '',
                    'instructor_email': ''
                }
            }
    
    def load_assignments(self):
        """Load assignments from Excel file"""
        try:
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile('assignments.xlsx')
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                self.assignments[sheet_name] = df.to_dict('records')
            
            if not self.assignments:
                messagebox.showwarning("No Assignments", 
                    "No assignments found in assignments.xlsx")
        
        except FileNotFoundError:
            messagebox.showerror("File Error", 
                "assignments.xlsx not found. Please create it with assignment tests.")
            self.assignments = {}
        except Exception as e:
            messagebox.showerror("Load Error", 
                f"Error loading assignments: {str(e)}")
            self.assignments = {}
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # ===== Student Information Section =====
        info_frame = ttk.LabelFrame(main_frame, text="Student Information", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_entry = ttk.Entry(info_frame, textvariable=self.student_name, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(info_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        email_entry = ttk.Entry(info_frame, textvariable=self.student_email, width=40)
        email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # ===== Assignment Selection Section =====
        selection_frame = ttk.LabelFrame(main_frame, text="Assignment Selection", padding="10")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(selection_frame, text="Assignment:").grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.assignment_combo = ttk.Combobox(
            selection_frame, 
            textvariable=self.selected_assignment,
            values=list(self.assignments.keys()),
            state='readonly',
            width=40
        )
        self.assignment_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(selection_frame, text="File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(selection_frame, textvariable=self.selected_file, width=40, state='readonly').grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        ttk.Button(selection_frame, text="Browse...", command=self.browse_file).grid(
            row=1, column=2, padx=5, pady=5
        )
        
        selection_frame.columnconfigure(1, weight=1)
        
        # ===== Action Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.check_button = ttk.Button(
            button_frame, 
            text="Check Code", 
            command=self.check_code,
            style='Accent.TButton'
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(
            side=tk.LEFT, padx=5
        )
        
        # ===== Results Section =====
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Text widget with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=('Courier', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.results_text.tag_config('pass', foreground='green')
        self.results_text.tag_config('fail', foreground='red')
        self.results_text.tag_config('header', font=('Courier', 12, 'bold'))
        
        main_frame.rowconfigure(3, weight=1)
        
        # ===== Status Bar =====
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def browse_file(self):
        """Open file dialog to select Python file"""
        filename = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
    
    def validate_inputs(self):
        """Validate user inputs before checking code"""
        if not self.student_name.get().strip():
            messagebox.showwarning("Missing Information", "Please enter your name.")
            return False
        
        if not self.student_email.get().strip():
            messagebox.showwarning("Missing Information", "Please enter your email.")
            return False
        
        if not self.selected_assignment.get():
            messagebox.showwarning("Missing Information", "Please select an assignment.")
            return False
        
        if not self.selected_file.get():
            messagebox.showwarning("Missing Information", "Please select a Python file.")
            return False
        
        if not os.path.exists(self.selected_file.get()):
            messagebox.showerror("File Error", "Selected file does not exist.")
            return False
        
        return True
    
    def check_code(self):
        """Run the autograder on the selected file"""
        if not self.validate_inputs():
            return
        
        self.status_var.set("Checking code...")
        self.check_button.config(state='disabled')
        self.results_text.delete(1.0, tk.END)
        
        try:
            # Get assignment tests
            assignment_name = self.selected_assignment.get()
            tests = self.assignments[assignment_name]
            
            # Initialize grader
            from AutoGrader import AutoGrader
            self.grader = AutoGrader(self.selected_file.get(), timeout=15)
            
            # Display header
            self.display_header()
            
            # Execute student script
            self.results_text.insert(tk.END, "\n>>> Executing script...\n", 'header')
            success = self.grader.execute_script()
            
            if not success:
                self.results_text.insert(tk.END, "\n✗ Script execution failed!\n", 'fail')
                self.results_text.insert(tk.END, "Please check your code for errors.\n\n")
            else:
                self.results_text.insert(tk.END, "✓ Script executed successfully!\n\n", 'pass')
            
            # Run all tests from Excel
            self.results_text.insert(tk.END, "\n>>> Running tests...\n", 'header')
            self.run_tests(tests)
            
            # Display summary
            self.display_summary()
            
            # Send email
            self.send_email()
            
            self.status_var.set("Code checking complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred")
            self.results_text.insert(tk.END, f"\n\nERROR: {str(e)}\n", 'fail')
        
        finally:
            self.check_button.config(state='normal')
    
    def run_tests(self, tests):
        """Execute tests based on Excel configuration"""
        for test in tests:
            test_type = test.get('test_type', '').lower()
            
            try:
                if test_type == 'variable_value':
                    self.grader.check_variable_value(
                        test['variable_name'],
                        self.parse_value(test['expected_value']),
                        tolerance=float(test.get('tolerance', 1e-6))
                    )
                
                elif test_type == 'variable_type':
                    type_map = {
                        'int': int, 'float': float, 'str': str, 
                        'list': list, 'dict': dict, 'tuple': tuple
                    }
                    expected_type = type_map.get(test['expected_value'], str)
                    self.grader.check_variable_type(test['variable_name'], expected_type)
                
                elif test_type == 'function_exists':
                    self.grader.check_function_exists(test['function_name'])
                
                elif test_type == 'function_called':
                    self.grader.check_function_called(test['function_name'])
                
                elif test_type == 'for_loop_used':
                    self.grader.check_for_loop_used()
                
                elif test_type == 'while_loop_used':
                    self.grader.check_while_loop_used()
                
                elif test_type == 'if_statement_used':
                    self.grader.check_if_statement_used()
                
                elif test_type == 'operator_used':
                    self.grader.check_operator_used(test['operator'])
                
                elif test_type == 'code_contains':
                    self.grader.check_code_contains(
                        test['phrase'],
                        case_sensitive=test.get('case_sensitive', 'true').lower() == 'true'
                    )
                
                elif test_type == 'plot_created':
                    self.grader.check_plot_created()
                
                elif test_type == 'plot_properties':
                    self.grader.check_plot_properties(
                        title=test.get('title'),
                        xlabel=test.get('xlabel'),
                        ylabel=test.get('ylabel'),
                        has_legend=self.parse_bool(test.get('has_legend')),
                        has_grid=self.parse_bool(test.get('has_grid'))
                    )
                
                elif test_type == 'plot_data_length':
                    self.grader.check_plot_data_length(
                        min_length=self.parse_int(test.get('min_length')),
                        max_length=self.parse_int(test.get('max_length')),
                        exact_length=self.parse_int(test.get('exact_length'))
                    )
                
                elif test_type == 'loop_iterations':
                    self.grader.count_loop_iterations(
                        test['loop_variable'],
                        expected_count=self.parse_int(test.get('expected_count'))
                    )
                
            except Exception as e:
                self.results_text.insert(tk.END, f"✗ Error in test: {str(e)}\n", 'fail')
    
    def parse_value(self, value):
        """Parse string value to appropriate Python type"""
        if pd.isna(value):
            return None
        
        value_str = str(value).strip()
        
        # Try to evaluate as Python literal
        try:
            return eval(value_str)
        except:
            return value_str
    
    def parse_bool(self, value):
        """Parse string to boolean or None"""
        if pd.isna(value):
            return None
        value_str = str(value).strip().lower()
        if value_str in ['true', 'yes', '1']:
            return True
        elif value_str in ['false', 'no', '0']:
            return False
        return None
    
    def parse_int(self, value):
        """Parse string to int or None"""
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except:
            return None
    
    def display_header(self):
        """Display header information"""
        self.results_text.insert(tk.END, "="*70 + "\n", 'header')
        self.results_text.insert(tk.END, "AUTOGRADER RESULTS\n", 'header')
        self.results_text.insert(tk.END, "="*70 + "\n", 'header')
        self.results_text.insert(tk.END, f"Student: {self.student_name.get()}\n")
        self.results_text.insert(tk.END, f"Email: {self.student_email.get()}\n")
        self.results_text.insert(tk.END, f"Assignment: {self.selected_assignment.get()}\n")
        self.results_text.insert(tk.END, f"File: {os.path.basename(self.selected_file.get())}\n")
        self.results_text.insert(tk.END, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.results_text.insert(tk.END, "="*70 + "\n")
        
        # Capture output and display in GUI
        self.capture_grader_output()
    
    def capture_grader_output(self):
        """Redirect grader print statements to GUI"""
        import sys
        from io import StringIO
        
        # Store original stdout
        original_stdout = sys.stdout
        
        # Create string buffer
        sys.stdout = StringIO()
        
        # After grader runs, restore and get output
        def restore_output():
            output = sys.stdout.getvalue()
            sys.stdout = original_stdout
            return output
        
        # Store for later use
        self.restore_output = restore_output
    
    def display_summary(self):
        """Display test summary"""
        summary = self.grader.get_summary()
        
        # Get captured output
        import sys
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__  # Restore original stdout
        
        # Display all test output
        for line in output.split('\n'):
            if '✓ PASS' in line or 'PASS:' in line:
                self.results_text.insert(tk.END, line + '\n', 'pass')
            elif '✗ FAIL' in line or 'FAIL:' in line:
                self.results_text.insert(tk.END, line + '\n', 'fail')
            else:
                self.results_text.insert(tk.END, line + '\n')
        
        # Display summary
        self.results_text.insert(tk.END, "\n" + "="*70 + "\n", 'header')
        self.results_text.insert(tk.END, "SUMMARY\n", 'header')
        self.results_text.insert(tk.END, "="*70 + "\n", 'header')
        self.results_text.insert(tk.END, f"Total Tests: {summary['total_tests']}\n")
        self.results_text.insert(tk.END, f"Passed: {summary['passed']}\n", 'pass')
        self.results_text.insert(tk.END, f"Failed: {summary['failed']}\n", 'fail')
        self.results_text.insert(tk.END, f"Success Rate: {summary['success_rate']:.1f}%\n")
        self.results_text.insert(tk.END, "="*70 + "\n")
    
    def send_email(self):
        """Send results via email"""
        try:
            email_config = self.config.get('email', {})
            
            if not email_config.get('sender_email') or not email_config.get('sender_password'):
                self.results_text.insert(tk.END, "\nNote: Email not configured. Results not sent.\n")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['instructor_email']
            msg['Subject'] = f"AutoGrader Results - {self.student_name.get()} - {self.selected_assignment.get()}"
            
            # Email body
            body = f"""
AutoGrader Submission

Student Name: {self.student_name.get()}
Student Email: {self.student_email.get()}
Assignment: {self.selected_assignment.get()}
Submission Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Results:
{self.results_text.get(1.0, tk.END)}
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach student's file
            with open(self.selected_file.get(), 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={os.path.basename(self.selected_file.get())}'
                )
                msg.attach(part)
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
            self.results_text.insert(tk.END, "\n✓ Results emailed to instructor!\n", 'pass')
            
        except Exception as e:
            self.results_text.insert(tk.END, f"\n✗ Failed to send email: {str(e)}\n", 'fail')
    
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AutoGraderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()