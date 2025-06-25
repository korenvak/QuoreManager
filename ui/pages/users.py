"""
Users Management Page for Kitchen Quote Management System
Admin-only page for managing user accounts and permissions
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Any, List, Optional

class UsersPage:
    """Users management page - Admin only"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.users_data = []
        
        # Check if user has permission to access this page
        if self.current_user.get('role') != 'admin':
            self.show_access_denied()
            return
            
        self.users_container = None
        
    def create_content(self):
        """Create users page content"""
        # Check permission again
        if self.current_user.get('role') != 'admin':
            self.show_access_denied()
            return
            
        # Main container with clean white background and blue border
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="#FFFFFF",
            corner_radius=0,
            border_width=1,
            border_color="#E1E8F7"
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner container with padding and blue border
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E1E8F7"
        )
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Page header
        self.create_header(content_frame)
        
        # Users list
        self.create_users_list(content_frame)
        
        # Load users data
        self.load_users()
    
    def show_access_denied(self):
        """Show access denied message for non-admin users"""
        access_frame = ctk.CTkFrame(self.parent)
        access_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Access denied message
        denied_label = ctk.CTkLabel(
            access_frame,
            text="🚫\n\nגישה מוגבלת\n\nדף זה מיועד למנהלי מערכת בלבד",
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold"),
            text_color="#EF4444",
            justify="center"
        )
        denied_label.pack(expand=True)
    
    def create_header(self, parent):
        """Create page header with actions"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ניהול משתמשים",
            font=ctk.CTkFont(family="Heebo", size=28, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="ניהול משתמשי המערכת והרשאותיהם",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray",
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(5, 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(anchor="e", pady=(15, 0))
        
        # Add new user button
        add_user_btn = ctk.CTkButton(
            actions_frame,
            text="➕ משתמש חדש",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            command=self.add_new_user
        )
        add_user_btn.pack(side="right", padx=(0, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 רענן",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.load_users
        )
        refresh_btn.pack(side="right")
    
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
            
            # Edit button
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="ערוך",
                font=ctk.CTkFont(family="Heebo", size=12),
                height=30,
                width=80,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                command=lambda u=user: self.edit_user(u)
            )
            edit_btn.pack(side="right", padx=(5, 0))
            
            # Toggle active status button
            status_text = "השבת" if is_active else "הפעל"
            status_color = "#EF4444" if is_active else "#10B981"
            status_hover = "#DC2626" if is_active else "#059669"
            
            status_btn = ctk.CTkButton(
                actions_frame,
                text=status_text,
                font=ctk.CTkFont(family="Heebo", size=12),
                height=30,
                width=80,
                fg_color=status_color,
                hover_color=status_hover,
                command=lambda u=user: self.toggle_user_status(u)
            )
            status_btn.pack(side="right", padx=(5, 0))
            
            # Delete button (only for non-admin users)
            if role != 'admin':
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="מחק",
                    font=ctk.CTkFont(family="Heebo", size=12),
                    height=30,
                    width=80,
                    fg_color="#EF4444",
                    hover_color="#DC2626",
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
    """Dialog for adding/editing users"""
    
    def __init__(self, parent, title: str, user_data: Optional[Dict] = None, db_manager=None, on_success=None):
        self.parent = parent
        self.title = title
        self.user_data = user_data or {}
        self.db_manager = db_manager
        self.on_success = on_success
        self.dialog = None
        
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
        """Create user dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        
        # Make dialog responsive to screen size
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Calculate appropriate dialog size (35% of screen width, 85% of height)
        dialog_width = min(500, int(screen_width * 0.35))
        dialog_height = min(700, int(screen_height * 0.85))
        
        # Ensure minimum sizes
        dialog_width = max(450, dialog_width)
        dialog_height = max(600, dialog_height)
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}")
        self.dialog.resizable(True, True)  # Allow resizing
        
        # Set minimum window size
        self.dialog.minsize(450, 600)
        
        # Center dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main container with white background and blue border
        main_frame = ctk.CTkScrollableFrame(self.dialog, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=self.title,
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Load existing data if editing
        if self.user_data:
            self.load_user_data()
    
    def create_form_fields(self, parent):
        """Create form input fields"""
        fields_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        fields_frame.pack(fill="x", pady=(0, 30))
        
        # Username
        self.create_field(fields_frame, "שם משתמש *", self.username_var, "username")
        
        # Password (only for new users)
        if not self.user_data:
            self.create_field(fields_frame, "סיסמה *", self.password_var, "password", show_password=True)
        
        # First name
        self.create_field(fields_frame, "שם פרטי", self.first_name_var, "first_name")
        
        # Last name
        self.create_field(fields_frame, "שם משפחה", self.last_name_var, "last_name")
        
        # Email
        self.create_field(fields_frame, "דואר אלקטרוני", self.email_var, "email")
        
        # Role
        self.create_role_field(fields_frame)
        
        # Max discount
        self.create_field(fields_frame, "הנחה מקסימלית (%)", self.max_discount_var, "max_discount")
        
        # Active status
        self.create_checkbox_field(fields_frame, "משתמש פעיל", self.is_active_var)
    
    def create_field(self, parent, label: str, variable: ctk.StringVar, field_key: str, show_password: bool = False):
        """Create individual form field"""
        field_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        field_frame.pack(fill="x", pady=10)
        
        # Label
        field_label = ctk.CTkLabel(
            field_frame,
            text=label,
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        field_label.pack(anchor="e")
        
        # Input field
        entry = ctk.CTkEntry(
            field_frame,
            textvariable=variable,
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            show="*" if show_password else None
        )
        entry.pack(fill="x", pady=(5, 0))
    
    def create_role_field(self, parent):
        """Create role selection field"""
        field_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        field_frame.pack(fill="x", pady=10)
        
        # Label
        role_label = ctk.CTkLabel(
            field_frame,
            text="תפקיד *",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        role_label.pack(anchor="e")
        
        # Role selection
        role_menu = ctk.CTkOptionMenu(
            field_frame,
            variable=self.role_var,
            values=["admin", "manager", "employee", "viewer"],
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40
        )
        role_menu.pack(fill="x", pady=(5, 0))
    
    def create_checkbox_field(self, parent, label: str, variable: ctk.BooleanVar):
        """Create checkbox field"""
        field_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        field_frame.pack(fill="x", pady=10)
        
        checkbox = ctk.CTkCheckBox(
            field_frame,
            text=label,
            variable=variable,
            font=ctk.CTkFont(family="Heebo", size=14)
        )
        checkbox.pack(anchor="e")
    
    def create_buttons(self, parent):
        """Create action buttons"""
        buttons_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        buttons_frame.pack(fill="x", pady=20)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="ביטול",
            font=ctk.CTkFont(family="Heebo", size=16),
            height=45,
            width=120,
            fg_color="gray",
            hover_color="#6B7280",
            command=self.cancel_dialog
        )
        cancel_button.pack(side="left")
        
        # Save button
        save_text = "עדכן משתמש" if self.user_data else "הוסף משתמש"
        save_button = ctk.CTkButton(
            buttons_frame,
            text=save_text,
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            height=45,
            width=150,
            fg_color="#10B981",
            hover_color="#059669",
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