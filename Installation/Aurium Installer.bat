@echo off
title Sapphire Macro Installer
setlocal enabledelayedexpansion

rem Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Installing Python...
    curl -L -o python-3.13.1.exe https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe
    if errorlevel 1 (
        echo Failed to download Python
        pause
        exit /b
    )
    start /wait python-3.13.1.exe /quiet InstallAllUsers=1 PrependPath=1
    if errorlevel 1 (
        echo Failed to install Python
        pause
        exit /b
    )
    echo Python installed successfully.
    echo Adding Python to PATH...
    setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python313\Scripts\" /m
    if errorlevel 1 (
        echo Failed to add Python to PATH
        pause
        exit /b
    )
    echo Python added to PATH successfully.
)

:main_menu
cls
echo Welcome to the Sapphire Macro Installer!
echo:
echo 1. Install Sapphire Macro
echo:
echo 2. Uninstall Sapphire Macro
echo:
echo 3. Upgrade your modules (do this after you install your modules)
echo:
echo 4. Exit
echo:
set /p choice="Select an option (1-3): "

if "%choice%"=="1" (
    goto install
) else if "%choice%"=="2" (
    goto uninstall
) else if "%choice%"=="3" (
    goto upgrade
) else if "%choice%"=="4" (
    cls
    exit /b
) else (
    echo Invalid option. Please try again.
    goto main_menu
)

:install
rem Check for pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    curl -L -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    if errorlevel 1 (
        echo Failed to download get-pip.py
        pause
        exit /b
    )
    python get-pip.py
    if errorlevel 1 (
        echo Failed to install pip
        pause
        exit /b
    )
    del get-pip.py
)

rem Install pip itself
python -m ensurepip --upgrade
if errorlevel 1 (
    echo Failed to upgrade pip
    pause
    exit /b
)
if errorlevel 0 (
    echo:
)
echo Installing required modules...
echo:

rem Install modules with full error checks:

pip install -q py-cord
if errorlevel 0 (
    echo Successfully Installed: py-cord
    echo:
)
if errorlevel 1 (
    echo Failed to install py-cord
    echo:
    exit /b
)

pip install -q customtkinter
if errorlevel 0 (
    echo Successfully Installed: customtkinter
    echo:
)
if errorlevel 1 (
    echo Failed to install customtkinter
    echo:
    exit /b
)

pip install -q pyautogui
if errorlevel 0 (
    echo Successfully Installed: pyautogui
    echo:
)
if errorlevel 1 (
    echo Failed to install pyautogui
    echo:
    exit /b
)

pip install -q pytesseract
if errorlevel 0 (
    echo Successfully Installed: pytesseract
    echo:
)
if errorlevel 1 (
    echo Failed to install pytesseract
    echo:
    exit /b
)

pip install -q keyboard
if errorlevel 0 (
    echo Successfully Installed: keyboard
    echo:
)
if errorlevel 1 (
    echo Failed to install keyboard
    echo:
    exit /b
)

pip install -q configparser
if errorlevel 0 (
    echo Successfully Installed: configparser
    echo:
)
if errorlevel 1 (
    echo Failed to install configparser
    echo:
    exit /b
)

pip install -q Pillow
if errorlevel 0 (
    echo Successfully Installed: Pillow
    echo:
)
if errorlevel 1 (
    echo Failed to install Pillow
    echo:
    exit /b
)

pip install -q mouse
if errorlevel 0 (
    echo Successfully Installed: mouse
    echo:
)
if errorlevel 1 (
    echo Failed to install mouse
    echo:
    exit /b
)

pip install -q pyinstaller
if errorlevel 0 (
        echo Successfully Installed: pyinstaller
    echo:
)
if errorlevel 1 (
    echo Failed to install pyinstaller
    echo:
    exit /b
)

rem Note: The user installed keyboard again below, mirroring the original script
pip install -q keyboard
if errorlevel 0 (
    echo Successfully Installed: keyboard
    echo:
)
if errorlevel 1 (
    echo Failed to install keyboard
    echo:
    exit /b
)

pip install -q pywin32
if errorlevel 0 (
    echo Successfully Installed: pywin32
    echo:
)
if errorlevel 1 (
    echo Failed to install pywin32
    echo:
    exit /b
)

pip install -q requests
if errorlevel 0 (
    echo Successfully Installed: requests
    echo:
)
if errorlevel 1 (
    echo Failed to install requests
    echo:
    exit /b
)

pip install -q pynput
if errorlevel 0 (
    echo Successfully Installed: pynput
    echo:
)
if errorlevel 1 (
    echo Failed to install pynput
    echo:
    exit /b
)

pip install -q numpy
if errorlevel 0 (
    echo Successfully Installed: numpy
    echo:
)
if errorlevel 1 (
    echo Failed to install numpy
    echo:
    exit /b
)

pip install -q opencv-python
if errorlevel 0 (
    echo Successfully Installed: opencv-python
    echo:
)
if errorlevel 1 (
    echo Failed to install opencv-python
    echo:
    exit /b
)

pip install -q ahk
if errorlevel 0 (
    echo Successfully Installed: AHK
    echo:
)
if errorlevel 1 (
    echo Failed to install AHK
    echo:
    exit /b
)
pip install -q PyQt6
if errorlevel 0 (
    echo Successfully Installed: PyQt6
    echo:
)
if errorlevel 1 (
    echo Failed to install PyQt6
    echo:
    exit /b
)
pip install -q threading
if errorlevel 0 (
    echo Successfully Installed: threading
    echo:
)
if errorlevel 1 (
    echo Failed to install threading
    echo:
    exit /b
)

echo Installation complete!
pause
goto main_menu

:uninstall
pip uninstall py-cord customtkinter pyautogui pytesseract keyboard configparser Pillow mouse pyinstaller keyboard pywin32 requests pynput numpy opencv-python ahk PyQt5 --no-input
echo successfully uninstalled your modules
pause
goto main_menu

:upgrade
upgrade py-cord customtkinter pyautogui pytesseract keyboard configparser Pillow mouse pyinstaller keyboard pywin32 requests pynput numpy opencv-python

if errorlevel 1 (
    echo Failed to upgrade your modules
    pause
    exit /b
)

echo i was lazy to do the whole thing so i did sum
goto main_menu
