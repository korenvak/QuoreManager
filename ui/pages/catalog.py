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
        """Create modern professional catalog page content with responsive design"""
        # Clear existing content
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Initialize theme system for professional styling
        from styling.theme_system import ModernThemeManager
        from config.settings import SettingsManager
        settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
        # Professional main container with modern gradient background
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=self.theme['bg_secondary'],
            corner_radius=0,
            scrollbar_button_color=self.theme['primary_light'],
            scrollbar_button_hover_color=self.theme['primary']
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Professional inner container with proper spacing
        inner_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Modern professional page header
        self.create_modern_header(inner_frame)
        
        # Professional search and filter bar
        self.create_modern_search_bar(inner_frame)
        
        # Modern catalog container with professional card design
        catalog_content_frame = self.theme_manager.create_modern_card(
            inner_frame,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        catalog_content_frame.pack(fill="both", expand=True)
        
        # Create scrollable catalog container inside the card
        self.catalog_container = ctk.CTkScrollableFrame(
            catalog_content_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.catalog_container.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('lg'))
        
        # Load catalog data with modern loading state
        self.load_catalog()
    
    def create_modern_header(self, parent):
        """Create modern professional page header"""
        header_card = self.theme_manager.create_modern_card(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        header_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        header_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Professional title with modern typography
        title_label = ctk.CTkLabel(
            header_frame,
            text="קטלוג מוצרים",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Professional subtitle with theme colors
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="עיין וחפש במוצרים זמינים ליצירת הצעות מחיר",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
    
    def create_modern_search_bar(self, parent):
        """Create modern professional search and filter bar"""
        search_card = self.theme_manager.create_modern_card(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        search_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        search_frame = ctk.CTkFrame(search_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Professional reload button
        reload_btn = self.theme_manager.create_modern_button(
            search_frame,
            text="🔄 רענן קטלוג",
            style="primary",
            command=self.reload_catalog
        )
        reload_btn.pack(side="right")
        
        # Professional search container
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(side="right", padx=(0, self.theme_manager.get_spacing('md')))
        
        # Modern search entry with professional styling
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="חפש מוצר...",
            font=self.theme_manager.create_ctk_font('body'),
            width=300,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=self.theme['border_light'],
            fg_color=self.theme['input_bg'],
            text_color=self.theme['text_primary']
        )
        self.search_entry.pack(side="right", padx=(0, self.theme_manager.get_spacing('sm')))
        self.search_entry.bind("<KeyRelease>", self.filter_catalog)
        
        # Professional search button
        search_btn = self.theme_manager.create_modern_button(
            search_container,
            text="🔍",
            style="secondary",
            size="medium",
            width=40,
            command=self.apply_filters
        )
        search_btn.pack(side="right")
        
        # Professional filter section
        filter_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_container.pack(side="right", padx=(0, self.theme_manager.get_spacing('lg')))
        
        # Category filter with modern styling
        filter_label = ctk.CTkLabel(
            filter_container,
            text="קטגוריה:",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_secondary']
        )
        filter_label.pack(side="right", padx=(self.theme_manager.get_spacing('sm'), 0))
        
        self.category_filter = ctk.CTkOptionMenu(
            filter_container,
            values=["הכל", "כיורים", "ארונות", "משטחים", "ברזים", "אביזרים"],
            font=self.theme_manager.create_ctk_font('body'),
            fg_color=self.theme['input_bg'],
            button_color=self.theme['primary'],
            button_hover_color=self.theme['primary_hover'],
            corner_radius=8,
            command=self.filter_catalog
        )
        self.category_filter.pack(side="right")
    
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
        """Create modern item card with new format support"""
        # Modern card with white background and blue border
        card = ctk.CTkFrame(
            self.catalog_container, 
            fg_color="#FFFFFF",
            border_width=1, 
            border_color="#E1E8F7",
            corner_radius=15
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Hover effect
        def on_enter(event):
            card.configure(border_color="#3B82F6")
        
        def on_leave(event):
            card.configure(border_color="#E1E8F7")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        
        # Header with name and approval indicator
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", anchor="e")
        
        # Item name (main title)
        name_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        name_frame.pack(side="right", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=item.get('שם מוצר', 'פריט ללא שם'),
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        name_label.pack(anchor="e")
        
        # Approval indicator (if required)
        requires_approval = item.get('דורש אישור', False)
        if requires_approval:
            approval_label = ctk.CTkLabel(
                header_frame,
                text="🔒",
                font=ctk.CTkFont(size=16),
                text_color="#EF4444"
            )
            approval_label.pack(side="left", padx=(0, 10))
            
            # Approval tooltip
            approval_text = ctk.CTkLabel(
                header_frame,
                text="דורש אישור מנהל",
                font=ctk.CTkFont(family="Assistant", size=12),
                text_color="#EF4444"
            )
            approval_text.pack(side="left")
        
        # Price and unit info
        price_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        price_frame.pack(fill="x", anchor="e", pady=(5, 0))
        
        price = item.get('מחיר', 0)
        units = item.get('יחידה', 'יח׳')
        
        if price and price > 0:
            # Standard pricing
            price_text = f"₪{price:,.0f} / {units}"
            price_color = "#10B981"  # Green for available pricing
        else:
            # Custom pricing required
            price_text = f"מחיר לפי הזמנה / {units}"
            price_color = "#F59E0B"  # Orange for custom pricing
        
        price_label = ctk.CTkLabel(
            price_frame,
            text=price_text,
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=price_color,
            anchor="e"
        )
        price_label.pack(anchor="e")
        
        # Unit type explanation
        if units == 'מ"א':
            unit_explanation = "מטר אורך - ניתן להזין כמות עשרונית"
        elif units == 'יח׳':
            unit_explanation = "יחידות - כמות שלמה בלבד"
        else:
            unit_explanation = f"יחידת מידה: {units}"
        
        unit_label = ctk.CTkLabel(
            price_frame,
            text=unit_explanation,
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color="#6B7280",
            anchor="e"
        )
        unit_label.pack(anchor="e", pady=(2, 0))
        
        # Comments (if available)
        comments = item.get('תיאור', '').strip()
        if comments:
            comments_label = ctk.CTkLabel(
                content_frame,
                text=f"הערות: {comments}",
                font=ctk.CTkFont(family="Assistant", size=12, slant="italic"),
                text_color="#6B7280",
                anchor="e",
                wraplength=400
            )
            comments_label.pack(anchor="e", pady=(5, 0))
        
        # Add button (modern style)
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Use theme manager for modern button
        theme_manager = ModernThemeManager(SettingsManager())
        
        add_button = theme_manager.create_modern_button(
            button_frame,
            text="הוסף לסל",
            style="primary",
            size="medium",
            command=lambda: self.add_to_quote_wizard(item)
        )
        add_button.pack(side="left")
        
        # Edit button (if user has permission)
        if self.has_permission('edit_catalog'):
            edit_button = theme_manager.create_modern_button(
                button_frame,
                text="ערוך",
                style="outline", 
                size="medium",
                command=lambda: self.edit_item(item)
            )
            edit_button.pack(side="left", padx=(10, 0))
    
    def add_to_quote_wizard(self, item):
        """Add item to quote wizard (placeholder for integration)"""
        from tkinter import messagebox
        messagebox.showinfo(
            "הוסף לסל",
            f"פריט '{item.get('שם מוצר', 'פריט')}' יתווסף לסל\n"
            f"יחידה: {item.get('יחידה', 'יח׳')}\n"
            f"מחיר: {'₪' + str(item.get('מחיר', 0)) if item.get('מחיר', 0) > 0 else 'מחיר לפי הזמנה'}\n"
            f"דורש אישור: {'כן' if item.get('דורש אישור', False) else 'לא'}"
        )
    
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
    
    def reload_catalog(self):
        """Reload catalog data"""
        self.load_catalog()
    
    def filter_catalog(self, *args):
        """Filter catalog based on search and category"""
        # This method filters the displayed catalog items
        self.load_catalog()  # For now, just reload - can be enhanced later
    
    def apply_filters(self):
        """Apply current filters to catalog"""
        self.filter_catalog() 