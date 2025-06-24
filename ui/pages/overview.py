"""
Overview/Dashboard Page for Kitchen Quote Management System
Shows system statistics, recent activity, and quick actions
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime, timedelta
from typing import Dict, Any

class OverviewPage:
    """Overview dashboard page"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.stats_data = {}
        
    def create_content(self):
        """Create overview page content"""
        # Main container with scrolling - clean white background
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner container with padding
        inner_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        inner_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Page header
        self.create_header(inner_frame)
        
        # Statistics cards
        self.create_stats_section(inner_frame)
        
        # Quick actions
        self.create_quick_actions(inner_frame)
        
        # Recent activity
        self.create_recent_activity(inner_frame)
        
        # Load data
        self.load_stats_data()
    
    def create_header(self, parent):
        """Create page header"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Welcome message
        user_name = f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}".strip()
        if not user_name:
            user_name = self.current_user.get('username', 'משתמש')
        
        welcome_text = f"שלום {user_name}"
        
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=welcome_text,
            font=ctk.CTkFont(family="Heebo", size=28, weight="bold"),
            anchor="e"
        )
        welcome_label.pack(anchor="e")
        
        # Current date
        current_date = datetime.now().strftime("%d/%m/%Y")
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"היום: {current_date}",
            font=ctk.CTkFont(family="Heebo", size=16),
            text_color="gray",
            anchor="e"
        )
        date_label.pack(anchor="e", pady=(5, 0))
    
    def create_stats_section(self, parent):
        """Create statistics cards section"""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))
        
        # Section title
        title_label = ctk.CTkLabel(
            stats_frame,
            text="סקירה כללית",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Stats cards container
        cards_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        # Configure grid
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create stats cards
        self.create_stat_card(cards_frame, "לקוחות", "0", "👥", 0, 0)
        self.create_stat_card(cards_frame, "הצעות מחיר", "0", "📋", 0, 1)
        self.create_stat_card(cards_frame, "הצעות החודש", "0", "📊", 0, 2)
        self.create_stat_card(cards_frame, "משתמשים", "0", "👤", 0, 3)
    
    def create_stat_card(self, parent, title: str, value: str, icon: str, row: int, col: int):
        """Create individual statistics card"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#FAFBFF",
            corner_radius=20,
            border_width=1,
            border_color="#E1E8F7"
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="ew")
        
        # Add hover effect
        def on_enter(event):
            card.configure(border_color="#3B82F6")
        
        def on_leave(event):
            card.configure(border_color="#E1E8F7")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=40)
        )
        icon_label.pack(pady=(20, 10))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family="Heebo", size=36, weight="bold"),
            text_color=("blue", "lightblue")
        )
        value_label.pack()
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Heebo", size=14),
            text_color="gray"
        )
        title_label.pack(pady=(5, 20))
        
        # Store reference for updating
        setattr(self, f"stat_{title.replace(' ', '_')}_value", value_label)
    
    def create_quick_actions(self, parent):
        """Create quick actions section"""
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 30))
        
        # Section title
        title_label = ctk.CTkLabel(
            actions_frame,
            text="פעולות מהירות",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Actions container
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Configure grid
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Quick action buttons
        self.create_action_button(
            buttons_frame, 
            "הצעת מחיר חדשה", 
            "📝", 
            self.new_quote_action,
            0, 0
        )
        
        self.create_action_button(
            buttons_frame,
            "לקוח חדש",
            "👤",
            self.new_customer_action,
            0, 1
        )
        
        self.create_action_button(
            buttons_frame,
            "עיון בקטלוג",
            "📁",
            self.view_catalog_action,
            0, 2
        )
    
    def create_action_button(self, parent, text: str, icon: str, command, row: int, col: int):
        """Create quick action button"""
        button = ctk.CTkButton(
            parent,
            text=f"{icon}\n{text}",
            font=ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            height=80,
            command=command
        )
        button.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
    
    def create_recent_activity(self, parent):
        """Create recent activity section"""
        activity_frame = ctk.CTkFrame(parent, fg_color="transparent")
        activity_frame.pack(fill="x", pady=(0, 30))
        
        # Section title
        title_label = ctk.CTkLabel(
            activity_frame,
            text="פעילות אחרונה",
            font=ctk.CTkFont(family="Heebo", size=20, weight="bold"),
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, 15))
        
        # Activity list container with modern styling
        self.activity_container = ctk.CTkFrame(
            activity_frame, 
            fg_color="#FFFFFF", 
            border_width=1, 
            border_color="#E2E8F0",
            corner_radius=15
        )
        self.activity_container.pack(fill="x")
        
        # Placeholder with modern styling
        placeholder_label = ctk.CTkLabel(
            self.activity_container,
            text="טוען פעילות אחרונה...",
            font=ctk.CTkFont(family="Heebo", size=16, weight="normal"),
            text_color="#6B7280"
        )
        placeholder_label.pack(pady=30)
    
    def load_stats_data(self):
        """Load statistics data in background"""
        def load_data():
            try:
                # Get statistics from database
                stats = self.db_manager.get_stats()
                
                # Update UI in main thread
                self.parent.after(0, self.update_stats_display, stats)
                
            except Exception as e:
                self.parent.after(0, self.handle_stats_error, str(e))
        
        # Load in background thread
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_stats_display(self, stats: Dict[str, Any]):
        """Update statistics display"""
        try:
            # Update stat cards
            if hasattr(self, 'stat_לקוחות_value'):
                self.stat_לקוחות_value.configure(text=str(stats.get('total_customers', 0)))
            
            if hasattr(self, 'stat_הצעות_מחיר_value'):
                self.stat_הצעות_מחיר_value.configure(text=str(stats.get('total_quotes', 0)))
            
            if hasattr(self, 'stat_הצעות_החודש_value'):
                self.stat_הצעות_החודש_value.configure(text=str(stats.get('quotes_this_month', 0)))
            
            if hasattr(self, 'stat_משתמשים_value'):
                self.stat_משתמשים_value.configure(text=str(stats.get('total_users', 0)))
            
            # Load recent activity
            self.load_recent_activity()
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating stats: {e}")
    
    def handle_stats_error(self, error: str):
        """Handle statistics loading error"""
        import logging
        logging.getLogger(__name__).error(f"Stats loading error: {error}")
        
        # Show error in activity container
        for widget in self.activity_container.winfo_children():
            widget.destroy()
        
        error_label = ctk.CTkLabel(
            self.activity_container,
            text="שגיאה בטעינת הנתונים",
            font=ctk.CTkFont(family="Heebo", size=16, weight="normal"),
            text_color="#EF4444"
        )
        error_label.pack(pady=30)
    
    def load_recent_activity(self):
        """Load recent activity data"""
        def load_activity():
            try:
                # Get recent quotes
                recent_quotes = self.db_manager.get_recent_quotes(5)
                
                # Update UI in main thread
                self.parent.after(0, self.update_activity_display, recent_quotes)
                
            except Exception as e:
                self.parent.after(0, self.handle_activity_error, str(e))
        
        threading.Thread(target=load_activity, daemon=True).start()
    
    def update_activity_display(self, recent_quotes):
        """Update activity display"""
        try:
            # Clear current content
            for widget in self.activity_container.winfo_children():
                widget.destroy()
            
            if not recent_quotes:
                no_activity_label = ctk.CTkLabel(
                    self.activity_container,
                    text="אין פעילות אחרונה",
                    font=ctk.CTkFont(family="Heebo", size=16, weight="normal"),
                    text_color="#6B7280"
                )
                no_activity_label.pack(pady=30)
                return
            
            # Create activity items
            for quote in recent_quotes:
                self.create_activity_item(quote)
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating activity: {e}")
    
    def create_activity_item(self, quote):
        """Create individual activity item with modern styling"""
        try:
            # Modern activity item card
            item_frame = ctk.CTkFrame(
                self.activity_container, 
                fg_color="#F8FAFC", 
                border_width=1, 
                border_color="#E5E7EB",
                corner_radius=12
            )
            item_frame.pack(fill="x", padx=20, pady=8)
            
            # Add hover effect
            def on_enter(event):
                item_frame.configure(border_color="#3B82F6", fg_color="#EBF4FF")
            
            def on_leave(event):
                item_frame.configure(border_color="#E5E7EB", fg_color="#F8FAFC")
            
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            
            # Content container
            content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=20, pady=15)
            
            # Get customer name
            try:
                customer = self.db_manager.get_customer_by_id(quote.get('customer_id'))
                customer_name = customer['name'] if customer else "לקוח"
            except:
                customer_name = "לקוח"
            
            # Quote info with modern styling
            quote_text = f"הצעת מחיר #{quote.get('quote_number', '')} ל{customer_name}"
            
            info_label = ctk.CTkLabel(
                content_frame,
                text=quote_text,
                font=ctk.CTkFont(family="Heebo", size=16, weight="bold"),
                text_color="#1F2937",
                anchor="e"
            )
            info_label.pack(anchor="e")
            
            # Date with better styling
            if quote.get('created_at'):
                try:
                    if isinstance(quote['created_at'], str):
                        from datetime import datetime
                        created_at = datetime.fromisoformat(quote['created_at'])
                    else:
                        created_at = quote['created_at']
                    date_str = created_at.strftime("%d/%m/%Y %H:%M")
                    
                    date_label = ctk.CTkLabel(
                        content_frame,
                        text=f"נוצר: {date_str}",
                        font=ctk.CTkFont(family="Heebo", size=13, weight="normal"),
                        text_color="#6B7280",
                        anchor="e"
                    )
                    date_label.pack(anchor="e", pady=(5, 0))
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Error formatting date: {e}")
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error creating activity item: {e}")
    
    def handle_activity_error(self, error: str):
        """Handle activity loading error"""
        import logging
        logging.getLogger(__name__).error(f"Activity loading error: {error}")
    
    def new_quote_action(self):
        """Handle new quote action"""
        messagebox.showinfo("פעולה", "יצירת הצעת מחיר חדשה - בפיתוח")
    
    def new_customer_action(self):
        """Handle new customer action"""
        messagebox.showinfo("פעולה", "הוספת לקוח חדש - בפיתוח")
    
    def view_catalog_action(self):
        """Handle view catalog action"""
        messagebox.showinfo("פעולה", "עיון בקטלוג - בפיתוח") 