"""
Customers Management Page for Kitchen Quote Management System - Modern Professional Design
Complete implementation with CRUD operations and search
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional, Dict, Any, Callable
from styling.theme_system import ModernThemeManager, THEMES
from config.settings import SettingsManager

class CustomersPage:
    """Modern professional customers management page"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.customers_data = []
        self.filtered_customers = []
        self.search_var: Optional[ctk.StringVar] = None
        self.customers_container: Optional[ctk.CTkFrame] = None
        self.stats_label: Optional[ctk.CTkLabel] = None
        
        # Initialize theme system
        self.settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
    def create_content(self):
        """Create modern professional customers page content"""
        # Main container with gradient background
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=self.theme['bg_secondary'],
            corner_radius=0,
            scrollbar_button_color=self.theme['primary_light'],
            scrollbar_button_hover_color=self.theme['primary']
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner container with compact spacing
        inner_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Professional page header
        self.create_modern_header(inner_frame)
        
        # Modern content area
        self.create_content_area(inner_frame)
        
        # Load customers data
        self.load_customers()
    
    def create_modern_header(self, parent):
        """Create modern professional page header"""
        header_card = ctk.CTkFrame(
            parent, 
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        header_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        header_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Title section
        title_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_section.pack(fill="x", pady=(0, self.theme_manager.get_spacing('md')))
        
        # Title
        title_label = ctk.CTkLabel(
            title_section,
            text="ניהול לקוחות",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_section,
            text="נהל פרטי לקוחות והצעות מחיר",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(anchor="e")
        
        # Add customer button - using theme colors
        add_button = self.theme_manager.create_modern_button(
            actions_frame,
            text="➕  הוסף לקוח חדש",
            style="primary", 
            command=self.show_add_customer_dialog
        )
        add_button.pack(side="right")
    
    def create_header(self, parent):
        """Create header with title, search, and actions"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ניהול לקוחות",
            font=ctk.CTkFont(family="Assistant", size=32, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Search and actions bar
        actions_frame = ctk.CTkFrame(
            header_frame,
            fg_color="#FDFDFE",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        actions_frame.pack(fill="x", pady=(0, 10))
        
        # Add customer button
        add_button = ctk.CTkButton(
            actions_frame,
            text="הוסף לקוח חדש",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            height=50,
            command=self.show_add_customer_dialog,
            fg_color="#3B82F6",
            hover_color="#1E40AF",
            corner_radius=12
        )
        add_button.pack(side="right", padx=20, pady=15)
        
        # Search frame
        search_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=(0, 20), pady=15)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="חיפוש:",
            font=ctk.CTkFont(family="Assistant", size=15, weight="bold"),
            text_color="#6B7280"
        )
        search_label.pack(side="right", padx=(10, 0))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="חיפוש לפי שם, טלפון או דואל...",
            width=300,
            font=ctk.CTkFont(family="Assistant", size=14),
            corner_radius=10,
            border_width=1,
            border_color="#C7D2FE"
        )
        search_entry.pack(side="right")
        
        # Statistics
        self.stats_label = ctk.CTkLabel(
            actions_frame,
            text="טוען נתונים...",
            font=ctk.CTkFont(family="Assistant", size=15),
            text_color="#9CA3AF"
        )
        self.stats_label.pack(side="left", padx=20, pady=15)
    
    def create_content_area(self, parent):
        """Create scrollable content area for customers"""
        self.customers_container = ctk.CTkFrame(
            parent,
            fg_color="#FAFBFF",
            corner_radius=15
        )
        self.customers_container.pack(fill="both", expand=True)
        
        # Loading placeholder
        loading_label = ctk.CTkLabel(
            self.customers_container,
            text="טוען לקוחות...",
            font=ctk.CTkFont(family="Assistant", size=16),
            text_color="gray"
        )
        loading_label.pack(expand=True, pady=50)
    
    def load_customers(self):
        """Load customers from database in background thread"""
        def load_data():
            try:
                customers = self.db_manager.get_all_customers()
                self.parent.after(0, self.on_customers_loaded, customers)
            except Exception as e:
                self.parent.after(0, self.on_customers_error, str(e))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def on_customers_loaded(self, customers):
        """Handle successful customers loading"""
        self.customers_data = customers
        self.filtered_customers = customers
        self.update_display()
        self.update_stats()
    
    def on_customers_error(self, error):
        """Handle customers loading error"""
        self.clear_container()
        
        if self.customers_container:
            error_frame = ctk.CTkFrame(self.customers_container)
            error_frame.pack(fill="x", padx=20, pady=20)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"שגיאה בטעינת לקוחות:\n{error}",
                font=ctk.CTkFont(family="Assistant", size=16),
                text_color="#EF4444",
                justify="center"
            )
            error_label.pack(pady=30)
            
            retry_button = ctk.CTkButton(
                error_frame,
                text="נסה שוב",
                command=self.load_customers,
                fg_color="#3B82F6",
                hover_color="#2563EB"
            )
            retry_button.pack(pady=(0, 20))
    
    def update_display(self):
        """Update customers display"""
        self.clear_container()
        
        if not self.filtered_customers:
            self.show_empty_state()
            return
        
        # Display customers
        for customer in self.filtered_customers:
            self.create_customer_card(customer)
    
    def clear_container(self):
        """Clear customers container"""
        if self.customers_container:
            for widget in self.customers_container.winfo_children():
                widget.destroy()
    
    def show_empty_state(self):
        """Show empty state message"""
        if not self.customers_container:
            return
            
        empty_frame = ctk.CTkFrame(self.customers_container, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both")
        
        if not self.customers_data:
            # No customers at all
            message = "אין לקוחות במערכת\nלחץ על 'הוסף לקוח חדש' כדי להתחיל"
            icon = "👥"
        else:
            # No customers match search
            message = "לא נמצאו לקוחות המתאימים לחיפוש\nנסה מונחי חיפוש אחרים"
            icon = "🔍"
        
        icon_label = ctk.CTkLabel(
            empty_frame,
            text=icon,
            font=ctk.CTkFont(size=48)
        )
        icon_label.pack(pady=(50, 20))
        
        message_label = ctk.CTkLabel(
            empty_frame,
            text=message,
            font=ctk.CTkFont(family="Assistant", size=16),
            text_color="gray",
            justify="center"
        )
        message_label.pack()
    
    def create_customer_card(self, customer):
        """Create individual customer card"""
        if not self.customers_container:
            return
            
        card = ctk.CTkFrame(
            self.customers_container,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        card.pack(fill="x", padx=20, pady=10)
        
        # Add hover effect
        def on_enter(event):
            card.configure(border_color="#3B82F6")
        
        def on_leave(event):
            card.configure(border_color="#E1E8F7")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Left side - customer info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True)
        
        # Customer name
        name_label = ctk.CTkLabel(
            info_frame,
            text=customer['name'],
            font=ctk.CTkFont(family="Assistant", size=19, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        name_label.pack(anchor="e")
        
        # Contact info
        phone_label = ctk.CTkLabel(
            info_frame,
            text=f"📞 {customer['phone']}",
            font=ctk.CTkFont(family="Assistant", size=14),
            text_color="#6B7280",
            anchor="e"
        )
        phone_label.pack(anchor="e", pady=(3, 0))
        
        email_label = ctk.CTkLabel(
            info_frame,
            text=f"📧 {customer['email']}",
            font=ctk.CTkFont(family="Assistant", size=14),
            text_color="#6B7280",
            anchor="e"
        )
        email_label.pack(anchor="e", pady=(2, 0))
        
        address_label = ctk.CTkLabel(
            info_frame,
            text=f"📍 {customer['address']}",
            font=ctk.CTkFont(family="Assistant", size=14),
            text_color="#6B7280",
            anchor="e"
        )
        address_label.pack(anchor="e", pady=(2, 0))
        
        # Right side - actions (single row layout with theme colors)
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="left", padx=(0, 20))
        
        # All buttons in single row with professional styling
        buttons_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_container.pack(fill="x")
        
        # Delete button (admin only) - rightmost for caution
        if self.has_permission('delete_customer'):
            delete_button = self.theme_manager.create_modern_button(
                buttons_container,
                text="מחיקה",
                style="danger",
                size="small",
                width=80,
                command=lambda c=customer: self.confirm_delete_customer(c)
            )
            delete_button.pack(side="right", padx=(5, 0))
        
        # Edit button - theme colors
        edit_button = self.theme_manager.create_modern_button(
            buttons_container,
            text="עריכה",
            style="primary",
            size="small",
            width=80,
            command=lambda c=customer: self.show_edit_customer_dialog(c)
        )
        edit_button.pack(side="right", padx=(5, 0))
        
        # View quotes button - theme colors
        quotes_button = self.theme_manager.create_modern_button(
            buttons_container,
            text="הצעות",
            style="secondary",
            size="small", 
            width=80,
            command=lambda c=customer: self.view_customer_quotes(c)
        )
        quotes_button.pack(side="right", padx=(5, 0))
    
    def on_search_changed(self, *args):
        """Handle search text change"""
        if not self.search_var:
            return
            
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            self.filtered_customers = self.customers_data
        else:
            self.filtered_customers = [
                customer for customer in self.customers_data
                if (search_term in customer['name'].lower() or
                    search_term in customer['phone'] or
                    search_term in customer['email'].lower() or
                    search_term in customer['address'].lower())
            ]
        
        self.update_display()
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        if not self.stats_label:
            return
            
        total = len(self.customers_data)
        filtered = len(self.filtered_customers)
        
        if total == filtered:
            stats_text = f"סה״כ {total} לקוחות"
        else:
            stats_text = f"מציג {filtered} מתוך {total} לקוחות"
        
        self.stats_label.configure(text=stats_text)
    
    def show_add_customer_dialog(self):
        """Show add customer dialog"""
        CustomerDialog(
            parent=self.parent,
            title="הוסף לקוח חדש",
            customer_data=None,
            db_manager=self.db_manager,
            on_success=self.on_customer_saved
        )
    
    def show_edit_customer_dialog(self, customer):
        """Show edit customer dialog"""
        CustomerDialog(
            parent=self.parent,
            title="עריכת לקוח",
            customer_data=customer,
            db_manager=self.db_manager,
            on_success=self.on_customer_saved
        )
    
    def on_customer_saved(self):
        """Handle successful customer save"""
        # Reload customers list
        self.load_customers()
    
    def view_customer_quotes(self, customer):
        """View customer's quotes"""
        messagebox.showinfo(
            "הצעות מחיר", 
            f"הצגת הצעות מחיר עבור {customer['name']}\n(יופעל בגרסה הבאה)"
        )
    
    def confirm_delete_customer(self, customer):
        """Confirm customer deletion"""
        # Get quotes count
        try:
            quotes = self.db_manager.get_quotes_by_customer(customer['id'])
            quotes_count = len(quotes)
        except:
            quotes_count = 0
        
        message = f"האם אתה בטוח שברצונך למחוק את הלקוח?\n\n"
        message += f"שם: {customer['name']}\n"
        message += f"טלפון: {customer['phone']}\n\n"
        
        if quotes_count > 0:
            message += f"⚠️ פעולה זו תמחק גם {quotes_count} הצעות מחיר של הלקוח!\n\n"
            message += "מחיקה זו אינה הפיכה."
        else:
            message += "מחיקה זו אינה הפיכה."
        
        result = messagebox.askyesno(
            "אישור מחיקה",
            message,
            icon="warning"
        )
        
        if result:
            self.delete_customer(customer)
    
    def delete_customer(self, customer):
        """Delete customer from database"""
        def delete_data():
            try:
                success = self.db_manager.delete_customer(customer['id'])
                self.parent.after(0, self.on_customer_deleted, success, customer['name'])
            except Exception as e:
                self.parent.after(0, self.on_delete_error, str(e))
        
        threading.Thread(target=delete_data, daemon=True).start()
    
    def on_customer_deleted(self, success, customer_name):
        """Handle customer deletion result"""
        if success:
            messagebox.showinfo("הצלחה", f"הלקוח {customer_name} נמחק בהצלחה")
            self.load_customers()
        else:
            messagebox.showerror("שגיאה", "מחיקת הלקוח נכשלה")
    
    def on_delete_error(self, error):
        """Handle deletion error"""
        messagebox.showerror("שגיאה", f"שגיאה במחיקת הלקוח:\n{error}")
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        role = self.current_user.get('role', 'viewer')
        
        if role == 'admin':
            return True
        elif role == 'manager':
            return permission in ['edit_customer', 'view_customer']
        elif role == 'employee':
            return permission in ['view_customer']
        
        return False


class CustomerDialog:
    """Customer creation/edit dialog with modern design and real-time validation"""
    
    def __init__(self, parent, title: str, customer_data: Optional[Dict] = None, 
                 db_manager=None, on_success: Callable = None):
        self.parent = parent
        self.title = title
        self.customer_data = customer_data
        self.db_manager = db_manager
        self.on_success = on_success
        self.dialog: Optional[ctk.CTkToplevel] = None
        
        # Import theme manager  
        from styling.theme_system import ModernThemeManager
        from config.settings import SettingsManager
        settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(settings_manager)
        
        # Form variables
        self.name_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.address_var = ctk.StringVar()
        self.notes_var = ctk.StringVar()
        
        # Validation state
        self.validation_state = {
            'name': {'valid': True, 'message': ''},
            'phone': {'valid': True, 'message': ''},
            'email': {'valid': True, 'message': ''},
            'address': {'valid': True, 'message': ''}
        }
        
        # UI references
        self.name_entry = None
        self.phone_entry = None
        self.email_entry = None
        self.address_entry = None
        self.save_button = None
        self.validation_labels = {}
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create modern customer dialog with beautiful design"""
        current_theme = self.theme_manager.get_current_theme()
        
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        
        # Modern sizing and positioning
        dialog_width = 580
        dialog_height = 720
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(500, 650)
        
        # Center dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Modern main container with beautiful styling
        main_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=0,
            fg_color=("#F8FAFC", "#1E293B")
        )
        main_container.pack(fill="both", expand=True)
        
        # Beautiful header with gradient
        self.create_modern_header(main_container)
        
        # Main content card
        self.create_content_card(main_container)
        
        # Load existing data if editing
        if self.customer_data:
            self.load_customer_data()
        
        # Setup validation
        self.setup_validation()
        
        # Focus first field
        if self.name_entry:
            self.name_entry.focus_set()
    
    def create_modern_header(self, parent):
        """Create beautiful header with gradient background"""
        current_theme = self.theme_manager.get_current_theme()
        
        header_frame = ctk.CTkFrame(
            parent,
            corner_radius=0,
            height=120,
            fg_color=current_theme['primary']
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both")
        
        # Icon
        icon_label = ctk.CTkLabel(
            header_content,
            text="👤" if not self.customer_data else "✏️",
            font=ctk.CTkFont(size=40),
            text_color=("#FFFFFF", "#F1F5F9"),
            fg_color="transparent"
        )
        icon_label.pack(pady=(20, 10))
        
        # Title with modern typography
        title_label = ctk.CTkLabel(
            header_content,
            text=self.title,
            font=ctk.CTkFont(family="Assistant", size=24, weight="bold"),
            text_color=("#FFFFFF", "#F1F5F9"),
            fg_color="transparent"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_text = "הוספת לקוח חדש למערכת" if not self.customer_data else "עריכת פרטי הלקוח"
        subtitle_label = ctk.CTkLabel(
            header_content,
            text=subtitle_text,
            font=ctk.CTkFont(family="Assistant", size=14),
            text_color=("#FFFFFF", "#F1F5F9"),
            fg_color="transparent"
        )
        subtitle_label.pack(pady=(5, 0))
    
    def create_content_card(self, parent):
        """Create main content card with form fields"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Card container
        card_frame = ctk.CTkFrame(
            parent,
            corner_radius=24,
            fg_color=("#FFFFFF", "#334155"),
            border_width=1,
            border_color=("#E2E8F0", "#475569")
        )
        card_frame.pack(fill="both", expand=True, padx=30, pady=(30, 30))
        
        # Scrollable content
        main_frame = ctk.CTkScrollableFrame(card_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Action buttons
        self.create_modern_buttons(main_frame)
    
    def create_form_fields(self, parent):
        """Create modern form input fields with validation"""
        current_theme = self.theme_manager.get_current_theme()
        
        fields_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color=current_theme['card_bg'],
            border_width=1,
            border_color=current_theme['border']
        )
        fields_frame.pack(fill="x", pady=(0, 30))
        
        # Form title
        form_title = ctk.CTkLabel(
            fields_frame,
            text="פרטי הלקוח",
            font=ctk.CTkFont(family="Assistant", size=18, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        form_title.pack(anchor="e", padx=20, pady=(20, 10))
        
        # Fields container
        fields_container = ctk.CTkFrame(fields_frame, fg_color="transparent")
        fields_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Name field
        self.create_modern_field(
            fields_container, "שם הלקוח *", self.name_var, 
            placeholder="שם מלא של הלקוח", field_key="name"
        )
        
        # Phone field
        self.create_modern_field(
            fields_container, "טלפון *", self.phone_var,
            placeholder="050-1234567", field_key="phone"
        )
        
        # Email field
        self.create_modern_field(
            fields_container, "דואר אלקטרוני *", self.email_var,
            placeholder="customer@email.com", field_key="email"
        )
        
        # Address field
        self.create_modern_field(
            fields_container, "כתובת *", self.address_var,
            placeholder="רחוב, עיר, מיקוד", field_key="address", 
            multiline=True
        )
        
        # Notes field (optional)
        self.create_modern_field(
            fields_container, "הערות", self.notes_var,
            placeholder="הערות נוספות על הלקוח (אופציונלי)",
            field_key="notes", multiline=True, required=False
        )
    
    def create_modern_field(self, parent, label: str, variable: ctk.StringVar, 
                    placeholder: str, field_key: str, multiline: bool = False, 
                    required: bool = True):
        """Create individual modern form field with validation"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=12)
        
        # Label with modern styling
        label_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 8))
        
        field_label = ctk.CTkLabel(
            label_frame,
            text=label,
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        field_label.pack(anchor="e")
        
        # Required indicator
        if required:
            required_label = ctk.CTkLabel(
                label_frame,
                text="שדה חובה",
                font=ctk.CTkFont(family="Assistant", size=11),
                text_color=current_theme['text_tertiary'],
                anchor="e"
            )
            required_label.pack(anchor="e")
        
        # Input field with modern styling
        if multiline:
            height = 90 if field_key == "address" else 110
            
            entry = ctk.CTkTextbox(
                field_frame,
                height=height,
                font=ctk.CTkFont(family="Assistant", size=14),
                corner_radius=12,
                border_width=2,
                border_color=current_theme['border'],
                fg_color=current_theme['input_bg'],
                text_color=current_theme['text_primary']
            )
            entry.pack(fill="x")
            
            # Bind text change event for textbox
            def on_text_change(event=None):
                content = entry.get("1.0", "end-1c")
                variable.set(content)
                
            entry.bind("<KeyRelease>", on_text_change)
            entry.bind("<Button-1>", on_text_change)
            
        else:
            entry = ctk.CTkEntry(
                field_frame,
                textvariable=variable,
                placeholder_text=placeholder,
                font=ctk.CTkFont(family="Assistant", size=14),
                height=48,
                corner_radius=12,
                border_width=2,
                border_color=current_theme['border'],
                fg_color=current_theme['input_bg'],
                text_color=current_theme['text_primary']
            )
            entry.pack(fill="x")
        
        # Store entry reference
        setattr(self, f"{field_key}_entry", entry)
        
        # Validation message label
        validation_label = ctk.CTkLabel(
            field_frame,
            text="",
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color=current_theme['error'],
            anchor="e"
        )
        validation_label.pack(anchor="e", pady=(4, 0))
        
        # Store validation label reference
        self.validation_labels[field_key] = validation_label
    
    def create_modern_buttons(self, parent):
        """Create modern action buttons with gradients and shadows"""
        # Buttons container
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=24)
        
        # Cancel button
        cancel_button = self.theme_manager.create_modern_button(
            buttons_frame,
            text="ביטול",
            style="outline",
            size="large",
            width=140,
            command=self.cancel_dialog
        )
        cancel_button.pack(side="left")
        
        # Save button
        save_text = "עדכן לקוח" if self.customer_data else "הוסף לקוח"
        self.save_button = self.theme_manager.create_modern_button(
            buttons_frame,
            text=save_text,
            style="primary",
            size="large",
            width=160,
            command=self.save_customer
        )
        self.save_button.pack(side="right")
    
    def setup_validation(self):
        """Setup real-time validation"""
        # Add trace to all variables for real-time validation
        self.name_var.trace("w", lambda *args: self.validate_field("name"))
        self.phone_var.trace("w", lambda *args: self.validate_field("phone"))
        self.email_var.trace("w", lambda *args: self.validate_field("email"))
        self.address_var.trace("w", lambda *args: self.validate_field("address"))
        
        # Initial validation
        self.update_save_button_state()
    
    def validate_field(self, field_key: str):
        """Validate individual field in real-time"""
        def validate():
            try:
                value = getattr(self, f"{field_key}_var").get().strip()
                
                # Reset validation state
                self.validation_state[field_key] = {'valid': True, 'message': ''}
                
                # Required field check
                if field_key != "notes" and not value:
                    self.validation_state[field_key] = {
                        'valid': False, 
                        'message': 'שדה חובה'
                    }
                    self.dialog.after(0, self.update_validation_ui, field_key)
                    return
                
                if not value and field_key == "notes":
                    # Notes is optional
                    self.dialog.after(0, self.update_validation_ui, field_key)
                    return
                
                # Format validation
                if field_key == "email" and value:
                    if not self.is_valid_email(value):
                        self.validation_state[field_key] = {
                            'valid': False,
                            'message': 'כתובת דואר אלקטרוני לא תקינה'
                        }
                        self.dialog.after(0, self.update_validation_ui, field_key)
                        return
                
                if field_key == "phone" and value:
                    if not self.is_valid_phone(value):
                        self.validation_state[field_key] = {
                            'valid': False,
                            'message': 'מספר טלפון לא תקין'
                        }
                        self.dialog.after(0, self.update_validation_ui, field_key)
                        return
                
                # Uniqueness check (skip for current customer when editing)
                if value and field_key != "notes":
                    existing_customer_id = None
                    if self.customer_data:
                        existing_customer_id = self.customer_data.get('id')
                    
                    if self.is_field_taken(field_key, value, existing_customer_id):
                        field_names = {
                            'name': 'שם לקוח',
                            'phone': 'מספר טלפון',
                            'email': 'כתובת דואר אלקטרוני',
                            'address': 'כתובת'
                        }
                        self.validation_state[field_key] = {
                            'valid': False,
                            'message': f'{field_names.get(field_key, "שדה")} זה כבר קיים במערכת'
                        }
                
                # Update UI
                self.dialog.after(0, self.update_validation_ui, field_key)
                
            except Exception as e:
                import logging
            logging.getLogger(__name__).error(f"Validation error for {field_key}: {e}")
        
        # Run validation in background to avoid blocking UI
        threading.Thread(target=validate, daemon=True).start()
    
    def is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_phone(self, phone: str) -> bool:
        """Basic phone validation for Israeli numbers"""
        import re
        # Remove all non-digits
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # Check for valid Israeli phone patterns
        # Mobile numbers: 05X-XXXXXXX (10 digits total)
        if len(digits_only) == 10 and digits_only.startswith('05'):
            return True
        # Landline numbers: 0X-XXXXXXX (9 digits total)
        if len(digits_only) == 9 and digits_only.startswith('0') and not digits_only.startswith('05'):
            return True
        # International format: +972-5X-XXXXXXX (remove +972)
        if len(digits_only) == 13 and digits_only.startswith('9725'):
            return True
        # International format without country code: 5X-XXXXXXX
        if len(digits_only) == 9 and digits_only.startswith('5'):
            return True
        
        return False
    
    def is_field_taken(self, field_key: str, value: str, exclude_customer_id: Optional[int] = None) -> bool:
        """Check if field value is already taken by another customer"""
        try:
            kwargs = {field_key: value}
            exists = self.db_manager.customer_exists(**kwargs)
            
            if exists and exclude_customer_id:
                # Check if the existing customer is the one we're editing
                with self.db_manager.get_session() as session:
                    from database.models import Customer
                    existing = session.query(Customer).filter(
                        getattr(Customer, field_key) == value
                    ).first()
                    
                    if existing and existing.id == exclude_customer_id:
                        return False  # It's the same customer, so it's OK
            
            return exists
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error checking field uniqueness: {e}")
            return False
    
    def update_validation_ui(self, field_key: str):
        """Update validation UI for specific field"""
        try:
            current_theme = self.theme_manager.get_current_theme()
            state = self.validation_state[field_key]
            label = self.validation_labels.get(field_key)
            
            if label:
                if state['valid']:
                    label.configure(text="", text_color=current_theme['success'])
                else:
                    label.configure(text=state['message'], text_color=current_theme['error'])
            
            # Update entry border color
            entry = getattr(self, f"{field_key}_entry", None)
            if entry:
                if state['valid']:
                    entry.configure(border_color=current_theme['border'])
                else:
                    entry.configure(border_color=current_theme['error'])
            
            # Update save button state
            self.update_save_button_state()
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating validation UI: {e}")
    
    def update_save_button_state(self):
        """Enable/disable save button based on validation state"""
        try:
            # Check if all required fields are valid
            all_valid = all(
                state['valid'] for field, state in self.validation_state.items()
                if field != "notes"  # Notes is optional
            )
            
            # Check if required fields have content
            required_fields_filled = all([
                self.name_var.get().strip(),
                self.phone_var.get().strip(),
                self.email_var.get().strip(),
                self.address_var.get().strip()
            ])
            
            can_save = all_valid and required_fields_filled
            
            if self.save_button:
                if can_save:
                    self.save_button.configure(state="normal")
                else:
                    self.save_button.configure(state="disabled")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating save button: {e}")
    
    def load_customer_data(self):
        """Load existing customer data for editing"""
        if not self.customer_data:
            return
        
        self.name_var.set(self.customer_data.get('name', ''))
        self.phone_var.set(self.customer_data.get('phone', ''))
        self.email_var.set(self.customer_data.get('email', ''))
        self.address_var.set(self.customer_data.get('address', ''))
        self.notes_var.set(self.customer_data.get('notes', ''))
        
        # Update textbox content for multiline fields
        if self.address_entry:
            self.address_entry.delete("1.0", "end")
            self.address_entry.insert("1.0", self.customer_data.get('address', ''))
        
        if hasattr(self, 'notes_entry'):
            self.notes_entry.delete("1.0", "end")
            self.notes_entry.insert("1.0", self.customer_data.get('notes', ''))
    
    def save_customer(self):
        """Save customer data"""
        try:
            # Final validation
            if not self.is_form_valid():
                messagebox.showerror("שגיאה", "אנא תקן את השגיאות בטופס לפני השמירה")
                return
            
            # Collect data
            customer_data = {
                'name': self.name_var.get().strip(),
                'phone': self.phone_var.get().strip(),
                'email': self.email_var.get().strip(),
                'address': self.address_var.get().strip(),
                'notes': self.notes_var.get().strip()
            }
            
            # Save to database
            if self.customer_data:
                # Update existing customer
                success = self.db_manager.update_customer(
                    self.customer_data['id'], **customer_data
                )
                if success:
                    messagebox.showinfo("הצלחה", "פרטי הלקוח עודכנו בהצלחה")
                else:
                    messagebox.showerror("שגיאה", "שגיאה בעדכון פרטי הלקוח")
                    return
            else:
                # Create new customer
                customer_id = self.db_manager.add_customer(**customer_data)
                if customer_id:
                    messagebox.showinfo("הצלחה", "הלקוח נוסף בהצלחה למערכת")
                else:
                    messagebox.showerror("שגיאה", "שגיאה ביצירת לקוח חדש")
                    return
            
            # Call success callback
            if self.on_success:
                self.on_success()
            
            # Close dialog
            if self.dialog:
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת הלקוח: {e}")
    
    def is_form_valid(self) -> bool:
        """Check if entire form is valid"""
        return all(state['valid'] for state in self.validation_state.values())
    
    def cancel_dialog(self):
        """Cancel and close dialog"""
        if self.dialog:
            self.dialog.destroy()
    
    def show(self):
        """Show the dialog"""
        if self.dialog:
            self.dialog.deiconify() 