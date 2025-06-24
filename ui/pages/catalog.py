"""
Catalog Management Page for Kitchen Quote Management System
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from typing import Optional, List
from utils.excel_handler import CatalogHandler

class CatalogPage:
    """Catalog management page"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.catalog_handler = CatalogHandler()
        self.catalog_items = []
        self.catalog_container: Optional[ctk.CTkScrollableFrame] = None
        self.stats_label: Optional[ctk.CTkLabel] = None
        
    def create_content(self):
        """Create catalog page content"""
        # Main container with clean white background
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner container with padding
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        self.create_header(content_frame)
        
        # Content area
        self.create_content_area(content_frame)
        
        # Load existing catalog
        self.load_catalog()
    
    def create_header(self, parent):
        """Create header with title and actions"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ניהול קטלוג",
            font=ctk.CTkFont(family="Assistant", size=32, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Actions bar
        actions_frame = ctk.CTkFrame(
            header_frame,
            fg_color="#FAFBFF",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        actions_frame.pack(fill="x", pady=(0, 10))
        
        # Import button
        import_button = ctk.CTkButton(
            actions_frame,
            text="טען קטלוג חדש",
            font=ctk.CTkFont(family="Assistant", size=15, weight="bold"),
            height=40,
            fg_color="#3B82F6",
            hover_color="#1E40AF",
            corner_radius=12,
            command=self.import_catalog
        )
        import_button.pack(side="right", padx=20, pady=15)
        
        # Template button
        template_button = ctk.CTkButton(
            actions_frame,
            text="הורד תבנית",
            font=ctk.CTkFont(family="Assistant", size=15, weight="bold"),
            height=40,
            fg_color="#6B7280",
            hover_color="#4B5563",
            corner_radius=12,
            command=self.download_template
        )
        template_button.pack(side="right", padx=(0, 10), pady=15)
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            actions_frame,
            text="רענן",
            font=ctk.CTkFont(family="Assistant", size=15, weight="bold"),
            height=40,
            fg_color="#6B7280",
            hover_color="#4B5563",
            corner_radius=12,
            command=self.load_catalog
        )
        refresh_button.pack(side="right", padx=(0, 10), pady=15)
        
        # Statistics
        self.stats_label = ctk.CTkLabel(
            actions_frame,
            text="טוען נתונים...",
            font=ctk.CTkFont(family="Assistant", size=14),
            text_color="#6B7280"
        )
        self.stats_label.pack(side="left", padx=20, pady=15)
    
    def create_content_area(self, parent):
        """Create scrollable content area for catalog items"""
        self.catalog_container = ctk.CTkScrollableFrame(
            parent,
            fg_color="#FAFBFF",
            corner_radius=20,
            border_width=1,
            border_color="#E1E8F7"
        )
        self.catalog_container.pack(fill="both", expand=True)
        
        # Loading placeholder
        loading_label = ctk.CTkLabel(
            self.catalog_container,
            text="טוען קטלוג...",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray"
        )
        loading_label.pack(expand=True, pady=50)
    
    def load_catalog(self):
        """Load catalog from Excel handler"""
        def load_data():
            try:
                # Get catalog items from the handler
                items = self.catalog_handler.get_catalog_items()
                self.parent.after(0, self.display_catalog, items)
            except Exception as e:
                self.parent.after(0, self.show_error, str(e))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def display_catalog(self, items):
        """Display catalog items"""
        self.catalog_items = items
        
        # Clear container
        if self.catalog_container:
            for widget in self.catalog_container.winfo_children():
                widget.destroy()
        
        if not items:
            # Empty state
            empty_frame = ctk.CTkFrame(self.catalog_container, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            
            icon_label = ctk.CTkLabel(
                empty_frame,
                text="📚",
                font=ctk.CTkFont(size=48)
            )
            icon_label.pack(pady=(50, 20))
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="אין פריטים בקטלוג\nלחץ על 'טען קטלוג חדש' כדי להתחיל",
                font=ctk.CTkFont(family="Heebo", size=16),
                text_color="gray",
                justify="center"
            )
            empty_label.pack()
            return
        
        # Group items by category
        categories = {}
        for item in items:
            category = item.get('קטגוריה', 'ללא קטגוריה')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Display categories
        for category, category_items in categories.items():
            self.create_category_section(category, category_items)
        
        # Update statistics
        self.update_stats()
    
    def create_category_section(self, category: str, items: List):
        """Create a category section"""
        # Category header
        category_frame = ctk.CTkFrame(self.catalog_container)
        category_frame.pack(fill="x", padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(category_frame, fg_color="#F3F4F6")
        header_frame.pack(fill="x")
        
        category_title = ctk.CTkLabel(
            header_frame,
            text=f"{category} ({len(items)} פריטים)",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            text_color="#374151"
        )
        category_title.pack(pady=10)
        
        # Items in this category
        for item in items:
            self.create_item_card(item)
    
    def create_item_card(self, item):
        """Create item card"""
        card = ctk.CTkFrame(self.catalog_container, border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", padx=10, pady=5)
        
        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Item info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True)
        
        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=item.get('שם מוצר', 'פריט ללא שם'),
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            anchor="e"
        )
        name_label.pack(anchor="e")
        
        # Price
        price = item.get('מחיר', 0)
        price_label = ctk.CTkLabel(
            info_frame,
            text=f"מחיר: ₪{price}",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        price_label.pack(anchor="e")
        
        # Description
        description = item.get('תיאור', '')
        if description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=f"הערות: {description}",
                font=ctk.CTkFont(family="Heebo", size=13),
                anchor="e"
            )
            desc_label.pack(anchor="e")
        
        # Edit button (if user has permission)
        if self.has_permission('edit_catalog'):
            edit_button = ctk.CTkButton(
                content_frame,
                text="ערוך",
                width=60,
                height=30,
                font=ctk.CTkFont(family="Heebo", size=12),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                command=lambda i=item: self.edit_item(i)
            )
            edit_button.pack(pady=2)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        role = self.current_user.get('role', 'viewer')
        
        if role == 'admin':
            return True
        elif role == 'manager':
            return permission in ['view_catalog', 'edit_catalog']
        elif role == 'employee':
            return permission in ['view_catalog']
        
        return False
    
    def edit_item(self, item):
        """Edit catalog item (placeholder)"""
        messagebox.showinfo(
            "עריכת פריט",
            f"עריכת פריט: {item.get('שם מוצר', 'פריט')}\n(יופעל בגרסה הבאה)"
        )
    
    def import_catalog(self):
        """Import catalog from Excel file"""
        file_path = filedialog.askopenfilename(
            title="בחר קובץ קטלוג",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if file_path:
            try:
                # Show loading message
                messagebox.showinfo("טוען", "טוען קטלוג, אנא המתן...")
                
                success = self.catalog_handler.load_catalog(file_path)
                if success:
                    stats = self.catalog_handler.get_catalog_stats()
                    messagebox.showinfo(
                        "הצלחה", 
                        f"הקטלוג נטען בהצלחה!\nפריטים: {stats['total_items']}\nקטגוריות: {stats['categories']}"
                    )
                    
                    # Reload catalog display
                    self.load_catalog()
                else:
                    messagebox.showerror("שגיאה", "שגיאה בטעינת הקטלוג")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בטעינת הקטלוג: {str(e)}")
    
    def download_template(self):
        """Download template for catalog creation"""
        try:
            # Get save location
            file_path = filedialog.asksaveasfilename(
                title="שמור תבנית קטלוג",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile="תבנית_קטלוג.xlsx"
            )
            
            if file_path:
                # Export template using the catalog handler
                success = self.catalog_handler.export_catalog_template(file_path)
                
                if success:
                    messagebox.showinfo(
                        "הצלחה", 
                        f"תבנית הקטלוג נשמרה בהצלחה:\n{file_path}\n\n"
                        "כעת תוכל למלא את התבנית עם הפריטים שלך ולטעון אותה חזרה למערכת."
                    )
                else:
                    messagebox.showerror("שגיאה", "שגיאה ביצירת תבנית הקטלוג")
                    
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בהורדת התבנית: {str(e)}")
    
    def show_error(self, error):
        """Show error message"""
        if self.catalog_container:
            for widget in self.catalog_container.winfo_children():
                widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.catalog_container,
            text=f"שגיאה בטעינת הקטלוג:\n{error}",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="#EF4444",
            justify="center"
        )
        error_label.pack(expand=True, pady=50)
    
    def update_stats(self):
        """Update statistics display"""
        if not self.stats_label:
            return
            
        if not self.catalog_items:
            self.stats_label.configure(
                text="אין פריטים בקטלוג • לחץ על 'טען קטלוג חדש' כדי להתחיל"
            )
        else:
            categories = len(set(item.get('קטגוריה', '') for item in self.catalog_items))
            total_items = len(self.catalog_items)
            self.stats_label.configure(
                text=f"{total_items} פריטים • {categories} קטגוריות"
            ) 