"""
Settings Page for Kitchen Quote Management System
"""

import customtkinter as ctk
from tkinter import messagebox

class SettingsPage:
    """Settings page"""
    
    def __init__(self, parent, db_manager, settings_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        self.current_user = current_user
        
    def create_content(self):
        """Create settings page content"""
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
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text="הגדרות מערכת",
            font=ctk.CTkFont(family="Assistant", size=32, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 30))
        
        # Company settings
        self.create_company_settings(content_frame)
        
        # Business settings
        self.create_business_settings(content_frame)
        
        # Theme settings
        self.create_theme_settings(content_frame)
        
        # Save button
        save_button = ctk.CTkButton(
            content_frame,
            text="שמור הגדרות",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            height=50,
            fg_color="#3B82F6",
            hover_color="#1E40AF",
            corner_radius=12,
            command=self.save_settings
        )
        save_button.pack(pady=30)
    
    def create_company_settings(self, parent):
        """Create company settings section"""
        company_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        company_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            company_frame,
            text="פרטי החברה",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            anchor="e"
        )
        title.pack(anchor="e", padx=20, pady=(20, 10))
        
        company_info = self.settings_manager.get_company_info()
        
        # Company name
        self.create_setting_field(company_frame, "שם החברה:", "company_name", 
                                 company_info.get('name', ''))
        
        # Phone
        self.create_setting_field(company_frame, "טלפון:", "company_phone",
                                 company_info.get('phone', ''))
        
        # Email
        self.create_setting_field(company_frame, "דואל:", "company_email",
                                 company_info.get('email', ''))
        
        # Address
        self.create_setting_field(company_frame, "כתובת:", "company_address",
                                 company_info.get('address', ''))
    
    def create_business_settings(self, parent):
        """Create business settings section"""
        business_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        business_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            business_frame,
            text="הגדרות עסקיות",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            anchor="e"
        )
        title.pack(anchor="e", padx=20, pady=(20, 10))
        
        business_settings = self.settings_manager.get_business_settings()
        
        # VAT rate
        self.create_setting_field(business_frame, "אחוז מע\"מ:", "vat_rate",
                                 str(business_settings.get('vat_rate', 17.0)))
        
        # Quote validity
        self.create_setting_field(business_frame, "תוקף הצעת מחיר (ימים):", "quote_validity",
                                 str(business_settings.get('quote_validity_days', 14)))
    
    def create_theme_settings(self, parent):
        """Create theme settings section"""
        theme_frame = ctk.CTkFrame(parent, fg_color="#FFFFFF", border_width=1, border_color="#E1E8F7")
        theme_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            theme_frame,
            text="הגדרות תצוגה",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            anchor="e"
        )
        title.pack(anchor="e", padx=20, pady=(20, 10))
        
        # Theme toggle
        current_theme = self.settings_manager.get('theme_mode', 'light')
        theme_text = "כהה" if current_theme == 'light' else "בהיר"
        
        theme_button = ctk.CTkButton(
            theme_frame,
            text=f"מצב נוכחי: {theme_text} - לחץ להחלפה",
            font=ctk.CTkFont(family="Heebo", size=14),
            command=self.toggle_theme
        )
        theme_button.pack(pady=20, padx=20)
    
    def create_setting_field(self, parent, label_text, field_name, value):
        """Create settings field"""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        label.pack(anchor="e", pady=(10, 5), padx=20)
        
        entry = ctk.CTkEntry(
            parent,
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40,
            justify="right"
        )
        entry.insert(0, value)
        entry.pack(fill="x", padx=20, pady=(0, 10))
        setattr(self, field_name, entry)
    
    def toggle_theme(self):
        """Toggle theme"""
        current_theme = self.settings_manager.get('theme_mode', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        self.settings_manager.set('theme_mode', new_theme)
        ctk.set_appearance_mode(new_theme)
        
        messagebox.showinfo("ערכת נושא", f"ערכת הנושא שונתה ל{new_theme}")
    
    def save_settings(self):
        """Save all settings"""
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
            
            messagebox.showinfo("הצלחה", "ההגדרות נשמרו בהצלחה")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת ההגדרות: {str(e)}") 