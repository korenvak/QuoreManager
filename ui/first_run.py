"""
First Run Setup Window for Kitchen Quote Management System
Handles creation of the first admin user
"""

import customtkinter as ctk
from tkinter import messagebox
import re
from typing import Callable, Dict, Any
from pathlib import Path

class FirstRunSetup:
    """First run setup window for creating admin user"""
    
    def __init__(self, auth_manager, on_complete: Callable):
        self.auth_manager = auth_manager
        self.on_complete = on_complete
        
        self.window = None
        self.setup_widgets()
    
    def setup_widgets(self):
        """Setup the first run window"""
        self.window = ctk.CTk()
        self.window.title("הגדרה ראשונית - מערכת ניהול הצעות מטבח")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Set window icon
        self.set_window_icon()
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        # Create UI
        self.create_ui()
    
    def center_window(self):
        """Center window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def set_window_icon(self):
        """Set window icon"""
        try:
            icon_path = Path(__file__).parent.parent / "resources" / "White_Logo.ico"
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass
    
    def create_ui(self):
        """Create user interface"""
        # Main container with white background
        main_frame = ctk.CTkFrame(self.window, corner_radius=0, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Form
        self.create_form(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo section
        logo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_frame.pack(pady=(0, 10))
        
        try:
            # Try to load logo with better quality
            from PIL import Image
            logo_path = Path(__file__).parent.parent / "resources" / "logo.png"
            if logo_path.exists():
                # Load and use PIL Image directly for better quality
                pil_image = Image.open(str(logo_path))
                logo_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(100, 100)  # Increased size for better visibility
                )
                logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="")
                logo_label.pack()
            else:
                raise FileNotFoundError("Logo not found")
        except Exception:
            # Professional fallback icon
            logo_label = ctk.CTkLabel(
                logo_frame,
                text="🏢",  # Changed to office building for professional look
                font=ctk.CTkFont(size=70)  # Slightly larger
            )
            logo_label.pack()
        
        # Welcome icon
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="🎉",
            font=ctk.CTkFont(size=50)
        )
        welcome_label.pack(pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ברוכים הבאים למערכת ניהול הצעות מטבח",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="כדי להתחיל, צור חשבון מנהל ראשון",
            font=ctk.CTkFont(family="Heebo", size=14),
            text_color="gray"
        )
        subtitle_label.pack()
    
    def create_form(self, parent):
        """Create form section"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Form title
        form_title = ctk.CTkLabel(
            form_frame,
            text="פרטי מנהל המערכת",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold")
        )
        form_title.pack(pady=(20, 15))
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="שם משתמש:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        username_label.pack(anchor="e", pady=(0, 5), padx=20)
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="הזן שם משתמש (לפחות 3 תווים)",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.username_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # First name field
        first_name_label = ctk.CTkLabel(
            form_frame,
            text="שם פרטי:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        first_name_label.pack(anchor="e", pady=(0, 5), padx=20)
        
        self.first_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="שם פרטי",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.first_name_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Last name field
        last_name_label = ctk.CTkLabel(
            form_frame,
            text="שם משפחה:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        last_name_label.pack(anchor="e", pady=(0, 5), padx=20)
        
        self.last_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="שם משפחה",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.last_name_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="סיסמה:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        password_label.pack(anchor="e", pady=(0, 5), padx=20)
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="סיסמה (לפחות 6 תווים)",
            show="•",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.password_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Confirm password field
        confirm_password_label = ctk.CTkLabel(
            form_frame,
            text="אישור סיסמה:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        confirm_password_label.pack(anchor="e", pady=(0, 5), padx=20)
        
        self.confirm_password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="הזן סיסמה שוב",
            show="•",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 20), padx=20)
    
    def create_buttons(self, parent):
        """Create buttons section"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        # Create admin button
        self.create_button = ctk.CTkButton(
            button_frame,
            text="צור מנהל וכנס למערכת",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            height=50,
            command=self.handle_create_admin
        )
        self.create_button.pack(fill="x", padx=20)
        
        # Exit button
        exit_button = ctk.CTkButton(
            button_frame,
            text="יציאה",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.handle_exit
        )
        exit_button.pack(fill="x", padx=20, pady=(10, 0))
    
    def validate_form(self) -> bool:
        """Validate form data"""
        username = self.username_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Username validation
        if len(username) < 3:
            messagebox.showerror("שגיאה", "שם המשתמש חייב להיות לפחות 3 תווים")
            self.username_entry.focus_set()
            return False
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messagebox.showerror("שגיאה", "שם משתמש יכול להכיל רק אותיות אנגליות, מספרים וקו תחתון")
            self.username_entry.focus_set()
            return False
        
        # Name validation
        if len(first_name) < 2:
            messagebox.showerror("שגיאה", "שם פרטי חייב להיות לפחות 2 תווים")
            self.first_name_entry.focus_set()
            return False
        
        if len(last_name) < 2:
            messagebox.showerror("שגיאה", "שם משפחה חייב להיות לפחות 2 תווים")
            self.last_name_entry.focus_set()
            return False
        
        # Password validation
        if len(password) < 6:
            messagebox.showerror("שגיאה", "הסיסמה חייבת להיות לפחות 6 תווים")
            self.password_entry.focus_set()
            return False
        
        if password != confirm_password:
            messagebox.showerror("שגיאה", "הסיסמאות אינן תואמות")
            self.confirm_password_entry.focus_set()
            return False
        
        return True
    
    def handle_create_admin(self):
        """Handle admin creation"""
        if not self.validate_form():
            return
        
        username = self.username_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        password = self.password_entry.get()
        
        # Disable button during creation
        self.create_button.configure(state="disabled", text="יוצר חשבון...")
        
        try:
            # Create admin user
            admin_user = self.auth_manager.create_admin_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            messagebox.showinfo(
                "הצלחה", 
                f"חשבון המנהל נוצר בהצלחה!\nשם משתמש: {username}"
            )
            
            # Close window and call completion callback
            self.window.destroy()
            self.on_complete(admin_user)
            
        except Exception as e:
            self.create_button.configure(state="normal", text="צור מנהל וכנס למערכת")
            messagebox.showerror("שגיאה", f"שגיאה ביצירת החשבון: {str(e)}")
    
    def handle_exit(self):
        """Handle exit"""
        if messagebox.askyesno("יציאה", "האם אתה בטוח שברצונך לצאת מהמערכת?"):
            self.window.quit()
    
    def show(self):
        """Show the setup window"""
        if self.window:
            self.window.mainloop() 