"""
Modern Overview/Dashboard Page for Kitchen Quote Management System
Shows system statistics, recent activity, and quick actions with beautiful theme integration
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime, timedelta
from typing import Dict, Any
from styling.theme_system import ModernThemeManager, THEMES
from config.settings import SettingsManager

class OverviewPage:
    """Modern overview dashboard page with theme integration"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.stats_data = {}
        
        # Initialize theme system
        self.settings_manager = SettingsManager()
        self.theme_manager = ModernThemeManager(self.settings_manager)
        self.theme = self.theme_manager.get_current_theme()
        
    def create_content(self):
        """Create beautiful modern overview page content with theme integration"""
        # Main container with gradient background and modern styling
        main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=self.theme['bg_secondary'],  # Beautiful gradient base
            corner_radius=0,
            scrollbar_button_color=self.theme['primary_light'],
            scrollbar_button_hover_color=self.theme['primary']
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Inner container with compact spacing
        inner_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        inner_frame.pack(fill="both", expand=True, padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))
        
        # Page header with modern styling
        self.create_modern_header(inner_frame)
        
        # Beautiful statistics cards
        self.create_modern_stats_section(inner_frame)
        
        # Modern quick actions
        self.create_modern_quick_actions(inner_frame)
        
        # Beautiful recent activity
        self.create_modern_recent_activity(inner_frame)
        
        # Load data
        self.load_stats_data()
    
    def create_modern_header(self, parent):
        """Create refined compact page header with professional styling"""
        # Compact header container 
        header_card = ctk.CTkFrame(
            parent, 
            fg_color=self.theme['bg_card'],
            corner_radius=12,  # Smaller, more refined
            border_width=1,
            border_color=self.theme['border_light']
        )
        header_card.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))  # Compact spacing
        
        # Header content frame with tight spacing
        header_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('lg'))  # Much tighter
        
        # Welcome message with refined typography
        user_name = f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}".strip()
        if not user_name:
            user_name = self.current_user.get('username', 'משתמש')
        
        welcome_text = f"שלום {user_name}"
        
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=welcome_text,
            font=self.theme_manager.create_ctk_font('hero'),  # Now much smaller (28px)
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        welcome_label.pack(anchor="e")
        
        # Current date with refined styling
        current_date = datetime.now().strftime("%d/%m/%Y")
        date_label = ctk.CTkLabel(
            header_frame,
            text=f"היום: {current_date}",
            font=self.theme_manager.create_ctk_font('helper'),  # Smaller font
            text_color=self.theme['text_muted'],
            anchor="e"
        )
        date_label.pack(anchor="e", pady=(self.theme_manager.get_spacing('xs'), 0))  # Tighter spacing
    
    def create_modern_stats_section(self, parent):
        """Create refined compact statistics cards section"""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))  # Compact spacing
        
        # Section title with refined typography
        title_label = ctk.CTkLabel(
            stats_frame,
            text="סקירה כללית",
            font=self.theme_manager.create_ctk_font('title'),  # Now 22px instead of 32px
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('lg')))  # Tighter spacing
        
        # Stats cards container
        cards_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        # Configure grid with tighter spacing
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create compact elegant stats cards with clean icons
        self.create_modern_stat_card(cards_frame, "לקוחות", "0", "●", 0, 0)       # Clean dot
        self.create_modern_stat_card(cards_frame, "הצעות מחיר", "0", "■", 0, 1)   # Clean square
        self.create_modern_stat_card(cards_frame, "הצעות החודש", "0", "▲", 0, 2)  # Clean triangle
        self.create_modern_stat_card(cards_frame, "משתמשים", "0", "◆", 0, 3)       # Clean diamond
    
    def create_modern_stat_card(self, parent, title: str, value: str, icon: str, row: int, col: int):
        """Create refined compact statistics card"""
        # Compact elegant card
        card = ctk.CTkFrame(
            parent,
            fg_color=self.theme['bg_card'],
            corner_radius=12,  # Smaller, more refined corners
            border_width=1,  # Thinner border
            border_color=self.theme['border_light']
        )
        card.grid(row=row, column=col, padx=self.theme_manager.get_spacing('md'), 
                 pady=self.theme_manager.get_spacing('md'), sticky="ew")  # Tighter spacing
        
        # Subtle hover effects
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
        
        # Clean, minimal icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=16),  # Much smaller, refined icon
            text_color=self.theme['primary']
        )
        icon_label.pack(pady=(self.theme_manager.get_spacing('lg'), self.theme_manager.get_spacing('sm')))  # Tighter spacing
        
        # Compact value with refined typography
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=self.theme_manager.create_ctk_font('stat_number'),  # Using new stat_number (24px)
            text_color=self.theme['primary']
        )
        value_label.pack()
        
        # Compact title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=self.theme_manager.create_ctk_font('stat_label'),  # Using new stat_label (13px)
            text_color=self.theme['text_muted']
        )
        title_label.pack(pady=(self.theme_manager.get_spacing('xs'), self.theme_manager.get_spacing('lg')))  # Tighter spacing
        
        # Store reference for updating
        setattr(self, f"stat_{title.replace(' ', '_')}_value", value_label)
    
    def create_modern_quick_actions(self, parent):
        """Create refined compact quick actions section"""
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))  # Compact spacing
        
        # Section title with refined typography
        title_label = ctk.CTkLabel(
            actions_frame,
            text="פעולות מהירות",
            font=self.theme_manager.create_ctk_font('title'),  # Now 22px instead of 32px
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('lg')))  # Tighter spacing
        
        # Actions container
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Configure grid with tighter spacing
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Refined compact action buttons with clean icons
        self.create_modern_action_button(
            buttons_frame, 
            "הצעת מחיר חדשה", 
            "+", 
            self.new_quote_action,
            0, 0
        )
        
        self.create_modern_action_button(
            buttons_frame,
            "לקוח חדש",
            "◎",
            self.new_customer_action,
            0, 1
        )
        
        self.create_modern_action_button(
            buttons_frame,
            "עיון בקטלוג",
            "≡",
            self.view_catalog_action,
            0, 2
        )
    
    def create_modern_action_button(self, parent, text: str, icon: str, command, row: int, col: int):
        """Create refined compact action button"""
        button = ctk.CTkButton(
            parent,
            text=f"{icon}  {text}",  # Horizontal layout instead of vertical
            font=self.theme_manager.create_ctk_font('card_title'),  # Now 16px instead of 18px
            height=60,  # Much smaller, more refined height
            fg_color=self.theme['primary'],
            hover_color=self.theme['primary_dark'],
            text_color="white",
            corner_radius=12,  # Smaller, more refined corners
            border_width=1,  # Thinner border
            border_color=self.theme['primary_light'],
            command=command
        )
        button.grid(row=row, column=col, 
                   padx=self.theme_manager.get_spacing('md'),  # Tighter spacing
                   pady=self.theme_manager.get_spacing('md'), 
                   sticky="ew")
    
    def create_modern_recent_activity(self, parent):
        """Create refined compact recent activity section"""
        activity_frame = ctk.CTkFrame(parent, fg_color="transparent")
        activity_frame.pack(fill="x", pady=(0, self.theme_manager.get_spacing('xl')))  # Compact spacing
        
        # Section title with refined typography
        title_label = ctk.CTkLabel(
            activity_frame,
            text="פעילות אחרונה",
            font=self.theme_manager.create_ctk_font('title'),  # Now 22px instead of 32px
            text_color=self.theme['text_primary'],
            anchor="e"
        )
        title_label.pack(anchor="e", pady=(0, self.theme_manager.get_spacing('lg')))  # Tighter spacing
        
        # Compact activity container with refined styling
        self.activity_container = ctk.CTkFrame(
            activity_frame, 
            fg_color=self.theme['bg_card'],
            border_width=1,  # Thinner border
            border_color=self.theme['border_light'],
            corner_radius=12  # Smaller, more refined corners
        )
        self.activity_container.pack(fill="x")
        
        # Placeholder with refined styling
        placeholder_label = ctk.CTkLabel(
            self.activity_container,
            text="טוען פעילות אחרונה...",
            font=self.theme_manager.create_ctk_font('body'),
            text_color=self.theme['text_muted']
        )
        placeholder_label.pack(pady=self.theme_manager.get_spacing('xl'))  # Much tighter spacing
    
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
        """Update activity display with beautiful professional styling"""
        try:
            # Clear current content
            for widget in self.activity_container.winfo_children():
                widget.destroy()
            
            if not recent_quotes:
                # Beautiful modern empty state
                empty_frame = ctk.CTkFrame(self.activity_container, fg_color="transparent")
                empty_frame.pack(fill="x", padx=self.theme_manager.get_spacing('xl'), pady=self.theme_manager.get_spacing('xl'))
                
                # Elegant empty icon with theme color
                empty_icon = ctk.CTkLabel(
                    empty_frame,
                    text="○",
                    font=ctk.CTkFont(size=28),
                    text_color=self.theme['primary_light']
                )
                empty_icon.pack()
                
                # Professional empty message
                no_activity_label = ctk.CTkLabel(
                    empty_frame,
                    text="אין פעילות אחרונה",
                    font=self.theme_manager.create_ctk_font('body'),
                    text_color=self.theme['text_muted']
                )
                no_activity_label.pack(pady=(self.theme_manager.get_spacing('sm'), 0))
                return
            
            # Create professional activity items with modern styling
            for i, quote in enumerate(recent_quotes):
                self.create_professional_activity_item(quote, i)
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error updating activity: {e}")
    
    def create_professional_activity_item(self, quote, index: int):
        """Create beautiful professional activity item with modern CRM-style design"""
        try:
            # Professional modern activity card with elegant styling
            item_frame = ctk.CTkFrame(
                self.activity_container, 
                fg_color=self.theme['bg_card'],  # Clean white background
                border_width=1,
                border_color=self.theme['border_light'],
                corner_radius=10  # Elegant rounded corners
            )
            item_frame.pack(fill="x", 
                          padx=self.theme_manager.get_spacing('lg'), 
                          pady=self.theme_manager.get_spacing('xs'))  # Compact but elegant spacing
            
            # Beautiful hover effects with smooth transitions
            def on_enter(event):
                item_frame.configure(
                    border_color=self.theme['primary'],
                    fg_color=self.theme['primary_ultra_light']
                )
            
            def on_leave(event):
                item_frame.configure(
                    border_color=self.theme['border_light'],
                    fg_color=self.theme['bg_card']
                )
            
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            
            # Main content area with professional layout
            main_content = ctk.CTkFrame(item_frame, fg_color="transparent")
            main_content.pack(fill="x", padx=self.theme_manager.get_spacing('lg'), pady=self.theme_manager.get_spacing('md'))
            
            # Create left side with status indicator and content
            left_frame = ctk.CTkFrame(main_content, fg_color="transparent")
            left_frame.pack(fill="x", side="right")  # RTL layout
            
            # Status indicator (beautiful colored dot)
            status_dot = ctk.CTkLabel(
                left_frame,
                text="●",
                font=ctk.CTkFont(size=14),
                text_color=self.theme['primary']
            )
            status_dot.pack(side="right", padx=(self.theme_manager.get_spacing('md'), 0))
            
            # Content container
            content_container = ctk.CTkFrame(left_frame, fg_color="transparent")
            content_container.pack(side="right", fill="x", expand=True)
            
            # Get customer information
            try:
                customer = self.db_manager.get_customer_by_id(quote.get('customer_id'))
                customer_name = customer['name'] if customer else "לקוח לא ידוע"
            except:
                customer_name = "לקוח לא ידוע"
            
            # Primary information - Quote details with beautiful typography
            quote_info = f"הצעת מחיר #{quote.get('quote_number', 'N/A')}"
            
            quote_label = ctk.CTkLabel(
                content_container,
                text=quote_info,
                font=self.theme_manager.create_ctk_font('card_title'),  # Slightly larger for hierarchy
                text_color=self.theme['text_primary'],
                anchor="e"
            )
            quote_label.pack(anchor="e", fill="x")
            
            # Secondary information - Customer name with elegant styling
            customer_label = ctk.CTkLabel(
                content_container,
                text=f"לקוח: {customer_name}",
                font=self.theme_manager.create_ctk_font('body'),
                text_color=self.theme['text_secondary'],
                anchor="e"
            )
            customer_label.pack(anchor="e", fill="x", pady=(self.theme_manager.get_spacing('xs'), 0))
            
            # Timestamp with refined styling
            if quote.get('created_at'):
                try:
                    if isinstance(quote['created_at'], str):
                        created_at = datetime.fromisoformat(quote['created_at'])
                    else:
                        created_at = quote['created_at']
                    
                    # Calculate relative time for better UX
                    now = datetime.now()
                    time_diff = now - created_at
                    
                    if time_diff.days == 0:
                        if time_diff.seconds < 3600:  # Less than 1 hour
                            time_text = f"לפני {time_diff.seconds // 60} דקות"
                        else:  # Less than 24 hours
                            time_text = f"לפני {time_diff.seconds // 3600} שעות"
                    elif time_diff.days == 1:
                        time_text = "אתמול"
                    elif time_diff.days < 7:
                        time_text = f"לפני {time_diff.days} ימים"
                    else:
                        time_text = created_at.strftime("%d/%m/%Y")
                    
                    time_label = ctk.CTkLabel(
                        content_container,
                        text=time_text,
                        font=self.theme_manager.create_ctk_font('caption'),
                        text_color=self.theme['text_muted'],
                        anchor="e"
                    )
                    time_label.pack(anchor="e", fill="x", pady=(self.theme_manager.get_spacing('xs'), 0))
                    
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Error formatting date: {e}")
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error creating professional activity item: {e}")
    
    def create_activity_item(self, quote):
        """Legacy method - redirects to professional version"""
        self.create_professional_activity_item(quote, 0)
    
    def handle_activity_error(self, error: str):
        """Handle activity loading error"""
        import logging
        logging.getLogger(__name__).error(f"Activity loading error: {error}")
    
    def new_quote_action(self):
        """Handle new quote action - open Quote Wizard"""
        from ui.pages.quote_wizard import QuoteWizard
        wizard = QuoteWizard(
            parent=self.parent.winfo_toplevel(),
            db_manager=self.db_manager,
            current_user=self.current_user,
            on_success=lambda: messagebox.showinfo("הצלחה", "הצעת מחיר נוצרה")
        )

    def new_customer_action(self):
        """Handle new customer action - open Customer dialog"""
        from ui.pages.customers import CustomerDialog
        dialog = CustomerDialog(
            parent=self.parent.winfo_toplevel(),
            title="הוסף לקוח חדש",
            customer_data=None,
            db_manager=self.db_manager,
            on_success=lambda: messagebox.showinfo("הצלחה", "לקוח נוצר בהצלחה")
        )

    def view_catalog_action(self):
        """Navigate to catalog page in dashboard"""
        root = self.parent.winfo_toplevel()
        if hasattr(root, 'show_catalog_page'):
            try:
                root.show_catalog_page()
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בפתיחת הקטלוג: {e}")
        else:
            messagebox.showinfo("פעולה", "לא ניתן לפתוח קטלוג" ) 