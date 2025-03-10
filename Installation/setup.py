#!/usr/bin/env python3

import sys
import subprocess
import os

# List of required packages
REQUIRED_PACKAGES = [
    "py-cord",
    "numpy",
    "customtkinter",
    "pyautogui",
    "keyboard",
    "mss",
    # 'subprocess' is part of the standard library, no need to install
    "configparser",
    "Pillow",  # 'PIL' is now 'Pillow' for pip install
    "mouse",
    "pyinstaller",
    # 'keyboard' is listed twice in the original script, so we'll keep it once  # This covers win32gui, win32con on Windows; does nothing on Mac/Linux
    "requests",
    "opencv-python",
    "pynput",
    "multiprocessing",
]

def ensure_pip_installed():
    """
    Ensure pip is installed. On some Python versions, ensurepip may
    be available to install/upgrade pip.
    """
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        # Attempt to install pip using ensurepip
        try:
            print("pip not found. Attempting to install using ensurepip...")
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
        except subprocess.CalledProcessError:
            print("Failed to install pip via ensurepip.")
            sys.exit(1)

def install_packages():
    """
    Installs the required packages via pip. Exits on failure.
    """
    ensure_pip_installed()

    print("Installing required modules...")
    for pkg in REQUIRED_PACKAGES:
        print(f"Installing {pkg}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--no-input", pkg, "--quiet", "--quiet", "--quiet",], check=True,)
            print(f"\n")
        except subprocess.CalledProcessError:
            print(f"Failed to install {pkg}\nExiting...")
            os.system("cls")
            sys.exit(1)


    print("\nInstallation complete!")

def uninstall_packages():
    print("We dont uninstall modules round here")
    os.system("cls")
    # Example:
    # for pkg in REQUIRED_PACKAGES:
    #     subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg])

def main_menu():
    while True:
        os.system("cls")
        print("\nWelcome to the Sapphire Macro Installer!")
        print("1. Install Sapphire Macro")
        print("2. Uninstall Sapphire Macro")
        print("3. Exit")
        choice = input("Select an option (1-3): ")

        if choice == "1":
            os.system("cls")
            install_packages()
        elif choice == "2":
            os.system("cls")
            uninstall_packages()
        elif choice == "3":
            os.system("cls")
            sys.exit(0)

        else:
            os.system("cls")
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main_menu() 
