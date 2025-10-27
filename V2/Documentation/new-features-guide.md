# AutoGrader Setup Instructions - Complete Workflow

Quick reference guide for setting up and using the AutoGrader system.

## Quick Setup (5 Steps)

```bash
# 1. Install dependencies
pip install pandas openpyxl matplotlib numpy reportlab pyinstaller

# 2. Generate assignments Excel file
python create_assignments_excel.py

# 3. Generate example submissions (optional, for testing)
python example_student_submissions.py

# 4. Embed resources
python encode_resources.py

# 5. Build executable
pyinstaller autograder.spec
```

## File Structure

```
AutoGrader/
├── autograder.py                    # Core AutoGrader class
├── autograder_gui.py                # GUI application
├── config.ini                       # Email configuration (will be embedded)
├── assignments.xlsx                 # Assignments (will be embedded)
├── encode_resources.py              # Script to embed files
├── embedded_resources.py            # Generated embedded files
├── create_assignments_excel.py      # Generate Excel