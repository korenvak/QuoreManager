"""
Modern Dashboard Window for Kitchen Quote Management System V2.0
Features: Left-side professional sidebar, modern theme system, clean design
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Callable, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from utils.permissions import PermissionManager
from styling.theme_system import ModernThemeManager

class DashboardWindow:
    """Modern dashboard with left-side professional sidebar"""
    
    def __init__(self, current_user: Dict[str, Any], db_manager, settings_manager, on_logout: Callable, on_switch_user: Optional[Callable] = None):
        self.current_user = current_user
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.on_logout = on_logout
        self.on_switch_user = on_switch_user or on_logout
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(db_manager)
        
        # Initialize modern theme system
        self.theme_manager = ModernThemeManager(settings_manager)
        self.theme_manager.apply_theme()
        
        # Get current theme configuration
        self.theme = self.theme_manager.get_current_theme()
        
        # Sidebar configuration (240px as per specifications)
        self.sidebar_width = self.theme_manager.get_component_config('sidebar')['width']
        
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
        
        # Apply modern theme
        self.window.configure(fg_color=self.theme['bg_primary'])
        
        # Window geometry
        geometry = self.settings_manager.get_window_geometry()
        width = geometry['width']
        height = geometry['height']
        self.window.geometry(f"{width}x{height}")
        
        if geometry['maximized']:
            self.window.state('zoomed')
        
        # Grid layout - content left, sidebar right  
        self.window.grid_columnconfigure(0, weight=1)  # Content (flexible)
        self.window.grid_columnconfigure(1, weight=0)  # Sidebar (fixed width)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Set window icon
        self.set_window_icon()
        
        # Create components - content first (left), then sidebar (right)
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
        """Create modern content area with professional gradient design"""
        # Main content container with gradient background
        self.content_area = ctk.CTkFrame(
            self.window,
            corner_radius=20,  # Rounded corners like sidebar
            fg_color=self.theme['bg_secondary'],  # Light gradient base
            border_width=0
        )
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=(15, 0), pady=15)  # Add padding for rounded effect
        
        # Top bar
        self.create_top_bar()
        
        # Content container with modern card design and beautiful styling
        self.main_content = ctk.CTkFrame(
            self.content_area,
            corner_radius=20,  # Large rounded corners for modern look
            fg_color=self.theme['bg_card'],
            border_width=1,
            border_color=self.theme['border_light']
        )
        self.main_content.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('xl'), pady=(0, self.theme_manager.get_spacing('xl')))
        
        # Welcome placeholder with better styling
        welcome_label = ctk.CTkLabel(
            self.main_content,
            text="ברוכים הבאים למערכת ניהול הצעות מטבח",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary']
        )
        welcome_label.pack(expand=True, pady=self.theme_manager.get_spacing('xxxl'))
    
    def create_top_bar(self):
        """Create modern professional top bar with gradient design"""
        top_bar = ctk.CTkFrame(
            self.content_area,
            height=90,  # Increased height for better proportions
            fg_color="transparent",  # Transparent to blend with content area
            corner_radius=0
        )
        top_bar.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('xl'))
        top_bar.pack_propagate(False)
        
        # Page title with professional styling
        self.page_title = ctk.CTkLabel(
            top_bar,
            text="סקירה כללית",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        self.page_title.pack(side="right", padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('xl'))
        
        # Color theme toggle buttons with modern styling
        button_frame = ctk.CTkFrame(
            top_bar, 
            fg_color=self.theme['bg_card'],  # Card background for elevation effect
            corner_radius=16,  # Rounded container
            border_width=1,
            border_color=self.theme['border_light']
        )
        button_frame.pack(side="left", padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('lg'))
        
        # Blue theme button with modern design
        blue_button = ctk.CTkButton(
            button_frame,
            text="🔵",
            width=45,
            height=45,
            font=ctk.CTkFont(size=18),
            fg_color=self.theme['primary'] if self.theme_manager.current_color_theme == 'blue' else "transparent",
            hover_color=self.theme['primary_light'],
            corner_radius=12,  # Rounded like navigation items
            border_width=2 if self.theme_manager.current_color_theme == 'blue' else 0,
            border_color=self.theme['primary_dark'] if self.theme_manager.current_color_theme == 'blue' else self.theme['border_light'],
            command=lambda: self.switch_color_theme('blue')
        )
        blue_button.pack(side="left", padx=(self.theme_manager.get_spacing('md'), self.theme_manager.get_spacing('sm')), pady=self.theme_manager.get_spacing('md'))
        
        # Red theme button with modern design
        red_button = ctk.CTkButton(
            button_frame,
            text="🔴",
            width=45,
            height=45,
            font=ctk.CTkFont(size=18),
            fg_color="#EF4444" if self.theme_manager.current_color_theme == 'red' else "transparent",
            hover_color="#FCA5A5",
            corner_radius=12,  # Rounded like navigation items
            border_width=2 if self.theme_manager.current_color_theme == 'red' else 0,
            border_color="#DC2626" if self.theme_manager.current_color_theme == 'red' else self.theme['border_light'],
            command=lambda: self.switch_color_theme('red')
        )
        red_button.pack(side="left", padx=(0, self.theme_manager.get_spacing('md')), pady=self.theme_manager.get_spacing('md'))
        
        # Modern separator with subtle styling
        separator = ctk.CTkFrame(
            self.content_area,
            height=2,  # Slightly thicker for better visibility
            fg_color=self.theme['border_light'],
            corner_radius=1
        )
        separator.pack(fill="x", padx=self.theme_manager.get_spacing('xxxl'), pady=(0, self.theme_manager.get_spacing('lg')))
    
    def create_modern_sidebar(self):
        """Create right-side professional sidebar with gradient and rounded corners"""
        # Professional sidebar with stronger gradient effect and rounded corners
        self.sidebar = ctk.CTkFrame(
            self.window,
            width=self.sidebar_width,
            corner_radius=20,  # Rounded corners like in the image
            fg_color=self.theme['sidebar_bg_solid'],  # Keep original base color, stronger gradient is for visual effect
            border_width=0
        )
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)  # Add padding for rounded effect
        self.sidebar.grid_propagate(False)
        
        # Create sections
        self.create_logo_section()
        self.create_navigation()
        self.create_user_section()
    
    def create_logo_section(self):
        """Create professional logo section in sidebar"""
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(32, 24), padx=self.theme_manager.get_spacing('lg'))
        
        # Load theme-appropriate .ico logo
        try:
            from PIL import Image
            import os
            
            # Use the theme-appropriate icon file
            icon_filename = self.theme_manager.get_current_theme()['icon_file']
            logo_path = os.path.join("resources", icon_filename)
            
            if os.path.exists(logo_path):
                pil_image = Image.open(logo_path)
                logo_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(48, 48)  # Slightly smaller for .ico files
                )
                logo_element = ctk.CTkLabel(
                    logo_frame,
                    image=logo_image,
                    text=""
                )
                logo_element.pack(pady=(0, 12))
            else:
                raise FileNotFoundError("Logo not found")
        except:
            # Professional fallback icon
            logo_element = ctk.CTkLabel(
                logo_frame,
                text="🏢", 
                font=self.theme_manager.create_ctk_font('card_title'),
                text_color=self.theme['sidebar_text']
            )
            logo_element.pack(pady=(0, 12))
        
        # Company name with professional styling
        self.company_name = ctk.CTkLabel(
            logo_frame,
            text="Panel Kitchens",
            font=self.theme_manager.create_ctk_font('heading'),
            text_color=self.theme['sidebar_text']
        )
        self.company_name.pack()
    
    def create_navigation(self):
        """Create professional navigation menu"""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('xl'))
        
        # Get accessible pages for current user
        accessible_pages = self.permission_manager.get_accessible_pages(self.current_user)
        
        # Professional navigation items (clean text, no emojis)
        nav_items = [
            ("overview", "סקירה כללית"),
            ("quotes", "הצעות מחיר") if "quotes" in accessible_pages else None,
            ("drafts", "טיוטות") if "drafts" in accessible_pages else None,
            ("customers", "לקוחות") if "customers" in accessible_pages else None,
            ("catalog", "קטלוג") if "catalog" in accessible_pages else None,
            ("users", "משתמשים") if "users" in accessible_pages else None,
            ("settings", "הגדרות") if "settings" in accessible_pages else None,
        ]
        
        # Filter out None items (pages user can't access)
        nav_items = [item for item in nav_items if item is not None]
        
        # Create professional navigation buttons
        sidebar_config = self.theme_manager.get_component_config('sidebar')
        
        for page_id, text in nav_items:
            nav_button = ctk.CTkButton(
                nav_frame,
                text=text,
                font=self.theme_manager.create_ctk_font('nav_item'),
                height=sidebar_config['item_height'],
                fg_color="transparent",
                text_color=self.theme['sidebar_text'],
                hover_color=self.theme['sidebar_hover_gradient'],  # Beautiful gradient hover effect
                corner_radius=12,  # Rounded corners like in the image
                anchor="e",  # Right align for RTL
                command=lambda p=page_id: self.navigate_to_page(p)
            )
            nav_button.pack(fill="x", pady=2)
            
            # Store button reference for highlighting
            self.nav_buttons[text] = nav_button
        
        # Show message if no pages accessible
        if len(nav_items) <= 1:  # Only overview
            no_access_label = ctk.CTkLabel(
                nav_frame,
                text="אין לך הרשאות לגשת לדפים נוספים",
                font=self.theme_manager.create_ctk_font('helper'),
                text_color=self.theme['sidebar_text'],
                justify="center"
            )
            no_access_label.pack(pady=self.theme_manager.get_spacing('xl'))
    
    def create_user_section(self):
        """Create professional user section at bottom of sidebar"""
        user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",  # Transparent background to blend with sidebar
            corner_radius=12
        )
        user_frame.pack(side="bottom", fill="x", padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('xl'))
        
        # User icon with light color for visibility on sidebar
        user_icon = ctk.CTkLabel(
            user_frame,
            text="👤",
            font=self.theme_manager.create_ctk_font('heading'),
            text_color=self.theme['sidebar_text']  # Light color for visibility
        )
        user_icon.pack(pady=(self.theme_manager.get_spacing('lg'), self.theme_manager.get_spacing('md')))
        
        # User details
        full_name = f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}".strip()
        if not full_name:
            full_name = self.current_user.get('username', 'משתמש')
        
        self.user_name = ctk.CTkLabel(
            user_frame,
            text=full_name,
            font=self.theme_manager.create_ctk_font('card_title'),
            text_color=self.theme['sidebar_text']  # Light color for visibility
        )
        self.user_name.pack(pady=(0, self.theme_manager.get_spacing('xs')))
        
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
            font=self.theme_manager.create_ctk_font('helper'),
            text_color=self.theme['sidebar_text']  # Light color for visibility
        )
        self.user_role.pack(pady=(0, self.theme_manager.get_spacing('lg')))
        
        # Action buttons
        button_config = self.theme_manager.get_component_config('button')
        
        # Logout button - using primary theme color
        self.logout_btn = ctk.CTkButton(
            user_frame,
            text="יציאה",
            font=self.theme_manager.create_ctk_font('helper'),
            height=button_config['height'] - 8,  # Slightly smaller
            fg_color=self.theme['primary_dark'],  # Use dark theme color
            hover_color=self.theme['primary'],    # Use primary theme color
            text_color="white",
            corner_radius=button_config['corner_radius'],
            command=self.handle_logout
        )
        self.logout_btn.pack(fill="x", padx=self.theme_manager.get_spacing('md'), pady=(0, self.theme_manager.get_spacing('sm')))
        
        # Switch user button - using lighter theme color
        self.switch_user_btn = ctk.CTkButton(
            user_frame,
            text="החלף משתמש",
            font=self.theme_manager.create_ctk_font('helper'),
            height=button_config['height'] - 8,  # Slightly smaller
            fg_color=self.theme['primary_light'],  # Use light theme color
            hover_color=self.theme['primary'],     # Use primary theme color
            text_color=self.theme['primary_dark'], # Dark text on light background
            corner_radius=button_config['corner_radius'],
            command=self.handle_switch_user
        )
        self.switch_user_btn.pack(fill="x", padx=self.theme_manager.get_spacing('md'), pady=(0, self.theme_manager.get_spacing('md')))
    
    def clear_content_area(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def highlight_nav_button(self, button_text: str):
        """Highlight active navigation with modern professional effects"""
        # Reset all buttons to default state
        for text, nav_button in self.nav_buttons.items():
            nav_button.configure(
                fg_color="transparent",
                text_color=self.theme['sidebar_text']
            )
        
        # Highlight active button with white background
        if button_text in self.nav_buttons:
            self.nav_buttons[button_text].configure(
                fg_color=self.theme['sidebar_active'],
                text_color=self.theme['sidebar_text_active']
            )
        
        # Update page title if it exists
        if hasattr(self, 'page_title'):
            self.page_title.configure(text=button_text)
    
    def switch_color_theme(self, new_theme):
        """Switch between blue and red color themes"""
        if self.theme_manager.switch_color_theme(new_theme):
            messagebox.showinfo(
                "ערכת צבעים", 
                f"ערכת הצבעים שונתה ל{new_theme}!\nאנא הפעל מחדש את התוכנה כדי לראות את השינויים."
            )
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        new_mode = self.theme_manager.toggle_mode()
        messagebox.showinfo(
            "מצב תצוגה", 
            f"מצב התצוגה שונה ל{new_mode}!\nאנא הפעל מחדש את התוכנה כדי לראות את השינויים."
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