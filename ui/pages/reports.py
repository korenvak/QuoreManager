"""
Reports Page for Kitchen Quote Management System - Modern Professional Design
"""

import customtkinter as ctk
from styling.theme_system import ModernThemeManager, THEMES
from config.settings import SettingsManager

class ReportsPage:
    """Modern professional reports page with theme integration"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        # Initialize theme system
        self.settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
    def create_content(self):
        """Create modern professional reports page content"""
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
        
        # Coming soon section with professional styling
        self.create_coming_soon_section(inner_frame)
        
        # Preview cards for future features
        self.create_preview_cards(inner_frame)
    
    def create_modern_header(self, parent):
        """Create refined compact page header"""
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
        
        # Page title with professional typography
        title_label = ctk.CTkLabel(
            header_frame,
            text="דוחות ואנליטיקה",
            font=self.theme_manager.create_ctk_font('title'),  # 22px compact title
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle with refined styling
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="מידע וסטטיסטיקות על פעילות העסק",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
    
    def create_coming_soon_section(self, parent):
        """Create professional coming soon section"""
        coming_soon_card = ctk.CTkFrame(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        coming_soon_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        content_frame = ctk.CTkFrame(coming_soon_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('xl'))
        
        # Coming soon icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text="📊",
            font=ctk.CTkFont(size=48),
            text_color=self.theme['primary']
        )
        icon_label.pack(pady=(0, self.theme_manager.get_spacing('lg')))
        
        # Main message
        message_label = ctk.CTkLabel(
            content_frame,
            text="דף דוחות ואנליטיקה - בפיתוח",
            font=self.theme_manager.create_ctk_font('heading'),
            text_color=self.theme['text_primary'],
            justify="center"
        )
        message_label.pack(pady=(0, self.theme_manager.get_spacing('sm')))
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text="כאן יוצגו דוחות מכירות מפורטים, סטטיסטיקות עסקיות וגרפים אינטראקטיביים",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            justify="center"
        )
        desc_label.pack()
    
    def create_preview_cards(self, parent):
        """Create preview cards for future features"""
        # Section title
        preview_title = ctk.CTkLabel(
            parent,
            text="תכונות עתידיות",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        preview_title.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('lg')))
        
        # Cards container
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        # Configure grid
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Feature cards
        features = [
            {"title": "דוחות מכירות", "desc": "דוחות מפורטים על מכירות והכנסות", "icon": "💰"},
            {"title": "סטטיסטיקות לקוחות", "desc": "ניתוח התנהגות לקוחות ומגמות", "icon": "👥"},
            {"title": "גרפים אינטראקטיביים", "desc": "תרשימים ויזואליים מתקדמים", "icon": "📈"}
        ]
        
        for i, feature in enumerate(features):
            self.create_feature_card(cards_frame, feature, 0, i)
    
    def create_feature_card(self, parent, feature, row, col):
        """Create professional feature preview card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        card.grid(row=row, column=col, padx=self.theme_manager.get_spacing('md'), 
                 pady=self.theme_manager.get_spacing('md'), sticky="ew")
        
        # Hover effects
        def on_enter(event):
            card.configure(
                border_color=self.theme['primary'],
                fg_color=self.theme['primary_ultra_light']
            )
        
        def on_leave(event):
            card.configure(
                border_color=self.theme['border_light'],
                fg_color=self.theme['bg_card']
            )
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('lg'))
        
        # Feature icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=feature["icon"],
            font=ctk.CTkFont(size=24),
            text_color=self.theme['primary']
        )
        icon_label.pack(pady=(0, self.theme_manager.get_spacing('sm')))
        
        # Feature title
        title_label = ctk.CTkLabel(
            content_frame,
            text=feature["title"],
            font=self.theme_manager.create_ctk_font('card_title'),
            text_color=self.theme['text_primary'],
            anchor="center"
        )
        title_label.pack(pady=(0, self.theme_manager.get_spacing('xs')))
        
        # Feature description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=feature["desc"],
            font=self.theme_manager.create_ctk_font('helper'),
            text_color=self.theme['text_muted'],
            anchor="center",
            justify="center"
        )
        desc_label.pack() 