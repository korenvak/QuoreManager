# Kitchen Quote Management System - Build & Deployment Guide

## 🚀 Building Standalone EXE

### Prerequisites

1. **Python Environment**
   - Python 3.9+ installed
   - All dependencies from `requirements.txt`

2. **Install Build Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Building Process

1. **Prepare for Build**
   ```bash
   # Ensure all dependencies are installed
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   
   # Test the application first
   python run.py
   ```

2. **Build the EXE**
   ```bash
   # Run the build script
   python build_exe.py
   ```

3. **Output**
   - EXE file: `dist/KitchenQuoteManager.exe`
   - Size: ~50-80 MB (includes Python runtime)
   - All resources and dependencies embedded

### Build Configuration

The build script creates a PyInstaller spec file with:

- **Included Resources:**
  - All UI resources (fonts, images, icons)
  - Configuration files
  - Documentation

- **Hidden Imports:**
  - CustomTkinter and all GUI dependencies
  - Database libraries (SQLAlchemy, SQLite)
  - Excel handling (openpyxl, pandas)
  - Hebrew text support (bidi, arabic-reshaper)

- **Optimizations:**
  - UPX compression enabled
  - Unused modules excluded
  - Console window disabled for production

## 📦 Creating Installer (Optional)

### Using NSIS

1. **Install NSIS**
   - Download from: https://nsis.sourceforge.io/
   - Install on Windows

2. **Build Installer**
   ```bash
   # After building EXE, the script creates installer.nsi
   makensis installer.nsi
   ```

3. **Result**
   - Professional Windows installer
   - Start menu shortcuts
   - Desktop shortcut
   - Uninstaller included
   - Registry entries for Add/Remove Programs

## 🔧 Development Workflow

### Directory Structure
```
QuoreManager/
├── main.py                 # Application entry point
├── run.py                  # Development launcher
├── build_exe.py           # EXE build script
├── requirements.txt       # Python dependencies
├── BUILD_GUIDE.md         # This guide
├── config/
│   ├── settings.json      # Application settings
│   └── kitchen_quotes.db  # SQLite database
├── ui/
│   ├── dashboard.py       # Main dashboard
│   ├── login.py          # Authentication
│   └── pages/            # Individual pages
├── database/
│   ├── models.py         # Database models
│   └── db_manager.py     # Database operations
├── resources/
│   ├── fonts/           # Hebrew fonts
│   ├── images/          # UI images
│   └── icons/           # Application icons
└── utils/
    ├── excel_handler.py  # Excel catalog management
    ├── pdf_generator.py  # PDF generation (future)
    └── helpers.py        # Utility functions
```

### Testing Before Build

1. **Run Development Version**
   ```bash
   python run.py
   ```

2. **Test All Features**
   - User authentication
   - Customer management
   - Quote creation wizard
   - Database operations
   - Excel catalog loading

3. **Check Database**
   - Verify database creation
   - Test CRUD operations
   - Confirm data persistence

## 🎯 Distribution Strategy

### For End Users

1. **Simple Distribution**
   - Share `KitchenQuoteManager.exe` directly
   - 50-80 MB single file
   - No installation required
   - Runs on any Windows 10/11 machine

2. **Professional Distribution**
   - Use NSIS installer
   - Proper installation experience
   - Start menu integration
   - Easy uninstallation

### System Requirements

- **Operating System:** Windows 10/11
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Storage:** 100MB free space
- **Display:** 1280x720 minimum resolution
- **Additional:** No admin rights required for running

## 🛠️ Advanced Configuration

### Performance Tuning

1. **Startup Optimization**
   ```python
   # In build_exe.py, modify spec file:
   # Use --onedir instead of --onefile for faster startup
   exe = EXE(..., onefile=False)  # Creates folder with files
   ```

2. **Size Optimization**
   ```python
   # Add more exclusions to reduce size
   excludes=[
       'matplotlib', 'numpy.testing', 'pytest',
       'setuptools', 'distutils', 'email',
       'html', 'http', 'urllib', 'xml'
   ]
   ```

### Debug Build

For troubleshooting, create debug version:

```python
# In kitchen_quotes.spec
console=True,  # Show console for debugging
debug=True,    # Enable debug output
```

### Custom Icon

Replace default icon:
1. Place new icon in `resources/White_Logo.ico`
2. Rebuild EXE
3. Icon will be embedded automatically

## 🔍 Troubleshooting

### Common Build Issues

1. **Missing Dependencies**
   ```bash
   # Solution: Install missing packages
   pip install package_name
   ```

2. **Import Errors**
   ```python
   # Add to hidden_imports in spec file
   hidden_imports = ['missing_module']
   ```

3. **Resource Files Missing**
   ```python
   # Add to datas in spec file
   datas = [('path/to/resource', 'destination')]
   ```

### Runtime Issues

1. **Application Won't Start**
   - Check Windows Defender / Antivirus
   - Run from command line to see errors
   - Try debug build

2. **Database Errors**
   - Ensure write permissions to app directory
   - Check if database file is created
   - Verify SQLite compatibility

3. **Font/UI Issues**
   - Verify Heebo font is included
   - Check display scaling settings
   - Test on different Windows versions

## 📋 Deployment Checklist

### Before Building
- [ ] All features tested and working
- [ ] No debug code or test data
- [ ] Version number updated
- [ ] Icon and resources finalized
- [ ] Database schema stable

### After Building
- [ ] EXE runs on clean Windows machine
- [ ] All features work in standalone mode
- [ ] Database creation and operations work
- [ ] UI displays correctly
- [ ] No console errors or warnings

### Distribution
- [ ] Installer tested (if using NSIS)
- [ ] Documentation prepared
- [ ] User guide created
- [ ] Support contact information included
- [ ] Update mechanism planned (for future)

## 🔄 Update Strategy

### Version Management

1. **Semantic Versioning**
   - Major.Minor.Patch (e.g., 1.0.0)
   - Update version in build script

2. **Database Migration**
   - Plan schema changes carefully
   - Implement migration scripts
   - Test upgrade process

3. **User Communication**
   - Release notes
   - Backup instructions
   - Migration guide

### Auto-Update (Future Enhancement)

Consider implementing:
- Update checker on startup
- Download and install mechanism
- Backup before update
- Rollback capability

## 🎨 Customization

### Branding

1. **Company Information**
   - Update in `config/settings.json`
   - Modify installer script
   - Replace logo images

2. **UI Theme**
   - Colors in `ui/dashboard.py`
   - Fonts in resources
   - Layout adjustments

3. **Legal Text**
   - Terms and conditions
   - Privacy policy
   - License information

## 📞 Support

### For Developers

- Review code comments
- Check database schema
- Test all user workflows
- Document any customizations

### For Users

- Prepare user manual
- Create video tutorials
- Set up support channels
- Plan training sessions

---

**Built with ❤️ for Kitchen Design Professionals**

*This application was designed specifically for Hebrew-speaking kitchen design professionals, with RTL support, modern UI, and comprehensive quote management capabilities.* 