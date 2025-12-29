@echo off
REM Simple setup script for Windows
echo Setting up EduPace development environment...

python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

echo Setup complete!
echo To activate the virtual environment, run: venv\Scripts\activate

