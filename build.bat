@echo off
REM Build script for Polyglot-LLM NVDA Addon

echo === Polyglot-LLM Build Script ===
echo.

REM Check if in virtual environment
if defined VIRTUAL_ENV (
    echo [OK] Virtual environment detected: %VIRTUAL_ENV%
    set PYTHON_CMD=python
) else (
    echo [WARNING] Not in virtual environment - using system Python
    set PYTHON_CMD=python
)

echo.
echo Checking for build dependencies...

REM Check for SCons and markdown
%PYTHON_CMD% -c "import SCons; import markdown" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build dependencies not found
    echo Installing build dependencies...
    pip install -r requirements-build.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
    echo [OK] Build dependencies installed
) else (
    echo [OK] Build dependencies found
)

echo.
echo Building addon...
%PYTHON_CMD% -m SCons

if %ERRORLEVEL% equ 0 (
    echo [OK] Build successful!
    echo.
    
    REM Find the addon file
    for %%f in (*.nvda-addon) do (
        echo Addon file created:
        echo   Name: %%f
        echo   Size: %%~zf bytes
        echo.
        echo Next steps:
        echo   1. Double-click %%f to install
        echo   2. Restart NVDA when prompted
        echo   3. Configure in NVDA -^> Preferences -^> Settings -^> Polyglot-LLM
        echo   4. See STATUS.md for testing checklist
        goto :found
    )
    
    echo [WARNING] .nvda-addon file not found
    :found
) else (
    echo [ERROR] Build failed - check errors above
    exit /b 1
)

echo.
echo === Build Complete ===
