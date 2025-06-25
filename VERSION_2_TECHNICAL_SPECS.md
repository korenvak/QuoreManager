# QuoreManager 2.0 - Technical Specifications

## 🗄️ Database Schema Changes

### New Catalog Table Structure
```sql
CREATE TABLE catalog_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    category TEXT NOT NULL,
    units TEXT NOT NULL, -- 'יחידה', 'מ"ר', 'מ"א', 'ק"ג', etc.
    cost DECIMAL(10,2) NOT NULL, -- Support decimal pricing
    manager_approve TEXT CHECK(manager_approve IN ('y', 'n')) DEFAULT 'n',
    comments TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Migration Strategy
```python
# Migration script to convert existing catalog
def migrate_catalog_v1_to_v2():
    # Map Hebrew columns to English
    # Convert integer prices to decimal
    # Add default values for new columns
    # Preserve existing data integrity
```

### User Management Simplification
```sql
-- Simplified users table
CREATE TABLE users_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user')) NOT NULL,
    full_name TEXT,
    email TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 🎨 Theme System Architecture

### Theme Configuration
```json
{
  "themes": {
    "dark_blue": {
      "name": "Dark Blue",
      "primary_color": "#1e3a8a",
      "background": "#0f172a",
      "surface": "#1e293b",
      "text": "#f1f5f9",
      "accent": "#3b82f6"
    },
    "dark_red": {
      "name": "Dark Red", 
      "primary_color": "#dc2626",
      "background": "#0f0f0f",
      "surface": "#1f1f1f",
      "text": "#f9fafb",
      "accent": "#ef4444"
    },
    "light_blue": {
      "name": "Light Blue",
      "primary_color": "#2563eb",
      "background": "#ffffff",
      "surface": "#f8fafc",
      "text": "#0f172a",
      "accent": "#3b82f6"
    }
  }
}
```

### CSS Variable System
```css
:root {
  --primary-color: var(--theme-primary);
  --bg-color: var(--theme-background);
  --surface-color: var(--theme-surface);
  --text-color: var(--theme-text);
  --accent-color: var(--theme-accent);
}
```

---

## 📝 Approval Workflow Logic

### Quote Status Flow
```python
class QuoteStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval" 
    APPROVED = "approved"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

def can_save_as_quote(items, user_role):
    """Check if all items are manager approved"""
    if user_role != 'admin':
        return False
    
    for item in items:
        if item.manager_approve != 'y':
            return False
    return True
```

### Permission Matrix
```
Action                  | Admin | User
------------------------|-------|------
View all quotes        |   ✓   |   ✗
View own quotes        |   ✓   |   ✓
Edit any quote         |   ✓   |   ✗
Edit own quotes        |   ✓   |   ✓
Save as quote          |   ✓   |   ✗
Save as draft          |   ✓   |   ✓
Approve catalog items  |   ✓   |   ✗
Manage users           |   ✓   |   ✗
```

---

## 📊 Enhanced PDF Generation

### Multi-Photo Layout Algorithm
```python
def calculate_photo_layout(photo_count):
    """Calculate optimal photo grid layout"""
    if photo_count <= 2:
        return (1, photo_count)  # 1 row
    elif photo_count <= 4:
        return (2, 2)  # 2x2 grid
    elif photo_count <= 6:
        return (2, 3)  # 2x3 grid
    else:
        return (3, 3)  # 3x3 grid (max 9 photos)
```

### Legal Terms Template
```python
LEGAL_TERMS_HEBREW = """
הצעת המחיר תקפה ל־14 ימים ממועד הפקתה.

ההצעה מיועדת ללקוח הספציפי בלבד, ואין להעבירה או להציג אותה בפני חברות אחרות או גורמים חיצוניים.

המחירים עשויים להשתנות, והחברה אינה אחראית לטעויות חישוב או הקלדה. רק הסכום המאושר סופית על ידי החברה הוא המחייב.

אישור ההצעה (בחתימה) מהווה התחייבות מצד הלקוח לביצוע העבודה.

במעמד האישור, ישולמו 10% מקדמה מסכום העסקה – תשלום זה אינו ניתן להחזר במקרה של ביטול מכל סיבה שהיא.

הלקוח מתחייב לוודא כי מיקום התקנת המטבח יהיה פנוי מכל ריהוט, ציוד או מכשול אחר, וכן שנקודות מים, חשמל וניקוז ימוקמו בהתאם לתכניות שסופקו לו מראש על ידי החברה.
כל עיכוב או שינוי הנובע מאי־עמידה בתנאים אלה עשוי לגרור עיכובים בעלויות ולוחות זמנים.
"""
```

---

## 🔄 Auto-Update System

### Update Check Mechanism
```python
class UpdateManager:
    def __init__(self):
        self.github_repo = "korenvak/QuoreManager"
        self.current_version = "2.0.0"
    
    async def check_for_updates(self):
        """Check GitHub releases for newer versions"""
        try:
            # Check GitHub API for latest release
            # Compare version numbers
            # Download update if available
            # Backup current installation
            # Apply update
        except (ConnectionError, TimeoutError):
            # Gracefully handle offline scenarios
            pass
    
    def apply_update(self, update_package):
        """Apply downloaded update package"""
        # Backup current version
        # Extract new files
        # Migrate database if needed
        # Restart application
```

---

## 🛠️ Professional Installer

### NSIS Installer Script Structure
```nsis
; QuoreManager 2.0 Installer
!define APP_NAME "QuoreManager"
!define APP_VERSION "2.0.0"
!define PUBLISHER "Panel Kitchens"

; Create installation directory
InstallDir "$PROGRAMFILES\${APP_NAME}"

; Create folders
CreateDirectory "$INSTDIR\database"
CreateDirectory "$INSTDIR\config" 
CreateDirectory "$INSTDIR\pdfs"
CreateDirectory "$INSTDIR\logs"
CreateDirectory "$INSTDIR\resources"

; Install files
File "dist\QuoreManager.exe"
File /r "resources\*.*"

; Create shortcuts
CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\QuoreManager.exe"
CreateShortCut "$SMPROGRAMS\${APP_NAME}.lnk" "$INSTDIR\QuoreManager.exe"

; Initialize database
ExecWait "$INSTDIR\QuoreManager.exe --init-db"
```

---

## 🔍 Enhanced Catalog Interface

### Catalog Item Display Component
```python
class CatalogItemWidget(tk.Frame):
    def __init__(self, parent, item):
        super().__init__(parent)
        self.item = item
        
        # Main item info
        self.item_label = tk.Label(self, text=item.name)
        
        # Units and cost
        self.details_label = tk.Label(
            self, 
            text=f"{item.cost}₪ per {item.units}"
        )
        
        # Approval status indicator
        self.approval_icon = self.create_approval_icon(item.manager_approve)
        
        # Comments (if any)
        if item.comments:
            self.comments_label = tk.Label(
                self, 
                text=item.comments, 
                font=("Arial", 8), 
                fg="gray"
            )
```

---

## 📈 Performance Optimizations

### Caching Strategy
```python
class CatalogCache:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def get_cached_catalog(self, category=None):
        cache_key = f"catalog_{category or 'all'}"
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return data
        
        # Cache miss - fetch from database
        data = self.fetch_from_database(category)
        self.cache[cache_key] = (data, time.time())
        return data
```

### Lazy Loading for Large Catalogs
```python
def load_catalog_items(page=0, page_size=50, category=None):
    """Load catalog items in chunks for better performance"""
    offset = page * page_size
    query = """
        SELECT * FROM catalog_v2 
        WHERE is_active = 1
        AND (category = ? OR ? IS NULL)
        ORDER BY item
        LIMIT ? OFFSET ?
    """
    return db.execute(query, (category, category, page_size, offset))
```

---

## 🔒 Security Enhancements

### Session Management
```python
class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, user_id):
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        return session_id
    
    def validate_session(self, session_id):
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if time.time() - session['last_activity'] > self.session_timeout:
            del self.active_sessions[session_id]
            return False
        
        session['last_activity'] = time.time()
        return True
```

---

## 📊 Data Validation

### Input Validation Rules
```python
class ValidationRules:
    @staticmethod
    def validate_decimal_price(value):
        """Validate decimal pricing input"""
        try:
            price = decimal.Decimal(str(value))
            if price < 0:
                raise ValueError("Price cannot be negative")
            if price > 999999.99:
                raise ValueError("Price too large")
            return price
        except (decimal.InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid price format: {e}")
    
    @staticmethod
    def validate_units(units):
        """Validate unit types"""
        valid_units = ['יחידה', 'מ"ר', 'מ"א', 'ק"ג', 'מטר', 'ליטר']
        if units not in valid_units:
            raise ValueError(f"Invalid unit type. Must be one of: {valid_units}")
        return units
```

---

This technical specification provides the foundation for implementing all the features outlined in the Version 2 roadmap. Each section can be developed incrementally, allowing for iterative testing and refinement. 