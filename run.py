#!/usr/bin/env python3
"""
Kitchen Quote Management System - Run Script
Simple launcher that sets up the environment and starts the application
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'customtkinter',
        'PIL',  # This is the import name for pillow
        'openpyxl', 
        'pandas',
        'reportlab',
        'cryptography',
        'sqlalchemy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main entry point"""
    print("Kitchen Quote Management System")
    print("=" * 50)
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return 1
    
    print("Dependencies OK ✓")
    
    # Import and run main application
    try:
        from main import main as app_main
        print("Starting application...")
        app_main()
        return 0
        
    except ImportError as e:
        print(f"Failed to import application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 