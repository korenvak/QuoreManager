"""
Modern Dashboard Window for Kitchen Quote Management System
Features: Right-side collapsible sidebar, hover animations, clean design
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Callable, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from utils.permissions import PermissionManager

class DashboardWindow:
    """Modern dashboard with right-side collapsible sidebar"""
    
    def __init__(self, current_user: Dict[str, Any], db_manager, settings_manager, on_logout: Callable, on_switch_user: Optional[Callable] = None):
        self.current_user = current_user
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.on_logout = on_logout
        self.on_switch_user = on_switch_user or on_logout  # Default to logout if not provided
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(db_manager)
        
        # Modern colors - Clean white/light-blue theme
        self.light_colors = {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#FAFBFF',
            'bg_glass': '#F8FAFC',
            'bg_sidebar': '#F1F5F9',
            'bg_sidebar_collapsed': '#FCFCFD',
            'bg_sidebar_hover': '#EBF4FF',
            'accent_primary': '#3B82F6',
            'accent_secondary': '#1E40AF',
            'accent_red': '#EF4444',
            'accent_light': '#DBEAFE',
            'text_primary': '#1F2937',
            'text_secondary': '#6B7280',
            'text_muted': '#9CA3AF',
            'border': '#E1E8F7',
            'shadow': '#F0F4F8',
        }
        
        self.dark_colors = {
            'bg_primary': '#0F172A',
            'bg_secondary': '#1E293B',
            'bg_glass': '#1A202C',
            'bg_sidebar': '#2D3748',
            'bg_sidebar_collapsed': '#1A1F2E',
            'bg_sidebar_hover': '#2A3441',
            'accent_primary': '#60A5FA',
            'accent_secondary': '#3B82F6',
            'accent_red': '#F87171',
            'accent_light': '#1E3A8A',
            'text_primary': '#F8FAFC',
            'text_secondary': '#CBD5E1',
            'text_muted': '#64748B',
            'border': '#374151',
            'shadow': '#1F2937',
        }
        
        # Get current theme colors
        current_theme = self.settings_manager.get('theme_mode', 'light')
        self.colors = self.light_colors if current_theme == 'light' else self.dark_colors
        
        # Fixed sidebar configuration
        self.sidebar_width = 280
        
        # UI components
        self.window = None
        self.sidebar = None
        self.content_area = None
        self.main_content = None
        self.current_page = None
        self.nav_buttons = {}
        
        self.setup_window()
    
    def setup_window(self):
        """Setup modern window"""
        self.window = ctk.CTk()
        self.window.title("מערכת ניהול הצעות מטבח - Panel Kitchens")
        
        # Apply theme
        current_theme = self.settings_manager.get('theme_mode', 'light')
        ctk.set_appearance_mode(current_theme)
        
        # Pure white background for light mode
        self.window.configure(fg_color=self.colors['bg_primary'])
        
        # Window geometry
        geometry = self.settings_manager.get_window_geometry()
        width = geometry['width']
        height = geometry['height']
        self.window.geometry(f"{width}x{height}")
        
        if geometry['maximized']:
            self.window.state('zoomed')
        
        # Grid layout - content left, sidebar right
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=0)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Set window icon
        self.set_window_icon()
        
        # Create components
        self.create_content_area()
        self.create_modern_sidebar()
        
        # Load initial page
        self.show_overview_page()
        
        # Window events
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.window.bind("<Configure>", self.on_window_configure)
    
    def set_window_icon(self):
        """Set window icon"""
        try:
            icon_path = Path(__file__).parent.parent / "resources" / "White_Logo.ico"
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass
    
    def create_content_area(self):
        """Create modern content area"""
        # Main content container
        self.content_area = ctk.CTkFrame(
            self.window,
            corner_radius=0,
            fg_color=self.colors['bg_primary']
        )
        self.content_area.grid(row=0, column=0, sticky="nsew")
        
        # Top bar
        self.create_top_bar()
        
        # Content container with glass effect
        self.main_content = ctk.CTkFrame(
            self.content_area,
            fg_color=self.colors['bg_glass'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        self.main_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome placeholder
        welcome_label = ctk.CTkLabel(
            self.main_content,
            text="ברוכים הבאים למערכת ניהול הצעות מטבח",
            font=ctk.CTkFont(family="Assistant", size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        welcome_label.pack(expand=True)
    
    def create_top_bar(self):
        """Create modern top bar"""
        top_bar = ctk.CTkFrame(
            self.content_area,
            height=70,
            fg_color=self.colors['bg_primary'],
            corner_radius=0
        )
        top_bar.pack(fill="x", padx=0, pady=0)
        top_bar.pack_propagate(False)
        
        # Page title
        self.page_title = ctk.CTkLabel(
            top_bar,
            text="סקירה כללית",
            font=ctk.CTkFont(family="Assistant", size=26, weight="bold"),
            text_color=self.colors['text_primary'],
            anchor="e"
        )
        self.page_title.pack(side="right", padx=30, pady=20)
        
        # Theme toggle
        current_theme = self.settings_manager.get('theme_mode', 'light')
        theme_icon = "🌙" if current_theme == "light" else "☀️"
        theme_button = ctk.CTkButton(
            top_bar,
            text=theme_icon,
            width=45,
            height=45,
            font=ctk.CTkFont(size=20),
            fg_color=self.colors['accent_primary'],
            hover_color=self.colors['accent_secondary'],
            corner_radius=25,
            command=self.toggle_theme
        )
        theme_button.pack(side="left", padx=25, pady=12)
        
        # Separator
        separator = ctk.CTkFrame(
            self.content_area,
            height=1,
            fg_color=self.colors['border']
        )
        separator.pack(fill="x", padx=30)
    
    def create_modern_sidebar(self):
        """Create right-side fixed sidebar"""
        # Sidebar frame with glass effect
        self.sidebar = ctk.CTkFrame(
            self.window,
            width=self.sidebar_width,
            corner_radius=25,
            fg_color=self.colors['bg_sidebar'],
            border_width=1,
            border_color=self.colors['border'],
        )
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(10, 15), pady=(15, 15))
        self.sidebar.grid_propagate(False)
        
        # Create sections
        self.create_logo_section()
        self.create_navigation()
        self.create_user_section()
    
    def create_logo_section(self):
        """Create logo section in sidebar"""
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(30, 20), padx=15)
        
        # Try to load actual logo, fallback to high-quality icon
        logo_element = None  # Will hold either logo_label or logo_icon
        try:
            from PIL import Image
            import os
            logo_path = os.path.join("resources", "logo.png")
            if os.path.exists(logo_path):
                # Load image and check dimensions for better quality
                pil_image = Image.open(logo_path)
                # Use larger size for better clarity, maintaining aspect ratio
                logo_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(80, 80)  # Increased from 45x45 for better quality
                )
                logo_element = ctk.CTkLabel(
                    logo_frame,
                    image=logo_image,
                    text=""
                )
                logo_element.pack(pady=15)
            else:
                raise FileNotFoundError("Logo not found")
        except:
            # Fallback to professional icon with better styling
            logo_element = ctk.CTkLabel(
                logo_frame,
                text="🏢",  # Changed from home to office building for more professional look
                font=ctk.CTkFont(size=40),  # Increased size
                text_color=self.colors['accent_primary']
            )
            logo_element.pack(pady=15)
        
        # Company name with modern styling
        self.company_name = ctk.CTkLabel(
            logo_frame,
            text="Panel Kitchens",
            font=ctk.CTkFont(family="Assistant", size=20, weight="bold"),
            text_color=self.colors['accent_primary']  # Use accent color for branding
        )
        self.company_name.pack(pady=(5, 10))  # Better spacing
    
    def create_navigation(self):
        """Create navigation menu with permission-based visibility"""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=15, pady=20)
        
        # Get accessible pages for current user
        accessible_pages = self.permission_manager.get_accessible_pages(self.current_user)
        
        # Navigation items with icons and permission checks
        nav_items = [
            ("overview", "📊 סקירה כללית", "#3B82F6"),
            ("quotes", "📋 הצעות מחיר", "#10B981") if "quotes" in accessible_pages else None,
            ("drafts", "📝 טיוטות", "#F59E0B") if "drafts" in accessible_pages else None,
            ("customers", "👥 לקוחות", "#8B5CF6") if "customers" in accessible_pages else None,
            ("catalog", "📚 קטלוג", "#06B6D4") if "catalog" in accessible_pages else None,
            ("users", "👤 משתמשים", "#EF4444") if "users" in accessible_pages else None,
            ("settings", "⚙️ הגדרות", "#6B7280") if "settings" in accessible_pages else None,
        ]
        
        # Filter out None items (pages user can't access)
        nav_items = [item for item in nav_items if item is not None]
        
        # Create navigation buttons
        for page_id, text, color in nav_items:
            nav_button = ctk.CTkButton(
                nav_frame,
                text=text,
                font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
                height=50,
                fg_color="transparent",
                text_color=color,
                hover_color=self.colors['bg_sidebar_hover'],
                corner_radius=12,
                anchor="e",
                command=lambda p=page_id: self.navigate_to_page(p)
            )
            nav_button.pack(fill="x", pady=3)
            
            # Store button reference for highlighting
            self.nav_buttons[text] = {
                'button': nav_button,
                'color': color
            }
        
        # Show message if no pages accessible
        if len(nav_items) <= 1:  # Only overview
            no_access_label = ctk.CTkLabel(
                nav_frame,
                text="אין לך הרשאות לגשת לדפים נוספים",
                font=ctk.CTkFont(family="Assistant", size=12),
                text_color="#6B7280",
                justify="center"
            )
            no_access_label.pack(pady=20)
    
    def create_user_section(self):
        """Create user section"""
        user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors['accent_primary'],
            corner_radius=20
        )
        user_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        # User icon
        user_icon = ctk.CTkLabel(
            user_frame,
            text="👤",
            font=ctk.CTkFont(size=28),
            text_color="white"
        )
        user_icon.pack(pady=(15, 10))
        
        # User details (always visible)
        full_name = f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}".strip()
        if not full_name:
            full_name = self.current_user.get('username', 'משתמש')
        
        self.user_name = ctk.CTkLabel(
            user_frame,
            text=full_name,
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color="white"
        )
        self.user_name.pack(pady=(0, 3))
        
        # Role
        role_text = {
            'admin': 'מנהל מערכת',
            'manager': 'מנהל',
            'employee': 'עובד',
            'viewer': 'צופה'
        }.get(self.current_user.get('role', 'viewer'), 'משתמש')
        
        self.user_role = ctk.CTkLabel(
            user_frame,
            text=role_text,
            font=ctk.CTkFont(family="Assistant", size=13),
            text_color="#E0E7FF"
        )
        self.user_role.pack(pady=(0, 8))
        
        # Logout button
        self.logout_btn = ctk.CTkButton(
            user_frame,
            text="יציאה",
            font=ctk.CTkFont(family="Assistant", size=13, weight="bold"),
            height=35,
            fg_color="white",
            hover_color="#DC2626",
            text_color=self.colors['accent_primary'],
            corner_radius=10,
            command=self.handle_logout
        )
        self.logout_btn.pack(fill="x", padx=12, pady=(0, 12))
        
        # Switch user button
        self.switch_user_btn = ctk.CTkButton(
            user_frame,
            text="החלף משתמש",
            font=ctk.CTkFont(family="Assistant", size=13, weight="bold"),
            height=35,
            fg_color="#F59E0B",
            hover_color="#D97706",
            text_color="white",
            corner_radius=10,
            command=self.handle_switch_user
        )
        self.switch_user_btn.pack(fill="x", padx=12, pady=(0, 12))
    
    def clear_content_area(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def highlight_nav_button(self, button_text: str):
        """Highlight active navigation with modern effects"""
        # Reset all buttons
        for text, nav_data in self.nav_buttons.items():
            nav_data['button'].configure(
                fg_color="transparent",
                text_color=nav_data['color']
            )
        
        # Highlight active
        if button_text in self.nav_buttons:
            nav_data = self.nav_buttons[button_text]
            nav_data['button'].configure(
                fg_color=nav_data['color'],
                text_color="white"
            )
        
        # Update page title
        self.page_title.configure(text=button_text)
    
    def toggle_theme(self):
        """Toggle theme with restart message"""
        current = self.settings_manager.get('theme_mode', 'light')
        new_theme = 'dark' if current == 'light' else 'light'
        
        self.settings_manager.set('theme_mode', new_theme)
        
        messagebox.showinfo(
            "ערכת נושא", 
            "ערכת הנושא שונתה!\nאנא הפעל מחדש את התוכנה כדי לראות את השינויים."
        )
    
    def navigate_to_page(self, page_id: str):
        """Navigate to a specific page based on page ID"""
        if page_id == "overview":
            self.show_overview_page()
        elif page_id == "quotes":
            self.show_quotes_page()
        elif page_id == "drafts":
            self.show_drafts_page()
        elif page_id == "customers":
            self.show_customers_page()
        elif page_id == "catalog":
            self.show_catalog_page()
        elif page_id == "users":
            self.show_users_page()
        elif page_id == "settings":
            self.show_settings_page()
    
    def show_overview_page(self):
        self.clear_content_area()
        self.highlight_nav_button("סקירה כללית")
        self.current_page = "overview"
        
        from ui.pages.overview import OverviewPage
        overview_page = OverviewPage(self.main_content, self.db_manager, self.current_user)
        overview_page.create_content()
    
    def show_quotes_page(self):
        self.clear_content_area()
        self.highlight_nav_button("הצעות מחיר")
        self.current_page = "quotes"
        
        from ui.pages.quotes import QuotesPage
        quotes_page = QuotesPage(self.main_content, self.db_manager, self.current_user)
        quotes_page.create_content()
    
    def show_drafts_page(self):
        self.clear_content_area()
        self.highlight_nav_button("טיוטות")
        self.current_page = "drafts"
        
        from ui.pages.drafts import DraftsPage
        drafts_page = DraftsPage(self.main_content, self.db_manager, self.current_user)
        drafts_page.create_content()
    
    def show_customers_page(self):
        self.clear_content_area()
        self.highlight_nav_button("לקוחות")
        self.current_page = "customers"
        
        from ui.pages.customers import CustomersPage
        customers_page = CustomersPage(self.main_content, self.db_manager, self.current_user)
        customers_page.create_content()
    
    def show_reports_page(self):
        self.clear_content_area()
        self.highlight_nav_button("דוחות")
        self.current_page = "reports"
        
        from ui.pages.reports import ReportsPage
        reports_page = ReportsPage(self.main_content, self.db_manager, self.current_user)
        reports_page.create_content()
    
    def show_catalog_page(self):
        if not self.has_permission('manage_catalog'):
            messagebox.showwarning("אין הרשאה", "אין לך הרשאה לגשת לדף זה")
            return
        
        self.clear_content_area()
        self.highlight_nav_button("קטלוג")
        self.current_page = "catalog"
        
        from ui.pages.catalog import CatalogPage
        catalog_page = CatalogPage(self.main_content, self.db_manager, self.current_user)
        catalog_page.create_content()
    
    def show_users_page(self):
        if not self.has_permission('manage_users'):
            messagebox.showwarning("אין הרשאה", "אין לך הרשאה לגשת לדף זה")
            return
        
        self.clear_content_area()
        self.highlight_nav_button("משתמשים")
        self.current_page = "users"
        
        from ui.pages.users import UsersPage
        users_page = UsersPage(self.main_content, self.db_manager, self.current_user)
        users_page.create_content()
    
    def show_settings_page(self):
        self.clear_content_area()
        self.highlight_nav_button("הגדרות")
        self.current_page = "settings"
        
        from ui.pages.settings import SettingsPage
        settings_page = SettingsPage(
            self.main_content, 
            self.db_manager, 
            self.settings_manager, 
            self.current_user
        )
        settings_page.create_content()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission using PermissionManager"""
        return self.permission_manager.check_user_permission(self.current_user, permission)
    
    def handle_logout(self):
        if messagebox.askyesno("יציאה", "האם אתה בטוח שברצונך לצאת?"):
            self.save_window_state()
            self.window.destroy()
            self.on_logout()
    
    def handle_switch_user(self):
        """Handle switch user request"""
        if messagebox.askyesno("החלף משתמש", "האם אתה בטוח שברצונך להחליף משתמש?\nהפעולה הנוכחית תאבד."):
            self.save_window_state()
            self.window.destroy()
            self.on_switch_user()  # This will take the user back to login screen
    
    def on_window_close(self):
        self.save_window_state()
        try:
            self.window.destroy()
        except Exception:
            pass
    
    def on_window_configure(self, event):
        if event.widget == self.window:
            self.window.after_idle(self.save_window_state)
    
    def save_window_state(self):
        try:
            is_maximized = self.window.state() == 'zoomed'
            
            if not is_maximized:
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                self.settings_manager.set_window_geometry(width, height, is_maximized)
            else:
                self.settings_manager.set_window_geometry(1400, 900, is_maximized)
        except Exception:
            pass
    
    def show(self):
        if self.window:
            self.window.mainloop() 