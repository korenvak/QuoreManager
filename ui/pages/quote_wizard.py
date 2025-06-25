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
        """Create wizard dialog with professional modern design and responsive layout"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("אשף יצירת הצעת מחיר - QuoreManager")
        
        # Initialize theme system for professional styling
        from styling.theme_system import ModernThemeManager
        from config.settings import SettingsManager
        settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
        # Advanced responsive sizing - works on all desktop sizes
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Professional responsive calculation
        # Use 85% of screen size with smart min/max limits based on screen size
        if screen_width >= 1920:  # 4K/Large monitors
            window_width = min(1600, int(screen_width * 0.8))
            window_height = min(1000, int(screen_height * 0.85))
        elif screen_width >= 1440:  # Standard large monitors
            window_width = min(1400, int(screen_width * 0.85))
            window_height = min(900, int(screen_height * 0.85))
        elif screen_width >= 1280:  # Standard monitors
            window_width = min(1200, int(screen_width * 0.9))
            window_height = min(800, int(screen_height * 0.85))
        else:  # Small monitors/laptops
            window_width = min(1000, int(screen_width * 0.95))
            window_height = min(700, int(screen_height * 0.9))
        
        # Ensure minimum usability sizes regardless of screen
        window_width = max(900, window_width)
        window_height = max(650, window_height)
        
        self.dialog.geometry(f"{window_width}x{window_height}")
        self.dialog.resizable(True, True)
        self.dialog.minsize(900, 650)  # Professional minimum size
        
        # Perfect centering on any monitor
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Professional window properties
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.attributes('-topmost', True)  # Ensure visibility
        self.dialog.focus_force()
        
        # Professional theme colors
        self.dialog.configure(fg_color=self.theme['bg_primary'])
        
        # Professional main container with modern styling
        self.main_scrollable_frame = ctk.CTkScrollableFrame(
            self.dialog,
            fg_color=self.theme['bg_secondary'],
            corner_radius=0,
            scrollbar_button_color=self.theme['primary_light'],
            scrollbar_button_hover_color=self.theme['primary']
        )
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Modern progress section with professional card design
        self.progress_frame = self.theme_manager.create_modern_card(
            self.main_scrollable_frame,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        self.progress_frame.pack(fill="x", padx=self.theme_manager.get_spacing('lg'), pady=(self.theme_manager.get_spacing('lg'), 0))
        
        # Professional content area with modern card styling
        self.content_frame = self.theme_manager.create_modern_card(
            self.main_scrollable_frame,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        self.content_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('lg'))
        
        # Professional navigation with modern styling - fixed at bottom
        self.create_navigation(self.dialog)
        
        # Show first step with modern progress
        self.show_step()
        
        # Professional window icon
        try:
            icon_path = self.theme_manager.get_icon_path()
            self.dialog.iconbitmap(icon_path)
        except:
            pass  # Fallback gracefully if icon not found
    
    def create_progress_bar(self):
        """Update progress bar with modern professional design"""
        # Clear existing progress
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        # Professional progress container
        progress_container = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        progress_container.pack(pady=self.theme_manager.get_spacing('lg'))
        
        # Modern step names with Hebrew text
        step_names = ["בחירת לקוח", "בחירת פריטים", "הנחות ומחירים", "סיכום ושמירה"]
        
        # Professional step indicators layout
        steps_layout = ctk.CTkFrame(progress_container, fg_color="transparent")
        steps_layout.pack()
        
        for i, step_name in enumerate(step_names, 1):
            step_container = ctk.CTkFrame(steps_layout, fg_color="transparent")
            step_container.pack(side="right", padx=self.theme_manager.get_spacing('lg'))
            
            # Professional step states with theme colors
            is_current = i == self.current_step
            is_completed = i < self.current_step
            
            if is_current:
                circle_color = self.theme['primary']
                text_color = self.theme['bg_primary']
                name_color = self.theme['text_primary']
                weight = "bold"
            elif is_completed:
                circle_color = self.theme['primary_dark']
                text_color = self.theme['bg_primary']
                name_color = self.theme['text_secondary']
                weight = "normal"
            else:
                circle_color = self.theme['border']
                text_color = self.theme['text_muted']
                name_color = self.theme['text_muted']
                weight = "normal"
            
            # Modern step circle with professional styling
            step_circle = ctk.CTkLabel(
                step_container,
                text=str(i),
                width=50,
                height=50,
                font=self.theme_manager.create_ctk_font('card_title'),
                fg_color=circle_color,
                text_color=text_color,
                corner_radius=25
            )
            step_circle.pack()
            
            # Professional step name with proper typography
            name_label = ctk.CTkLabel(
                step_container,
                text=step_name,
                font=ctk.CTkFont(family="Assistant", size=13, weight=weight),
                text_color=name_color
            )
            name_label.pack(pady=(self.theme_manager.get_spacing('sm'), 0))
    
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
        """Create professional navigation with modern button styling"""
        # Professional fixed navigation frame at the bottom
        nav_container = ctk.CTkFrame(parent, fg_color="transparent", height=90)
        nav_container.pack(side="bottom", fill="x", padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('md'))
        nav_container.pack_propagate(False)
        
        # Modern navigation card with professional styling
        nav_frame = self.theme_manager.create_modern_card(
            nav_container,
            fg_color=self.theme['bg_card'],
            corner_radius=12,
            border_color=self.theme['border_light']
        )
        nav_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('sm'), pady=self.theme_manager.get_spacing('xs'))
        
        # Professional button container
        button_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Professional Cancel button
        cancel_button = self.theme_manager.create_modern_button(
            button_frame,
            text="ביטול",
            style="outline",
            size="medium",
            width=100,
            command=self.cancel_wizard
        )
        cancel_button.pack(side="left")
        
        # Professional Save Draft button
        save_draft_button = self.theme_manager.create_modern_button(
            button_frame,
            text="שמור כטיוטה",
            style="secondary",
            size="medium",
            width=130,
            command=self.save_draft
        )
        save_draft_button.pack(side="left", padx=(self.theme_manager.get_spacing('sm'), 0))
        
        # Professional step info in center
        step_info_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        step_info_frame.pack(side="left", fill="x", expand=True, padx=self.theme_manager.get_spacing('lg'))
        
        # Modern step indicator with professional typography
        self.step_info_label = ctk.CTkLabel(
            step_info_frame,
            text=f"שלב {self.current_step} מתוך {self.max_steps}",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_secondary']
        )
        self.step_info_label.pack()
        
        # Professional Previous button
        self.prev_button = self.theme_manager.create_modern_button(
            button_frame,
            text="◀ הקודם",
            style="secondary",
            size="medium",
            width=100,
            command=self.prev_step
        )
        self.prev_button.pack(side="right", padx=(0, self.theme_manager.get_spacing('sm')))
        
        # Professional Next/Finish button
        self.next_button = self.theme_manager.create_modern_button(
            button_frame,
            text="הבא ▶",
            style="primary",
            size="medium",
            width=100,
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
        
        # Next/Finish button - check for approval requirements
        if self.current_step == self.max_steps:
            # Check if any items require approval for non-admin/manager users
            user_role = self.current_user.get('role', 'viewer')
            if user_role not in ['admin', 'manager']:
                # Check if any selected items require approval
                approval_required = False
                if hasattr(self, 'selected_items') and self.selected_items:
                    catalog_handler = CatalogHandler()
                    catalog_items = catalog_handler.get_catalog_items()
                    
                    for item in self.selected_items:
                        item_name = item.get('שם מוצר', item.get('name', ''))
                        # Find matching catalog item
                        for cat_item in catalog_items:
                            if cat_item.get('שם מוצר') == item_name:
                                if cat_item.get('דורש אישור', False):
                                    approval_required = True
                                    break
                        if approval_required:
                            break
                
                if approval_required:
                    self.next_button.configure(text="שמור כטיוטה לאישור ⚠️", fg_color="#F59E0B", hover_color="#D97706")
                else:
                    self.next_button.configure(text="סיום ושמירה ✓", fg_color="#3B82F6", hover_color="#2563EB")
            else:
                self.next_button.configure(text="סיום ושמירה ✓", fg_color="#3B82F6", hover_color="#2563EB")
        else:
            self.next_button.configure(text="הבא ▶", fg_color="#3B82F6", hover_color="#2563EB")
        
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
        # Safety check - ensure container still exists
        if not hasattr(self, 'customers_container') or self.customers_container is None:
            print("Warning: customers_container is None, skipping display")
            return
        
        try:
            # Check if container widget still exists
            if not self.customers_container.winfo_exists():
                print("Warning: customers_container no longer exists, skipping display")
                return
        except Exception as e:
            print(f"Warning: Error checking customers_container existence: {e}")
            return
        
        # Clear existing - with additional safety
        try:
            for widget in self.customers_container.winfo_children():
                widget.destroy()
        except Exception as e:
            print(f"Warning: Error clearing customers_container: {e}")
            return
        
        if not customers:
            try:
                no_customers_label = ctk.CTkLabel(
                    self.customers_container,
                    text="אין לקוחות במערכת\nלחץ על 'לקוח חדש' ליצירת לקוח ראשון",
                    font=ctk.CTkFont(family="Heebo", size=16),
                    justify="center"
                )
                no_customers_label.pack(expand=True, pady=50)
            except Exception as e:
                print(f"Warning: Error creating no customers label: {e}")
            return
        
        # Display customers as selectable cards
        for customer in customers:
            try:
                self.create_customer_card(customer)
            except Exception as e:
                print(f"Warning: Error creating customer card for {customer.get('name', 'Unknown')}: {e}")
                continue
    
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
        # Safety check - ensure container still exists
        if not hasattr(self, 'customers_container') or self.customers_container is None:
            print(f"Warning: customers_container is None, cannot show error: {error}")
            return
        
        try:
            # Check if container widget still exists
            if not self.customers_container.winfo_exists():
                print(f"Warning: customers_container no longer exists, cannot show error: {error}")
                return
        except Exception as e:
            print(f"Warning: Error checking customers_container existence: {e}")
            return
        
        try:
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
        except Exception as e:
            print(f"Warning: Error showing customer error: {e}")
    
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
        """Create modern catalog item card with new format support"""
        # Modern card styling with theme support
        card = ctk.CTkFrame(
            self.catalog_table,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E1E8F7",
            corner_radius=15
        )
        card.pack(fill="x", padx=5, pady=3)
        
        # Add hover effects
        def on_enter(event):
            card.configure(border_color="#3B82F6")
        
        def on_leave(event):
            card.configure(border_color="#E1E8F7")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)
        
        # Header with item name and approval indicator
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        # Left side - Add button
        add_btn = ctk.CTkButton(
            header_frame,
            text="הוסף",
            width=70,
            height=32,
            font=ctk.CTkFont(family="Assistant", size=13, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=8,
            command=lambda: self.add_to_cart_with_dialog(item)
        )
        add_btn.pack(side="left")
        
        # Right side - Item info
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Item name with approval indicator
        name_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_container.pack(fill="x", anchor="e")
        
        # Approval status (if required)
        requires_approval = item.get('דורש אישור', False)
        if requires_approval:
            approval_indicator = ctk.CTkLabel(
                name_container,
                text="🔒",
                font=ctk.CTkFont(size=14),
                text_color="#EF4444"
            )
            approval_indicator.pack(side="left", padx=(0, 5))
        
        # Item name
        item_name = ctk.CTkLabel(
            name_container,
            text=item.get('שם מוצר', 'פריט ללא שם'),
            font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        item_name.pack(side="right", fill="x", expand=True)
        
        # Price and unit information
        price_info_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        price_info_frame.pack(fill="x", anchor="e", pady=(3, 0))
        
        price = item.get('מחיר', 0)
        units = item.get('יחידה', '')
        has_custom_pricing = item.get('has_custom_pricing', False) or price == 0
        is_unitless = item.get('is_unitless', False) or not units
        
        # Price display with unit info
        if has_custom_pricing:
            if is_unitless:
                price_text = "מחיר לפי הזמנה"
                price_color = "#F59E0B"  # Orange for custom pricing
            else:
                price_text = f"מחיר מותאם / {units}"
                price_color = "#F59E0B"  # Orange for custom pricing
        else:
            if is_unitless:
                price_text = f"₪{price:,.0f} - פריט קבוע"
                price_color = "#10B981"  # Green for fixed pricing
            else:
                price_text = f"₪{price:,.0f} / {units}"
                price_color = "#10B981"  # Green for available pricing
        
        price_label = ctk.CTkLabel(
            price_info_frame,
            text=price_text,
            font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
            text_color=price_color,
            anchor="e"
        )
        price_label.pack(anchor="e")
        
        # Unit explanation
        if is_unitless:
            unit_text = "פריט ללא יחידות - כמות קבועה: 1"
            unit_color = "#6B7280"  # Gray for unitless items
        elif units == 'מ"א':
            unit_text = "מטר אורך - כמות עשרונית"
            unit_color = "#8B5CF6"  # Purple for linear meters
        elif units == 'יח׳':
            unit_text = "יחידות - כמות שלמה"
            unit_color = "#3B82F6"  # Blue for pieces
        else:
            unit_text = f"יחידה: {units}" if units else "ללא יחידות"
            unit_color = "#6B7280"  # Gray for other/unknown units
        
        unit_explanation = ctk.CTkLabel(
            price_info_frame,
            text=unit_text,
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color=unit_color,
            anchor="e"
        )
        unit_explanation.pack(anchor="e")
        
        # Category
        category_label = ctk.CTkLabel(
            info_frame,
            text=f"קטגוריה: {item.get('קטגוריה', 'ללא קטגוריה')}",
            font=ctk.CTkFont(family="Assistant", size=12),
            text_color="#6B7280",
            anchor="e"
        )
        category_label.pack(anchor="e", pady=(2, 0))
        
        # Comments (if available and not too long)
        comments = item.get('תיאור', '').strip()
        if comments and len(comments) < 100:  # Only show short comments
            comments_label = ctk.CTkLabel(
                info_frame,
                text=f"הערות: {comments}",
                font=ctk.CTkFont(family="Assistant", size=11, slant="italic"),
                text_color="#6B7280",
                anchor="e",
                wraplength=300
            )
            comments_label.pack(anchor="e", pady=(2, 0))
        
        # Make card clickable
        def add_item_click(event=None):
            self.add_to_cart_with_dialog(item)
        
        # Bind click events (but not to button)
        card.bind("<Button-1>", add_item_click)
        content_frame.bind("<Button-1>", add_item_click)
        header_frame.bind("<Button-1>", add_item_click)
        info_frame.bind("<Button-1>", add_item_click)
    
    def add_to_cart_with_dialog(self, item):
        """Add item to cart with quantity and custom price dialog if needed"""
        try:
            units = item.get('יחידה', '')
            price = item.get('מחיר', 0)
            requires_approval = item.get('דורש אישור', False)
            has_custom_pricing = item.get('has_custom_pricing', False) or price == 0
            is_unitless = item.get('is_unitless', False) or not units
            
            # Check approval permissions
            if requires_approval:
                user_role = self.current_user.get('role', 'viewer')
                if user_role not in ['admin', 'manager']:
                    # Force save as draft workflow will be handled in finish_wizard
                    pass  # Continue to allow adding, restriction enforced at save time
            
            # Create dialog for quantity (and custom price if needed)
            dialog = ctk.CTkToplevel(self.dialog)
            dialog.title("הוסף פריט לסל")
            dialog.geometry("400x550")
            dialog.transient(self.dialog)
            dialog.grab_set()
            
            # Center dialog
            dialog.geometry("+%d+%d" % (
                self.dialog.winfo_rootx() + 50,
                self.dialog.winfo_rooty() + 50
            ))
            
            # Main frame
            main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="הוסף פריט לסל",
                font=ctk.CTkFont(family="Assistant", size=20, weight="bold"),
                text_color="#1F2937"
            )
            title_label.pack(pady=(0, 20))
            
            # Item info card
            info_card = ctk.CTkFrame(main_frame, fg_color="#F8FAFC", corner_radius=12)
            info_card.pack(fill="x", pady=(0, 20))
            
            # Item name
            ctk.CTkLabel(
                info_card,
                text=item.get('שם מוצר', 'פריט'),
                font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
                anchor="center"
            ).pack(pady=15)
            
            # Unit and pricing info
            if is_unitless:
                unit_info = "פריט ללא יחידות מידה - כמות: 1"
                quantity_var = ctk.StringVar(value="1")  # Fixed quantity for unitless items
                show_quantity_input = False
            else:
                if units == 'מ"א':
                    unit_info = f"יחידה: {units} - ניתן להזין כמות עשרונית"
                elif units == 'יח׳':
                    unit_info = f"יחידה: {units} - כמות שלמה בלבד"
                else:
                    unit_info = f"יחידה: {units}"
                quantity_var = ctk.StringVar(value="1")
                show_quantity_input = True
            
            ctk.CTkLabel(
                info_card,
                text=unit_info,
                font=ctk.CTkFont(family="Assistant", size=12),
                text_color="#6B7280"
            ).pack(pady=(0, 15))
            
            # Approval warning
            if requires_approval:
                warning_frame = ctk.CTkFrame(main_frame, fg_color="#FEF2F2", corner_radius=8)
                warning_frame.pack(fill="x", pady=(0, 15))
                
                ctk.CTkLabel(
                    warning_frame,
                    text="⚠️ פריט זה דורש אישור מנהל",
                    font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
                    text_color="#EF4444"
                ).pack(pady=10)
                
                user_role = self.current_user.get('role', 'viewer')
                if user_role not in ['admin', 'manager']:
                    ctk.CTkLabel(
                        warning_frame,
                        text="ההצעה תישמר כטיוטה לאישור",
                        font=ctk.CTkFont(family="Assistant", size=12),
                        text_color="#DC2626"
                    ).pack(pady=(0, 10))
            
            # Quantity input (only if not unitless)
            if show_quantity_input:
                qty_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                qty_frame.pack(fill="x", pady=(0, 15))
                
                ctk.CTkLabel(
                    qty_frame,
                    text=f"כמות ({units}):",
                    font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
                    anchor="e"
                ).pack(anchor="e")
                
                # Unit-specific quantity input
                if units == 'יח׳':
                    # Integer only for pieces
                    qty_entry = ctk.CTkEntry(
                        qty_frame,
                        textvariable=quantity_var,
                        placeholder_text="הזן כמות שלמה (1, 2, 3...)",
                        font=ctk.CTkFont(family="Assistant", size=14),
                        height=40
                    )
                    help_text = "כמות שלמה בלבד (יחידות)"
                else:
                    # Float allowed for linear meters
                    qty_entry = ctk.CTkEntry(
                        qty_frame,
                        textvariable=quantity_var,
                        placeholder_text="הזן כמות (1.5, 2.25...)",
                        font=ctk.CTkFont(family="Assistant", size=14),
                        height=40
                    )
                    help_text = "ניתן להזין כמות עשרונית"
                
                qty_entry.pack(fill="x", pady=(5, 0))
                
                ctk.CTkLabel(
                    qty_frame,
                    text=help_text,
                    font=ctk.CTkFont(family="Assistant", size=11),
                    text_color="#6B7280"
                ).pack(anchor="e", pady=(2, 0))
            
            # Custom price (if needed)
            custom_price_var = None
            if has_custom_pricing:
                price_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                price_frame.pack(fill="x", pady=(0, 15))
                
                price_label_text = "מחיר מותאם (₪):" if not is_unitless else "מחיר כולל (₪):"
                ctk.CTkLabel(
                    price_frame,
                    text=price_label_text,
                    font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
                    anchor="e"
                ).pack(anchor="e")
                
                custom_price_var = ctk.StringVar()
                price_entry = ctk.CTkEntry(
                    price_frame,
                    textvariable=custom_price_var,
                    placeholder_text="הזן מחיר",
                    font=ctk.CTkFont(family="Assistant", size=14),
                    height=40
                )
                price_entry.pack(fill="x", pady=(5, 0))
                
                price_help_text = "מחיר כולל לפריט" if is_unitless else f"מחיר לפי {units if units else 'יחידה'}"
                ctk.CTkLabel(
                    price_frame,
                    text=price_help_text,
                    font=ctk.CTkFont(family="Assistant", size=11),
                    text_color="#6B7280"
                ).pack(anchor="e", pady=(2, 0))
            
            # Buttons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(20, 0))
            
            def add_item():
                try:
                    # Handle quantity based on item type
                    if is_unitless:
                        quantity = 1  # Fixed quantity for unitless items
                    else:
                        # Validate quantity
                        qty_text = quantity_var.get().strip()
                        if not qty_text:
                            messagebox.showerror("שגיאה", "יש להזין כמות")
                            return
                        
                        # Parse quantity based on unit type
                        if units == 'יח׳':
                            # Integer only
                            try:
                                quantity = int(float(qty_text))  # Parse as float then convert to int
                                if quantity <= 0:
                                    raise ValueError()
                            except ValueError:
                                messagebox.showerror("שגיאה", "יש להזין כמות שלמה חיובית")
                                return
                        else:
                            # Float allowed
                            try:
                                quantity = float(qty_text)
                                if quantity <= 0:
                                    raise ValueError()
                            except ValueError:
                                messagebox.showerror("שגיאה", "יש להזין כמות חיובית")
                                return
                    
                    # Get final price
                    final_price = price
                    if custom_price_var:
                        try:
                            custom_price = float(custom_price_var.get().strip() or "0")
                            if custom_price <= 0:
                                messagebox.showerror("שגיאה", "יש להזין מחיר חיובי")
                                return
                            final_price = custom_price
                        except ValueError:
                            messagebox.showerror("שגיאה", "יש להזין מחיר תקין")
                            return
                    
                    # Add to cart
                    self.add_item_to_cart(item, quantity, final_price)
                    dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("שגיאה", f"שגיאה בהוספת הפריט: {e}")
            
            def cancel():
                dialog.destroy()
            
            # Add button
            add_button = ctk.CTkButton(
                button_frame,
                text="הוסף לסל",
                font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
                height=40,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                command=add_item
            )
            add_button.pack(side="right", padx=(10, 0))
            
            # Cancel button
            cancel_button = ctk.CTkButton(
                button_frame,
                text="ביטול",
                font=ctk.CTkFont(family="Assistant", size=14, weight="bold"),
                height=40,
                fg_color="#6B7280",
                hover_color="#4B5563",
                command=cancel
            )
            cancel_button.pack(side="right")
            
            # Focus on appropriate entry
            if show_quantity_input:
                qty_entry.focus()
            elif custom_price_var:
                price_entry.focus()
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בפתיחת דיאלוג: {e}")
    
    def add_item_to_cart(self, item, quantity, final_price):
        """Add item to cart with specified quantity and price"""
        # Check if already in cart
        item_name = item.get('שם מוצר', item.get('name', 'פריט'))
        item_category = item.get('קטגוריה', item.get('category', ''))
        
        for cart_item in self.selected_items:
            if (cart_item.get('שם מוצר') == item_name and 
                cart_item.get('קטגוריה') == item_category):
                # Update existing item
                cart_item['כמות'] += quantity
                cart_item['quantity'] += quantity
                # If this item has custom pricing, update the price
                if final_price != item.get('מחיר', 0):
                    cart_item['מחיר'] = final_price
                    cart_item['price'] = final_price
                    cart_item['custom_price'] = True
                self.update_cart()
                self.update_navigation_buttons()
                return
        
        # Add new item with both Hebrew and English keys
        formatted_item = {
            'שם מוצר': item.get('שם מוצר', item.get('name', 'פריט')),
            'name': item.get('שם מוצר', item.get('name', 'פריט')),
            'קטגוריה': item.get('קטגוריה', item.get('category', '')),
            'category': item.get('קטגוריה', item.get('category', '')),
            'כמות': quantity,
            'quantity': quantity,
            'מחיר': final_price,
            'price': final_price,
            'תיאור': item.get('תיאור', item.get('description', '')),
            'description': item.get('תיאור', item.get('description', '')),
            'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
            'unit': item.get('יחידה', item.get('unit', 'יח׳')),
            'דורש אישור': item.get('דורש אישור', False),
            'requires_approval': item.get('דורש אישור', False),
            'custom_price': final_price != item.get('מחיר', 0)  # Track if price was customized
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
                header.grid_columnconfigure(2, weight=2)  # Total
                header.grid_columnconfigure(3, weight=0)  # Remove
                
                for col, text in enumerate(["כמות", "שם מוצר", "סה\"כ", "הסר"]):
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
                    row.grid_columnconfigure(3, weight=0)
                    
                    # Quantity (editable with unit awareness)
                    item_units = item.get('יחידה', 'יח׳')
                    qty_value = item.get('quantity', 1)
                    
                    # Format quantity based on unit type
                    if item_units == 'יח׳':
                        qty_display = str(int(qty_value))  # Integer for pieces
                    else:
                        qty_display = f"{qty_value:.2f}".rstrip('0').rstrip('.')  # Clean decimal for meters
                    
                    qty_var = ctk.StringVar(value=qty_display)
                    
                    # Create entry first
                    qty_entry = ctk.CTkEntry(
                        row, 
                        textvariable=qty_var, 
                        width=80, 
                        height=30,
                        justify="center",
                        font=ctk.CTkFont(family="Assistant", size=14, weight="bold")
                    )
                    qty_entry.grid(row=0, column=0, padx=8, pady=8)
                    
                    # Unit indicator
                    unit_color = "#8B5CF6" if item_units == 'מ"א' else "#3B82F6"
                    unit_badge = ctk.CTkLabel(
                        row,
                        text=item_units,
                        font=ctk.CTkFont(family="Assistant", size=10, weight="bold"),
                        text_color=unit_color,
                        width=30
                    )
                    unit_badge.grid(row=0, column=0, padx=(60, 8), pady=8, sticky="e")
                    
                    # Then set up the trace with proper closure and unit validation
                    def create_qty_handler(index, units):
                        def on_qty_change(*args):
                            try:
                                qty_text = qty_var.get().strip()
                                if not qty_text:
                                    return
                                
                                if units == 'יח׳':
                                    # Integer only for pieces
                                    val = int(float(qty_text))
                                    if val < 1:
                                        val = 1
                                    qty_var.set(str(val))  # Update display
                                else:
                                    # Float allowed for meters
                                    val = float(qty_text)
                                    if val <= 0:
                                        val = 0.1
                                
                                self.selected_items[index]['quantity'] = val
                                self.selected_items[index]['כמות'] = val
                                self.update_cart()
                                self.update_navigation_buttons()
                            except ValueError:
                                # Reset to valid value
                                if units == 'יח׳':
                                    qty_var.set(str(int(self.selected_items[index]['quantity'])))
                                else:
                                    current_val = self.selected_items[index]['quantity']
                                    qty_var.set(f"{current_val:.2f}".rstrip('0').rstrip('.'))
                        return on_qty_change
                    
                    qty_var.trace("w", create_qty_handler(idx, item_units))
                    
                    # Name
                    font_row = ctk.CTkFont(family="Heebo", size=15, weight="normal")
                    font_category = ctk.CTkFont(family="Heebo", size=14, weight="normal")
                    font_price = ctk.CTkFont(family="Heebo", size=15, weight="bold")
                    
                    ctk.CTkLabel(row, text=item['name'], anchor="e", font=font_row).grid(row=0, column=1, padx=8, pady=8, sticky="ew")
                    # Item total
                    item_total = item['price'] * item['quantity']
                    total += item_total
                    ctk.CTkLabel(row, text=f"₪{item_total:,.0f}", anchor="center", font=font_price, text_color="#10B981").grid(row=0, column=2, padx=8, pady=8, sticky="ew")
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
                    remove_btn.grid(row=0, column=3, padx=8, pady=8)
                
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
        
        # If we're editing a quote or draft, ensure the values are properly set
        if hasattr(self, '_editing_quote') and self._editing_quote:
            # Force set the values again to ensure they're properly loaded
            print(f"Editing mode detected, forcing discount values: regular={existing_regular_discount}, contractor={existing_contractor_discount}, vat={existing_vat_rate}")
            self.regular_discount_var.set(str(existing_regular_discount))
            self.contractor_discount_var.set(str(existing_contractor_discount))
            self.vat_rate_var.set(str(existing_vat_rate))
        
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
            
            # Step 1: Sum of items
            subtotal = 0.0
            if self.selected_items:
                subtotal = sum(
                    float(item.get('מחיר', item.get('price', 0))) * 
                    int(item.get('כמות', item.get('quantity', 1))) 
                    for item in self.selected_items
                )
            
            # Step 2: Apply VAT as multiplier (17% = 1.17)
            vat_multiplier = 1 + (vat_rate / 100)  # 17% becomes 1.17
            after_vat = subtotal * vat_multiplier
            vat_amount = after_vat - subtotal  # Calculate VAT amount for display
            
            # Step 3: Subtract contractor discount (fixed amount)
            contractor_discount_amount = contractor_discount  # Fixed amount, not percentage
            after_contractor = after_vat - contractor_discount_amount
            after_contractor = max(0, after_contractor)  # Can't go below 0
            
            # Step 4: Apply regular discount as reduction factor (18% = 0.82)
            discount_factor = 1 - (regular_discount / 100)  # 18% becomes 0.82
            final_total = after_contractor * discount_factor
            regular_discount_amount = after_contractor - final_total  # Calculate discount amount for display
            
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
            def safe_config(widget, **kwargs):
                try:
                    if widget and widget.winfo_exists():
                        widget.configure(**kwargs)
                except Exception:
                    pass
            
            safe_config(getattr(self, 'subtotal_label', None), text=f"סכום ביניים: ₪{subtotal:,.2f}")
            
            contractor_label = getattr(self, 'contractor_discount_label', None)
            if contractor_discount > 0:
                safe_config(contractor_label, text=f"הנחת קבלן: -₪{contractor_discount:,.2f}", text_color="#F59E0B")
            else:
                safe_config(contractor_label, text="")
            
            discount_label = getattr(self, 'discount_label', None)
            if regular_discount_amount > 0:
                safe_config(discount_label, text=f"הנחה כללית: -₪{regular_discount_amount:,.2f}", text_color="#F59E0B")
            else:
                safe_config(discount_label, text="")
            
            safe_config(getattr(self, 'vat_label', None), text=f"מע״מ: ₪{vat_amount:,.2f}")
            safe_config(getattr(self, 'total_label', None), text=f"סה״כ לתשלום: ₪{final_total:,.2f}")
            
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
        
        # Enhanced Image upload section with categories
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
            text="תמונות להצעה (ללא הגבלה)",
            font=ctk.CTkFont(family="Heebo", size=18, weight="bold"),
            text_color="#1F2937"
        )
        images_title.pack(pady=(20, 10))
        
        images_subtitle = ctk.CTkLabel(
            images_frame,
            text="כל תמונה תופיע בעמוד נפרד ב-PDF. תמונות לרוחב יסובבו אוטומטית לאורך.",
            font=ctk.CTkFont(family="Heebo", size=13, weight="normal"),
            text_color="#6B7280"
        )
        images_subtitle.pack(pady=(0, 15))
        
        # Image upload container with modern styling
        images_container = ctk.CTkFrame(images_frame, fg_color="transparent")
        images_container.pack(fill="x", padx=25, pady=(0, 20))
        
        # Initialize images list if not exists (backward compatibility)
        if 'images' not in self.quote_data:
            self.quote_data['images'] = []
        
        # Initialize new categorized image system
        if 'visualization_images' not in self.quote_data:
            self.quote_data['visualization_images'] = []
        if 'technical_images' not in self.quote_data:
            self.quote_data['technical_images'] = []
        
        # Create categorized image sections
        self.create_image_category_section(images_container, "visualization", "הדמיה", "#3B82F6")
        self.create_image_category_section(images_container, "technical", "הדמיית נקודות מים וחשמל", "#8B5CF6")
    
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
            
            # Get values from UI variables if in step 3 (pricing/discounts)
            if self.current_step == 3:
                if hasattr(self, 'regular_discount_var') and self.regular_discount_var:
                    try:
                        regular_discount = float(self.regular_discount_var.get() or 0)
                        print(f"Step 3: Captured regular_discount from UI: {regular_discount}")
                    except (ValueError, AttributeError):
                        regular_discount = self.quote_data.get('regular_discount', 0.0)
                        print(f"Step 3: Failed to get regular_discount from UI, using quote_data: {regular_discount}")
                        
                if hasattr(self, 'contractor_discount_var') and self.contractor_discount_var:
                    try:
                        contractor_discount = float(self.contractor_discount_var.get() or 0)
                        print(f"Step 3: Captured contractor_discount from UI: {contractor_discount}")
                    except (ValueError, AttributeError):
                        contractor_discount = self.quote_data.get('contractor_discount', 0.0)
                        print(f"Step 3: Failed to get contractor_discount from UI, using quote_data: {contractor_discount}")
                        
                if hasattr(self, 'vat_rate_var') and self.vat_rate_var:
                    try:
                        vat_rate = float(self.vat_rate_var.get() or 17)
                        print(f"Step 3: Captured vat_rate from UI: {vat_rate}")
                    except (ValueError, AttributeError):
                        vat_rate = self.quote_data.get('vat_rate', 17.0)
                        print(f"Step 3: Failed to get vat_rate from UI, using quote_data: {vat_rate}")
            else:
                # For other steps, use existing quote_data values
                regular_discount = self.quote_data.get('regular_discount', 0.0)
                contractor_discount = self.quote_data.get('contractor_discount', 0.0)
                vat_rate = self.quote_data.get('vat_rate', 17.0)
                print(f"Step {self.current_step}: Using existing quote_data values")
            
            # Update quote_data with captured values
            self.quote_data.update({
                'regular_discount': regular_discount,
                'contractor_discount': contractor_discount,
                'vat_rate': vat_rate
            })
            
            print(f"save_step_data: Updated quote_data with discounts: regular={regular_discount}, contractor={contractor_discount}, vat={vat_rate}")
            
            # Recalculate totals
            self.calculate_totals()
            
            # Save notes if on summary step
            if self.current_step == 4 and hasattr(self, 'notes_textbox'):
                notes_content = self.notes_textbox.get("1.0", "end-1c")
                self.quote_data['notes'] = notes_content
                print(f"Step 4: Captured notes: {notes_content}")
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error saving step data: {e}")
            print(f"Error in save_step_data: {e}")
    
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
            
            # Check approval requirements - CRITICAL LOGIC
            user_role = self.current_user.get('role', 'viewer')
            
            # First, check if any items require approval
            approval_required_items = []
            for item in self.selected_items:
                # Get original catalog item to check approval status
                item_name = item.get('שם מוצר', item.get('name', ''))
                catalog_handler = CatalogHandler()
                catalog_items = catalog_handler.get_catalog_items()
                
                # Find matching catalog item
                catalog_item = None
                for cat_item in catalog_items:
                    if cat_item.get('שם מוצר') == item_name:
                        catalog_item = cat_item
                        break
                
                # Check if this item requires approval
                if catalog_item and catalog_item.get('דורש אישור', False):
                    approval_required_items.append(item_name)
            
            # If there are items requiring approval and user is not admin, force save as draft
            if approval_required_items and user_role != 'admin':
                items_list = '\n• '.join(approval_required_items)
                result = messagebox.askquestion(
                    "פריטים דורשים אישור",
                    f"הפריטים הבאים דורשים אישור מנהל:\n\n• {items_list}\n\n"
                    f"רק מנהל יכול לשמור הצעה עם פריטים אלה.\n"
                    f"האם תרצה לשמור כטיוטה עבור אישור מנהל?",
                    icon="warning"
                )
                if result == 'yes':
                    self.save_draft()
                    return
                else:
                    return
            
            # Enforce discount permission check right before saving
            regular_discount = self.quote_data.get('regular_discount', 0)
            user_max_discount = self.current_user.get('max_discount', 0.0)
            has_unlimited_discount = user_role == 'admin'
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
                        images=self._combine_images_for_database(),
                        acting_user_id=self.current_user['id']
                    )
                    if not success:
                        messagebox.showerror("שגיאה", "אין לך הרשאה לערוך את ההצעה או שהעריכה נכשלה")
                        return
                    # Get the updated quote data
                    quote = self.db_manager.get_quote_dict_by_id(quote_id_existing)
                    if not quote:
                        messagebox.showerror("שגיאה", "שגיאה בטעינת הצעת המחיר המעודכנת")
                        return
                    # Ensure quote is a dict for downstream usage
                    if isinstance(quote, dict):
                        quote = quote
                    else:
                        try:
                            # Use the internal helper to convert
                            quote = self.db_manager._quote_to_dict(quote)
                        except Exception:
                            # Fallback minimal dict
                            quote = {
                                'id': getattr(quote, 'id', quote_id_existing),
                                'quote_number': getattr(quote, 'quote_number', quote_id_existing)
                            }
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
                        images=self._combine_images_for_database()
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

            # Check if any items require approval and store this information
            approval_required_items = []
            for item in self.selected_items:
                # Get original catalog item to check approval status
                item_name = item.get('שם מוצר', item.get('name', ''))
                catalog_handler = CatalogHandler()
                catalog_items = catalog_handler.get_catalog_items()
                
                # Find matching catalog item
                catalog_item = None
                for cat_item in catalog_items:
                    if cat_item.get('שם מוצר') == item_name:
                        catalog_item = cat_item
                        break
                
                # Check if this item requires approval
                if catalog_item and catalog_item.get('דורש אישור', False):
                    approval_required_items.append(item_name)
            
            # Prepare draft state with consistent item format
            draft_items = []
            for item in self.selected_items:
                draft_item = {
                    'שם מוצר': item.get('שם מוצר', item.get('name', '')),
                    'name': item.get('שם מוצר', item.get('name', '')),
                    'קטגוריה': item.get('קטגוריה', item.get('category', '')),
                    'category': item.get('קטגוריה', item.get('category', '')),
                    'כמות': item.get('כמות', item.get('quantity', 1)),
                    'quantity': item.get('כמות', item.get('quantity', 1)),
                    'מחיר': item.get('מחיר', item.get('price', 0)),
                    'price': item.get('מחיר', item.get('price', 0)),
                    'תיאור': item.get('תיאור', item.get('description', '')),
                    'description': item.get('תיאור', item.get('description', '')),
                    'יחידה': item.get('יחידה', item.get('unit', 'יח׳')),
                    'unit': item.get('יחידה', item.get('unit', 'יח׳')),
                    'דורש אישור': item.get('דורש אישור', False),
                    'requires_approval': item.get('דורש אישור', False)
                }
                draft_items.append(draft_item)
            
            # Create serializable quote data
            serializable_quote_data = self.quote_data.copy()
            if 'customer_data' in serializable_quote_data:
                del serializable_quote_data['customer_data']
            
            draft_state = {
                'step': self.current_step,
                'quote_data': serializable_quote_data,
                'selected_items': draft_items,
                'current_step': self.current_step,
                'approval_required_items': approval_required_items,  # Store approval requirement info
                'requires_manager_approval': len(approval_required_items) > 0 and user_role not in ['admin', 'manager']
            }
            
            # Save draft to DB
            self.db_manager.save_draft(
                state=draft_state,
                created_by=self.current_user['id'],
                customer_id=self.quote_data.get('customer_id'),
                step=self.current_step
            )
            self.logger.info(f"Draft saved at step {self.current_step} with {len(self.selected_items)} items")
            
            # Show success message with approval information
            if approval_required_items and user_role not in ['admin', 'manager']:
                items_list = ', '.join(approval_required_items[:3])  # Show first 3 items
                if len(approval_required_items) > 3:
                    items_list += f" ועוד {len(approval_required_items) - 3}"
                
                success_message = (
                    "הטיוטה נשמרה בהצלחה!\n\n"
                    f"⚠️ הטיוטה מכילה פריטים הדורשים אישור מנהל:\n{items_list}\n\n"
                    "🔒 ממתין לאישור מנהל"
                )
                messagebox.showinfo("טיוטה נשמרה לאישור", success_message)
            else:
                messagebox.showinfo("הצלחה", "הטיוטה נשמרה בהצלחה!")
                
            # Close wizard
            if self.dialog:
                self.dialog.destroy()
                
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
            # Handle both Quote objects and dictionaries
            def safe_get(data, key, default=None):
                """Safely get value from either dict or object"""
                if isinstance(data, dict):
                    return data.get(key, default)
                else:
                    # Handle SQLAlchemy object
                    return getattr(data, key, default)
            
            # Check if user has permission to edit this quote with its current discounts
            existing_regular_discount = safe_get(quote_data, 'regular_discount', 0)
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
            
            # Populate quote data using safe_get
            self.quote_data.update({
                'customer_id': safe_get(quote_data, 'customer_id'),
                'customer_data': None,  # Will be loaded in customer selection step
                'regular_discount': safe_get(quote_data, 'regular_discount', 0),
                'contractor_discount': safe_get(quote_data, 'contractor_discount', 0),
                'vat_rate': safe_get(quote_data, 'vat_rate', 17),
                'notes': safe_get(quote_data, 'notes', ''),
                'images': safe_get(quote_data, 'images', []),
                'quote_id': safe_get(quote_data, 'id')  # Store original quote ID for updating
            })

            
            # Convert items to expected format with both key sets
            items = safe_get(quote_data, 'items', [])
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
                customer = self.db_manager.get_customer_by_id(safe_get(quote_data, 'customer_id'))
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
            # Explicitly set the StringVars if they exist with proper values
            if hasattr(self, 'regular_discount_var') and self.regular_discount_var:
                discount_value = self.quote_data.get('regular_discount', 0)
                self.regular_discount_var.set(str(discount_value))
                print(f"Set regular_discount_var to: {discount_value}")
                
            if hasattr(self, 'contractor_discount_var') and self.contractor_discount_var:
                contractor_value = self.quote_data.get('contractor_discount', 0)
                self.contractor_discount_var.set(str(contractor_value))
                print(f"Set contractor_discount_var to: {contractor_value}")
                
            if hasattr(self, 'vat_rate_var') and self.vat_rate_var:
                vat_value = self.quote_data.get('vat_rate', 17)
                self.vat_rate_var.set(str(vat_value))
                print(f"Set vat_rate_var to: {vat_value}")
            
            # Also set notes if we have the textbox
            if hasattr(self, 'notes_textbox') and self.notes_textbox:
                notes_value = self.quote_data.get('notes', '')
                self.notes_textbox.delete("1.0", "end")
                self.notes_textbox.insert("1.0", notes_value)
                print(f"Set notes to: {notes_value}")
            
            # Clear the editing flag
            self._editing_quote = False
            
            # Force update the quote_data with the correct values before calculating
            self.quote_data.update({
                'regular_discount': self.quote_data.get('regular_discount', 0),
                'contractor_discount': self.quote_data.get('contractor_discount', 0),
                'vat_rate': self.quote_data.get('vat_rate', 17)
            })
            
            # Now calculate totals with the correct values
            self.calculate_totals()
            
            print(f"Finished edit setup with quote_data: {self.quote_data}")
            
        except Exception as e:
            print(f"Error in _finish_edit_setup: {e}")
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

    def create_image_category_section(self, parent, category_key, title, color):
        """Create an image category section with multiple image support"""
        category_frame = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D1D5DB",
            corner_radius=12
        )
        category_frame.pack(fill="x", pady=(0, 15))
        
        # Category title
        title_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
            text_color=color,
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Images display frame
        images_display_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        images_display_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Store reference for dynamic updates
        setattr(self, f"{category_key}_images_display", images_display_frame)
        
        # Add image button
        add_btn = ctk.CTkButton(
            category_frame,
            text=f"הוסף תמונה ל{title}",
            font=ctk.CTkFont(family="Heebo", size=13, weight="bold"),
            height=35,
            fg_color=color,
            hover_color=self.adjust_color_brightness(color, -20),
            corner_radius=8,
            command=lambda: self.add_categorized_image(category_key)
        )
        add_btn.pack(pady=(0, 15))
        
        # Update display
        self.update_categorized_images_display(category_key)

    def adjust_color_brightness(self, hex_color, adjustment):
        """Adjust hex color brightness by a given amount"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Adjust brightness
            rgb = tuple(max(0, min(255, c + adjustment)) for c in rgb)
            # Convert back to hex
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except:
            return hex_color  # Return original if conversion fails

    def add_categorized_image(self, category_key):
        """Add an image to a specific category"""
        from tkinter import filedialog
        
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        image_path = filedialog.askopenfilename(
            title=f"בחר תמונה לקטגוריה",
            filetypes=filetypes
        )
        
        if image_path:
            list_key = f"{category_key}_images"
            if list_key not in self.quote_data:
                self.quote_data[list_key] = []
            self.quote_data[list_key].append(image_path)
            self.update_categorized_images_display(category_key)

    def remove_categorized_image(self, category_key, index):
        """Remove an image from a specific category"""
        list_key = f"{category_key}_images"
        if list_key in self.quote_data and 0 <= index < len(self.quote_data[list_key]):
            self.quote_data[list_key].pop(index)
            self.update_categorized_images_display(category_key)

    def update_categorized_images_display(self, category_key):
        """Update the display of images for a category"""
        display_frame = getattr(self, f"{category_key}_images_display", None)
        if not display_frame:
            return
        
        # Clear existing display
        for widget in display_frame.winfo_children():
            widget.destroy()
        
        list_key = f"{category_key}_images"
        images = self.quote_data.get(list_key, [])
        
        if not images:
            no_images_label = ctk.CTkLabel(
                display_frame,
                text="לא נבחרו תמונות",
                font=ctk.CTkFont(family="Heebo", size=12),
                text_color="#9CA3AF",
                anchor="e"
            )
            no_images_label.pack(anchor="e", pady=5)
            return
        
        # Display images
        for i, img_path in enumerate(images):
            img_frame = ctk.CTkFrame(display_frame, fg_color="#F9FAFB", corner_radius=8)
            img_frame.pack(fill="x", pady=2)
            
            img_info_frame = ctk.CTkFrame(img_frame, fg_color="transparent")
            img_info_frame.pack(fill="x", padx=10, pady=8)
            
            # Image filename
            import os
            filename = os.path.basename(img_path)
            if len(filename) > 40:
                filename = filename[:37] + "..."
            
            img_label = ctk.CTkLabel(
                img_info_frame,
                text=f"{i+1}. {filename}",
                font=ctk.CTkFont(family="Heebo", size=12),
                text_color="#374151",
                anchor="e"
            )
            img_label.pack(side="right", fill="x", expand=True)
            
            # Remove button
            remove_btn = ctk.CTkButton(
                img_info_frame,
                text="הסר",
                width=50,
                height=25,
                font=ctk.CTkFont(family="Heebo", size=11),
                fg_color="#EF4444",
                hover_color="#DC2626",
                corner_radius=6,
                command=lambda idx=i: self.remove_categorized_image(category_key, idx)
            )
            remove_btn.pack(side="left")

    def select_image(self, image_number):
        """Select an image for the quote (backward compatibility)"""
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

    def _combine_images_for_database(self):
        """Combine categorized images into a single format for database storage"""
        combined_images = []
        
        # Add old-style images for backward compatibility
        old_images = self.quote_data.get('images', [])
        for img in old_images:
            if img:  # Filter out None values
                combined_images.append({
                    'path': img,
                    'category': 'demo',  # Legacy category
                    'type': 'old'
                })
        
        # Add visualization images
        viz_images = self.quote_data.get('visualization_images', [])
        for img in viz_images:
            if img:
                combined_images.append({
                    'path': img,
                    'category': 'visualization',
                    'type': 'הדמיה'
                })
        
        # Add technical images
        tech_images = self.quote_data.get('technical_images', [])
        for img in tech_images:
            if img:
                combined_images.append({
                    'path': img,
                    'category': 'technical',
                    'type': 'הדמיית נקודות מים וחשמל'
                })
        
        return combined_images

    def update_image_labels(self):
        """Update the image path labels (backward compatibility - deprecated)"""
        # This method is kept for backward compatibility but the UI has been updated
        # to use the new categorized image system
        pass 