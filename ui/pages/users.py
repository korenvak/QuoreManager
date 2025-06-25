"""
Users Management Page for Kitchen Quote Management System - Modern Professional Design
Admin-only page for managing user accounts and permissions
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Any, List, Optional
from styling.theme_system import ModernThemeManager, THEMES
from config.settings import SettingsManager

class UsersPage:
    """Modern professional users management page - Admin only"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.users_data = []
        
        # Initialize theme system
        self.settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
        # Check if user has permission to access this page
        if self.current_user.get('role') != 'admin':
            self.show_access_denied()
            return
            
        self.users_container = None
        
    def create_content(self):
        """Create modern professional users page content"""
        # Check permission again
        if self.current_user.get('role') != 'admin':
            self.show_access_denied()
            return
            
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
        
        # Modern users list
        self.create_users_list(inner_frame)
        
        # Load users data
        self.load_users()
    
    def show_access_denied(self):
        """Show modern access denied message for non-admin users"""
        access_frame = ctk.CTkFrame(
            self.parent,
            fg_color=self.theme['bg_secondary']
        )
        access_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Access denied card
        denied_card = ctk.CTkFrame(
            access_frame,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        denied_card.pack(expand=True, padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('xl'))
        
        # Access denied message
        denied_label = ctk.CTkLabel(
            denied_card,
            text="🚫\n\nגישה מוגבלת\n\nדף זה מיועד למנהלי מערכת בלבד",
            font=self.theme_manager.create_ctk_font('heading'),
            text_color="#EF4444",
            justify="center"
        )
        denied_label.pack(expand=True, padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('xl'))
    
    def create_modern_header(self, parent):
        """Create modern professional page header with actions"""
        # Header card
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
            text="ניהול משתמשים",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_section,
            text="ניהול משתמשי המערכת והרשאותיהם",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(anchor="e")
        
        # Refresh button - using theme colors
        refresh_btn = self.theme_manager.create_modern_button(
            actions_frame,
            text="🔄  רענן",
            style="primary",
            command=self.load_users
        )
        refresh_btn.pack(side="right")
        
        # Add new user button - using theme colors  
        add_user_btn = self.theme_manager.create_modern_button(
            actions_frame,
            text="➕  משתמש חדש",
            style="secondary",
            command=self.add_new_user
        )
        add_user_btn.pack(side="right", padx=(0, self.theme_manager.get_spacing('sm')))
    
    def create_users_list(self, parent):
        """Create users list container"""
        # Users container – plain frame (outer page already scrollable)
        self.users_container = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        self.users_container.pack(fill="both", expand=True)
        
        # Loading placeholder
        loading_label = ctk.CTkLabel(
            self.users_container,
            text="טוען משתמשים...",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray"
        )
        loading_label.pack(pady=50)
    
    def load_users(self):
        """Load users asynchronously"""
        def load_data():
            try:
                # Use get_all_users_dict to avoid session binding issues
                users = self.db_manager.get_all_users_dict()
                self.parent.after(0, lambda: self.display_users(users))
            except Exception as e:
                self.parent.after(0, lambda: self.handle_users_error(str(e)))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def display_users(self, users):
        """Display users in the container"""
        # Clear existing content
        if self.users_container:
            for widget in self.users_container.winfo_children():
                widget.destroy()
        
        if not users:
            if self.users_container:
                empty_label = ctk.CTkLabel(
                    self.users_container,
                    text="אין משתמשים במערכת",
                    font=ctk.CTkFont(family="Heebo", size=16),
                    text_color="gray"
                )
                empty_label.pack(pady=50)
            return
        
        # Display users as cards
        for user in users:
            self.create_user_card(user)
    
    def create_user_card(self, user):
        """Create individual user card"""
        if not self.users_container:
            return
            
        try:
            card = ctk.CTkFrame(self.users_container, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
            card.pack(fill="x", padx=10, pady=8)
            
            # User info
            info_frame = ctk.CTkFrame(card, fg_color="#FFFFFF")
            info_frame.pack(fill="x", padx=20, pady=15)
            
            # User name - handle dict objects
            full_name = f"{user.get('first_name', '') or ''} {user.get('last_name', '') or ''}".strip()
            display_name = full_name if full_name else user.get('username', 'משתמש')
            role = user.get('role', 'viewer')
            is_active = user.get('is_active', False)
            max_discount = user.get('max_discount', 0)
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=display_name,
                font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
                anchor="e"
            )
            name_label.pack(anchor="e")
            
            # Role and status
            role_text = {
                'admin': 'מנהל מערכת',
                'manager': 'מנהל',
                'employee': 'עובד',
                'viewer': 'צופה'
            }.get(role, 'לא ידוע')
            
            status_text = "פעיל" if is_active else "לא פעיל"
            
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"תפקיד: {role_text} | סטטוס: {status_text} | הנחה מקסימלית: {max_discount}%",
                font=ctk.CTkFont(family="Heebo", size=12),
                text_color="gray",
                anchor="e"
            )
            details_label.pack(anchor="e", pady=(5, 0))
            
            # Action buttons
            actions_frame = ctk.CTkFrame(card, fg_color="#FFFFFF")
            actions_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # Edit button - using theme colors
            edit_btn = self.theme_manager.create_modern_button(
                actions_frame,
                text="ערוך",
                style="primary",
                size="small",
                width=80,
                command=lambda u=user: self.edit_user(u)
            )
            edit_btn.pack(side="right", padx=(5, 0))
            
            # Toggle active status button - using theme colors
            status_text = "השבת" if is_active else "הפעל"
            status_style = "danger" if is_active else "success"
            
            status_btn = self.theme_manager.create_modern_button(
                actions_frame,
                text=status_text,
                style=status_style,
                size="small",
                width=80,
                command=lambda u=user: self.toggle_user_status(u)
            )
            status_btn.pack(side="right", padx=(5, 0))
            
            # Delete button (only for non-admin users) - using theme colors
            if role != 'admin':
                delete_btn = self.theme_manager.create_modern_button(
                    actions_frame,
                    text="מחק",
                    style="danger",
                    size="small", 
                    width=80,
                    command=lambda u=user: self.delete_user(u)
                )
                delete_btn.pack(side="right", padx=(5, 0))
            
        except Exception as e:
            # Create error card
            if self.users_container:
                error_card = ctk.CTkFrame(self.users_container, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
                error_card.pack(fill="x", padx=10, pady=8)
                
                error_label = ctk.CTkLabel(
                    error_card,
                    text=f"שגיאה בהצגת משתמש: {e}",
                    font=ctk.CTkFont(family="Heebo", size=14),
                    text_color="#EF4444"
                )
                error_label.pack(pady=20)
    
    def handle_users_error(self, error: str):
        """Handle users loading error"""
        # Clear existing content
        if self.users_container:
            for widget in self.users_container.winfo_children():
                widget.destroy()
            
            error_label = ctk.CTkLabel(
                self.users_container,
                text=f"שגיאה בטעינת משתמשים: {error}",
                font=ctk.CTkFont(family="Heebo", size=16),
                text_color="#EF4444"
            )
            error_label.pack(pady=50)
    
    def add_new_user(self):
        """Add new user dialog"""
        if self.db_manager:
            dialog = UserDialog(
                parent=self.parent,
                title="הוסף משתמש חדש",
                user_data={},  # Empty dict for new user
                db_manager=self.db_manager,
                on_success=self.load_users
            )

    def edit_user(self, user):
        """Edit user dialog"""
        if self.db_manager:
            dialog = UserDialog(
                parent=self.parent,
                title="ערוך משתמש",
                user_data=user,
                db_manager=self.db_manager,
                on_success=self.load_users
            )

    def toggle_user_status(self, user):
        """Toggle user active status"""
        current_status = user.get('is_active', False)
        new_status = not current_status
        status_text = "להפעיל" if new_status else "להשבית"
        
        if messagebox.askyesno("שינוי סטטוס", f"האם אתה בטוח שברצונך {status_text} את המשתמש {user.get('username', '')}?"):
            success = self.db_manager.update_user_status(user['id'], new_status)
            if success:
                messagebox.showinfo("הצלחה", f"סטטוס המשתמש שונה בהצלחה")
                self.load_users()
            else:
                messagebox.showerror("שגיאה", "שגיאה בשינוי סטטוס המשתמש")

    def delete_user(self, user):
        """Delete user - permanently if possible, else deactivate"""
        username = user.get('username', '')
        if not messagebox.askyesno("מחיקת משתמש", f"האם אתה בטוח שברצונך למחוק לצמיתות את המשתמש {username}?"):
            return
        # Attempt permanent delete first
        success = self.db_manager.delete_user(user['id'], force=True)
        if success:
            messagebox.showinfo("הצלחה", "המשתמש נמחק לצמיתות")
            self.load_users()
            return
        # Fallback: deactivate
        if messagebox.askyesno("לא ניתן למחוק", "למשתמש יש הצעות או טיוטות קיימות. האם להפוך אותו ללא פעיל במקום?"):
            success = self.db_manager.update_user_status(user['id'], False)
            if success:
                messagebox.showinfo("עודכן", "המשתמש הוגדר כלא פעיל")
                self.load_users()
            else:
                messagebox.showerror("שגיאה", "שגיאה בעדכון סטטוס המשתמש")


class UserDialog:
    """Modern dialog for adding/editing users with beautiful design"""
    
    def __init__(self, parent, title: str, user_data: Optional[Dict] = None, db_manager=None, on_success=None):
        self.parent = parent
        self.title = title
        self.user_data = user_data or {}
        self.db_manager = db_manager
        self.on_success = on_success
        self.dialog = None
        
        # Import theme manager
        from styling.theme_system import ModernThemeManager
        from config.settings import SettingsManager
        settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(settings_manager)
        
        # Form variables
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.first_name_var = ctk.StringVar()
        self.last_name_var = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.role_var = ctk.StringVar(value="employee")
        self.max_discount_var = ctk.StringVar(value="0")
        self.is_active_var = ctk.BooleanVar(value=True)
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create modern user dialog with beautiful design"""
        current_theme = self.theme_manager.get_current_theme()
        
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        
        # Modern sizing and positioning
        dialog_width = 520
        dialog_height = 700
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(480, 650)
        
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
        if self.user_data:
            self.load_user_data()
    
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
        icon_text = "👥" if not self.user_data else "✏️"
        icon_label = ctk.CTkLabel(
            header_content,
            text=icon_text,
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
        subtitle_text = "הוספת משתמש חדש למערכת" if not self.user_data else "עריכת פרטי המשתמש"
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
        card_frame.pack(fill="both", expand=True, padx=25, pady=(25, 25))
        
        # Scrollable content
        main_frame = ctk.CTkScrollableFrame(card_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Action buttons
        self.create_modern_buttons(main_frame)
    
    def create_form_fields(self, parent):
        """Create modern form input fields"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Main form container
        fields_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            fg_color=current_theme['card_bg'],
            border_width=1,
            border_color=current_theme['border']
        )
        fields_frame.pack(fill="x", pady=(0, 25))
        
        # Form title
        form_title = ctk.CTkLabel(
            fields_frame,
            text="פרטי המשתמש",
            font=ctk.CTkFont(family="Assistant", size=18, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        form_title.pack(anchor="e", padx=20, pady=(20, 15))
        
        # Fields container
        fields_container = ctk.CTkFrame(fields_frame, fg_color="transparent")
        fields_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Username field
        self.create_modern_field(fields_container, "שם משתמש *", self.username_var, "username")
        
        # Password field (only for new users)
        if not self.user_data:
            self.create_modern_field(fields_container, "סיסמה *", self.password_var, "password", show_password=True)
        
        # Personal details section
        section_label = ctk.CTkLabel(
            fields_container,
            text="פרטים אישיים",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        section_label.pack(anchor="e", pady=(20, 10))
        
        # First name
        self.create_modern_field(fields_container, "שם פרטי", self.first_name_var, "first_name")
        
        # Last name
        self.create_modern_field(fields_container, "שם משפחה", self.last_name_var, "last_name")
        
        # Email
        self.create_modern_field(fields_container, "דואר אלקטרוני", self.email_var, "email")
        
        # Role and permissions section
        section_label2 = ctk.CTkLabel(
            fields_container,
            text="תפקיד והרשאות",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        section_label2.pack(anchor="e", pady=(20, 10))
        
        # Role
        self.create_modern_role_field(fields_container)
        
        # Max discount
        self.create_modern_field(fields_container, "הנחה מקסימלית (%)", self.max_discount_var, "max_discount")
        
        # Active status
        self.create_modern_checkbox_field(fields_container, "משתמש פעיל", self.is_active_var)
    
    def create_modern_field(self, parent, label: str, variable: ctk.StringVar, field_key: str, show_password: bool = False):
        """Create individual modern form field"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=10)
        
        # Label with modern styling
        field_label = ctk.CTkLabel(
            field_frame,
            text=label,
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        field_label.pack(anchor="e", pady=(0, 6))
        
        # Input field with modern styling
        entry = ctk.CTkEntry(
            field_frame,
            textvariable=variable,
            font=ctk.CTkFont(family="Assistant", size=14),
            height=46,
            corner_radius=12,
            border_width=2,
            border_color=current_theme['border'],
            fg_color=current_theme['input_bg'],
            text_color=current_theme['text_primary'],
            show="*" if show_password else None
        )
        entry.pack(fill="x")
    
    def create_modern_role_field(self, parent):
        """Create modern role selection field"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=10)
        
        # Label
        role_label = ctk.CTkLabel(
            field_frame,
            text="תפקיד *",
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_primary'],
            anchor="e"
        )
        role_label.pack(anchor="e", pady=(0, 6))
        
        # Role selection with modern styling
        role_menu = ctk.CTkOptionMenu(
            field_frame,
            variable=self.role_var,
            values=["admin", "manager", "employee", "viewer"],
            font=ctk.CTkFont(family="Assistant", size=14),
            height=46,
            corner_radius=12,
            fg_color=current_theme['primary'],
            button_color=current_theme['primary'],
            button_hover_color=current_theme['primary_hover'],
            dropdown_fg_color=current_theme['card_bg'],
            dropdown_text_color=current_theme['text_primary']
        )
        role_menu.pack(fill="x")
    
    def create_modern_checkbox_field(self, parent, label: str, variable: ctk.BooleanVar):
        """Create modern checkbox field"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=15)
        
        # Checkbox with modern styling
        checkbox = ctk.CTkCheckBox(
            field_frame,
            text=label,
            variable=variable,
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_primary'],
            fg_color=current_theme['primary'],
            hover_color=current_theme['primary_hover'],
            checkmark_color=("#FFFFFF", "#F1F5F9")
        )
        checkbox.pack(anchor="e")
    
    def create_modern_buttons(self, parent):
        """Create modern action buttons with gradients and shadows"""
        # Buttons container
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=25)
        
        # Cancel button
        cancel_button = self.theme_manager.create_modern_button(
            buttons_frame,
            text="ביטול",
            style="outline",
            size="large",
            width=130,
            command=self.cancel_dialog
        )
        cancel_button.pack(side="left")
        
        # Save button
        save_text = "עדכן משתמש" if self.user_data else "הוסף משתמש"
        save_button = self.theme_manager.create_modern_button(
            buttons_frame,
            text=save_text,
            style="primary",
            size="large",
            width=150,
            command=self.save_user
        )
        save_button.pack(side="right")
    
    def load_user_data(self):
        """Load existing user data for editing"""
        if not self.user_data:
            return
        
        self.username_var.set(self.user_data.get('username', ''))
        self.first_name_var.set(self.user_data.get('first_name', ''))
        self.last_name_var.set(self.user_data.get('last_name', ''))
        self.email_var.set(self.user_data.get('email', ''))
        self.role_var.set(self.user_data.get('role', 'employee'))
        self.max_discount_var.set(str(self.user_data.get('max_discount', 0)))
        self.is_active_var.set(self.user_data.get('is_active', True))
    
    def save_user(self):
        """Save user data"""
        try:
            # Validate required fields
            if not self.username_var.get().strip():
                messagebox.showerror("שגיאה", "שם משתמש הוא שדה חובה")
                return
            
            if not self.user_data and not self.password_var.get().strip():
                messagebox.showerror("שגיאה", "סיסמה היא שדה חובה")
                return
            
            # Validate max discount
            try:
                max_discount = float(self.max_discount_var.get() or 0)
                if max_discount < 0 or max_discount > 100:
                    messagebox.showerror("שגיאה", "הנחה מקסימלית חייבת להיות בין 0 ל-100")
                    return
            except ValueError:
                messagebox.showerror("שגיאה", "הנחה מקסימלית חייבת להיות מספר")
                return
            
            # Collect data
            user_data = {
                'username': self.username_var.get().strip(),
                'first_name': self.first_name_var.get().strip(),
                'last_name': self.last_name_var.get().strip(),
                'email': self.email_var.get().strip(),
                'role': self.role_var.get(),
                'max_discount': max_discount,
                'is_active': self.is_active_var.get()
            }
            
            # Add password for new users
            if not self.user_data:
                user_data['password'] = self.password_var.get().strip()
            
            # Save to database
            if self.user_data and self.db_manager:
                # Update existing user
                success = self.db_manager.update_user(self.user_data['id'], **user_data)
                if success:
                    messagebox.showinfo("הצלחה", "פרטי המשתמש עודכנו בהצלחה")
                else:
                    messagebox.showerror("שגיאה", "שגיאה בעדכון פרטי המשתמש")
                    return
            elif self.db_manager:
                # Create new user
                from core.auth import AuthManager
                auth_manager = AuthManager(self.db_manager)
                success = auth_manager.create_user(**user_data)
                if success:
                    messagebox.showinfo("הצלחה", "המשתמש נוסף בהצלחה למערכת")
                else:
                    messagebox.showerror("שגיאה", "שגיאה ביצירת משתמש חדש")
                    return
            
            # Call success callback
            if self.on_success:
                self.on_success()
            
            # Close dialog
            if self.dialog:
                self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת המשתמש: {e}")
    
    def cancel_dialog(self):
        """Cancel and close dialog"""
        if self.dialog:
            self.dialog.destroy() 