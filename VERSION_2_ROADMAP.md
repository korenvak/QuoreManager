# QuoreManager Version 2.0 - Feature Roadmap

## 🎯 Core Missions

### 1. **Enhanced Catalog System**
**Mission:** Modernize and internationalize the catalog with flexible unit support

**Features:**
- **English Column Names:** 
  - `id` (unique identifier)
  - `item` (product name)  
  - `category` (product category)
  - `units` (measurement type: מ"ר, יחידה, מ"א, etc.)
  - `cost` (decimal pricing support)
  - `manager_approve` (y/n approval status)
  - `comments` (additional notes/specifications)

- **Flexible Pricing:** Support decimal numbers (not just integers)
- **Unit Types:** Pre-defined unit options with Hebrew display names
- **Enhanced Catalog Selector:** Display units and comments in selection interface

### 2. **Simplified User Management**
**Mission:** Streamline user roles for better workflow control

**User Types:**
- **Admin:** Full system access (manage users, approve items, create/edit all quotes)
- **User:** Limited access (view/edit own quotes/drafts only)

**Workflow Changes:**
- Remove complex permission system
- Clear role-based access control
- Simplified user creation process

### 3. **Approval Workflow System**
**Mission:** Implement manager approval control for quote creation

**Workflow Logic:**
- Items with `manager_approve = "n"` → Can only save as **Draft**
- Items with `manager_approve = "y"` → Can save as **Quote** (Admin only)
- **Users** can always edit their quotes/drafts after Admin saves them
- **Visual indicators** for approval status in catalog

### 4. **Advanced Theme System**
**Mission:** Create truly dark mode and color customization

**Theme Features:**
- **True Dark Mode:** Fix all white backgrounds, ensure complete dark theme
- **Color Options:** 
  - Default Blue theme
  - Soft Red alternative theme
  - Theme persistence per user
- **Improved Contrast:** Better readability in both modes
- **Theme Preview:** Live preview before applying

### 5. **Enhanced PDF Generation**
**Mission:** Professional PDF output with updated legal terms

**PDF Improvements:**
- **Multiple Photos:** Support 3+ photos per quote (flexible grid layout)
- **Fixed Page Numbering:** Proper page numbers on all pages
- **Unit Display:** Show amount + unit type (e.g., "25 מ"ר", "5 יחידות")
- **Updated Legal Terms:** New Hebrew legal text as provided
- **Better Formatting:** Improved table layouts and spacing

### 6. **Professional Installation System**
**Mission:** One-click installation with complete setup

**Installer Features:**
- **Complete Setup:** Creates all necessary folders (database/, config/, pdfs/, logs/)
- **Database Initialization:** Sets up fresh database with sample data
- **Desktop Shortcut:** QuoreManager icon with proper branding
- **Start Menu Entry:** Professional Windows integration
- **Uninstaller:** Clean removal option
- **Admin Rights:** Proper Windows installation with UAC handling

### 7. **Auto-Update System**
**Mission:** Seamless updates while maintaining offline capability

**Update Features:**
- **Git Integration:** Check GitHub releases for new versions
- **Smart Updates:** Download and apply updates automatically
- **Offline Resilience:** Full functionality without internet
- **Update Notifications:** Non-intrusive update available alerts
- **Rollback Capability:** Backup current version before update
- **Selective Updates:** Option to skip non-critical updates

---

## 💡 Additional Suggestions

### 8. **Enhanced Data Management**
- **Backup System:** Automated local backups of database
- **Export/Import:** Export quotes to Excel/CSV format
- **Data Validation:** Input validation for all numeric fields
- **Search & Filter:** Advanced catalog search by category, units, approval status

### 9. **Improved User Experience**
- **Keyboard Shortcuts:** Common actions (Ctrl+S save, Ctrl+N new quote, etc.)
- **Recent Items:** Quick access to recently used catalog items
- **Quote Templates:** Save frequently used quote configurations
- **Drag & Drop:** Drag items from catalog to quote builder

### 10. **Enhanced Quote Management**
- **Quote Versioning:** Track quote revisions and changes
- **Status Tracking:** Draft → Pending Approval → Approved → Sent → Accepted
- **Due Date Tracking:** Alert for quotes nearing 14-day expiration
- **Quote Comparison:** Side-by-side comparison of quote versions

### 11. **Reporting & Analytics**
- **Sales Dashboard:** Visual charts of quote activity
- **Approval Reports:** Track approval rates and pending items
- **User Activity:** Monitor user productivity and quote creation
- **Export Reports:** PDF/Excel reports for management

### 12. **Enhanced Security**
- **Session Management:** Auto-logout after inactivity
- **Audit Log:** Track all user actions and changes
- **Data Encryption:** Encrypt sensitive configuration data
- **Password Policies:** Enforce strong password requirements

### 13. **Catalog Enhancements**
- **Bulk Import:** Import catalog items from Excel/CSV
- **Category Management:** Create/edit product categories
- **Price History:** Track price changes over time
- **Item Images:** Attach product images to catalog items

### 14. **PDF Customization**
- **Company Branding:** Customizable logo and company colors
- **Template Selection:** Multiple PDF layout templates
- **Custom Fields:** Add custom fields to quotes
- **Language Support:** Option for English/Hebrew mixed PDFs

---

## 🚀 Implementation Priority

### Phase 1 (Core Features)
1. Enhanced Catalog System
2. Simplified User Management  
3. Approval Workflow System

### Phase 2 (User Experience)
4. Advanced Theme System
5. Enhanced PDF Generation
6. Auto-Update System

### Phase 3 (Professional Features)
7. Professional Installation System
8. Enhanced Data Management
9. Improved User Experience

### Phase 4 (Advanced Features)
10. Enhanced Quote Management
11. Reporting & Analytics
12. Enhanced Security

---

## 📋 Technical Considerations

### Database Schema Changes
- Migrate existing catalog to new English schema
- Add approval status tracking
- Implement user session management
- Add audit logging tables

### UI/UX Modernization
- Redesign catalog selector interface
- Implement responsive layouts
- Add loading states and progress indicators
- Improve error handling and user feedback

### Performance Optimization
- Optimize database queries
- Implement caching for frequently accessed data
- Lazy loading for large catalogs
- Background processing for PDF generation

### Compatibility
- Maintain backward compatibility with existing quotes
- Data migration tools for version 1 users
- Graceful handling of corrupted/missing data

---

## 🎯 Success Metrics

- **User Adoption:** Smooth migration from v1 to v2
- **Workflow Efficiency:** Reduced time to create quotes
- **Error Reduction:** Fewer approval workflow mistakes
- **User Satisfaction:** Positive feedback on new features
- **System Stability:** Reliable offline operation and updates

---

*This roadmap represents a comprehensive vision for QuoreManager 2.0, focusing on professional workflow management while maintaining the simplicity that makes the current system effective.* 