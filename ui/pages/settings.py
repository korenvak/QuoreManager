"""
Settings Page for Kitchen Quote Management System - Modern Professional Design
"""

import customtkinter as ctk
from tkinter import messagebox
from styling.theme_system import ModernThemeManager, THEMES

class SettingsPage:
    """Modern professional settings page with theme integration"""
    
    def __init__(self, parent, db_manager, settings_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.current_user = current_user
        
        # Initialize theme system
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
    def create_content(self):
        """Create modern professional settings page content"""
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
        
        # Settings sections
        self.create_company_settings(inner_frame)
        self.create_business_settings(inner_frame) 
        self.create_theme_settings(inner_frame)
        
        # Save button with modern styling
        self.create_save_button(inner_frame)
    
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
        
        # Page title
        title_label = ctk.CTkLabel(
            header_frame,
            text="הגדרות מערכת",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="נהל את הגדרות החברה, העסק והתצוגה",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
    
    def create_company_settings(self, parent):
        """Create modern company settings section"""
        company_card = ctk.CTkFrame(
            parent, 
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        company_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        # Section header
        self.create_section_header(company_card, "פרטי החברה", "🏢")
        
        # Form container
        form_frame = ctk.CTkFrame(company_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=(0, self.theme_manager.get_spacing('xl')))
        
        company_info = self.settings_manager.get_company_info()
        
        # Company fields
        self.create_modern_field(form_frame, "שם החברה:", "company_name", company_info.get('name', ''))
        self.create_modern_field(form_frame, "טלפון:", "company_phone", company_info.get('phone', ''))
        self.create_modern_field(form_frame, "דואל:", "company_email", company_info.get('email', ''))
        self.create_modern_field(form_frame, "כתובת:", "company_address", company_info.get('address', ''))
    
    def create_business_settings(self, parent):
        """Create modern business settings section"""
        business_card = ctk.CTkFrame(
            parent, 
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        business_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        # Section header
        self.create_section_header(business_card, "הגדרות עסקיות", "💼")
        
        # Form container
        form_frame = ctk.CTkFrame(business_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=(0, self.theme_manager.get_spacing('xl')))
        
        business_settings = self.settings_manager.get_business_settings()
        
        # Business fields
        self.create_modern_field(form_frame, "אחוז מע\"מ:", "vat_rate", str(business_settings.get('vat_rate', 17.0)))
        self.create_modern_field(form_frame, "תוקף הצעת מחיר (ימים):", "quote_validity", str(business_settings.get('quote_validity_days', 14)))
    
    def create_theme_settings(self, parent):
        """Create modern theme settings section"""
        theme_card = ctk.CTkFrame(
            parent, 
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        theme_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        # Section header
        self.create_section_header(theme_card, "הגדרות תצוגה", "🎨")
        
        # Theme controls container
        controls_frame = ctk.CTkFrame(theme_card, fg_color="transparent")
        controls_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=(0, self.theme_manager.get_spacing('xl')))
        
        # Color theme section
        color_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=(0, self.theme_manager.get_spacing('lg')))
        
        color_label = ctk.CTkLabel(
            color_frame,
            text="ערכת צבעים:",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        color_label.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('sm')))
        
        # Color theme buttons
        color_buttons_frame = ctk.CTkFrame(color_frame, fg_color="transparent")
        color_buttons_frame.pack(fill="x")
        
        current_color_theme = self.theme_manager.current_color_theme
        
        blue_button = ctk.CTkButton(
            color_buttons_frame,
            text="🔵 כחול",
            font=self.theme_manager.create_ctk_font('body'),
            height=40,
            fg_color=self.theme['primary'] if current_color_theme == 'blue' else self.theme['bg_secondary'],
            hover_color=self.theme['primary_light'],
            text_color="white" if current_color_theme == 'blue' else self.theme['text_primary'],
            corner_radius=8,
            command=lambda: self.switch_color_theme('blue')
        )
        blue_button.pack(side="right", padx=(self.theme_manager.get_spacing('sm'), 0))
        
        red_button = ctk.CTkButton(
            color_buttons_frame,
            text="🔴 אדום",
            font=self.theme_manager.create_ctk_font('body'),
            height=40,
            fg_color="#EF4444" if current_color_theme == 'red' else self.theme['bg_secondary'],
            hover_color="#F87171",
            text_color="white" if current_color_theme == 'red' else self.theme['text_primary'],
            corner_radius=8,
            command=lambda: self.switch_color_theme('red')
        )
        red_button.pack(side="right", padx=(self.theme_manager.get_spacing('sm'), 0))
    
    def create_section_header(self, parent, title, icon):
        """Create professional section header"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=(self.theme_manager.get_spacing('xl'), self.theme_manager.get_spacing('lg')))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon}  {title}",
            font=self.theme_manager.create_ctk_font('heading'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
    
    def create_modern_field(self, parent, label_text, field_name, value):
        """Create modern form field"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=(0, self.theme_manager.get_spacing('md')))
        
        # Label
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        label.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('xs')))
        
        # Entry field
        entry = ctk.CTkEntry(
            field_frame,
            font=self.theme_manager.create_ctk_font('body'),
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=self.theme['border_light'],
            fg_color=self.theme['bg_card'],
            text_color=self.theme['text_primary'],
            justify="right"
        )
        entry.insert(0, value)
        entry.pack(fill="x")
        
        setattr(self, field_name, entry)
    
    def create_save_button(self, parent):
        """Create modern save button"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=self.theme_manager.get_spacing('xl'))
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾  שמור הגדרות",
            font=self.theme_manager.create_ctk_font('card_title'),
            height=50,
            fg_color=self.theme['primary'],
            hover_color=self.theme['primary_dark'],
            text_color="white",
            corner_radius=12,
            command=self.save_settings
        )
        save_button.pack()
    
    def switch_color_theme(self, new_theme):
        """Switch color theme"""
        if self.theme_manager.switch_color_theme(new_theme):
            messagebox.showinfo(
                "ערכת צבעים", 
                f"ערכת הצבעים שונתה ל{new_theme}!\nאנא הפעל מחדש את התוכנה כדי לראות את השינויים."
            )
    
    def save_settings(self):
        """Save all settings with modern feedback"""
        try:
            # Save company info
            company_info = {
                'name': self.company_name.get(),
                'phone': self.company_phone.get(),
                'email': self.company_email.get(),
                'address': self.company_address.get()
            }
            self.settings_manager.set_company_info(company_info)
            
            # Save business settings
            self.settings_manager.set('vat_rate', float(self.vat_rate.get()))
            self.settings_manager.set('quote_validity_days', int(self.quote_validity.get()))
            
            messagebox.showinfo("הצלחה", "ההגדרות נשמרו בהצלחה ✅")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת ההגדרות: {str(e)}") 