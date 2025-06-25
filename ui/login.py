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
    """Login window with authentication and modern design"""
    
    def __init__(self, auth_manager, settings_manager, on_success: Callable, on_error: Callable):
        self.auth_manager = auth_manager
        self.settings_manager = settings_manager
        self.on_success = on_success
        self.on_error = on_error
        
        # Import theme manager
        from styling.theme_system import ModernThemeManager
        self.theme_manager = ModernThemeManager(settings_manager)
        
        self.window = None
        self.username_entry = None
        self.password_entry = None
        self.login_button = None
        self.theme_button = None
        
        self.setup_window()
    
    def setup_window(self):
        """Setup the login window with modern design"""
        self.window = ctk.CTk()
        self.window.title("מערכת ניהול הצעות מטבח - כניסה")
        
        # Configure modern colors
        current_theme = self.theme_manager.get_current_theme()
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("light")
        
        # Window size and positioning
        window_width = 520
        window_height = 680
        
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.resizable(False, False)  # Fixed size for login
        
        # Center window on screen
        self.center_window()
        
        # Set window icon using version 5 icons
        self.set_window_icon()
        
        # Create modern UI
        self.create_modern_widgets()
        
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
        """Set window icon using version 2 icons"""
        try:
            # Use correct version 2 icons for each theme
            icon_name = "version2_blue_icon.ico" if self.theme_manager.current_color_theme == 'blue' else "version2_icon.ico"
            icon_path = Path(__file__).parent.parent / "resources" / icon_name
            
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass  # Ignore icon errors
    
    def create_modern_widgets(self):
        """Create modern UI widgets with beautiful design"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Main container with beautiful gradient background
        main_frame = ctk.CTkFrame(
            self.window, 
            corner_radius=0,
            fg_color=("#F8FAFC", "#1E293B")  # Light/dark mode support
        )
        main_frame.pack(fill="both", expand=True)
        
        # Beautiful gradient header
        header_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=0,
            height=220,
            fg_color=current_theme['primary']
        )
        header_frame.pack(fill="x", pady=0)
        header_frame.pack_propagate(False)
        
        # Logo section with version 2 icon
        self.create_modern_logo_section(header_frame)
        
        # Login card container
        card_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=24,
            fg_color=("#FFFFFF", "#334155"),
            border_width=1,
            border_color=("#E2E8F0", "#475569")
        )
        card_frame.pack(pady=(40, 60), padx=40, fill="x")
        
        # Add subtle shadow effect (visual styling)
        shadow_frame = ctk.CTkFrame(
            card_frame,
            corner_radius=20,
            fg_color="transparent"
        )
        shadow_frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Card content
        self.create_login_card_content(shadow_frame)
        
        # Theme toggle in bottom corner
        self.create_modern_theme_toggle(main_frame)
        
        # Professional footer
        self.create_modern_footer(main_frame)
    
    def create_modern_logo_section(self, parent):
        """Create beautiful logo section with version 2 icon"""
        logo_container = ctk.CTkFrame(parent, fg_color="transparent")
        logo_container.pack(expand=True, fill="both")
        
        try:
            # Use correct version 2 icons for each theme
            icon_name = "version2_blue_icon.ico" if self.theme_manager.current_color_theme == 'blue' else "version2_icon.ico"
            
            # Try to load version 2 icon as image
            from PIL import Image
            icon_path = Path(__file__).parent.parent / "resources" / icon_name
            
            if icon_path.exists():
                # Load the icon file and convert to image
                try:
                    pil_image = Image.open(str(icon_path))
                    # Convert to RGBA if needed
                    if pil_image.mode != 'RGBA':
                        pil_image = pil_image.convert('RGBA')
                    
                    logo_image = ctk.CTkImage(
                        light_image=pil_image,
                        dark_image=pil_image,
                        size=(120, 120)
                    )
                    logo_label = ctk.CTkLabel(
                        logo_container, 
                        image=logo_image, 
                        text="",
                        fg_color="transparent"
                    )
                    logo_label.pack(pady=(30, 20))
                except Exception:
                    raise FileNotFoundError("Could not process icon")
            else:
                raise FileNotFoundError("Icon not found")
                
        except Exception:
            # Professional fallback with beautiful styling
            logo_label = ctk.CTkLabel(
                logo_container,
                text="🏢",
                font=ctk.CTkFont(size=80),
                text_color=["#FFFFFF", "#F1F5F9"],
                fg_color="transparent"
            )
            logo_label.pack(pady=(30, 20))
        
        # Welcome text with modern typography
        welcome_label = ctk.CTkLabel(
            logo_container,
            text="ברוכים הבאים למערכת",
            font=ctk.CTkFont(family="Assistant", size=24, weight="bold"),
            text_color=("#FFFFFF", "#F1F5F9"),
            fg_color="transparent"
        )
        welcome_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            logo_container,
            text="ניהול הצעות מטבח מקצועי",
            font=ctk.CTkFont(family="Assistant", size=16),
            text_color=("#FFFFFF", "#F1F5F9"),
            fg_color="transparent"
        )
        subtitle_label.pack()
    
    def create_login_card_content(self, parent):
        """Create beautiful login form inside card"""
        current_theme = self.theme_manager.get_current_theme()
        
        # Card inner container
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=32, pady=32)
        
        # Title with modern typography
        title_label = ctk.CTkLabel(
            content_frame,
            text="כניסה למערכת",
            font=ctk.CTkFont(family="Assistant", size=28, weight="bold"),
            text_color=current_theme['text_primary']
        )
        title_label.pack(pady=(0, 32))
        
        # Username field with modern styling
        username_label = ctk.CTkLabel(
            content_frame,
            text="שם משתמש",
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_secondary'],
            anchor="e"
        )
        username_label.pack(anchor="e", pady=(0, 8))
        
        self.username_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="הזן שם משתמש",
            font=ctk.CTkFont(family="Assistant", size=16),
            height=50,
            corner_radius=12,
            border_width=2,
            border_color=current_theme['border'],
            fg_color=current_theme['input_bg'],
            text_color=current_theme['text_primary']
        )
        self.username_entry.pack(fill="x", pady=(0, 20))
        
        # Password field with modern styling
        password_label = ctk.CTkLabel(
            content_frame,
            text="סיסמה",
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=current_theme['text_secondary'],
            anchor="e"
        )
        password_label.pack(anchor="e", pady=(0, 8))
        
        self.password_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="הזן סיסמה",
            show="•",
            font=ctk.CTkFont(family="Assistant", size=16),
            height=50,
            corner_radius=12,
            border_width=2,
            border_color=current_theme['border'],
            fg_color=current_theme['input_bg'],
            text_color=current_theme['text_primary']
        )
        self.password_entry.pack(fill="x", pady=(0, 32))
        
        # Modern login button with gradient and shadow
        self.login_button = self.theme_manager.create_modern_button(
            content_frame,
            text="כניסה למערכת",
            style="primary",
            size="large",
            command=self.handle_login
        )
        self.login_button.pack(fill="x", pady=(0, 16))
        
        # Forgot password text with modern styling
        forgot_label = ctk.CTkLabel(
            content_frame,
            text="שכחת סיסמה? פנה למנהל המערכת",
            font=ctk.CTkFont(family="Assistant", size=13),
            text_color=current_theme['text_tertiary']
        )
        forgot_label.pack(pady=(16, 0))
    
    def create_modern_theme_toggle(self, parent):
        """Create modern theme toggle button"""
        theme_container = ctk.CTkFrame(parent, fg_color="transparent")
        theme_container.pack(side="bottom", anchor="w", padx=20, pady=20)
        
        current_theme_name = self.theme_manager.current_color_theme
        theme_text = "🔴 עבור לנושא אדום" if current_theme_name == 'blue' else "🔵 עבור לנושא כחול"
        
        self.theme_button = self.theme_manager.create_modern_button(
            theme_container,
            text=theme_text,
            style="outline",
            size="small",
            width=160,
            command=self.toggle_theme
        )
        self.theme_button.pack()
    
    def create_modern_footer(self, parent):
        """Create modern footer section"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=(0, 20))
        
        current_theme = self.theme_manager.get_current_theme()
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="גרסה 2.0",
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color=current_theme['text_tertiary']
        )
        version_label.pack()
        
        company_label = ctk.CTkLabel(
            footer_frame,
            text="© Panel Kitchens 2024",
            font=ctk.CTkFont(family="Assistant", size=12, weight="bold"),
            text_color=current_theme['text_tertiary']
        )
        company_label.pack()
    
    def handle_login(self):
        """Handle login attempt with modern feedback"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("שגיאה", "אנא הזן שם משתמש וסיסמה")
            return
        
        # Modern loading state
        self.login_button.configure(state="disabled", text="מתחבר... ⏳")
        
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
        self.login_button.configure(state="normal", text="כניסה למערכת")
        
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
        self.login_button.configure(state="normal", text="כניסה למערכת")
        
        messagebox.showerror("שגיאה", f"שגיאה בהתחברות: {error}")
        self.on_error(error)
    
    def toggle_theme(self):
        """Toggle between blue and red themes"""
        current_theme_name = self.theme_manager.current_color_theme
        new_theme_name = 'red' if current_theme_name == 'blue' else 'blue'
        
        # Switch theme
        self.theme_manager.set_theme(new_theme_name)
        
        # Update button text
        theme_text = "🔴 עבור לנושא אדום" if new_theme_name == 'blue' else "🔵 עבור לנושא כחול"
        self.theme_button.configure(text=theme_text)
        
        # Update window icon
        self.set_window_icon()
        
        # Recreate UI with new theme
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI with new theme colors"""
        # Clear and recreate UI
        for widget in self.window.winfo_children():
            widget.destroy()
        
        self.create_modern_widgets()
        
        # Restore focus
        self.window.after(100, self.username_entry.focus_set)
    
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