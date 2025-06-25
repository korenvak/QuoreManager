"""
Quotes Management Page for Kitchen Quote Management System - Modern Professional Design
Complete implementation with CRUD operations, search, and quote creation wizard
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import json
import tempfile
import os
from utils.permissions import PermissionManager
from styling.theme_system import ModernThemeManager, THEMES
from config.settings import SettingsManager

class QuotesPage:
    """Modern professional quotes management page"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.quotes_data = []
        self.filtered_quotes = []
        self.search_var: Optional[ctk.StringVar] = None
        self.filter_var: Optional[ctk.StringVar] = None
        self.quotes_container: Optional[ctk.CTkFrame] = None
        self.stats_label: Optional[ctk.CTkLabel] = None
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(db_manager)
        
        # Initialize theme system
        self.settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
    def create_content(self):
        """Create modern professional quotes page content"""
        # Clear existing content
        for widget in self.parent.winfo_children():
            widget.destroy()
        
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
        
        # Modern search and actions bar  
        self.create_modern_search_bar(inner_frame)
        
        # Modern quotes container
        self.quotes_container = ctk.CTkFrame(
            inner_frame,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        self.quotes_container.pack(fill="both", expand=True)
        
        # Load quotes data
        self.load_quotes()
    
    def create_modern_header(self, parent):
        """Create modern professional page header"""
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
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ניהול הצעות מחיר",
            font=self.theme_manager.create_ctk_font('title'),
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="נהל, ערוך וצר הצעות מחיר מקצועיות",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        subtitle_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))
    
    def create_modern_search_bar(self, parent):
        """Create modern search and actions bar"""
        search_card = ctk.CTkFrame(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_light']
        )
        search_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))
        
        search_frame = ctk.CTkFrame(search_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # New quote button - using theme colors
        new_quote_btn = self.theme_manager.create_modern_button(
            search_frame,
            text="➕  הצעת מחיר חדשה",
            style="primary",
            command=self.start_new_quote_wizard
        )
        new_quote_btn.pack(side="right")
        
        # Search frame
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(side="right", padx=(0, self.theme_manager.get_spacing('md')))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="חפש הצעת מחיר...",
            font=self.theme_manager.create_ctk_font('body'),
            width=250,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=self.theme['border_light'],
            fg_color=self.theme['bg_card'],
            text_color=self.theme['text_primary']
        )
        self.search_entry.pack(side="right", padx=(0, self.theme_manager.get_spacing('sm')))
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)
        
        # Search button - using theme colors
        search_btn = self.theme_manager.create_modern_button(
            search_container,
            text="🔍",
            style="secondary",
            width=40,
            command=self.apply_filters
        )
        search_btn.pack(side="right")
    
    def create_header(self, parent):
        """Create header with title, search, filters, and actions"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="ניהול הצעות מחיר",
            font=ctk.CTkFont(family="Heebo", size=28, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Search and actions bar
        actions_frame = ctk.CTkFrame(header_frame)
        actions_frame.pack(fill="x", pady=(0, 10))
        
        # New quote button
        new_quote_button = self.theme_manager.create_modern_button(
            actions_frame,
            text="הצעת מחיר חדשה",
            style="primary",
            size="large",
            width=180,
            command=self.start_new_quote_wizard
        )
        new_quote_button.pack(side="right", padx=20, pady=15)
        
        # Status filter
        filter_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=(0, 20), pady=15)
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="סטטוס:",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold")
        )
        filter_label.pack(side="right", padx=(10, 0))
        
        self.filter_var = ctk.StringVar(value="הכל")
        filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=["הכל", "טיוטה", "נשלח", "אושר", "בוטל"],
            font=ctk.CTkFont(family="Heebo", size=14),
            command=self.on_filter_changed
        )
        filter_menu.pack(side="right")
        
        # Search frame
        search_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=(0, 20), pady=15)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="חיפוש:",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold")
        )
        search_label.pack(side="right", padx=(10, 0))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="חיפוש לפי לקוח או מספר הצעה...",
            width=300,
            font=ctk.CTkFont(family="Heebo", size=14)
        )
        search_entry.pack(side="right")
        
        # Statistics
        self.stats_label = ctk.CTkLabel(
            actions_frame,
            text="טוען נתונים...",
            font=ctk.CTkFont(family="Heebo", size=14),
            text_color="gray"
        )
        self.stats_label.pack(side="left", padx=20, pady=15)
    
    def create_content_area(self, parent):
        """Create scrollable content area for quotes"""
        self.quotes_container = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        self.quotes_container.pack(fill="both", expand=True)
        
        # Loading placeholder
        loading_label = ctk.CTkLabel(
            self.quotes_container,
            text="טוען הצעות מחיר...",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray"
        )
        loading_label.pack(expand=True, pady=50)
    
    def load_quotes(self):
        """Load quotes data in background"""
        def load_data():
            try:
                # Get quotes based on user role
                current_user_role = self.current_user.get('role', 'viewer')
                current_user_id = self.current_user.get('id')
                
                if current_user_role in ['admin', 'manager', 'employee']:
                    # Admin, manager, and employee see all quotes
                    quotes = self.db_manager.get_all_quotes()
                else:
                    # Viewer sees only their own quotes
                    quotes = self.db_manager.get_quotes_by_creator(current_user_id)
                
                # Process quotes data
                processed_quotes = []
                for quote in quotes:
                    try:
                        # Ensure items is a list
                        raw_items = quote['items']
                        if isinstance(raw_items, str):
                            import json
                            raw_items = json.loads(raw_items)
                        
                        # Customer & creator names
                        customer = self.db_manager.get_customer_by_id(quote['customer_id'])
                        customer_name = customer['name'] if customer else "לקוח לא ידוע"
                        creator = self.db_manager.get_user_by_id(quote['created_by'])
                        creator_name = creator['username'] if creator else "לא ידוע"
                        if creator and (creator.get('first_name') or creator.get('last_name')):
                            creator_name = f"{creator.get('first_name','')} {creator.get('last_name','')}".strip()
                        
                        # Permission flags - use the new permission manager methods
                        can_edit = self.permission_manager.can_edit_quote(self.current_user, quote['id'])
                        can_delete = self.permission_manager.can_delete_quote(self.current_user, quote['id'])
                        
                        enriched = {
                            **quote,
                            'items': raw_items,
                            'items_count': len(raw_items),
                            'customer_name': customer_name,
                            'creator_name': creator_name,
                            'can_edit': can_edit,
                            'can_delete': can_delete
                        }
                        processed_quotes.append(enriched)
                        
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Error processing quote {quote.get('id', 'unknown')}: {e}")
                        continue
                
                self.quotes_data = processed_quotes
                self.filtered_quotes = processed_quotes.copy()
                
                # Update UI on main thread
                self.parent.after(0, self.display_quotes)
                
            except Exception as e:
                self.parent.after(0, lambda: self.handle_quotes_error(str(e)))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def can_user_edit_quote(self, quote) -> bool:
        """Check if current user can edit this quote"""
        user_role = self.current_user.get('role', 'viewer')
        user_id = self.current_user.get('id')
        
        # Admin can edit everything
        if user_role == 'admin':
            return True
        
        # Manager can edit all quotes
        if user_role == 'manager':
            return True
        
        # Employee can only edit their own quotes
        if user_role == 'employee':
            return quote.get('created_by') == user_id
        
        # Viewer cannot edit
        return False
    
    def can_user_delete_quote(self, quote) -> bool:
        """Check if current user can delete this quote"""
        user_role = self.current_user.get('role', 'viewer')
        user_id = self.current_user.get('id')
        
        # Only admin and manager can delete quotes
        if user_role in ['admin', 'manager']:
            return True
        
        # Employees cannot delete quotes (as per specification)
        return False
    
    def on_search_changed(self, *args):
        """Handle search text change"""
        self.apply_filters()
    
    def on_filter_changed(self, *args):
        """Handle filter change"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search criteria"""
        search_term = ""
        if hasattr(self, 'search_entry') and self.search_entry:
            search_term = self.search_entry.get().lower().strip()
        
        filtered = self.quotes_data.copy()
        
        # Apply search filter
        if search_term:
            filtered = []
            for quote in self.quotes_data:
                # Search in quote number
                if search_term in str(quote.get('quote_number', '')):
                    filtered.append(quote)
                    continue
                # Search in customer name
                if search_term in quote.get('customer_name', '').lower():
                    filtered.append(quote)
                    continue
                # Search in creator name
                if search_term in quote.get('creator_name', '').lower():
                    filtered.append(quote)
                    continue
        
        self.filtered_quotes = filtered
        self.display_quotes()
    
    def update_stats(self):
        """Update statistics display"""
        if not self.stats_label:
            return
            
        total = len(self.quotes_data)
        filtered = len(self.filtered_quotes)
        
        if total == filtered:
            stats_text = f"סה״כ {total} הצעות מחיר"
        else:
            stats_text = f"מציג {filtered} מתוך {total} הצעות מחיר"
        
        self.stats_label.configure(text=stats_text)
    
    def start_new_quote_wizard(self):
        """Start new quote creation wizard"""
        from ui.pages.quote_wizard import QuoteWizard
        
        QuoteWizard(
            parent=self.parent,
            db_manager=self.db_manager,
            current_user=self.current_user,
            on_success=self.on_quote_created
        )
    
    def edit_quote(self, quote):
        """Edit an existing quote"""
        try:
            # Check permissions before allowing edit
            can_edit = self.permission_manager.can_edit_quote(self.current_user, quote['id'])
            
            if not can_edit:
                messagebox.showerror("הרשאה נדרשת", "אין לך הרשאה לערוך הצעת מחיר זו")
                return
            
            # Additional check for discount permissions
            can_edit_with_discount = self.permission_manager.can_edit_quote_with_discount(self.current_user, quote['id'])
            
            if not can_edit_with_discount:
                quote_discount = quote.get('regular_discount', 0)
                user_max_discount = self.current_user.get('max_discount', 0)
                messagebox.showerror(
                    "הרשאה נדרשת", 
                    f"אין לך הרשאה לערוך הצעת מחיר עם הנחה של {quote_discount}%.\n"
                    f"ההנחה המקסימלית המותרת לך היא {user_max_discount}%."
                )
                return
            
            # Import here to avoid circular imports
            from ui.pages.quote_wizard import QuoteWizard
            
            def on_success():
                self.load_quotes()  # Refresh quotes
            
            # Create quote wizard for editing
            wizard = QuoteWizard(
                parent=self.parent.winfo_toplevel(),
                db_manager=self.db_manager,
                current_user=self.current_user,
                on_success=on_success
            )
            
            # Load the existing quote data into the wizard
            wizard.edit_existing_quote(quote)
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בעריכת הצעת המחיר: {e}")
    
    def view_quote(self, quote):
        """View quote details (read-only)"""
        messagebox.showinfo("צפייה", "צפייה בהצעת מחיר - יופעל בגרסה הבאה")
    
    def generate_pdf(self, quote):
        """Generate PDF for quote"""
        try:
            from pathlib import Path
            import os
            from tkinter import filedialog
            
            # Import PDF generator
            from backhand.pdf_generator import create_professional_pdf
            from config.settings import SettingsManager
            from utils.helpers import generate_quote_filename
            import pandas as pd
            
            # Get customer data
            customer = self.db_manager.get_customer_by_id(quote['customer_id'])
            if not customer:
                messagebox.showerror("שגיאה", "לא ניתן למצוא פרטי לקוח")
                return
            
            # Prepare customer data for PDF
            customer_data = {
                'name': customer['name'],
                'phone': customer['phone'],
                'email': customer['email'],
                'address': customer['address'],
                'date': quote['created_at'].strftime('%Y-%m-%d') if quote['created_at'] else None
            }
            
            # Prepare items data
            items = quote['items']
            if isinstance(items, str):
                import json
                items = json.loads(items)
            
            # Convert to DataFrame for PDF generation
            items_data = []
            for item in items:
                items_data.append({
                    'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
                    'כמות': item.get('כמות', item.get('quantity', 1)),
                    'מחיר': item.get('מחיר', item.get('price', 0)),
                    'קטגוריה': item.get('קטגוריה', item.get('category', ''))
                })
            
            items_df = pd.DataFrame(items_data)
            
            # Prepare calculations
            calculations = {
                'subtotal': quote.get('subtotal', 0),
                'regular_discount': quote.get('regular_discount', 0),
                'contractor_discount': quote.get('contractor_discount', 0),
                'vat_rate': quote.get('vat_rate', 17),
                'total_amount': quote.get('total_amount', 0),
                'discount_val': quote.get('discount_amount', 0),  # Regular discount amount
                'contractor_discount_val': quote.get('contractor_discount_amount', 0),  # Contractor discount amount
                'vat_amount': quote.get('vat_amount', 0),
                'final_total': quote.get('final_total', quote.get('total_amount', 0)),
                'discount_percent': quote.get('regular_discount', 0)  # Regular discount percentage
            }
            
            # Get settings manager
            settings_manager = SettingsManager()
            
            # Generate PDF filename
            pdf_filename = generate_quote_filename(customer['name'], quote['quote_number'])
            
            # Prompt user for save location
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=pdf_filename,
                title="בחר מיקום לשמירת הצעת המחיר כ-PDF"
            )
            
            if not save_path:
                messagebox.showinfo("שמירה בוטלה", "שמירת קובץ ה-PDF בוטלה על ידי המשתמש.")
                return
            
            # Generate PDF
            demo1 = quote.get('images', [])[0] if quote.get('images') and len(quote.get('images', [])) > 0 else None
            demo2 = quote.get('images', [])[1] if quote.get('images') and len(quote.get('images', [])) > 1 else None
            
            success = create_professional_pdf(
                customer_data=customer_data,
                items_df=items_df,
                calculations=calculations,
                settings_manager=settings_manager,
                quote_id=quote['id'],
                save_path=save_path,
                demo1=demo1,
                demo2=demo2
            )
            
            if success:
                # Update quote with PDF path
                self.db_manager.update_quote(quote['id'], pdf_path=save_path)
                
                # Ask user if they want to open the PDF
                result = messagebox.askyesno(
                    "הצלחה!",
                    f"הקובץ נשמר בהצלחה:\n{save_path}\n\nהאם ברצונך לפתוח את הקובץ?"
                )
                if result:
                    os.startfile(save_path)
            else:
                messagebox.showerror("שגיאה", "שגיאה ביצירת קובץ ה-PDF")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה ביצירת PDF: {e}")
    
    def duplicate_quote(self, quote):
        """Duplicate an existing quote"""
        messagebox.showinfo("שכפול", "שכפול הצעת מחיר - יופעל בגרסה הבאה")
    
    def view_pdf(self, quote):
        """Generate PDF in a temp file and open it for viewing"""
        try:
            from backhand.pdf_generator import create_professional_pdf
            from config.settings import SettingsManager
            from utils.helpers import generate_quote_filename
            import pandas as pd
            from pathlib import Path
            import tempfile
            import os
            
            # Prepare customer data
            customer = self.db_manager.get_customer_by_id(quote['customer_id'])
            if not customer:
                messagebox.showerror("שגיאה", "לא ניתן למצוא פרטי לקוח")
                return
                
            customer_data = {
                'name': customer['name'],
                'phone': customer['phone'],
                'email': customer['email'],
                'address': customer['address'],
                'date': quote.get('created_at', '')
            }
            
            # Prepare items data - ensure all items have Hebrew keys
            items = quote['items']
            if isinstance(items, str):
                import json
                items = json.loads(items)
            
            # Convert items to ensure they have Hebrew keys
            processed_items = []
            for item in items:
                processed_item = {
                    'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
                    'כמות': item.get('כמות', item.get('quantity', 1)),
                    'מחיר': item.get('מחיר', item.get('price', 0)),
                    'קטגוריה': item.get('קטגוריה', item.get('category', ''))
                }
                processed_items.append(processed_item)
            
            items_df = pd.DataFrame(processed_items)
            
            # Prepare calculations
            calculations = {
                'subtotal': quote.get('subtotal', 0),
                'regular_discount': quote.get('regular_discount', 0),
                'contractor_discount': quote.get('contractor_discount', 0),
                'vat_rate': quote.get('vat_rate', 17),
                'total_amount': quote.get('total_amount', 0),
                'discount_val': quote.get('discount_amount', 0),
                'contractor_discount_val': quote.get('contractor_discount_amount', 0),
                'vat_amount': quote.get('vat_amount', 0),
                'final_total': quote.get('final_total', quote.get('total_amount', 0)),
                'discount_percent': quote.get('regular_discount', 0)
            }
            
            # Generate temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
                temp_pdf_path = tmpfile.name
            
            settings_manager = SettingsManager()
            demo1 = quote.get('images', [])[0] if quote.get('images') and len(quote.get('images', [])) > 0 else None
            demo2 = quote.get('images', [])[1] if quote.get('images') and len(quote.get('images', [])) > 1 else None
            
            success = create_professional_pdf(
                customer_data=customer_data,
                items_df=items_df,
                calculations=calculations,
                save_path=temp_pdf_path,
                settings_manager=settings_manager,
                quote_id=quote['id'],
                demo1=demo1,
                demo2=demo2
            )
            
            if success:
                # Open the PDF
                try:
                    if os.name == 'nt':
                        os.startfile(temp_pdf_path)
                    else:
                        import subprocess
                        subprocess.Popen(['xdg-open', temp_pdf_path])
                except Exception as e:
                    messagebox.showerror("שגיאה", f"לא ניתן לפתוח את קובץ ה-PDF: {e}")
            else:
                messagebox.showerror("שגיאה", "שגיאה ביצירת קובץ ה-PDF לצפייה.")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בצפייה ב-PDF: {e}")

    def delete_quote(self, quote):
        """Delete a quote after confirmation"""
        if messagebox.askyesno("אישור מחיקה", "האם אתה בטוח שברצונך למחוק את הצעת המחיר?"):
            try:
                self.db_manager.delete_quote(quote['id'])
                messagebox.showinfo("נמחק", "הצעת המחיר נמחקה בהצלחה.")
                self.load_quotes()
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה במחיקת הצעת המחיר: {e}")
    
    def on_quote_created(self):
        """Handle successful quote creation"""
        self.load_quotes()
    
    def display_quotes(self):
        """Display quotes in the UI"""
        self.clear_container()
        
        if not self.filtered_quotes:
            self.show_empty_state()
            return
        
        # Display quotes
        for quote in self.filtered_quotes:
            self.create_quote_card(quote)
        
        # Update stats
        self.update_stats()
    
    def handle_quotes_error(self, error: str):
        """Handle quotes loading error"""
        self.clear_container()
        
        if self.quotes_container:
            error_frame = ctk.CTkFrame(self.quotes_container)
            error_frame.pack(fill="x", padx=20, pady=20)
            
            current_theme = self.theme_manager.get_current_theme()
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"שגיאה בטעינת הצעות מחיר:\n{error}",
                font=ctk.CTkFont(family="Heebo", size=16),
                text_color=current_theme['error'],
                justify="center"
            )
            error_label.pack(pady=30)
            
            retry_button = self.theme_manager.create_modern_button(
                error_frame,
                text="נסה שוב",
                style="primary",
                size="medium",
                width=120,
                command=self.load_quotes
            )
            retry_button.pack(pady=(0, 20))
    
    def clear_container(self):
        """Clear quotes container"""
        if self.quotes_container:
            for widget in self.quotes_container.winfo_children():
                widget.destroy()
    
    def show_empty_state(self):
        """Show empty state message"""
        if not self.quotes_container:
            return
            
        empty_frame = ctk.CTkFrame(self.quotes_container, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both")
        
        if not self.quotes_data:
            # No quotes at all
            message = "אין הצעות מחיר במערכת\nלחץ על 'הצעת מחיר חדשה' כדי להתחיל"
            icon = "📋"
        else:
            # No quotes match search/filter
            message = "לא נמצאו הצעות מחיר המתאימות לחיפוש\nנסה מונחי חיפוש או מסננים אחרים"
            icon = "🔍"
        
        icon_label = ctk.CTkLabel(
            empty_frame,
            text=icon,
            font=ctk.CTkFont(size=48)
        )
        icon_label.pack(pady=(50, 20))
        
        message_label = ctk.CTkLabel(
            empty_frame,
            text=message,
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray",
            justify="center"
        )
        message_label.pack()
    
    def create_quote_card(self, quote):
        """Create individual quote card with permission checks (no status badge)"""
        if not self.quotes_container:
            return
        card = ctk.CTkFrame(
            self.quotes_container,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        card.pack(fill="x", padx=20, pady=12)
        # Add hover effect with theme colors
        current_theme = self.theme_manager.get_current_theme()
        def on_enter(event):
            card.configure(border_color=current_theme['primary'])
        def on_leave(event):
            card.configure(border_color="#E1E8F7")
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=15)
        # Left side - quote info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True)
        # Quote header
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        # Quote number and customer
        quote_title = f"הצעה #{quote['quote_number']} - {quote['customer_name']}"
        title_label = ctk.CTkLabel(
            header_frame,
            text=quote_title,
            font=ctk.CTkFont(family="Assistant", size=18, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        title_label.pack(anchor="e")
        # Quote details
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill="x", pady=(8, 0))
        # Total amount with theme color
        total_label = ctk.CTkLabel(
            details_frame,
            text=f"סה״כ: ₪{quote.get('total_amount', 0):,.2f}",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color=current_theme['primary'],
            anchor="e"
        )
        total_label.pack(anchor="e")
        # Creation date and creator
        if quote.get('created_at'):
            try:
                if isinstance(quote['created_at'], str):
                    from datetime import datetime
                    created_at = datetime.fromisoformat(quote['created_at'])
                else:
                    created_at = quote['created_at']
                date_str = created_at.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = "לא ידוע"
            date_creator_text = f"נוצר: {date_str}"
            if quote.get('creator_name'):
                date_creator_text += f" ע״י {quote['creator_name']}"
            date_label = ctk.CTkLabel(
                details_frame,
                text=date_creator_text,
                font=ctk.CTkFont(family="Assistant", size=12),
                text_color="#6B7280",
                anchor="e"
            )
            date_label.pack(anchor="e", pady=(2, 0))
        # Items count
        items_count = quote.get('items_count', 0)
        items_label = ctk.CTkLabel(
            details_frame,
            text=f"פריטים: {items_count}",
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color="#6B7280",
            anchor="e"
        )
        items_label.pack(anchor="e", pady=(2, 0))
        # Right side - actions (single row layout with theme colors)
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(side="left", padx=(0, 20))
        
        # All buttons in single row with professional styling
        buttons_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_container.pack(fill="x")
        
        # Delete button (only if user can delete) - rightmost for caution
        if quote.get('can_delete', False):
            delete_button = self.theme_manager.create_modern_button(
                buttons_container,
                text="מחיקה",
                style="danger",
                size="small",
                width=80,
                command=lambda q=quote: self.delete_quote(q)
            )
            delete_button.pack(side="right", padx=(5, 0))
        
        # Generate PDF button - success style for positive action
        pdf_button = self.theme_manager.create_modern_button(
            buttons_container,
            text="הורדה",
            style="success",
            size="small",
            width=80,
            command=lambda q=quote: self.generate_pdf(q)
        )
        pdf_button.pack(side="right", padx=(5, 0))
        
        # View PDF button - secondary style
        view_pdf_button = self.theme_manager.create_modern_button(
            buttons_container,
            text="צפייה PDF",
            style="secondary",
            size="small",
            width=90,
            command=lambda q=quote: self.view_pdf(q)
        )
        view_pdf_button.pack(side="right", padx=(5, 0))
        
        # View/Edit button (only if user can edit)
        if quote.get('can_edit', False):
            edit_button = self.theme_manager.create_modern_button(
                buttons_container,
                text="עריכה",
                style="primary",
                size="small",
                width=80,
                command=lambda q=quote: self.edit_quote(q)
            )
            edit_button.pack(side="right", padx=(5, 0))
        else:
            view_button = self.theme_manager.create_modern_button(
                buttons_container,
                text="צפייה",
                style="outline",
                size="small",
                width=80,
                command=lambda q=quote: self.view_quote(q)
            )
            view_button.pack(side="right", padx=(5, 0))


# QuoteWizard and QuoteViewer are now implemented in separate files 