import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numpy')

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import socket
import getpass
from datetime import datetime
from pathlib import Path
import sys

# For PDF export
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from reportlab.lib.enums import TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import embedded resources (contains config.ini and assignments.xlsx)
try:
    import embedded_resources
    EMBEDDED_MODE = True
    print("✓ Embedded resources loaded successfully")
except ImportError as e:
    EMBEDDED_MODE = False
    print(f"WARNING: embedded_resources not found: {e}")
    print("Please run 'python encode_resources.py' first!")
except Exception as e:
    EMBEDDED_MODE = False
    print(f"ERROR loading embedded_resources: {e}")

# Import the AutoGrader class
try:
    from autograder import AutoGrader
    print("✓ AutoGrader class imported successfully")
except ImportError as e:
    print(f"ERROR: Could not import AutoGrader: {e}")
    print("Make sure autograder.py is in the same directory")
except Exception as e:
    print(f"ERROR importing AutoGrader: {e}")


class AutoGraderGUI:
    """GUI Application for the AutoGrader system."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AutoGrader - Student Code Checker")
        self.root.geometry("900x700")
        
        print("Initializing AutoGraderGUI...")
        
        # Student info
        self.student_name = tk.StringVar()
        self.selected_file = tk.StringVar()
        self.selected_assignment = tk.StringVar()
        
        # System info
        try:
            self.computer_name = socket.gethostname()
            self.username = getpass.getuser()
            print(f"✓ System info: {self.computer_name} ({self.username})")
        except Exception as e:
            print(f"WARNING: Could not get system info: {e}")
            self.computer_name = "Unknown"
            self.username = "Unknown"
        
        # Data storage
        self.assignments = {}
        self.config = None
        self.grader = None
        self.debug_mode = True
        self.excel_temp_file = None
        
        # Load configuration and assignments
        print("Loading configuration...")
        self.load_config()
        
        print("Loading assignments...")
        self.load_assignments()
        
        # Build UI
        print("Creating widgets...")
        self.create_widgets()
        
        print("✓ AutoGraderGUI initialization complete")
        
    def load_config(self):
        """Load configuration from embedded resources"""
        if not EMBEDDED_MODE:
            print("ERROR: Embedded resources not available")
            messagebox.showerror("Config Error", 
                "Embedded resources not found. Please run encode_resources.py and rebuild.")
            self.config = None
            return
        
        try:
            self.config = embedded_resources.get_config_parser()
            self.debug_mode = self.config.getboolean('settings', 'debug', fallback=True)
            print(f"✓ Config loaded (debug={self.debug_mode})")
            
        except Exception as e:
            print(f"ERROR loading config: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Config Error", 
                f"Error reading configuration: {str(e)}")
            self.config = None
    
    def load_assignments(self):
        """Load assignments from embedded Excel file"""
        if not EMBEDDED_MODE:
            print("ERROR: Cannot load assignments - embedded mode not available")
            self.assignments = {}
            return
        
        try:
            # Get temporary Excel file from embedded resources
            self.excel_temp_file = embedded_resources.get_excel_file()
            print(f"✓ Excel temp file created: {self.excel_temp_file}")
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(self.excel_temp_file)
            print(f"✓ Excel file opened, sheets: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                self.assignments[sheet_name] = df.to_dict('records')
                print(f"  ✓ Loaded {len(df)} tests from '{sheet_name}'")
            
            if not self.assignments:
                messagebox.showwarning("No Assignments", 
                    "No assignments found in embedded Excel file")
            else:
                print(f"✓ Total assignments loaded: {len(self.assignments)}")
        
        except Exception as e:
            print(f"ERROR loading assignments: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Load Error", 
                f"Error loading assignments: {str(e)}")
            self.assignments = {}
    
    def __del__(self):
        """Cleanup temporary Excel file on exit"""
        if self.excel_temp_file:
            embedded_resources.cleanup_temp_file(self.excel_temp_file)
    
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
        
        # Display system info (read-only)
        ttk.Label(info_frame, text="Computer:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        computer_label = ttk.Label(info_frame, text=f"{self.computer_name} ({self.username})")
        computer_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
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
        
        ttk.Button(button_frame, text="Export to PDF", command=self.export_to_pdf).pack(
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
            
            # Check if AutoGrader is available
            try:
                from autograder import AutoGrader
            except ImportError as e:
                raise Exception(f"AutoGrader module not found: {e}. Make sure autograder.py is in the same directory.")
            
            # Initialize grader
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
                    case_sensitive = test.get('case_sensitive', True)
                    # Handle various representations of boolean values
                    if isinstance(case_sensitive, str):
                        case_sensitive = case_sensitive.lower() in ['true', 'yes', '1']
                    elif pd.isna(case_sensitive):
                        case_sensitive = True
                    
                    self.grader.check_code_contains(
                        test['phrase'],
                        case_sensitive=bool(case_sensitive)
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
                
                elif test_type == 'list_equals':
                    expected_list = self.parse_value(test.get('expected_list'))
                    order_matters = self.parse_bool(test.get('order_matters'))
                    if order_matters is None:
                        order_matters = True
                    
                    self.grader.check_list_equals(
                        test['variable_name'],
                        expected_list,
                        order_matters=order_matters,
                        tolerance=float(test.get('tolerance', 1e-6))
                    )
                
                elif test_type == 'array_equals':
                    expected_array = self.parse_value(test.get('expected_array'))
                    self.grader.check_array_equals(
                        test['variable_name'],
                        expected_array,
                        tolerance=float(test.get('tolerance', 1e-6))
                    )
                
                elif test_type == 'compare_solution':
                    solution_file = test.get('solution_file')
                    variables_to_compare = self.parse_value(test.get('variables_to_compare'))
                    
                    if isinstance(variables_to_compare, str):
                        # If it's a comma-separated string, split it
                        variables_to_compare = [v.strip() for v in variables_to_compare.split(',')]
                    
                    self.grader.compare_with_solution(
                        solution_file,
                        variables_to_compare,
                        tolerance=float(test.get('tolerance', 1e-6))
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
        self.results_text.insert(tk.END, f"Computer: {self.computer_name}\n")
        self.results_text.insert(tk.END, f"Username: {self.username}\n")
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
            if not self.config:
                if self.debug_mode:
                    self.results_text.insert(tk.END, "\nNote: Email not configured. Results not sent.\n")
                return
            
            sender_email = self.config.get('email', 'sender_email', fallback='')
            sender_password = self.config.get('email', 'sender_password', fallback='')
            instructor_email = self.config.get('email', 'instructor_email', fallback='')
            
            if not sender_email or not sender_password or not instructor_email:
                if self.debug_mode:
                    self.results_text.insert(tk.END, "\nNote: Email not fully configured. Results not sent.\n")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = instructor_email
            
            # Format: Assignment Name, Student Name, Date, Time
            timestamp = datetime.now()
            subject = f"{self.selected_assignment.get()}, {self.student_name.get()}, {timestamp.strftime('%Y-%m-%d')}, {timestamp.strftime('%H:%M:%S')}"
            msg['Subject'] = subject
            
            # Email body
            body = f"""
AutoGrader Submission

Student Name: {self.student_name.get()}
Computer Name: {self.computer_name}
Username: {self.username}
Assignment: {self.selected_assignment.get()}
Submission Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

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
            smtp_server = self.config.get('email', 'smtp_server')
            smtp_port = self.config.getint('email', 'smtp_port')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            if self.debug_mode:
                self._results_text.insert(tk.END, "\n✓ Results emailed to instructor!\n", 'pass')
            
        except Exception as e:
            if self.debug_mode:
                self.results_text.insert(tk.END, f"\n✗ Failed to send email: {str(e)}\n", 'fail')
    
    def export_to_pdf(self):
        """Export code and results to PDF"""
        if not self.selected_file.get():
            messagebox.showwarning("No File", "Please select a file and check code first.")
            return
        
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Export Error", 
                "ReportLab library not installed. Install with: pip install reportlab")
            return
        
        try:
            # Ask where to save PDF
            pdf_filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                initialfile=f"{self.student_name.get()}_{self.selected_assignment.get()}_results.pdf"
            )
            
            if not pdf_filename:
                return
            
            # Create PDF
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for PDF elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor='darkblue',
                spaceAfter=30,
                alignment=TA_LEFT
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor='darkblue',
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Title
            elements.append(Paragraph("AutoGrader Results", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Student Information
            summary = self.grader.get_summary()
            info_text = f"""
            <b>Student:</b> {self.student_name.get()}<br/>
            <b>Computer:</b> {self.computer_name}<br/>
            <b>Username:</b> {self.username}<br/>
            <b>Assignment:</b> {self.selected_assignment.get()}<br/>
            <b>File:</b> {os.path.basename(self.selected_file.get())}<br/>
            <b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Score:</b> {summary['score']} ({summary['success_rate']:.1f}%)
            """
            elements.append(Paragraph(info_text, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Student Code Section
            elements.append(Paragraph("Student Code", heading_style))
            with open(self.selected_file.get(), 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            code_style = ParagraphStyle(
                'Code',
                parent=styles['Code'],
                fontSize=8,
                leading=10,
                leftIndent=10,
                rightIndent=10
            )
            elements.append(Preformatted(code_content, code_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Results Section
            elements.append(Paragraph("AutoGrader Results", heading_style))
            results_content = self.results_text.get(1.0, tk.END)
            elements.append(Preformatted(results_content, code_style))
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", f"PDF exported successfully to:\n{pdf_filename}")
            self.status_var.set(f"PDF exported to {os.path.basename(pdf_filename)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF: {str(e)}")
    
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Ready")


def main():
    """Main entry point"""
    try:
        print("Starting AutoGrader GUI...")
        root = tk.Tk()
        print("✓ Tk root window created")
        
        app = AutoGraderGUI(root)
        print("✓ AutoGraderGUI initialized")
        
        print("✓ Starting main loop...")
        root.mainloop()
        
    except Exception as e:
        print(f"ERROR in main(): {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
    