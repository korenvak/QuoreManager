"""
Permissions Utility for Kitchen Quote Management System
Provides comprehensive permission checking and validation functions
"""

from typing import Dict, Any, Optional
from core.auth import AuthManager

class PermissionManager:
    """Centralized permission management"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.auth_manager = AuthManager(db_manager)
    
    def check_user_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Check if user has a specific permission"""
        if not user or not user.get('is_active', False):
            return False
        
        return self.auth_manager.has_permission(user, permission)
    
    def can_edit_quote(self, user: Dict[str, Any], quote_id: int) -> bool:
        """Check if user can edit a specific quote"""
        if not user:
            return False
        
        # Admin and manager can edit any quote
        if user.get('role') in ['admin', 'manager']:
            return True
        
        # Check if user created the quote
        return self.db_manager.can_user_edit_quote(user['id'], quote_id)
    
    def can_edit_quote_with_discount(self, user: Dict[str, Any], quote_id: int) -> bool:
        """Check if user can edit a quote considering its current discount"""
        if not user:
            return False
        if user.get('role') in ['admin', 'manager']:
            return True
        if user.get('role') == 'employee':
            try:
                # Use the database manager's session to get quote data
                with self.db_manager.get_session() as session:
                    from database.models import Quote
                    quote = session.query(Quote).filter_by(id=quote_id).first()
                    if not quote:
                        return False
                    
                    quote_discount = float(quote.regular_discount or 0)
                    user_max_discount = float(user.get('max_discount', 0) or 0)
                    result = quote_discount <= user_max_discount
                    return result
            except Exception as e:
                return False
        return False
    
    def can_delete_quote(self, user: Dict[str, Any], quote_id: int) -> bool:
        """Check if user can delete a specific quote"""
        if not user:
            return False
        
        # Only admin can delete quotes
        if user.get('role') == 'admin':
            return True
        
        return False
    
    def can_edit_draft(self, user: Dict[str, Any], draft) -> bool:
        """Check if user can edit a specific draft"""
        if not user:
            return False
        
        # Admin can edit everything
        if user.get('role') == 'admin':
            return True
        
        # Manager can edit any draft
        if user.get('role') == 'manager':
            return True
        
        # Employee can edit any draft that doesn't exceed their discount limit
        if user.get('role') == 'employee':
            # Check discount permissions
            try:
                draft_state = draft.state if hasattr(draft, 'state') else draft.get('state')
                if isinstance(draft_state, str):
                    import json
                    draft_state = json.loads(draft_state)
                
                # Check if the draft state has quote_data with regular_discount
                if isinstance(draft_state, dict) and 'quote_data' in draft_state:
                    quote_data = draft_state['quote_data']
                    if isinstance(quote_data, dict):
                        draft_discount = float(quote_data.get('regular_discount', 0))
                        user_max_discount = float(user.get('max_discount', 0))
                        return draft_discount <= user_max_discount
                
                return True  # If can't parse discount, allow editing
            except:
                return True  # If can't parse, allow editing
        
        # Other roles (like viewer) cannot edit drafts
        return False
    
    def can_apply_discount(self, user: Dict[str, Any], discount_percent: float) -> bool:
        """Check if user can apply the requested discount"""
        return self.auth_manager.can_apply_discount(user, discount_percent)
    
    def can_manage_users(self, user: Dict[str, Any]) -> bool:
        """Check if user can manage other users"""
        return self.check_user_permission(user, 'manage_users')
    
    def can_manage_catalog(self, user: Dict[str, Any]) -> bool:
        """Check if user can manage catalog"""
        return self.check_user_permission(user, 'manage_catalog')
    
    def can_manage_customers(self, user: Dict[str, Any]) -> bool:
        """Check if user can manage customers"""
        return self.check_user_permission(user, 'manage_customers')
    
    def can_create_quotes(self, user: Dict[str, Any]) -> bool:
        """Check if user can create quotes"""
        return self.check_user_permission(user, 'create_quotes')
    
    def can_edit_quotes(self, user: Dict[str, Any]) -> bool:
        """Check if user can edit quotes"""
        return self.check_user_permission(user, 'edit_quotes')
    
    def can_delete_quotes(self, user: Dict[str, Any]) -> bool:
        """Check if user can delete quotes"""
        return self.check_user_permission(user, 'delete_quotes')
    
    def can_view_all_quotes(self, user: Dict[str, Any]) -> bool:
        """Check if user can view all quotes"""
        return self.check_user_permission(user, 'view_all_quotes')
    
    def can_access_system_settings(self, user: Dict[str, Any]) -> bool:
        """Check if user can access system settings"""
        return self.check_user_permission(user, 'system_settings')
    
    def get_user_role_display_name(self, role: str) -> str:
        """Get display name for user role"""
        role_names = {
            'admin': 'מנהל מערכת',
            'manager': 'מנהל',
            'employee': 'עובד',
            'viewer': 'צופה'
        }
        return role_names.get(role, 'לא ידוע')
    
    def get_user_permissions_summary(self, user: Dict[str, Any]) -> Dict[str, bool]:
        """Get a summary of all user permissions"""
        if not user:
            return {}
        
        return {
            'can_create_quotes': self.can_create_quotes(user),
            'can_edit_quotes': self.can_edit_quotes(user),
            'can_delete_quotes': self.can_delete_quotes(user),
            'can_manage_customers': self.can_manage_customers(user),
            'can_manage_users': self.can_manage_users(user),
            'can_manage_catalog': self.can_manage_catalog(user),
            'can_view_all_quotes': self.can_view_all_quotes(user),
            'can_access_system_settings': self.can_access_system_settings(user),
            'has_unlimited_discount': self.auth_manager.has_permission(user, 'unlimited_discount'),
            'max_discount': user.get('max_discount', 0.0)
        }
    
    def validate_discount_permission(self, user: Dict[str, Any], discount_percent: float) -> tuple[bool, str]:
        """Validate discount permission and return (is_valid, error_message)"""
        if not user:
            return False, "משתמש לא תקין"
        
        if not self.can_apply_discount(user, discount_percent):
            max_discount = user.get('max_discount', 0.0)
            return False, f"ההנחה מוגבלת ל-{max_discount}% עבור התפקיד שלך"
        
        return True, ""
    
    def get_accessible_pages(self, user: Dict[str, Any]) -> list[str]:
        """Get list of pages user can access"""
        if not user:
            return []
        
        pages = ['overview']  # Everyone can access overview
        
        if self.can_create_quotes(user):
            pages.append('quotes')
            pages.append('drafts')
        
        if self.can_manage_customers(user):
            pages.append('customers')
        
        if self.can_manage_catalog(user):
            pages.append('catalog')
        
        if self.can_manage_users(user):
            pages.append('users')
        
        if self.can_access_system_settings(user):
            pages.append('settings')
        
        return pages 