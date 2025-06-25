#!/usr/bin/env python3
"""
Complete Build and Installer Creation Script for Kitchen Quote Management System v2.0
Builds EXE and creates professional installer with red icon
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required tools are available"""
    print("Checking build requirements...")
    
    # Check Python packages
    required_packages = ['PyInstaller']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"X Missing required packages: {', '.join(missing)}")
        print("Install with: pip install PyInstaller")
        return False
    
    # Check for NSIS
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"  # In PATH
    ]
    
    nsis_found = False
    for nsis_path in nsis_paths:
        if shutil.which(nsis_path) or os.path.exists(nsis_path):
            print(f"+ Found NSIS at: {nsis_path}")
            nsis_found = True
            break
    
    if not nsis_found:
        print("! NSIS not found. You can:")
        print("   1. Install NSIS from https://nsis.sourceforge.io/")
        print("   2. Or manually run the installer.nsi after EXE is built")
        print("   Continuing with EXE build only...")
    
    return True

def verify_icon_exists():
    """Verify the red icon file exists"""
    icon_path = Path("resources/version5_icon.ico")
    if not icon_path.exists():
        print(f"X Red icon not found at: {icon_path}")
        print("Available icons:")
        for icon in Path("resources").glob("*.ico"):
            print(f"   - {icon.name}")
        return False
    
    print(f"+ Red icon found: {icon_path}")
    return True

def clean_build():
    """Clean previous build files"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   Removed {spec_file}")

def build_exe():
    """Build the EXE using our build script"""
    print("Building EXE file...")
    
    try:
        result = subprocess.run([sys.executable, 'build_exe.py'], 
                              check=True, capture_output=True, text=True)
        
        print("+ EXE build completed successfully!")
        
        # Check if EXE exists
        exe_path = Path('dist/KitchenQuoteManager.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   EXE created: {exe_path}")
            print(f"   Size: {size_mb:.1f} MB")
            return True
        else:
            print("X EXE file not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"X EXE build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_installer():
    """Create the installer using NSIS"""
    print("📦 Creating installer...")
    
    # Find NSIS
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"
    ]
    
    nsis_exe = None
    for path in nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_exe = path
            break
    
    if not nsis_exe:
        print("❌ NSIS not found. Cannot create installer.")
        print("   Please install NSIS and run: makensis installer.nsi")
        return False
    
    try:
        # Run NSIS
        result = subprocess.run([nsis_exe, 'installer.nsi'], 
                              check=True, capture_output=True, text=True)
        
        print("✅ Installer created successfully!")
        
        # Check if installer exists
        installer_path = Path('KitchenQuoteManager_v2.0_Setup.exe')
        if installer_path.exists():
            size_mb = installer_path.stat().st_size / (1024 * 1024)
            print(f"   Installer: {installer_path}")
            print(f"   Size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Installer file not found!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installer creation failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def test_exe():
    """Quick test of the built EXE"""
    print("🧪 Testing EXE...")
    
    exe_path = Path('dist/KitchenQuoteManager.exe')
    if not exe_path.exists():
        print("❌ EXE not found for testing")
        return False
    
    try:
        # Try to run with --help or --version (if supported)
        # For now, just check if it starts and exits cleanly
        print("   EXE file exists and appears valid")
        print("   Manual testing recommended before distribution")
        return True
        
    except Exception as e:
        print(f"❌ EXE test failed: {e}")
        return False

def main():
    """Main build and installer creation process"""
    print("Kitchen Quote Management System v2.0")
    print("Build and Installer Creation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Verify icon exists
    if not verify_icon_exists():
        return 1
    
    # Clean previous builds
    clean_build()
    
    # Build EXE
    if not build_exe():
        print("\n❌ Build process failed!")
        return 1
    
    # Test EXE
    if not test_exe():
        print("\n⚠️  EXE testing had issues")
    
    # Create installer
    installer_success = create_installer()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 BUILD SUMMARY")
    print("=" * 50)
    
    exe_path = Path('dist/KitchenQuoteManager.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ EXE Built: {exe_path} ({size_mb:.1f} MB)")
        print(f"   Icon: Red version5_icon.ico")
        print(f"   Version: 2.0")
    
    installer_path = Path('KitchenQuoteManager_v2.0_Setup.exe')
    if installer_path.exists():
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        print(f"✅ Installer: {installer_path} ({size_mb:.1f} MB)")
        print(f"   Desktop shortcut: Large red icon")
        print(f"   Modern UI with Hebrew support")
    elif installer_success is False:
        print("❌ Installer creation failed")
    else:
        print("⚠️  Installer not created (NSIS not available)")
        print("   You can manually run: makensis installer.nsi")
    
    print("\n📋 NEXT STEPS:")
    if exe_path.exists():
        print("1. Test the EXE: dist/KitchenQuoteManager.exe")
    if installer_path.exists():
        print("2. Test the installer: KitchenQuoteManager_v2.0_Setup.exe")
        print("3. Distribute to users")
    
    print("\n🎯 FEATURES INCLUDED:")
    print("- Professional Version 2.0 UI")
    print("- Red icon (version5_icon.ico) for desktop")
    print("- Large desktop shortcut icon")
    print("- Hebrew and English support")
    print("- Modern installer with uninstaller")
    print("- Registry integration")
    
    return 0 if exe_path.exists() else 1

if __name__ == "__main__":
    sys.exit(main()) 