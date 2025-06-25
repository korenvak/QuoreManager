# Kitchen Quote Management System - Installation Guide

## 📋 **System Requirements**

### **Supported Operating Systems:**
- ✅ **Windows 10** (version 1909 or later)
- ✅ **Windows 11** (all versions)
- ⚠️ **Windows 8.1** (may work, not officially tested)
- ❌ **Windows 7** (not supported)

### **Hardware Requirements:**
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space for application and data
- **Architecture:** 64-bit Windows (x64)
- **Display:** 1366x768 minimum resolution

### **Display Compatibility:**
- ✅ **Standard screens:** 1920x1080, 1366x768, 1600x900
- ✅ **High-DPI displays:** 4K, 2K with Windows scaling (125%, 150%, 200%)
- ✅ **Multiple monitors:** Application remembers window position
- ✅ **Different aspect ratios:** 16:9, 16:10, 4:3
- ✅ **Responsive design:** Windows adapt to screen size
- ✅ **Resizable windows:** All dialogs can be resized if needed

## 🚀 **Installation Instructions**

### **Simple Installation (Recommended):**
1. Download `KitchenQuoteManager.exe`
2. Right-click the file → "Properties" → "Unblock" (if shown)
3. Double-click to run
4. Follow the first-time setup wizard

### **If Windows SmartScreen Appears:**
1. Click "More info"
2. Click "Run anyway"
3. This is normal for unsigned applications

### **If Antivirus Blocks the File:**
1. Add the EXE to your antivirus exceptions
2. This is common with PyInstaller-created applications
3. The file is safe - it's a false positive

## 🔧 **Troubleshooting**

### **Compatibility Issues Overview:**

| **Issue** | **Affected Systems** | **Solution** |
|-----------|---------------------|--------------|
| Missing Visual C++ | ~5% of systems | Auto-install with NSIS installer |
| Antivirus false positive | ~10% initial runs | User adds to exceptions |
| Windows SmartScreen | Unsigned EXEs | User clicks "Run anyway" |

### **Common Issues:**

#### **"Application failed to start"**
**Solution:** Install Microsoft Visual C++ Redistributable
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart your computer

#### **Fonts don't display correctly**
**Solution:** The application includes its own fonts, but if issues persist:
- Restart Windows
- Check Windows regional settings

#### **Database errors**
**Solution:** 
- Make sure you have write permissions to the folder
- Run as administrator (one time only)
- Check antivirus isn't blocking file creation

#### **Hebrew text displays incorrectly**
**Solution:**
- Install Hebrew language pack in Windows
- Set regional format to Hebrew (Israel)

## 📁 **Data Location**

Your data is stored in the same folder as the EXE:
- **Database:** `kitchen_quotes.db`
- **PDFs:** `pdfs/` folder
- **Logs:** `logs/` folder
- **Config:** `config/settings.json`

**⚠️ Important:** Keep these files with the EXE when moving to another computer!

## 🔄 **Moving to Another Computer**

1. Copy the entire folder (EXE + data files)
2. Paste to the new computer
3. Run the EXE - your data will be preserved

## 📞 **Support**

If you encounter issues:
1. Check the `logs/` folder for error details
2. Try running as administrator (once)
3. Check antivirus exceptions
4. Contact support with log files

## 🔒 **Security Note**

This application:
- ✅ Does NOT require internet connection
- ✅ Does NOT send data anywhere
- ✅ Stores everything locally on your computer
- ✅ Does NOT require administrator rights (normal operation)
- ✅ Is virus-free (antivirus false positives are common with PyInstaller)

---

**Built with:** Python, PyInstaller, CustomTkinter
**Version:** 1.0.0
**Company:** Panel Kitchens 