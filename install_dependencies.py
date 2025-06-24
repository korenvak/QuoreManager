#!/usr/bin/env python3
"""
Dependency Installer for Kitchen Quote Management System
Installs all required dependencies automatically
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install all dependencies"""
    print("Kitchen Quote Management System - Dependency Installer")
    print("=" * 60)
    
    # Check if requirements.txt exists
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing dependencies from requirements.txt...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("✓ All dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies: {e}")
            return False
    else:
        print("requirements.txt not found, installing packages individually...")
        
        packages = [
            'customtkinter>=5.2.0',
            'pillow>=10.0.0',
            'openpyxl>=3.1.0',
            'pandas>=2.0.0',
            'reportlab>=4.0.0',
            'cryptography>=41.0.0',
            'python-bidi>=0.4.2',
            'arabic-reshaper>=3.0.0',
            'sqlalchemy>=2.0.0'
        ]
        
        failed_packages = []
        
        for package in packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✓ {package} installed")
            else:
                print(f"✗ Failed to install {package}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\nFailed to install: {', '.join(failed_packages)}")
            return False
        else:
            print("\n✓ All dependencies installed successfully!")
            return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nYou can now run the application with:")
        print("python main.py")
    else:
        print("\nPlease check the error messages above and try again.")
    
    input("Press Enter to continue...")
    sys.exit(0 if success else 1) 