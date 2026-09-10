@echo off
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

set "VENV_PYTHON=%ROOT_DIR%\venv\Scripts\python.exe"
set "PACKAGE_DIR=%ROOT_DIR%\pyslick_package\pyslick"
set "MAIN_PY=%PACKAGE_DIR%\__main__.py"
set "PYSLICK_BAT=%ROOT_DIR%\pyslick.bat"

echo =======================================================
echo Setting up PySlick Environment and PATH Configuration
echo =======================================================

if exist "%PACKAGE_DIR%" (
    echo Creating __main__.py entry point...
    (
        echo import sys
        echo from pyslick import main
        echo.
        echo if __name__ == "__main__":
        echo     main^(^)
    ) > "%MAIN_PY%"
    echo [OK] __main__.py created at %MAIN_PY%
) else (
    echo [ERROR] Could not find package directory at %PACKAGE_DIR%
    goto :END
)

echo Creating pyslick.bat wrapper...
(
    echo @echo off
    echo set "VENV_PYTHON=%%~dp0venv\Scripts\python.exe"
    echo if exist "%%VENV_PYTHON%%" ^(
    echo     "%%VENV_PYTHON%%" -m pyslick %%*
    echo ^) else ^(
    echo     python -m pyslick %%*
    echo ^)
) > "%PYSLICK_BAT%"
echo [OK] pyslick.bat created at %PYSLICK_BAT%

if exist "%VENV_PYTHON%" (
    echo Installing pyslick_package in editable mode...
    "%VENV_PYTHON%" -m pip install -e "%ROOT_DIR%\pyslick_package"
    echo [OK] Package installed in editable mode.
) else (
    echo [WARNING] Virtual environment not found at %VENV_PYTHON%. Skipping pip install.
)

echo Adding %ROOT_DIR% to User PATH...
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"

echo !USER_PATH! | find /i "%ROOT_DIR%" >nul
if %errorlevel% equ 0 (
    echo [NOTICE] Directory already exists in User PATH.
) else (
    if defined USER_PATH (
        set "NEW_PATH=!USER_PATH!;%ROOT_DIR%"
    ) else (
        set "NEW_PATH=%ROOT_DIR%"
    )
    setx PATH "!NEW_PATH!" >nul
    echo [OK] Successfully added %ROOT_DIR% to User PATH!
)

echo.
echo =======================================================
echo Setup Complete!
echo Restart your terminal for PATH changes to take effect.
echo You can then run 'pyslick --help' from anywhere.
echo =======================================================

:END
pause
