"""
Reports Page for Kitchen Quote Management System
"""

import customtkinter as ctk

class ReportsPage:
    """Reports page"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
    def create_content(self):
        """Create reports page content"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="דוחות ואנליטיקה",
            font=ctk.CTkFont(family="Heebo", size=28, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 20))
        
        content_label = ctk.CTkLabel(
            main_frame,
            text="דף דוחות ואנליטיקה - בפיתוח\nכאן יוצגו דוחות מכירות, סטטיסטיקות וגרפים",
            font=ctk.CTkFont(family="Heebo", size=16),
            justify="center"
        )
        content_label.pack(expand=True) 