"""
Login Window for Kitchen Quote Management System
Handles user authentication with modern UI and theme support
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Callable, Optional, Dict, Any
from pathlib import Path

class LoginWindow:
    """Login window with authentication"""
    
    def __init__(self, auth_manager, settings_manager, on_success: Callable, on_error: Callable):
        self.auth_manager = auth_manager
        self.settings_manager = settings_manager
        self.on_success = on_success
        self.on_error = on_error
        
        self.window = None
        self.username_entry = None
        self.password_entry = None
        self.login_button = None
        self.theme_button = None
        
        self.setup_window()
    
    def setup_window(self):
        """Setup the login window"""
        self.window = ctk.CTk()
        self.window.title("מערכת ניהול הצעות מטבח - כניסה")
        
        # Make window responsive to screen size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate appropriate window size
        window_width = min(400, int(screen_width * 0.4))
        window_height = min(550, int(screen_height * 0.7))
        
        # Ensure minimum sizes
        window_width = max(350, window_width)
        window_height = max(500, window_height)
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.resizable(True, True)  # Allow resizing
        
        # Set minimum window size
        self.window.minsize(350, 500)
        
        # Center window on screen
        self.center_window()
        
        # Set window icon
        self.set_window_icon()
        
        # Create UI elements
        self.create_widgets()
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.handle_login())
        
        # Set focus to username entry
        self.window.after(100, self.username_entry.focus_set)
    
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
            pass  # Ignore icon errors
    
    def create_widgets(self):
        """Create and arrange UI widgets"""
        # Main container with white background
        main_frame = ctk.CTkFrame(self.window, corner_radius=0, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo section
        self.create_logo_section(main_frame)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="כניסה למערכת",
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.pack(pady=(20, 30))
        
        # Login form
        self.create_login_form(main_frame)
        
        # Theme toggle button
        self.create_theme_toggle(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_logo_section(self, parent):
        """Create logo section"""
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        logo_frame.pack(pady=(10, 0))
        
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
    
    def create_login_form(self, parent):
        """Create login form"""
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(pady=20, padx=40, fill="x")
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="שם משתמש:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        username_label.pack(anchor="e", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="הזן שם משתמש",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="סיסמה:",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        password_label.pack(anchor="e", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="הזן סיסמה",
            show="•",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Login button
        self.login_button = ctk.CTkButton(
            form_frame,
            text="כניסה",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            height=45,
            command=self.handle_login
        )
        self.login_button.pack(fill="x", pady=(0, 10))
        
        # Forgot password link (placeholder)
        forgot_label = ctk.CTkLabel(
            form_frame,
            text="שכחת סיסמה? פנה למנהל המערכת",
            font=ctk.CTkFont(family="Heebo", size=12),
            text_color="gray"
        )
        forgot_label.pack(pady=(10, 0))
    
    def create_theme_toggle(self, parent):
        """Create theme toggle button"""
        theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        theme_frame.pack(pady=10)
        
        current_theme = self.settings_manager.get('theme_mode', 'light')
        theme_text = "מצב כהה" if current_theme == 'light' else "מצב בהיר"
        
        self.theme_button = ctk.CTkButton(
            theme_frame,
            text=theme_text,
            font=ctk.CTkFont(family="Heebo", size=12),
            width=100,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.pack()
    
    def create_footer(self, parent):
        """Create footer section"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=10)
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="גרסה 1.0.0",
            font=ctk.CTkFont(family="Heebo", size=10),
            text_color="gray"
        )
        version_label.pack()
        
        company_label = ctk.CTkLabel(
            footer_frame,
            text="© Panel Kitchens 2024",
            font=ctk.CTkFont(family="Heebo", size=10),
            text_color="gray"
        )
        company_label.pack()
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("שגיאה", "אנא הזן שם משתמש וסיסמה")
            return
        
        # Disable login button during authentication
        self.login_button.configure(state="disabled", text="מתחבר...")
        
        # Perform authentication in background thread
        threading.Thread(target=self.authenticate, args=(username, password), daemon=True).start()
    
    def authenticate(self, username: str, password: str):
        """Authenticate user in background thread"""
        try:
            user = self.auth_manager.authenticate(username, password)
            
            # Update UI in main thread
            self.window.after(0, self.handle_auth_result, user)
            
        except Exception as e:
            self.window.after(0, self.handle_auth_error, str(e))
    
    def handle_auth_result(self, user: Optional[Dict[str, Any]]):
        """Handle authentication result"""
        # Re-enable login button
        self.login_button.configure(state="normal", text="כניסה")
        
        if user:
            # Clear password field
            self.password_entry.delete(0, 'end')
            self.on_success(user)
        else:
            messagebox.showerror("שגיאת כניסה", "שם משתמש או סיסמה שגויים")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus_set()
            self.on_error("Invalid credentials")
    
    def handle_auth_error(self, error: str):
        """Handle authentication error"""
        # Re-enable login button
        self.login_button.configure(state="normal", text="כניסה")
        
        messagebox.showerror("שגיאה", f"שגיאה בהתחברות: {error}")
        self.on_error(error)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.settings_manager.get('theme_mode', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        # Update settings
        self.settings_manager.set('theme_mode', new_theme)
        
        # Apply theme
        ctk.set_appearance_mode(new_theme)
        
        # Update button text
        theme_text = "מצב כהה" if new_theme == 'light' else "מצב בהיר"
        self.theme_button.configure(text=theme_text)
    
    def show(self):
        """Show the login window"""
        if self.window:
            self.window.deiconify()
            self.window.mainloop()
    
    def destroy(self):
        """Destroy the login window"""
        if self.window:
            self.window.destroy()
            self.window = None 