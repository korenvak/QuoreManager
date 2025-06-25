"""
Complete Quote Creation Wizard for Kitchen Quote Management System
Multi-step wizard for creating professional kitchen quotes
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import json
from utils.excel_handler import CatalogHandler
from utils.permissions import PermissionManager

class QuoteWizard:
    """Complete multi-step quote creation wizard"""
    
    def __init__(self, parent, db_manager, current_user, on_success: Callable, existing_draft=None):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.on_success = on_success
        self.existing_draft = existing_draft
        self.dialog: Optional[ctk.CTkToplevel] = None
        self.draft_id = None  # Store draft ID for deletion after successful quote creation
        
        # Add logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        # Wizard state
        self.current_step = 1
        self.max_steps = 4
        self.quote_data = {
            'customer_id': None,
            'customer_data': None,
            'items': [],
            'regular_discount': 0.0,
            'contractor_discount': 0.0,
            'vat_rate': self.db_manager.get_setting('vat_rate', 17.0),
            'notes': '',
            'images': []
        }
        
        # UI references
        self.content_frame = None
        self.progress_frame = None
        self.next_button = None
        self.prev_button = None
        
        # Step-specific data
        self.customers_list = []
        self.catalog_items = []
        self.selected_items = []
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(db_manager)
        
        # Load existing draft if provided
        if existing_draft:
            # Store draft ID for later deletion
            if isinstance(existing_draft, dict):
                self.draft_id = existing_draft.get('id')
            else:
                self.draft_id = getattr(existing_draft, 'id', None)
            self.load_from_draft(existing_draft)
            
        self.create_wizard()
    
    def create_wizard(self):
        """Create wizard dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("אשף יצירת הצעת מחיר")
        
        # Make window larger and responsive
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Use 90% of screen size but with min and max limits
        window_width = min(1400, int(screen_width * 0.9))
        window_height = min(900, int(screen_height * 0.9))
        # Ensure minimum usability sizes
        window_width = max(1000, window_width)
        window_height = max(700, window_height)
        
        self.dialog.geometry(f"{window_width}x{window_height}")
        self.dialog.resizable(True, True)
        
        # Center dialog on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set clean white background
        self.dialog.configure(fg_color="#FFFFFF")
        
        # Main frame - make it scrollable with white background
        self.main_scrollable_frame = ctk.CTkScrollableFrame(
            self.dialog,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E1E8F7"
        )
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Progress bar
        self.progress_frame = ctk.CTkFrame(
            self.main_scrollable_frame,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        self.progress_frame.pack(fill="x", pady=(20, 0))
        
        # Content area - now inside scrollable frame with white background
        self.content_frame = ctk.CTkFrame(
            self.main_scrollable_frame, 
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E1E8F7"
        )
        self.content_frame.pack(fill="both", expand=True, pady=20)
        
        # Navigation buttons - fixed at bottom of dialog (not scrollable)
        self.create_navigation(self.dialog)
        
        # Show first step
        self.show_step()
        
        # No auto-save - only manual save as draft
    
    def create_progress_bar(self, parent):
        """Create progress bar showing current step"""
        self.progress_frame = ctk.CTkFrame(parent)
        self.progress_frame.pack(fill="x", pady=(20, 0))
        
        # Step indicators will be created in show_step
        
    def update_progress_bar(self):
        """Update progress bar for current step"""
        # Clear existing progress
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        steps_container = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        steps_container.pack(pady=25)
        
        step_names = ["בחירת לקוח", "בחירת פריטים", "הנחות ומחירים", "סיכום ושמירה"]
        
        for i, step_name in enumerate(step_names, 1):
            step_frame = ctk.CTkFrame(steps_container, fg_color="transparent")
            step_frame.pack(side="right", padx=20)
            
            is_current = i == self.current_step
            is_completed = i < self.current_step
            
            if is_current:
                color = "#3B82F6"  # Primary blue
                text_color = "white"
            elif is_completed:
                color = "#1E40AF"  # Darker blue
                text_color = "white"
            else:
                color = "#EBF4FF"
                text_color = "#9CA3AF"
            
            step_circle = ctk.CTkLabel(
                step_frame,
                text=str(i),
                width=50,
                height=50,
                font=ctk.CTkFont(family="Assistant", size=18, weight="bold"),
                fg_color=color,
                text_color=text_color,
                corner_radius=25
            )
            step_circle.pack()
            
            name_label = ctk.CTkLabel(
                step_frame,
                text=step_name,
                font=ctk.CTkFont(family="Assistant", size=13, weight="bold" if is_current else "normal"),
                text_color="#1F2937" if is_current else "#9CA3AF"
            )
            name_label.pack(pady=(8, 0))
    
    def create_navigation(self, parent):
        """Create navigation buttons"""
        # Create a fixed navigation frame at the bottom
        nav_container = ctk.CTkFrame(parent, fg_color="transparent", height=90)
        nav_container.pack(side="bottom", fill="x", padx=25, pady=15)
        nav_container.pack_propagate(False)
        
        nav_frame = ctk.CTkFrame(
            nav_container, 
            fg_color="#FDFDFE",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        nav_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        # Button container
        button_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=18)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="ביטול",
            font=ctk.CTkFont(family="Assistant", size=16),
            height=50,
            width=100,
            fg_color="#9CA3AF",
            hover_color="#6B7280",
            corner_radius=12,
            command=self.cancel_wizard
        )
        cancel_button.pack(side="left")
        
        # Save draft button
        save_draft_button = ctk.CTkButton(
            button_frame,
            text="שמור כטיוטה",
            font=ctk.CTkFont(family="Assistant", size=16),
            height=50,
            width=130,
            fg_color="#F59E0B",
            hover_color="#D97706",
            corner_radius=12,
            command=self.save_draft
        )
        save_draft_button.pack(side="left", padx=(10, 0))
        
        # Step info in center
        step_info_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        step_info_frame.pack(side="left", fill="x", expand=True, padx=20)
        
        self.step_info_label = ctk.CTkLabel(
            step_info_frame,
            text="",
            font=ctk.CTkFont(family="Assistant", size=15),
            text_color="#6B7280"
        )
        self.step_info_label.pack(expand=True)
        
        # Previous button
        self.prev_button = ctk.CTkButton(
            button_frame,
            text="◀ הקודם",
            font=ctk.CTkFont(family="Assistant", size=16),
            height=50,
            width=100,
            fg_color="#9CA3AF",
            hover_color="#4B5563",
            corner_radius=12,
            command=self.prev_step
        )
        self.prev_button.pack(side="right", padx=(10, 0))
        
        # Next/Finish button
        self.next_button = ctk.CTkButton(
            button_frame,
            text="הבא ▶",
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            height=50,
            width=100,
            fg_color="#3B82F6",
            hover_color="#1E40AF",
            corner_radius=12,
            command=self.next_step
        )
        self.next_button.pack(side="right")
        
        # Update button states
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update navigation button states"""
        if not self.prev_button or not self.next_button:
            return
            
        # Previous button
        if self.current_step == 1:
            self.prev_button.configure(state="disabled")
        else:
            self.prev_button.configure(state="normal")
        
        # Next/Finish button
        if self.current_step == self.max_steps:
            self.next_button.configure(text="סיום ושמירה ✓")
        else:
            self.next_button.configure(text="הבא ▶")
        
        # Enable/disable based on step validation
        can_proceed = self.validate_current_step()
        self.next_button.configure(state="normal" if can_proceed else "disabled")
        
        # Update step info label
        if hasattr(self, 'step_info_label'):
            step_names = ["בחירת לקוח", "בחירת פריטים", "הנחות ומחירים", "סיכום ושמירה"]
            if self.current_step <= len(step_names):
                step_text = f"שלב {self.current_step} מתוך {self.max_steps}: {step_names[self.current_step - 1]}"
                self.step_info_label.configure(text=step_text)
    
    def validate_current_step(self) -> bool:
        """Validate current step data"""
        if self.current_step == 1:
            return self.quote_data['customer_id'] is not None
        elif self.current_step == 2:
            return len(self.selected_items) > 0
        elif self.current_step == 3:
            return True  # Pricing step is always valid
        elif self.current_step == 4:
            return True  # Summary step is always valid
        return False
    
    def show_step(self):
        """Show current step content"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update progress bar
        self.update_progress_bar()
        
        # Show appropriate step
        if self.current_step == 1:
            self.show_customer_selection()
        elif self.current_step == 2:
            self.show_items_selection()
        elif self.current_step == 3:
            self.show_pricing_discounts()
        elif self.current_step == 4:
            self.show_summary()
        
        self.update_navigation_buttons()
    
    def show_customer_selection(self):
        """Show customer selection step"""
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="שלב 1: בחירת לקוח",
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Customer selection container
        selection_frame = ctk.CTkFrame(self.content_frame)
        selection_frame.pack(fill="both", expand=True, padx=20)
        
        # Search and new customer bar
        search_frame = ctk.CTkFrame(selection_frame)
        search_frame.pack(fill="x", padx=20, pady=20)
        
        # New customer button
        new_customer_btn = ctk.CTkButton(
            search_frame,
            text="לקוח חדש",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            command=self.create_new_customer
        )
        new_customer_btn.pack(side="right", padx=(0, 20))
        
        # Search entry
        self.customer_search_var = ctk.StringVar()
        self.customer_search_var.trace("w", self.filter_customers)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.customer_search_var,
            placeholder_text="חיפוש לקוח לפי שם, טלפון או דואל...",
            font=ctk.CTkFont(family="Heebo", size=14),
            height=40
        )
        search_entry.pack(side="right", fill="x", expand=True, padx=(20, 20))
        
        # Customers list
        self.customers_container = ctk.CTkScrollableFrame(selection_frame)
        self.customers_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Load and display customers
        self.load_customers()
    
    def load_customers(self):
        """Load customers from database"""
        def load_data():
            try:
                customers = self.db_manager.get_all_customers()
                self.customers_list = customers
                self.dialog.after(0, self.display_customers, customers)
            except Exception as e:
                self.dialog.after(0, self.show_customer_error, str(e))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def display_customers(self, customers):
        """Display customers in selectable list"""
        # Clear existing
        for widget in self.customers_container.winfo_children():
            widget.destroy()
        
        if not customers:
            no_customers_label = ctk.CTkLabel(
                self.customers_container,
                text="אין לקוחות במערכת\nלחץ על 'לקוח חדש' ליצירת לקוח ראשון",
                font=ctk.CTkFont(family="Heebo", size=16),
                justify="center"
            )
            no_customers_label.pack(expand=True, pady=50)
            return
        
        # Display customers as selectable cards
        for customer in customers:
            self.create_customer_card(customer)
    
    def create_customer_card(self, customer):
        """Create selectable customer card"""
        # Determine if this customer is selected
        is_selected = self.quote_data['customer_id'] == customer['id']
        
        card = ctk.CTkFrame(
            self.customers_container,
            fg_color="#E0F2FE" if is_selected else "transparent",
            border_width=2,
            border_color="#0EA5E9" if is_selected else "#E5E7EB"
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Make card clickable
        def select_customer(event=None, c=customer):
            self.select_customer(c)
        
        card.bind("<Button-1>", select_customer)
        card.configure(cursor="hand2")
        
        # Customer info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        info_frame.bind("<Button-1>", select_customer)
        
        # Customer name
        name_label = ctk.CTkLabel(
            info_frame,
            text=customer['name'],
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            anchor="e"
        )
        name_label.pack(anchor="e")
        name_label.bind("<Button-1>", select_customer)
        
        # Contact info
        contact_text = f"📞 {customer['phone']} | 📧 {customer['email']}"
        contact_label = ctk.CTkLabel(
            info_frame,
            text=contact_text,
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e",
            text_color="gray"
        )
        contact_label.pack(anchor="e", pady=(5, 0))
        contact_label.bind("<Button-1>", select_customer)
        
        # Address
        address_label = ctk.CTkLabel(
            info_frame,
            text=f"📍 {customer['address']}",
            font=ctk.CTkFont(family="Heebo", size=12),
            anchor="e",
            text_color="gray"
        )
        address_label.pack(anchor="e", pady=(2, 0))
        address_label.bind("<Button-1>", select_customer)
    
    def select_customer(self, customer):
        """Select a customer"""
        self.quote_data['customer_id'] = customer['id']
        
        # Convert datetime objects to strings for JSON serialization
        customer_data = customer.copy()
        for key, value in customer_data.items():
            if hasattr(value, 'isoformat'):  # Check if it's a datetime
                customer_data[key] = value.isoformat()
        
        self.quote_data['customer_data'] = customer_data
        
        # Refresh display to show selection
        self.display_customers(self.customers_list)
        self.update_navigation_buttons()
    
    def filter_customers(self, *args):
        """Filter customers based on search"""
        search_term = self.customer_search_var.get().lower().strip()
        
        if not search_term:
            filtered = self.customers_list
        else:
            filtered = [
                customer for customer in self.customers_list
                if (search_term in customer['name'].lower() or
                    search_term in customer['phone'] or
                    search_term in customer['email'].lower())
            ]
        
        self.display_customers(filtered)
    
    def create_new_customer(self):
        """Create new customer dialog"""
        from ui.pages.customers import CustomerDialog

        def on_customer_created():
            # Reload customers and refresh display
            self.load_customers()
            # Try to select the newest customer and advance
            def select_and_advance():
                if self.customers_list:
                    # Assume the newest customer is last in the list
                    new_customer = self.customers_list[-1]
                    self.select_customer(new_customer)
                    self.current_step += 1
                    self.show_step()
            # Wait a bit for the thread to finish loading
            self.dialog.after(300, select_and_advance)

        CustomerDialog(
            parent=self.dialog,
            title="לקוח חדש להצעת מחיר",
            customer_data=None,
            db_manager=self.db_manager,
            on_success=on_customer_created
        )
    
    def show_customer_error(self, error):
        """Show customer loading error"""
        for widget in self.customers_container.winfo_children():
            widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.customers_container,
            text=f"שגיאה בטעינת לקוחות:\n{error}",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="red",
            justify="center"
        )
        error_label.pack(expand=True, pady=50)
    
    def show_items_selection(self):
        """Show item selection step with side-by-side catalog and cart layout"""
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="שלב 2: בחירת פריטים מהקטלוג",
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold"),
            anchor="e"
        )
        title_label.pack(pady=(20, 10), anchor="e")
        
        # Catalog handler
        self.catalog_handler = CatalogHandler()
        self.catalog_items = self.catalog_handler.get_catalog_items()
        self.categories = self.catalog_handler.get_categories()
        
        # Main container with horizontal layout
        main_container = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Configure columns for better balance: 40% catalog, 60% cart
        main_container.grid_columnconfigure(0, weight=2)  # Catalog - 40%
        main_container.grid_columnconfigure(1, weight=3)  # Cart - 60%
        
        # Catalog (40%)
        catalog_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E1E8F7"
        )
        catalog_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # --- Catalog selector and table (restored) ---
        selector_frame = ctk.CTkFrame(catalog_frame, fg_color="#FFFFFF")
        selector_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.catalog_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            selector_frame,
            textvariable=self.catalog_search_var,
            placeholder_text="חיפוש פריט...",
            font=ctk.CTkFont(family="Heebo", size=14, weight="normal"),
            width=200,
            justify="right"
        )
        search_entry.pack(side="right", padx=(0, 10))
        self.catalog_search_var.trace("w", lambda *args: self.update_catalog_table())

        self.category_var = ctk.StringVar(value="הכל")
        category_menu = ctk.CTkOptionMenu(
            selector_frame,
            variable=self.category_var,
            values=["הכל"] + self.categories,
            font=ctk.CTkFont(family="Heebo", size=14, weight="normal"),
            width=150
        )
        category_menu.pack(side="right", padx=(0, 10))
        self.category_var.trace("w", lambda *args: self.update_catalog_table())

        # Catalog table (scrollable)
        self.catalog_table = ctk.CTkScrollableFrame(
            catalog_frame,
            fg_color="#FFFFFF",
            corner_radius=0,
            scrollbar_button_color="#E5E7EB",
        )
        self.catalog_table.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        # --- End catalog selector and table ---
        
        # Cart (60% - wider now)
        cart_frame = ctk.CTkFrame(
            main_container,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E1E8F7"
        )
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # Cart title
        cart_header = ctk.CTkFrame(cart_frame, fg_color="transparent")
        cart_header.pack(fill="x", padx=15, pady=(15, 10))
        
        cart_title = ctk.CTkLabel(
            cart_header,
            text="סל קניות",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            anchor="e"
        )
        cart_title.pack(anchor="e")
        
        # Items count
        self.items_count_label = ctk.CTkLabel(
            cart_header,
            text="0 פריטים",
            font=ctk.CTkFont(family="Heebo", size=14, weight="normal"),
            text_color="#6B7280",
            anchor="e"
        )
        self.items_count_label.pack(anchor="e", pady=(5, 0))
        
        # Cart contents - make it more spacious
        self.cart_frame = ctk.CTkScrollableFrame(cart_frame, fg_color="#FFFFFF")
        self.cart_frame.pack(fill="both", expand=True, padx=15, pady=(10, 10))
        
        # Cart summary
        cart_summary = ctk.CTkFrame(cart_frame, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0")
        cart_summary.pack(fill="x", padx=15, pady=(0, 15))
        
        # Total label
        self.total_label = ctk.CTkLabel(
            cart_summary,
            text="סה\"כ: ₪0.00",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            text_color="#10B981",
            anchor="e"
        )
        self.total_label.pack(pady=20, anchor="e")
        
        # Clear cart button
        clear_cart_btn = ctk.CTkButton(
            cart_summary,
            text="נקה סל",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=120,
            height=40,
            corner_radius=8,
            command=self.clear_cart
        )
        clear_cart_btn.pack(pady=(0, 15))
        
        # Now update the catalog table and cart
        self.update_catalog_table()
        self.update_cart()
        self.update_navigation_buttons()

    def update_catalog_table(self):
        for widget in self.catalog_table.winfo_children():
            widget.destroy()
        search = self.catalog_search_var.get().lower().strip()
        category = self.category_var.get()
        items = self.catalog_items
        if category != "הכל":
            items = [item for item in items if item.get('קטגוריה') == category]
        if search:
            items = [item for item in items if search in item.get('שם מוצר', '').lower() or search in item.get('תיאור', '').lower() or search in item.get('קטגוריה', '').lower()]
        
        # Header
        header = ctk.CTkFrame(self.catalog_table, fg_color="#E0E7EF", height=35)
        header.pack(fill="x", padx=2, pady=(2, 0))
        
        header_label = ctk.CTkLabel(
            header, 
            text="פריטים זמינים (לחץ להוספה)", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            anchor="center"
        )
        header_label.pack(pady=8)
        
        # Items - more compact card layout
        for idx, item in enumerate(items):
            self.create_catalog_item_card(item, idx)
    
    def create_catalog_item_card(self, item, idx):
        """Create a compact item card for the catalog"""
        # Get price safely
        price = item.get('מחיר', 0)
        if price is None:
            price = 0
        
        # Item card with light blue hover effect
        card_color = "#F9FAFB" if idx % 2 == 0 else "#FFFFFF"
        card = ctk.CTkFrame(
            self.catalog_table, 
            fg_color=card_color, 
            height=80,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.pack(fill="x", padx=2, pady=1)
        
        # Add hover effect
        def on_enter(event):
            card.configure(border_color="#3B82F6")
        
        def on_leave(event):
            card.configure(border_color="#E5E7EB")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Main content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Top row - name and price
        top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_frame.pack(fill="x")
        
        # Product name (truncated if too long)
        name = item.get('שם מוצר', '')
        if len(name) > 30:
            name = name[:27] + "..."
        
        name_label = ctk.CTkLabel(
            top_frame,
            text=name,
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        name_label.pack(side="right", fill="x", expand=True)
        
        # Price
        price_label = ctk.CTkLabel(
            top_frame,
            text=f"₪{float(price):,.0f}",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            text_color="#10B981",
            anchor="w"
        )
        price_label.pack(side="left")
        
        # Bottom row - category and add button
        bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(5, 0))
        
        # Category
        category_label = ctk.CTkLabel(
            bottom_frame,
            text=item.get('קטגוריה', ''),
            font=ctk.CTkFont(family="Heebo", size=12),
            text_color="gray",
            anchor="e"
        )
        category_label.pack(side="right", fill="x", expand=True)
        
        # Add button
        add_btn = ctk.CTkButton(
            bottom_frame,
            text="הוסף +",
            font=ctk.CTkFont(family="Heebo", size=12, weight="bold"),
            width=70,
            height=25,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=lambda i=item: self.add_to_cart(i)
        )
        add_btn.pack(side="left")
        
        # Make whole card clickable
        def add_item(event=None):
            self.add_to_cart(item)
        
        card.bind("<Button-1>", add_item)
        content_frame.bind("<Button-1>", add_item)
        # Don't bind to labels as it interferes with button clicks

    def add_to_cart(self, item):
        # Check if already in cart
        for cart_item in self.selected_items:
            if cart_item['name'] == item.get('שם מוצר') and cart_item['category'] == item.get('קטגוריה'):
                cart_item['quantity'] += 1
                cart_item['כמות'] += 1
                self.update_cart()
                self.update_navigation_buttons()
                return
        # Add new item with both Hebrew and English keys
        formatted_item = {
            'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
            'name': item.get('שם מוצר', item.get('name', 'פריט')),
            'קטגוריה': item.get('קטגוריה', item.get('category', '')),
            'category': item.get('קטגוריה', item.get('category', '')),
            'כמות': item.get('כמות', item.get('quantity', 1)),
            'quantity': item.get('כמות', item.get('quantity', 1)),
            'מחיר': item.get('מחיר', item.get('price', 0)),
            'price': item.get('מחיר', item.get('price', 0)),
            'תיאור': item.get('תיאור', item.get('description', '')),
            'description': item.get('תיאור', item.get('description', '')),
            'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
            'unit': item.get('יחידה', item.get('unit', 'יח׳'))
        }
        self.selected_items.append(formatted_item)
        self.update_cart()
        self.update_navigation_buttons()

    def update_cart(self):
        # Check if we're in step 2 (items selection) or step 3 (pricing/discounts)
        if self.current_step == 2:
            # Step 2 - use cart_frame (if it exists)
            if hasattr(self, 'cart_frame') and self.cart_frame:
                for widget in self.cart_frame.winfo_children():
                    widget.destroy()
                
                if not self.selected_items:
                    empty_label = ctk.CTkLabel(
                        self.cart_frame,
                        text="הסל ריק - בחר פריטים מהקטלוג",
                        font=ctk.CTkFont(family="Heebo", size=16, weight="normal"),
                        text_color="#6B7280"
                    )
                    empty_label.pack(pady=40)
                    if hasattr(self, 'total_label') and self.total_label:
                        self.total_label.configure(text="סה\"כ: ₪0.00")
                    # Update navigation buttons
                    self.update_navigation_buttons()
                    return
                
                # Create scrollable frame for cart - no fixed height, let it expand
                cart_scroll = ctk.CTkScrollableFrame(self.cart_frame, fg_color="#FFFFFF")
                cart_scroll.pack(fill="both", expand=True)
                
                # Header
                header = ctk.CTkFrame(cart_scroll, fg_color="#EBF4FF", height=40, border_width=1, border_color="#D1E7FF")
                header.pack(fill="x", padx=5, pady=(5, 2))
                header.grid_columnconfigure(0, weight=0)  # Quantity
                header.grid_columnconfigure(1, weight=3)  # Name
                header.grid_columnconfigure(2, weight=2)  # Category
                header.grid_columnconfigure(3, weight=2)  # Total
                header.grid_columnconfigure(4, weight=0)  # Remove
                
                for col, text in enumerate(["כמות", "שם מוצר", "קטגוריה", "סה\"כ", "הסר"]):
                    label = ctk.CTkLabel(header, text=text, font=ctk.CTkFont(family="Heebo", size=15, weight="bold"), anchor="center")
                    label.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
                
                # Rows
                total = 0
                for idx, item in enumerate(self.selected_items):
                    row_color = "#F8FAFC" if idx % 2 == 0 else "#FFFFFF"
                    row = ctk.CTkFrame(
                        cart_scroll, 
                        fg_color=row_color, 
                        height=45,
                        border_width=1,
                        border_color="#E5E7EB"
                    )
                    row.pack(fill="x", padx=5, pady=2)
                    
                    # Add hover effect for cart rows
                    def create_hover_effect(row_widget):
                        def on_enter(event):
                            row_widget.configure(border_color="#3B82F6", fg_color="#EBF4FF")
                        
                        def on_leave(event):
                            row_widget.configure(border_color="#E5E7EB", fg_color=row_color)
                        
                        row_widget.bind("<Enter>", on_enter)
                        row_widget.bind("<Leave>", on_leave)
                    
                    create_hover_effect(row)
                    
                    row.grid_columnconfigure(0, weight=0)
                    row.grid_columnconfigure(1, weight=3)
                    row.grid_columnconfigure(2, weight=2)
                    row.grid_columnconfigure(3, weight=2)
                    row.grid_columnconfigure(4, weight=0)
                    
                    # Quantity (editable)
                    qty_var = ctk.StringVar(value=str(item['quantity']))
                    
                    # Create entry first
                    qty_entry = ctk.CTkEntry(
                        row, 
                        textvariable=qty_var, 
                        width=60, 
                        height=30,
                        justify="center",
                        font=ctk.CTkFont(family="Heebo", size=14, weight="bold")
                    )
                    qty_entry.grid(row=0, column=0, padx=8, pady=8)
                    
                    # Then set up the trace with proper closure
                    def create_qty_handler(index):
                        def on_qty_change(*args):
                            try:
                                val = int(qty_var.get())
                                if val < 1:
                                    val = 1
                                self.selected_items[index]['quantity'] = val
                                self.update_cart()
                                self.update_navigation_buttons()
                            except ValueError:
                                pass
                        return on_qty_change
                    
                    qty_var.trace("w", create_qty_handler(idx))
                    
                    # Name
                    font_row = ctk.CTkFont(family="Heebo", size=15, weight="normal")
                    font_category = ctk.CTkFont(family="Heebo", size=14, weight="normal")
                    font_price = ctk.CTkFont(family="Heebo", size=15, weight="bold")
                    
                    ctk.CTkLabel(row, text=item['name'], anchor="e", font=font_row).grid(row=0, column=1, padx=8, pady=8, sticky="ew")
                    # Category
                    ctk.CTkLabel(row, text=item['category'], anchor="center", font=font_category, text_color="#6B7280").grid(row=0, column=2, padx=8, pady=8, sticky="ew")
                    # Item total
                    item_total = item['price'] * item['quantity']
                    total += item_total
                    ctk.CTkLabel(row, text=f"₪{item_total:,.0f}", anchor="center", font=font_price, text_color="#10B981").grid(row=0, column=3, padx=8, pady=8, sticky="ew")
                    # Remove button
                    remove_btn = ctk.CTkButton(
                        row, 
                        text="הסר", 
                        width=60, 
                        height=30,
                        font=ctk.CTkFont(family="Heebo", size=12, weight="bold"),
                        fg_color="#EF4444", 
                        hover_color="#DC2626",
                        corner_radius=6,
                        command=lambda i=idx: self.remove_from_cart(i)
                    )
                    remove_btn.grid(row=0, column=4, padx=8, pady=8)
                
                if hasattr(self, 'total_label') and self.total_label:
                    self.total_label.configure(text=f"סה\"כ: ₪{total:,.2f}")
                
                # Update items count if label exists
                if hasattr(self, 'items_count_label'):
                    items_count = len(self.selected_items)
                    count_text = f"{items_count} פריטים" if items_count != 1 else "פריט אחד"
                    self.items_count_label.configure(text=count_text)
                
                # Update navigation buttons since cart changed
                self.update_navigation_buttons()
        
        elif self.current_step == 3:
            # Step 3 - use update_cart_summary for the pricing/discounts step
            self.update_cart_summary()
            # Also recalculate totals for pricing step
            self.calculate_totals()

    def remove_from_cart(self, idx):
        if 0 <= idx < len(self.selected_items):
            self.selected_items.pop(idx)
            self.update_cart()
            self.update_navigation_buttons()

    def show_pricing_discounts(self):

        # Clear previous content
        if hasattr(self, 'content_frame') and self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        
        # Create main container
        main_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="מחירים והנחות",
            font=ctk.CTkFont(family="Heebo", size=24, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Two-column layout
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Left column - Cart summary
        left_frame = ctk.CTkFrame(content_frame, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        cart_title = ctk.CTkLabel(
            left_frame,
            text="סיכום פריטים",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold")
        )
        cart_title.pack(pady=15)
        
        # Cart items
        self.cart_container = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.cart_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Update cart display
        self.update_cart_summary()
        
        # Right column - Pricing and discounts
        right_frame = ctk.CTkFrame(content_frame, fg_color="#F8FAFC", border_width=1, border_color="#E2E8F0")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        pricing_title = ctk.CTkLabel(
            right_frame,
            text="הגדרות מחיר",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold")
        )
        pricing_title.pack(pady=15)
        
        # Regular discount with permission validation
        regular_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        regular_frame.pack(fill="x", padx=15, pady=5)
        
        # Get user's maximum allowed discount
        max_discount = self.current_user.get('max_discount', 0.0)
        has_unlimited_discount = self.current_user.get('role') in ['admin', 'manager']
        
        regular_label = ctk.CTkLabel(
            regular_frame,
            text=f"הנחה כללית (%) - מקסימום: {max_discount}%" if not has_unlimited_discount else "הנחה כללית (%)",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        regular_label.pack(anchor="e")
        
        # Regular discount entry with validation - Load existing value
        existing_regular_discount = self.quote_data.get('regular_discount', 0)
        self.regular_discount_var = ctk.StringVar()
        self.regular_discount_var.set(str(existing_regular_discount))
        self.regular_discount_entry = ctk.CTkEntry(
            regular_frame,
            textvariable=self.regular_discount_var,
            font=ctk.CTkFont(family="Heebo", size=14),
            height=35,
            placeholder_text="0"
        )
        self.regular_discount_entry.pack(fill="x", pady=(5, 0))
        
        # Real-time validation for regular discount
        self.regular_discount_var.trace("w", self.validate_regular_discount)
        
        # Validation message for regular discount
        self.regular_discount_error = ctk.CTkLabel(
            regular_frame,
            text="",
            font=ctk.CTkFont(family="Heebo", size=12),
            text_color="#EF4444",
            anchor="e"
        )
        self.regular_discount_error.pack(anchor="e", pady=(2, 0))
        
        # Contractor discount (unlimited for all roles)
        contractor_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        contractor_frame.pack(fill="x", padx=15, pady=5)
        
        contractor_label = ctk.CTkLabel(
            contractor_frame,
            text="הנחת קבלן (₪) - ללא הגבלה",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        contractor_label.pack(anchor="e")
        
        # Contractor discount entry - Load existing value
        existing_contractor_discount = self.quote_data.get('contractor_discount', 0)
        self.contractor_discount_var = ctk.StringVar()
        self.contractor_discount_var.set(str(existing_contractor_discount))
        contractor_discount_entry = ctk.CTkEntry(
            contractor_frame,
            textvariable=self.contractor_discount_var,
            font=ctk.CTkFont(family="Heebo", size=14),
            height=35,
            placeholder_text="0"
        )
        contractor_discount_entry.pack(fill="x", pady=(5, 0))
        
        # VAT rate
        vat_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        vat_frame.pack(fill="x", padx=15, pady=5)
        
        vat_label = ctk.CTkLabel(
            vat_frame,
            text="מע״מ (%)",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        vat_label.pack(anchor="e")
        
        # VAT rate entry - Load existing value
        existing_vat_rate = self.quote_data.get('vat_rate', 17.0)
        self.vat_rate_var = ctk.StringVar()
        self.vat_rate_var.set(str(existing_vat_rate))
        vat_rate_entry = ctk.CTkEntry(
            vat_frame,
            textvariable=self.vat_rate_var,
            font=ctk.CTkFont(family="Heebo", size=14),
            height=35,
            placeholder_text="17.0"
        )
        vat_rate_entry.pack(fill="x", pady=(5, 0))
        
        # Real-time calculation
        self.regular_discount_var.trace("w", lambda *args: self.calculate_totals())
        self.contractor_discount_var.trace("w", lambda *args: self.calculate_totals())
        self.vat_rate_var.trace("w", lambda *args: self.calculate_totals())
        
        # Totals section
        totals_title = ctk.CTkLabel(
            right_frame,
            text="סיכום",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold")
        )
        totals_title.pack(pady=(30, 10))
        
        # Totals labels
        self.subtotal_label = ctk.CTkLabel(
            right_frame,
            text="סכום ביניים: ₪0.00",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        self.subtotal_label.pack(anchor="e", padx=15, pady=2)
        
        self.contractor_discount_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        self.contractor_discount_label.pack(anchor="e", padx=15, pady=2)
        
        self.discount_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        self.discount_label.pack(anchor="e", padx=15, pady=2)
        
        self.vat_label = ctk.CTkLabel(
            right_frame,
            text="מע״מ: ₪0.00",
            font=ctk.CTkFont(family="Heebo", size=14),
            anchor="e"
        )
        self.vat_label.pack(anchor="e", padx=15, pady=2)
        
        # Final total
        total_frame = ctk.CTkFrame(right_frame, fg_color="#F3F4F6")
        total_frame.pack(fill="x", padx=15, pady=10)
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="סה״כ לתשלום: ₪0.00",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            anchor="e"
        )
        self.total_label.pack(anchor="e", padx=15, pady=10)
        
        # Notes section
        notes_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        notes_frame.pack(fill="x", padx=15, pady=10)
        
        notes_label = ctk.CTkLabel(
            notes_frame,
            text="הערות",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            anchor="e"
        )
        notes_label.pack(anchor="e")
        
        # Notes textbox - Load existing value
        existing_notes = self.quote_data.get('notes', '')
        self.notes_textbox = ctk.CTkTextbox(
            notes_frame,
            font=ctk.CTkFont(family="Heebo", size=12),
            height=80
        )
        self.notes_textbox.pack(fill="x", pady=(5, 0))
        self.notes_textbox.insert("1.0", existing_notes)
        
        # Bind notes change
        self.notes_textbox.bind("<KeyRelease>", self.on_notes_change)
        
        # Calculate initial totals after setting up the UI
        self.calculate_totals()
    
    def validate_regular_discount(self, *args):
        """Validate regular discount against user permissions"""
        try:
            discount_text = self.regular_discount_var.get().strip()
            
            # Clear previous error
            if hasattr(self, 'regular_discount_error') and self.regular_discount_error:
                self.regular_discount_error.configure(text="")
            if hasattr(self, 'regular_discount_entry') and self.regular_discount_entry:
                self.regular_discount_entry.configure(border_color="gray")
            
            # Empty is valid (0 discount)
            if not discount_text:
                self.quote_data['regular_discount'] = 0.0
                self.calculate_totals()
                self.update_navigation_buttons()
                return
            
            # Try to parse as float
            try:
                discount_value = float(discount_text)
            except ValueError:
                if hasattr(self, 'regular_discount_error') and self.regular_discount_error:
                    self.regular_discount_error.configure(text="יש להזין מספר תקין")
                if hasattr(self, 'regular_discount_entry') and self.regular_discount_entry:
                    self.regular_discount_entry.configure(border_color="#EF4444")
                self.update_navigation_buttons()
                return
            
            # Check if negative
            if discount_value < 0:
                if hasattr(self, 'regular_discount_error') and self.regular_discount_error:
                    self.regular_discount_error.configure(text="ההנחה לא יכולה להיות שלילית")
                if hasattr(self, 'regular_discount_entry') and self.regular_discount_entry:
                    self.regular_discount_entry.configure(border_color="#EF4444")
                self.update_navigation_buttons()
                return
            
            # Check if exceeds 100%
            if discount_value > 100:
                if hasattr(self, 'regular_discount_error') and self.regular_discount_error:
                    self.regular_discount_error.configure(text="ההנחה לא יכולה לעלות על 100%")
                if hasattr(self, 'regular_discount_entry') and self.regular_discount_entry:
                    self.regular_discount_entry.configure(border_color="#EF4444")
                self.update_navigation_buttons()
                return
            
            # Check user permissions using PermissionManager
            is_valid, error_message = self.permission_manager.validate_discount_permission(self.current_user, discount_value)
            
            if not is_valid:
                if hasattr(self, 'regular_discount_error') and self.regular_discount_error:
                    self.regular_discount_error.configure(text=error_message)
                if hasattr(self, 'regular_discount_entry') and self.regular_discount_entry:
                    self.regular_discount_entry.configure(border_color="#EF4444")
                self.update_navigation_buttons()
                return
            
            # Valid discount
            self.quote_data['regular_discount'] = discount_value
            self.calculate_totals()
            self.update_navigation_buttons()
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error validating discount: {e}")
    
    def update_cart_summary(self):
        """Update cart summary display"""
        try:
            # Clear existing cart display
            if hasattr(self, 'cart_container') and self.cart_container:
                for widget in self.cart_container.winfo_children():
                    widget.destroy()
            
            if not self.selected_items:
                # Show empty cart message
                if hasattr(self, 'cart_container') and self.cart_container:
                    empty_label = ctk.CTkLabel(
                        self.cart_container,
                        text="הסל ריק",
                        font=ctk.CTkFont(family="Heebo", size=16),
                        text_color="gray"
                    )
                    empty_label.pack(pady=50)
                return
            
            # Display cart items
            for idx, item in enumerate(self.selected_items):
                if hasattr(self, 'cart_container') and self.cart_container:
                    self.create_cart_item_card(item, idx)
                    
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating cart summary: {e}")
    
    def create_cart_item_card(self, item, idx):
        """Create individual cart item card"""
        try:
            # Create item frame
            item_frame = ctk.CTkFrame(self.cart_container, fg_color="#FFFFFF", border_width=1, border_color="#E2E8F0")
            item_frame.pack(fill="x", padx=5, pady=5)
            
            # Item details
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=15, pady=10)
            
            # Item name
            name_label = ctk.CTkLabel(
                details_frame,
                text=item.get('שם מוצר', item.get('name', 'פריט')),
                font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
                anchor="e"
            )
            name_label.pack(anchor="e")
            
            # Item details row
            details_row = ctk.CTkFrame(details_frame, fg_color="transparent")
            details_row.pack(fill="x", pady=(5, 0))
            
            # Quantity
            qty_label = ctk.CTkLabel(
                details_row,
                text=f"כמות: {item.get('כמות', item.get('quantity', 1))}",
                font=ctk.CTkFont(family="Heebo", size=12),
                text_color="#6B7280"
            )
            qty_label.pack(side="right")
            
            # Price
            price = float(item.get('מחיר', item.get('price', 0)))
            qty = int(item.get('כמות', item.get('quantity', 1)))
            total = price * qty
            
            price_label = ctk.CTkLabel(
                details_row,
                text=f"מחיר: ₪{price:,.2f}",
                font=ctk.CTkFont(family="Heebo", size=12),
                text_color="#6B7280"
            )
            price_label.pack(side="right", padx=(10, 0))
            
            # Total
            total_label = ctk.CTkLabel(
                details_row,
                text=f"סה״כ: ₪{total:,.2f}",
                font=ctk.CTkFont(family="Heebo", size=12, weight="bold"),
                text_color="#1F2937"
            )
            total_label.pack(side="left")
            
            # Remove button
            remove_button = ctk.CTkButton(
                details_frame,
                text="הסר",
                font=ctk.CTkFont(family="Heebo", size=11),
                height=25,
                width=60,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda i=idx: self.remove_from_cart(i)
            )
            remove_button.pack(anchor="e", pady=(5, 0))
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error creating cart item card: {e}")
    
    def calculate_totals(self):
        """Calculate and display totals with correct order: Subtotal → Contractor Discount → Regular Discount → VAT"""
        try:
            # If we're in the middle of editing setup, don't overwrite values
            editing_flag = getattr(self, '_editing_quote', False)
            if editing_flag:
                return
            
            # Get values with safe defaults - use quote_data values if StringVars don't exist yet
            regular_discount = self.quote_data.get('regular_discount', 0.0)
            contractor_discount = self.quote_data.get('contractor_discount', 0.0)
            vat_rate = self.quote_data.get('vat_rate', 17.0)
            
            # Safely get values from variables if they exist (override quote_data values)
            if hasattr(self, 'regular_discount_var') and self.regular_discount_var:
                try:
                    regular_discount = float(self.regular_discount_var.get() or 0)
                except (ValueError, AttributeError):
                    regular_discount = self.quote_data.get('regular_discount', 0.0)
            
            if hasattr(self, 'contractor_discount_var') and self.contractor_discount_var:
                try:
                    contractor_discount = float(self.contractor_discount_var.get() or 0)
                except (ValueError, AttributeError):
                    contractor_discount = self.quote_data.get('contractor_discount', 0.0)
            
            if hasattr(self, 'vat_rate_var') and self.vat_rate_var:
                try:
                    vat_rate = float(self.vat_rate_var.get() or 17)
                except (ValueError, AttributeError):
                    vat_rate = self.quote_data.get('vat_rate', 17.0)
            
            # Calculate subtotal from selected items
            subtotal = 0.0
            if self.selected_items:
                subtotal = sum(
                    float(item.get('מחיר', item.get('price', 0))) * 
                    int(item.get('כמות', item.get('quantity', 1))) 
                    for item in self.selected_items
                )
            
            # Step 1: Subtract contractor discount from subtotal (fixed amount)
            contractor_discount_amount = contractor_discount  # Fixed amount, not percentage
            after_contractor = subtotal - contractor_discount_amount
            after_contractor = max(0, after_contractor)  # Can't go below 0
            
            # Step 2: Apply regular discount percentage to the amount after contractor discount
            regular_discount_amount = after_contractor * (regular_discount / 100)
            after_regular = after_contractor - regular_discount_amount
            
            # Step 3: Apply VAT to final amount
            vat_amount = after_regular * (vat_rate / 100)
            final_total = after_regular + vat_amount
            
            # Store in quote data with all the fields the PDF generator expects
            self.quote_data.update({
                'regular_discount': regular_discount,
                'contractor_discount': contractor_discount,
                'vat_rate': vat_rate,
                'subtotal': subtotal,
                'contractor_discount_amount': contractor_discount_amount,
                'regular_discount_amount': regular_discount_amount,
                'discount_amount': regular_discount_amount,  # For PDF compatibility
                'discount_val': regular_discount_amount,  # For PDF compatibility
                'contractor_discount_val': contractor_discount_amount,  # For PDF compatibility
                'vat_amount': vat_amount,
                'total_amount': final_total,
                'final_total': final_total  # For PDF compatibility
            })
            
            # Update display using the new label system
            self.update_totals_display(subtotal, contractor_discount_amount, regular_discount_amount, vat_amount, final_total)
            
            print(f"Calculated totals: subtotal={subtotal}, contractor_discount={contractor_discount_amount}, regular_discount={regular_discount_amount}, final_total={final_total}")
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error in calculate_totals: {e}")
            # Set default values if calculation fails
            self.quote_data.update({
                'subtotal': 0.0,
                'total_amount': 0.0,
                'regular_discount': 0.0,
                'contractor_discount': 0.0,
                'vat_rate': 17.0,
                'discount_amount': 0.0,
                'discount_val': 0.0,
                'contractor_discount_amount': 0.0,
                'contractor_discount_val': 0.0,
                'vat_amount': 0.0,
                'final_total': 0.0
            })
    
    def update_totals_display(self, subtotal, contractor_discount, regular_discount_amount, vat_amount, final_total):
        """Update totals display using the label system"""
        try:
            # Update the labels if they exist
            if hasattr(self, 'subtotal_label') and self.subtotal_label:
                self.subtotal_label.configure(text=f"סכום ביניים: ₪{subtotal:,.2f}")
            
            if hasattr(self, 'contractor_discount_label') and self.contractor_discount_label:
                if contractor_discount > 0:
                    self.contractor_discount_label.configure(
                        text=f"הנחת קבלן: -₪{contractor_discount:,.2f}",
                        text_color="#F59E0B"
                    )
                else:
                    self.contractor_discount_label.configure(text="")
            
            if hasattr(self, 'discount_label') and self.discount_label:
                if regular_discount_amount > 0:
                    self.discount_label.configure(
                        text=f"הנחה כללית: -₪{regular_discount_amount:,.2f}",
                        text_color="#F59E0B"
                    )
                else:
                    self.discount_label.configure(text="")
            
            if hasattr(self, 'vat_label') and self.vat_label:
                self.vat_label.configure(text=f"מע״מ: ₪{vat_amount:,.2f}")
            
            if hasattr(self, 'total_label') and self.total_label:
                self.total_label.configure(text=f"סה״כ לתשלום: ₪{final_total:,.2f}")
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating totals display: {e}")
    
    def on_notes_change(self, event=None):
        """Handle notes text changes"""
        try:
            content = self.notes_textbox.get("1.0", "end-1c")
            self.quote_data['notes'] = content
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating notes: {e}")
    
    def show_summary(self):
        """Show summary step with modern white design"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Main container with modern styling
        main_container = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title with modern styling
        title_label = ctk.CTkLabel(
            main_container,
            text="שלב 4: סיכום ושמירה",
            font=ctk.CTkFont(family="Heebo", size=26, weight="bold"),
            text_color="#1F2937"
        )
        title_label.pack(pady=(25, 35))
        
        # Customer summary with modern card design
        customer = self.quote_data['customer_data']
        if customer:
            customer_frame = ctk.CTkFrame(
                main_container, 
                fg_color="#F8FAFC", 
                border_width=1, 
                border_color="#E2E8F0",
                corner_radius=15
            )
            customer_frame.pack(fill="x", padx=25, pady=(0, 20))
            
            customer_title = ctk.CTkLabel(
                customer_frame,
                text="פרטי לקוח",
                font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
                text_color="#1F2937"
            )
            customer_title.pack(pady=(20, 15))
            
            customer_info = f"שם: {customer['name']}\nטלפון: {customer['phone']}\nדואל: {customer['email']}\nכתובת: {customer['address']}"
            customer_details = ctk.CTkLabel(
                customer_frame,
                text=customer_info,
                font=ctk.CTkFont(family="Heebo", size=15, weight="normal"),
                text_color="#374151",
                justify="right"
            )
            customer_details.pack(padx=25, pady=(0, 20))
        
        # Quote summary with modern card design
        quote_summary_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#F8FAFC", 
            border_width=1, 
            border_color="#E2E8F0",
            corner_radius=15
        )
        quote_summary_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        quote_title = ctk.CTkLabel(
            quote_summary_frame,
            text="סיכום הצעת המחיר",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            text_color="#1F2937"
        )
        quote_title.pack(pady=(20, 15))
        
        # Final total display with modern styling
        # Recalculate totals to ensure we have the latest values
        self.calculate_totals()
        
        total_display = ctk.CTkLabel(
            quote_summary_frame,
            text=f"סה״כ לתשלום: ₪{self.quote_data.get('total_amount', 0):,.0f}",
            font=ctk.CTkFont(family="Heebo", size=28, weight="bold"),
            text_color="#059669",
            fg_color="#ECFDF5",
            corner_radius=15,
            height=70
        )
        total_display.pack(pady=25, padx=25, fill="x")
        
        # Optional notes with modern styling
        notes_frame = ctk.CTkFrame(quote_summary_frame, fg_color="transparent")
        notes_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        notes_label = ctk.CTkLabel(
            notes_frame,
            text="הערות (אופציונלי):",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        notes_label.pack(anchor="e", pady=(0, 10))
        
        self.notes_textbox = ctk.CTkTextbox(
            notes_frame,
            height=100,
            font=ctk.CTkFont(family="Heebo", size=14, weight="normal"),
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=10
        )
        self.notes_textbox.pack(fill="x")
        
        # Load existing notes
        if self.quote_data.get('notes'):
            self.notes_textbox.insert("1.0", self.quote_data['notes'])
        
        # Image upload section with modern styling
        images_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#F8FAFC", 
            border_width=1, 
            border_color="#E2E8F0",
            corner_radius=15
        )
        images_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        images_title = ctk.CTkLabel(
            images_frame,
            text="תמונות להצעה (עד 2 תמונות)",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            text_color="#1F2937"
        )
        images_title.pack(pady=(20, 15))
        
        # Image upload container with modern styling
        images_container = ctk.CTkFrame(images_frame, fg_color="transparent")
        images_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Initialize images list if not exists
        if 'images' not in self.quote_data:
            self.quote_data['images'] = []
        
        # Image 1 with modern card styling
        img1_frame = ctk.CTkFrame(
            images_container, 
            fg_color="#FFFFFF", 
            border_width=1, 
            border_color="#D1D5DB",
            corner_radius=12
        )
        img1_frame.pack(side="right", fill="x", expand=True, padx=(0, 10))
        
        img1_label = ctk.CTkLabel(
            img1_frame,
            text="תמונה 1:",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        img1_label.pack(anchor="e", pady=(15, 8))
        
        self.img1_path_label = ctk.CTkLabel(
            img1_frame,
            text="לא נבחרה תמונה",
            font=ctk.CTkFont(family="Heebo", size=13, weight="normal"),
            text_color="#6B7280",
            anchor="e"
        )
        self.img1_path_label.pack(anchor="e", pady=(0, 10))
        
        img1_buttons = ctk.CTkFrame(img1_frame, fg_color="transparent")
        img1_buttons.pack(fill="x", pady=(0, 15))
        
        img1_select_btn = ctk.CTkButton(
            img1_buttons,
            text="בחר תמונה",
            font=ctk.CTkFont(family="Heebo", size=13, weight="bold"),
            height=35,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=8,
            command=lambda: self.select_image(1)
        )
        img1_select_btn.pack(side="right", padx=(0, 8))
        
        self.img1_remove_btn = ctk.CTkButton(
            img1_buttons,
            text="הסר",
            font=ctk.CTkFont(family="Heebo", size=13, weight="bold"),
            height=35,
            width=70,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=8,
            command=lambda: self.remove_image(1),
            state="disabled"
        )
        self.img1_remove_btn.pack(side="right")
        
        # Image 2 with modern card styling
        img2_frame = ctk.CTkFrame(
            images_container, 
            fg_color="#FFFFFF", 
            border_width=1, 
            border_color="#D1D5DB",
            corner_radius=12
        )
        img2_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        img2_label = ctk.CTkLabel(
            img2_frame,
            text="תמונה 2:",
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        img2_label.pack(anchor="e", pady=(15, 8))
        
        self.img2_path_label = ctk.CTkLabel(
            img2_frame,
            text="לא נבחרה תמונה",
            font=ctk.CTkFont(family="Heebo", size=13, weight="normal"),
            text_color="#6B7280",
            anchor="e"
        )
        self.img2_path_label.pack(anchor="e", pady=(0, 10))
        
        img2_buttons = ctk.CTkFrame(img2_frame, fg_color="transparent")
        img2_buttons.pack(fill="x", pady=(0, 15))
        
        img2_select_btn = ctk.CTkButton(
            img2_buttons,
            text="בחר תמונה",
            font=ctk.CTkFont(family="Heebo", size=13, weight="bold"),
            height=35,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=8,
            command=lambda: self.select_image(2)
        )
        img2_select_btn.pack(side="right", padx=(0, 8))
        
        self.img2_remove_btn = ctk.CTkButton(
            img2_buttons,
            text="הסר",
            font=ctk.CTkFont(family="Heebo", size=13, weight="bold"),
            height=35,
            width=70,
            fg_color="#EF4444",
            hover_color="#DC2626",
            corner_radius=8,
            command=lambda: self.remove_image(2),
            state="disabled"
        )
        self.img2_remove_btn.pack(side="right")
        
        # Load existing images
        self.update_image_labels()
    
    def next_step(self):
        """Move to next step or finish"""
        if self.current_step < self.max_steps:
            # Save current step data
            self.save_step_data()
            self.current_step += 1
            self.show_step()
        else:
            # Finish wizard
            self.finish_wizard()
    
    def prev_step(self):
        """Move to previous step"""
        if self.current_step > 1:
            self.save_step_data()
            self.current_step -= 1
            self.show_step()
    
    def save_step_data(self):
        """Save current step data"""
        try:
            # Always update quote_data from UI variables if they exist
            regular_discount = 0.0
            contractor_discount = 0.0
            vat_rate = 17.0
            if hasattr(self, 'regular_discount_var') and self.regular_discount_var:
                try:
                    regular_discount = float(self.regular_discount_var.get() or 0)
                except (ValueError, AttributeError):
                    regular_discount = 0.0
            if hasattr(self, 'contractor_discount_var') and self.contractor_discount_var:
                try:
                    contractor_discount = float(self.contractor_discount_var.get() or 0)
                except (ValueError, AttributeError):
                    contractor_discount = 0.0
            if hasattr(self, 'vat_rate_var') and self.vat_rate_var:
                try:
                    vat_rate = float(self.vat_rate_var.get() or 17)
                except (ValueError, AttributeError):
                    vat_rate = 17.0
            self.quote_data.update({
                'regular_discount': regular_discount,
                'contractor_discount': contractor_discount,
                'vat_rate': vat_rate
            })
            # Recalculate totals
            self.calculate_totals()
            # Save notes if on summary step
            if self.current_step == 4 and hasattr(self, 'notes_textbox'):
                self.quote_data['notes'] = self.notes_textbox.get("1.0", "end-1c")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error saving step data: {e}")
    
    def finish_wizard(self):
        """Finish wizard and create active quote (not draft)"""
        try:
            self.save_step_data()
            if not self.quote_data.get('customer_id'):
                messagebox.showerror("שגיאה", "יש לבחור לקוח")
                return
            if not self.selected_items:
                messagebox.showerror("שגיאה", "יש לבחור לפחות פריט אחד")
                return
            # Enforce permission check right before saving
            regular_discount = self.quote_data.get('regular_discount', 0)
            user_max_discount = self.current_user.get('max_discount', 0.0)
            user_role = self.current_user.get('role', 'viewer')
            has_unlimited_discount = user_role in ['admin', 'manager']
            if not has_unlimited_discount and regular_discount > user_max_discount:
                messagebox.showerror(
                    "שגיאה בהרשאות", 
                    f"אין לך הרשאה ליצור או לערוך הצעת מחיר עם הנחה של {regular_discount}%.\n"
                    f"ההנחה המקסימלית המותרת לך היא {user_max_discount}%."
                )
                return
            
            # Prepare items for database with both key sets
            db_items = []
            for item in self.selected_items:
                db_items.append({
                    'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
                    'name': item.get('שם מוצר', item.get('name', 'פריט')),
                    'קטגוריה': item.get('קטגוריה', item.get('category', '')),
                    'category': item.get('קטגוריה', item.get('category', '')),
                    'כמות': item.get('כמות', item.get('quantity', 1)),
                    'quantity': item.get('כמות', item.get('quantity', 1)),
                    'מחיר': item.get('מחיר', item.get('price', 0)),
                    'price': item.get('מחיר', item.get('price', 0)),
                    'תיאור': item.get('תיאור', item.get('description', '')),
                    'description': item.get('תיאור', item.get('description', '')),
                    'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
                    'unit': item.get('יחידה', item.get('unit', 'יח׳'))
                })
            quote_id_existing = self.quote_data.get('quote_id')
            if quote_id_existing:
                try:
                    success = self.db_manager.update_quote(
                        quote_id_existing,
                        items=db_items,
                        regular_discount=self.quote_data.get('regular_discount', 0),
                        contractor_discount=self.quote_data.get('contractor_discount', 0),
                        vat_rate=self.quote_data.get('vat_rate', 17),
                        subtotal=self.quote_data.get('subtotal', 0),
                        total_amount=self.quote_data.get('total_amount', 0),
                        notes=self.quote_data.get('notes', ''),
                        images=self.quote_data.get('images', []),
                        acting_user_id=self.current_user['id']
                    )
                    if not success:
                        messagebox.showerror("שגיאה", "אין לך הרשאה לערוך את ההצעה או שהעריכה נכשלה")
                        return
                    # Get the updated quote data
                    quote = self.db_manager.get_quote_by_id(quote_id_existing)
                    if not quote:
                        messagebox.showerror("שגיאה", "שגיאה בטעינת הצעת המחיר המעודכנת")
                        return
                except ValueError as ve:
                    messagebox.showerror("שגיאה בהרשאות", str(ve))
                    return
            else:
                try:
                    quote = self.db_manager.create_quote(
                        customer_id=self.quote_data['customer_id'],
                        items=db_items,
                        created_by=self.current_user['id'],
                        regular_discount=self.quote_data.get('regular_discount', 0),
                        contractor_discount=self.quote_data.get('contractor_discount', 0),
                        vat_rate=self.quote_data.get('vat_rate', 17),
                        subtotal=self.quote_data.get('subtotal', 0),
                        total_amount=self.quote_data.get('total_amount', 0),
                        notes=self.quote_data.get('notes', ''),
                        images=self.quote_data.get('images', [])
                    )
                except ValueError as ve:
                    messagebox.showerror("שגיאה בהרשאות", str(ve))
                    return
            if quote:
                # Delete the draft if this was created from a draft
                if hasattr(self, 'draft_id') and self.draft_id:
                    try:
                        self.db_manager.delete_draft_by_id(self.draft_id)
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Error deleting draft: {e}")
                
                if quote_id_existing:
                    msg = f"הצעת מחיר #{quote['quote_number']} עודכנה בהצלחה!"
                else:
                    msg = f"הצעת מחיר #{quote['quote_number']} נוצרה בהצלחה!"
                messagebox.showinfo("הצלחה!", msg)
                
                # Call success callback to refresh quotes list
                if self.on_success:
                    self.on_success()
                
                # Close wizard
                if self.dialog:
                    self.dialog.destroy()
            else:
                messagebox.showerror("שגיאה", "שגיאה ביצירת הצעת המחיר")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה ביצירת הצעת המחיר: {e}")
    
    def save_draft(self):
        """Save current state as draft"""
        try:
            # Save current step data to ensure UI values are captured
            self.save_step_data()
            
            # Check permissions before saving draft
            regular_discount = self.quote_data.get('regular_discount', 0)
            user_max_discount = self.current_user.get('max_discount', 0.0)
            user_role = self.current_user.get('role', 'viewer')
            has_unlimited_discount = user_role in ['admin', 'manager']
            
            if not has_unlimited_discount and regular_discount > user_max_discount:
                messagebox.showerror(
                    "שגיאה בהרשאות", 
                    f"אין לך הרשאה לשמור טיוטה עם הנחה של {regular_discount}%.\n"
                    f"ההנחה המקסימלית המותרת לך היא {user_max_discount}%."
                )
                return
            
            # Prepare draft state with consistent item format
            draft_items = []
            for item in self.selected_items:
                draft_items.append({
                    '\u05e9\u05dd \u05de\u05d5\u05e6\u05e8': item.get('\u05e9\u05dd \u05de\u05d5\u05e6\u05e8', item.get('name', '\u05e4\u05e8\u05d9\u05d8')),
                    'name': item.get('\u05e9\u05dd \u05de\u05d5\u05e6\u05e8', item.get('name', '\u05e4\u05e8\u05d9\u05d8')),
                    '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4': item.get('\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4', item.get('category', '')),
                    'category': item.get('\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4', item.get('category', '')),
                    '\u05db\u05de\u05d5\u05ea': item.get('\u05db\u05de\u05d5\u05ea', item.get('quantity', 1)),
                    'quantity': item.get('\u05db\u05de\u05d5\u05ea', item.get('quantity', 1)),
                    '\u05de\u05d7\u05d9\u05e8': item.get('\u05de\u05d7\u05d9\u05e8', item.get('price', 0)),
                    'price': item.get('\u05de\u05d7\u05d9\u05e8', item.get('price', 0)),
                    '\u05ea\u05d9\u05d0\u05d5\u05e8': item.get('\u05ea\u05d9\u05d0\u05d5\u05e8', item.get('description', '')),
                    'description': item.get('\u05ea\u05d9\u05d0\u05d5\u05e8', item.get('description', '')),
                    '\u05d9\u05d7\u05d9\u05d3\u05d4': item.get('\u05d9\u05d7\u05d9\u05d3\u05d4', item.get('unit', '\u05d9\u05d7\u05f3')),
                    'unit': item.get('\u05d9\u05d7\u05d9\u05d3\u05d4', item.get('unit', '\u05d9\u05d7\u05f3'))
                })
            # Ensure all values in quote_data are serializable
            serializable_quote_data = {}
            for k, v in self.quote_data.items():
                if isinstance(v, (datetime)):
                    serializable_quote_data[k] = v.isoformat()
                else:
                    serializable_quote_data[k] = v
            draft_state = {
                'step': self.current_step,
                'quote_data': serializable_quote_data,
                'selected_items': draft_items,
                'current_step': self.current_step
            }
            # Save draft to DB
            self.db_manager.save_draft(
                state=draft_state,
                created_by=self.current_user['id'],
                customer_id=self.quote_data.get('customer_id'),
                step=self.current_step
            )
            self.logger.info(f"Draft saved at step {self.current_step} with {len(self.selected_items)} items")
            
            # Show success message
            messagebox.showinfo("הצלחה", "הטיוטה נשמרה בהצלחה!")
        except Exception as e:
            self.logger.error(f"Error saving draft: {e}")
            messagebox.showerror("שגיאה", f"שגיאה בשמירת הטיוטה: {e}")
    
    def setup_auto_save(self):
        """Auto-save disabled - only manual draft saving"""
        pass
    
    def load_from_draft(self, draft):
        """Load wizard state from existing draft"""
        try:
            if isinstance(draft, dict):
                draft_state = draft.get('draft_data', {})
                self.current_step = draft.get('step', 1)
            else:
                draft_state = draft.state if hasattr(draft, 'state') else {}
                self.current_step = draft.step if hasattr(draft, 'step') else 1
            if isinstance(draft_state, str):
                import json
                draft_state = json.loads(draft_state)
            if 'quote_data' in draft_state:
                self.quote_data.update(draft_state['quote_data'])
            if 'selected_items' in draft_state:
                # Ensure all items have both key sets
                self.selected_items = []
                for item in draft_state['selected_items']:
                    formatted_item = {
                        'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
                        'name': item.get('שם מוצר', item.get('name', 'פריט')),
                        'קטגוריה': item.get('קטגוריה', item.get('category', '')),
                        'category': item.get('קטגוריה', item.get('category', '')),
                        'כמות': item.get('כמות', item.get('quantity', 1)),
                        'quantity': item.get('כמות', item.get('quantity', 1)),
                        'מחיר': item.get('מחיר', item.get('price', 0)),
                        'price': item.get('מחיר', item.get('price', 0)),
                        'תיאור': item.get('תיאור', item.get('description', '')),
                        'description': item.get('תיאור', item.get('description', '')),
                        'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
                        'unit': item.get('יחידה', item.get('unit', 'יח׳'))
                    }
                    self.selected_items.append(formatted_item)
            if 'current_step' in draft_state:
                self.current_step = draft_state['current_step']
            self.logger.info(f"Loaded draft at step {self.current_step} with {len(self.selected_items)} items")
        except Exception as e:
            self.logger.error(f"Error loading draft: {e}")
            self.current_step = 1
            self.selected_items = []
    
    def cancel_wizard(self):
        """Cancel wizard with option to save as draft"""
        # Check if there's any meaningful progress to save
        has_progress = (
            self.quote_data.get('customer_id') or 
            len(self.selected_items) > 0 or
            self.quote_data.get('regular_discount', 0) > 0 or
            self.quote_data.get('contractor_discount', 0) > 0 or
            self.quote_data.get('notes', '').strip()
        )
        
        if has_progress:
            # Ask user if they want to save as draft
            result = messagebox.askyesnocancel(
                "שמירת טיוטה",
                "האם ברצונך לשמור את ההתקדמות כטיוטה?\n\n"
                "כן - שמור כטיוטה\n"
                "לא - צא ללא שמירה\n"
                "ביטול - המשך לעבוד",
                icon="question"
            )
            
            if result is None:  # Cancel - stay in wizard
                return
            elif result:  # Yes - save as draft
                self.save_draft()
            # If No (False) - just close without saving
        
        # Close wizard
        if self.dialog:
            self.dialog.destroy()
    
    def edit_existing_quote(self, quote_data):
        """Load wizard for editing an existing quote"""
        try:
            # Check if user has permission to edit this quote with its current discounts
            existing_regular_discount = quote_data.get('regular_discount', 0)
            user_max_discount = self.current_user.get('max_discount', 0.0)
            user_role = self.current_user.get('role', 'viewer')
            has_unlimited_discount = user_role in ['admin', 'manager']
            
            if not has_unlimited_discount and existing_regular_discount > user_max_discount:
                from tkinter import messagebox
                messagebox.showerror(
                    "שגיאה בהרשאות", 
                    f"אין לך הרשאה לערוך הצעת מחיר עם הנחה של {existing_regular_discount}%.\n"
                    f"ההנחה המקסימלית המותרת לך היא {user_max_discount}%."
                )
                return
            
            # Set a flag to prevent calculate_totals from overwriting values during UI creation
            self._editing_quote = True
            
            # Populate quote data
            self.quote_data.update({
                'customer_id': quote_data.get('customer_id'),
                'customer_data': None,  # Will be loaded in customer selection step
                'regular_discount': quote_data.get('regular_discount', 0),
                'contractor_discount': quote_data.get('contractor_discount', 0),
                'vat_rate': quote_data.get('vat_rate', 17),
                'notes': quote_data.get('notes', ''),
                'images': quote_data.get('images', []),
                'quote_id': quote_data.get('id')  # Store original quote ID for updating
            })

            
            # Convert items to expected format with both key sets
            items = quote_data.get('items', [])
            if isinstance(items, str):
                import json
                items = json.loads(items)
            self.selected_items = []
            for item in items:
                formatted_item = {
                    'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
                    'name': item.get('שם מוצר', item.get('name', 'פריט')),
                    'קטגוריה': item.get('קטגוריה', item.get('category', '')),
                    'category': item.get('קטגוריה', item.get('category', '')),
                    'כמות': item.get('כמות', item.get('quantity', 1)),
                    'quantity': item.get('כמות', item.get('quantity', 1)),
                    'מחיר': item.get('מחיר', item.get('price', 0)),
                    'price': item.get('מחיר', item.get('price', 0)),
                    'תיאור': item.get('תיאור', item.get('description', '')),
                    'description': item.get('תיאור', item.get('description', '')),
                    'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
                    'unit': item.get('יחידה', item.get('unit', 'יח׳'))
                }
                self.selected_items.append(formatted_item)
            
            # Set current step to 3 (pricing/discounts) and show it
            self.current_step = 3
            
            # Load customer data for the quote
            try:
                customer = self.db_manager.get_customer_by_id(quote_data.get('customer_id'))
                if customer:
                    # Convert datetime objects to strings for JSON serialization
                    customer_data = customer.copy()
                    for key, value in customer_data.items():
                        if hasattr(value, 'isoformat'):  # Check if it's a datetime
                            customer_data[key] = value.isoformat()
                    
                    self.quote_data['customer_data'] = customer_data
            except Exception as e:
                pass
            
            # Show the correct step (step 3)
            self.show_step()
            
            # Clear the flag after UI is created
            self.dialog.after(100, self._finish_edit_setup)
            

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("שגיאה", f"שגיאה בטעינת הצעת המחיר לעריכה: {e}")
            self.current_step = 1
    
    def _finish_edit_setup(self):
        """Finish the edit setup after UI is created"""
        try:
            # Explicitly set the StringVars if they exist
            if hasattr(self, 'regular_discount_var'):
                self.regular_discount_var.set(str(self.quote_data.get('regular_discount', 0)))
            if hasattr(self, 'contractor_discount_var'):
                self.contractor_discount_var.set(str(self.quote_data.get('contractor_discount', 0)))
            if hasattr(self, 'vat_rate_var'):
                self.vat_rate_var.set(str(self.quote_data.get('vat_rate', 17)))
            
            # Clear the editing flag
            self._editing_quote = False
            
            # Now calculate totals with the correct values
            self.calculate_totals()
            
        except Exception as e:
            self._editing_quote = False
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.selected_items:
            from tkinter import messagebox
            result = messagebox.askyesno(
                "נקה סל",
                "האם אתה בטוח שברצונך לנקות את הסל?\nכל הפריטים יוסרו.",
                icon="warning"
            )
            if result:
                self.selected_items.clear()
                self.update_cart()
                self.update_navigation_buttons()

    def select_image(self, image_number):
        """Select an image for the quote"""
        from tkinter import filedialog
        
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        image_path = filedialog.askopenfilename(
            title=f"בחר תמונה {image_number} להצעה",
            filetypes=filetypes
        )
        
        if image_path:
            # Ensure images list exists and has correct size
            while len(self.quote_data['images']) < image_number:
                self.quote_data['images'].append(None)
            
            # Set the specific image
            self.quote_data['images'][image_number - 1] = image_path
            self.update_image_labels()

    def remove_image(self, image_number):
        """Remove an image from the quote"""
        if len(self.quote_data['images']) >= image_number:
            self.quote_data['images'][image_number - 1] = None
            self.update_image_labels()

    def update_image_labels(self):
        """Update the image path labels"""
        # Update image 1
        if hasattr(self, 'img1_path_label'):
            if len(self.quote_data['images']) > 0 and self.quote_data['images'][0]:
                import os
                filename = os.path.basename(self.quote_data['images'][0])
                self.img1_path_label.configure(text=filename, text_color="green")
                self.img1_remove_btn.configure(state="normal")
            else:
                self.img1_path_label.configure(text="לא נבחרה תמונה", text_color="gray")
                self.img1_remove_btn.configure(state="disabled")
        
        # Update image 2
        if hasattr(self, 'img2_path_label'):
            if len(self.quote_data['images']) > 1 and self.quote_data['images'][1]:
                import os
                filename = os.path.basename(self.quote_data['images'][1])
                self.img2_path_label.configure(text=filename, text_color="green")
                self.img2_remove_btn.configure(state="normal")
            else:
                self.img2_path_label.configure(text="לא נבחרה תמונה", text_color="gray")
                self.img2_remove_btn.configure(state="disabled") 