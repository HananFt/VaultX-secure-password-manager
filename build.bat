@echo off
echo ==========================================
echo   Building VaultX Windows Application
echo ==========================================

:: 1. Clean old builds
echo [1/3] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output

:: 2. Build the executable with PyInstaller
echo [2/3] Compiling Python to EXE...
pyinstaller VaultX.spec --noconfirm
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller failed!
    pause
    exit /b %errorlevel%
)

:: 3. Build the Installer with Inno Setup
echo [3/3] Creating Windows Installer...
:: Note: This assumes Inno Setup 6 is installed in the default directory.
:: If it fails, ensure Inno Setup is installed and update the path below.
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup failed! Is Inno Setup 6 installed?
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo   BUILD SUCCESSFUL!
echo   Installer located at: installer_output\VaultX-Setup.exe
echo ==========================================
pause