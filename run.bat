@echo off
echo ========================================
echo    QR Code Generator - Starting...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run the following commands first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask not found in virtual environment!
    echo Please install dependencies:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Starting Flask application...
echo.
echo ========================================
echo    Application will be available at:
echo    http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask application
python app.py

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat