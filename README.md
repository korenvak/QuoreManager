# Kitchen Quote Management System
## מערכת ניהול הצעות מטבח

A comprehensive desktop application for managing kitchen quotes with customer management, catalog integration, PDF generation, and user permissions. Built with Python and CustomTkinter for a modern, professional interface with full Hebrew RTL support.

## Features / תכונות

### Core Features
- **Customer Management** - ניהול לקוחות מתקדם
- **Quote Creation** - יצירת הצעות מחיר מקצועיות
- **Catalog Integration** - אינטגרציה עם קטלוג Excel
- **PDF Generation** - יצירת PDF מקצועי עם לוגו וחותמת מים
- **User Management** - ניהול משתמשים עם הרשאות
- **Auto-save Drafts** - שמירה אוטומטית של טיוטות
- **Theme Support** - תמיכה בערכות נושא בהיר/כהה

### User Roles / תפקידי משתמש
- **Admin** - מנהל מערכת (הרשאות מלאות)
- **Manager** - מנהל (יצירת הצעות ללא הגבלת הנחה)
- **Employee** - עובד (יצירת הצעות עם הגבלת הנחה)
- **Viewer** - צופה (צפייה בלבד)

### Technical Features
- Modern UI with CustomTkinter
- Hebrew RTL text support
- SQLite database with SQLAlchemy ORM
- Excel catalog reading with image support
- PDF generation with ReportLab
- Secure password hashing
- Session management
- Audit logging
- Automatic backups

## Installation / התקנה

### Prerequisites / דרישות מקדימות
- Python 3.8 or higher
- Windows 10/11 (recommended)

### Quick Start / התחלה מהירה

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd QuoreManager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

### Alternative Installation / התקנה אלטרנטיבית

1. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## First Run Setup / הגדרה ראשונית

On first run, the application will guide you through creating an admin user:

1. Enter username (minimum 3 characters)
2. Enter first and last name
3. Create a secure password
4. Click "Create Admin and Enter System"

## Usage / שימוש

### Customer Management / ניהול לקוחות
- Add new customers with unique identifiers
- Search and filter customer list
- Edit customer information
- View customer quote history

### Quote Creation / יצירת הצעות מחיר
The quote creation wizard includes 5 steps:
1. **Customer Selection** - בחירת לקוח
2. **Customer Details** - פרטי לקוח (אם חדש)
3. **Item Selection** - בחירת פריטים מהקטלוג
4. **Discounts & Calculations** - הנחות וחישובים
5. **Images & Finalization** - תמונות וסיום

### Catalog Management / ניהול קטלוג
- Import catalog from Excel files
- Support for categories and subcategories
- Image integration from Excel
- Search and filter catalog items

### PDF Generation / יצירת PDF
- Professional Hebrew RTL layout
- Company logo and watermark
- Item breakdown with calculations
- Terms and conditions
- Signature section

## Configuration / תצורה

### Catalog File Format / פורמט קובץ קטלוג
The system supports Excel files with the following structure:
- Categories in single cells above item groups
- Item rows with name, price, description
- Images embedded in Excel cells
- Multiple worksheets supported

Example structure:
```
Category: Kitchen Cabinets
Item Name          Price    Description
Base Cabinet 60cm  1200     Standard base cabinet
Base Cabinet 80cm  1500     Wide base cabinet
```

### Settings / הגדרות
Configure the system through the Settings page:
- Company information
- VAT rates and calculations
- Theme preferences
- File paths
- User permissions

## File Structure / מבנה קבצים

```
QuoreManager/
├── main.py                 # Main application entry point
├── run.py                  # Simple run script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/              # Database models and management
│   ├── models.py          # SQLAlchemy models
│   └── db_manager.py      # Database operations
├── core/                  # Core business logic
│   └── auth.py           # Authentication and permissions
├── ui/                    # User interface components
│   ├── login.py          # Login window
│   ├── first_run.py      # First run setup
│   ├── dashboard.py      # Main dashboard
│   └── pages/            # Individual pages
├── utils/                 # Utility functions
│   ├── logger.py         # Logging configuration
│   ├── helpers.py        # Helper functions
│   ├── rtl.py           # Hebrew RTL support
│   └── excel_handler.py  # Excel/catalog handling
├── backhand/             # Backend services
│   └── pdf_generator.py  # PDF generation (existing)
├── resources/            # Static resources
│   ├── fonts/           # Hebrew fonts
│   ├── images/          # Icons and logos
│   └── modern_theme.css # UI styling
└── config/              # Configuration files
    ├── settings.py      # Settings manager
    └── kitchen_quotes.db # SQLite database (created on first run)
```

## Development / פיתוח

### Running in Development Mode
```bash
python main.py
```

### Building Executable
To create a standalone EXE file:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "resources;resources" main.py
```

### Database Schema
The application uses SQLite with the following main tables:
- `users` - User accounts and roles
- `customers` - Customer information
- `quotes` - Quote data with items and calculations
- `drafts` - Auto-saved draft data
- `audit_logs` - System activity logging
- `system_settings` - Configuration storage

## Troubleshooting / פתרון בעיות

### Common Issues / בעיות נפוצות

1. **Import Errors:**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

2. **Font Issues:**
   - Hebrew fonts (Heebo) are included in resources/
   - System will fallback to default fonts if Heebo unavailable

3. **Database Issues:**
   - Database is created automatically on first run
   - Check write permissions in application directory

4. **Catalog Loading Issues:**
   - Ensure Excel file is not password protected
   - Check file format matches expected structure
   - Images should be embedded in Excel cells

### Logs / רישום פעילות
Application logs are stored in the `logs/` directory:
- `kitchen_quotes_YYYYMMDD.log` - General application logs
- `kitchen_quotes_errors_YYYYMMDD.log` - Error-only logs

## Security / אבטחה

- Passwords are hashed using SHA-256 with salt
- Session management with configurable timeouts
- Role-based access control
- Audit logging for all critical operations
- Input validation and sanitization

## License / רישיון

This project is proprietary software for Kitchen Studio.

## Support / תמיכה

For support and questions, contact the development team.

---

**Kitchen Quote Management System** - Built with ❤️ for professional kitchen designers 