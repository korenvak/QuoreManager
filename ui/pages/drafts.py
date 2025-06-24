"""
Drafts Management Page for Kitchen Quote Management System
Shows all drafts with age grouping, permission checks, and management options
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.permissions import PermissionManager

class DraftsPage:
    """Drafts management page with age grouping and permission checks"""
    
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        self.drafts_data = []
        self.היום_container = None  # For linter
        self.ישן_יותר_container = None  # For linter
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(db_manager)
        
    def create_content(self):
        """Create drafts page content
        NOTE: Only the main_frame uses pack() on self.parent. All children use pack() on their respective parents.
        Do NOT use grid() on self.parent or any direct child of self.parent.
        """
        # Main container with white background
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#FFFFFF",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True)  # Use pack instead of grid
        
        # All children of main_frame use pack()
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Page header
        self.create_header(content_frame)
        
        # Draft groups (Today, Older)
        self.create_draft_groups(content_frame)
        
        # Load drafts data after UI is fully set up
        # Load drafts data
        self.load_drafts_data()
    
    def create_header(self, parent):
        """Create page header with actions"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="טיוטות הצעות מחיר",
            font=ctk.CTkFont(family="Assistant", size=32, weight="bold"),
            text_color="#1F2937",
            anchor="e"
        )
        title_label.pack(anchor="e")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(anchor="e", pady=(10, 0))
        
        # Cleanup old drafts button (admin only)
        if self.current_user.get('role') == 'admin':
            cleanup_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️ נקה טיוטות ישנות",
                font=ctk.CTkFont(family="Assistant", size=14),
                height=35,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=self.cleanup_old_drafts
            )
            cleanup_btn.pack(side="right", padx=(0, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 רענן",
            font=ctk.CTkFont(family="Assistant", size=14),
            height=35,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.load_drafts_data
        )
        refresh_btn.pack(side="right")
    
    def create_draft_groups(self, parent):
        """Create draft groups by age (only today and older)"""
        self.groups_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.groups_container.pack(fill="both", expand=True)
        
        # Create group containers
        self.today_frame = self.create_group_section("היום", "#10B981")
        self.older_frame = self.create_group_section("ישן יותר", "#EF4444")
    
    def create_group_section(self, title: str, color: str):
        """Create a group section for drafts"""
        print(f"create_group_section called with title={title!r}")
        # Group container
        group_frame = ctk.CTkFrame(
            self.groups_container,
            fg_color="#FAFBFF",
            corner_radius=15,
            border_width=1,
            border_color="#E1E8F7"
        )
        group_frame.pack(fill="x", pady=(0, 20))
        
        # Group header
        header_frame = ctk.CTkFrame(group_frame, fg_color=color, corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=15)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Assistant", size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=10)
        
        # Drafts container
        drafts_container = ctk.CTkFrame(group_frame, fg_color="transparent")
        drafts_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Store reference based on title
        if title == "היום":
            print("Setting self.היום_container")
            self.היום_container = drafts_container
        elif title == "ישן יותר":
            print("Setting self.ישן_יותר_container")
            self.ישן_יותר_container = drafts_container
        else:
            print(f"Unknown title: {title!r}")
        
        return group_frame
    
    def load_drafts_data(self):
        """Load drafts data in background"""
        def load_data():
            try:
                # Get all drafts or user-specific drafts based on role
                if self.current_user.get('role') in ['admin', 'manager', 'employee']:
                    drafts = self.db_manager.get_all_drafts()
                else:
                    drafts = self.db_manager.get_drafts_by_user(self.current_user['id'])
                
                # Process drafts data
                processed_drafts = []
                
                for draft in drafts:
                    
                    # Get draft details
                    draft_id = draft.id if hasattr(draft, 'id') else draft.get('id')
                    customer_id = draft.customer_id if hasattr(draft, 'customer_id') else draft.get('customer_id')
                    step = draft.step if hasattr(draft, 'step') else draft.get('step')
                    
                    # Get customer name
                    customer_name = "לקוח לא ידוע"
                    if customer_id:
                        customer = self.db_manager.get_customer_by_id(customer_id)
                        if customer:
                            customer_name = customer.name if hasattr(customer, 'name') else customer.get('name', 'לקוח לא ידוע')
                    
                    # Get creator name
                    creator_name = "משתמש לא ידוע"
                    created_by = draft.created_by if hasattr(draft, 'created_by') else draft.get('created_by')
                    if created_by:
                        creator = self.db_manager.get_user_by_id(created_by)
                        if creator:
                            first_name = creator.first_name if hasattr(creator, 'first_name') else creator.get('first_name', '')
                            last_name = creator.last_name if hasattr(creator, 'last_name') else creator.get('last_name', '')
                            creator_name = f"{first_name} {last_name}".strip() or creator.username
                    
                    # Get last modified
                    last_modified = draft.last_modified if hasattr(draft, 'last_modified') else draft.get('last_modified', datetime.now())
                    
                    # Calculate age
                    age_days = (datetime.now() - last_modified).days
                    
                    # Check if user can edit this draft
                    can_edit = self.permission_manager.can_edit_draft(self.current_user, draft)
                    
                    # Get draft state for additional info
                    draft_state = draft.state if hasattr(draft, 'state') else draft.get('state', {})
                    
                    draft_info = {
                        'id': draft_id,
                        'customer_name': customer_name,
                        'creator_name': creator_name,
                        'step': step,
                        'last_modified': last_modified,
                        'age_days': age_days,
                        'can_edit': can_edit,
                        'draft_data': draft_state,
                        'age_group': 'today' if age_days == 0 else 'older'
                    }
                    
                    processed_drafts.append(draft_info)
                
                # Update UI in main thread
                self.drafts_data = processed_drafts
                self.parent.after(0, self.display_drafts)
                
            except Exception as e:
                # Update UI with error in main thread
                self.parent.after(0, lambda: self.handle_drafts_error(str(e)))
        
        # Run in background thread
        threading.Thread(target=load_data, daemon=True).start()
    
    def get_age_group(self, age_days: int) -> str:
        """Get age group for draft (only today and older)"""
        if age_days == 0:
            return "today"
        else:
            return "older"
    
    def can_user_edit_draft(self, draft) -> bool:
        """Check if current user can edit this draft"""
        return self.permission_manager.can_edit_draft(self.current_user, draft)
    
    def get_user_name(self, user_id: int) -> str:
        """Get user display name"""
        try:
            user = self.db_manager.get_user_by_id(user_id)
            if user:
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                return full_name if full_name else user.get('username', 'משתמש לא ידוע')
            return "משתמש לא ידוע"
        except:
            return "משתמש לא ידוע"
    
    def display_drafts(self):
        """Display drafts in appropriate groups"""
        try:
            # Clear existing drafts more carefully
            for container_name in ['היום_container', 'ישן_יותר_container']:
                if hasattr(self, container_name):
                    container = getattr(self, container_name)
                    if container and container.winfo_exists():
                        # Destroy all children widgets
                        for widget in container.winfo_children():
                            try:
                                widget.destroy()
                            except:
                                pass  # Ignore errors during destruction
            
            # Group drafts by age
            groups = {'today': [], 'older': []}
            for draft in self.drafts_data:
                groups[draft['age_group']].append(draft)
            
            # Display each group
            if self.היום_container and self.היום_container.winfo_exists():
                self.display_group_drafts(self.היום_container, groups['today'], "אין טיוטות מהיום")
                
            if self.ישן_יותר_container and self.ישן_יותר_container.winfo_exists():
                self.display_group_drafts(self.ישן_יותר_container, groups['older'], "אין טיוטות ישנות")
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error displaying drafts: {e}")
            import traceback
            traceback.print_exc()
    
    def display_group_drafts(self, container, drafts: List[Dict], empty_message: str):
        """Display drafts in a specific group"""
        try:
            if not container or not container.winfo_exists():
                return
                
            if not drafts:
                empty_label = ctk.CTkLabel(
                    container,
                    text=empty_message,
                    font=ctk.CTkFont(family="Assistant", size=14),
                    text_color="gray"
                )
                empty_label.pack(pady=20)
                return
            
            for draft in drafts:
                self.create_draft_card(container, draft)
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error displaying group drafts: {e}")
            import traceback
            traceback.print_exc()
    
    def create_draft_card(self, parent, draft: Dict):
        """Create individual draft card with white background"""
        try:
            if not parent or not parent.winfo_exists():
                return
                
            # Determine card color based on age and permissions
            if not draft['can_edit']:
                bg_color = "#FEE2E2"  # Light red
                border_color = "#EF4444"
            elif draft['age_days'] == 0:
                bg_color = "#FFFFFF"  # White
                border_color = "#10B981"
            else:
                bg_color = "#FFFFFF"  # White
                border_color = "#EF4444"
            
            card = ctk.CTkFrame(
                parent,
                fg_color=bg_color,
                border_width=1,
                border_color=border_color,
                corner_radius=15
            )
            card.pack(fill="x", padx=10, pady=5)
            
            # Add hover effect
            def on_enter(event):
                card.configure(border_color="#3B82F6")
            
            def on_leave(event):
                card.configure(border_color=border_color)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            
            # Card content
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=20, pady=15)
            
            # Top row: Customer name and actions
            top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            top_frame.pack(fill="x")
            
            # Customer name
            customer_label = ctk.CTkLabel(
                top_frame,
                text=draft['customer_name'],
                font=ctk.CTkFont(family="Assistant", size=16, weight="bold"),
                text_color="#1F2937",
                anchor="e"
            )
            customer_label.pack(side="right")
            
            # Permission lock icon
            if not draft['can_edit']:
                lock_icon = ctk.CTkLabel(
                    top_frame,
                    text="🔒",
                    font=ctk.CTkFont(size=16)
                )
                lock_icon.pack(side="right", padx=(10, 0))
            
            # Action buttons
            actions_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            actions_frame.pack(side="left")
            
            # Button configuration
            button_config = {
                'width': 80,
                'height': 32,
                'font': ctk.CTkFont(family="Assistant", size=12, weight="bold"),
                'corner_radius': 8
            }
            
            if draft['can_edit']:
                continue_btn = ctk.CTkButton(
                    actions_frame,
                    text="המשך",
                    fg_color="#3B82F6",
                    hover_color="#1E40AF",
                    command=lambda d=draft: self.continue_draft(d),
                    **button_config
                )
                continue_btn.pack(side="left", padx=(0, 5))
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="מחק",
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda d=draft: self.delete_draft(d),
                **button_config
            )
            delete_btn.pack(side="left")
            
            # Details row
            details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            details_frame.pack(fill="x", pady=(10, 0))
            
            # Step info
            step_text = f"שלב {draft['step']} מתוך 4"
            step_label = ctk.CTkLabel(
                details_frame,
                text=step_text,
                font=ctk.CTkFont(family="Assistant", size=12),
                text_color="#6B7280",
                anchor="e"
            )
            step_label.pack(anchor="e")
            
            # Creator and time
            time_str = draft['last_modified'].strftime("%d/%m/%Y %H:%M")
            creator_text = f"נוצר על ידי: {draft['creator_name']} | עודכן: {time_str}"
            
            creator_label = ctk.CTkLabel(
                details_frame,
                text=creator_text,
                font=ctk.CTkFont(family="Assistant", size=10),
                text_color="#6B7280",
                anchor="e"
            )
            creator_label.pack(anchor="e", pady=(2, 0))
            
            # Permission message
            if not draft['can_edit']:
                permission_label = ctk.CTkLabel(
                    details_frame,
                    text="הטיוטה מכילה הנחות החורגות מההרשאות שלך",
                    font=ctk.CTkFont(family="Assistant", size=10),
                    text_color="#EF4444",
                    anchor="e"
                )
                permission_label.pack(anchor="e", pady=(5, 0))
                
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error creating draft card: {e}")
    
    def continue_draft(self, draft: Dict):
        """Continue editing a draft"""
        try:
            # Check permissions before allowing edit
            if not self.permission_manager.can_edit_draft(self.current_user, draft):
                messagebox.showerror("הרשאה נדרשת", "אין לך הרשאה לערוך טיוטה זו")
                return
            
            # Import here to avoid circular imports
            from ui.pages.quote_wizard import QuoteWizard
            
            def on_success():
                self.load_drafts_data()  # Refresh drafts
            
            # Create quote wizard with existing draft
            QuoteWizard(
                parent=self.parent.winfo_toplevel(),
                db_manager=self.db_manager,
                current_user=self.current_user,
                on_success=on_success,
                existing_draft=draft
            )
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בפתיחת הטיוטה: {e}")
    
    def delete_draft(self, draft: Dict):
        """Delete a draft"""
        result = messagebox.askyesno(
            "מחיקת טיוטה",
            f"האם אתה בטוח שברצונך למחוק את הטיוטה עבור {draft['customer_name']}?\n\nפעולה זו אינה ניתנת לביטול."
        )
        
        if result:
            try:
                success = self.db_manager.delete_draft_by_id(draft['id'])
                if success:
                    messagebox.showinfo("הצלחה", "הטיוטה נמחקה בהצלחה")
                    self.load_drafts_data()  # Refresh
                else:
                    messagebox.showerror("שגיאה", "שגיאה במחיקת הטיוטה")
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה במחיקת הטיוטה: {e}")
    
    def cleanup_old_drafts(self):
        """Cleanup drafts older than 30 days (admin only)"""
        if self.current_user.get('role') != 'admin':
            messagebox.showerror("שגיאה", "רק מנהל מערכת יכול לבצע ניקוי טיוטות")
            return
        
        result = messagebox.askyesno(
            "ניקוי טיוטות ישנות",
            "האם אתה בטוח שברצונך למחוק את כל הטיוטות שישנות מ-30 ימים?\n\nפעולה זו אינה ניתנת לביטול."
        )
        
        if result:
            try:
                count = self.db_manager.cleanup_old_drafts(30)
                messagebox.showinfo("הצלחה", f"נמחקו {count} טיוטות ישנות")
                self.load_drafts_data()  # Refresh
            except Exception as e:
                messagebox.showerror("שגיאה", f"שגיאה בניקוי טיוטות: {e}")
    
    def handle_drafts_error(self, error: str):
        """Handle drafts loading error"""
        messagebox.showerror("שגיאה", f"שגיאה בטעינת טיוטות: {error}") 