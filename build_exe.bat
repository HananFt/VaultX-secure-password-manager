@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo        VaultX - Windows EXE Builder
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [1/4] Creating virtual environment...
    py -3 -m venv venv
    if errorlevel 1 (
        echo ERROR: Could not create the virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Using existing virtual environment...
)

echo.
echo [2/4] Installing build dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements-build.txt
if errorlevel 1 (
    echo.
    echo ERROR: Could not install build dependencies.
    pause
    exit /b 1
)

echo.
echo [3/4] Building VaultX.exe...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

venv\Scripts\python.exe -m PyInstaller --clean --noconfirm "VaultX.spec"
if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete.
echo.
echo Executable:
echo     %CD%\dist\VaultX.exe
echo.
echo You can run it by double-clicking the EXE.
echo Your local vault data remains in vault.json beside the EXE.
echo.
pause
