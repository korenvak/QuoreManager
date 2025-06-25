"""
Authentication Manager for Kitchen Quote Management System
Handles user authentication, password hashing, and session management
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database.db_manager import DatabaseManager

class AuthManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.active_sessions = {}  # In-memory session storage
        
    def is_first_run(self) -> bool:
        """Check if this is the first run (no users exist)"""
        return not self.db_manager.user_exists()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        # Generate a random salt
        salt = secrets.token_hex(16)
        
        # Create hash
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Return salt + hash for storage
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_value = stored_hash.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == hash_value
        except ValueError:
            # Handle legacy hashes without salt
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    
    def create_admin_user(self, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """Create the first admin user"""
        try:
            password_hash = self.hash_password(password)
            
            # Set default admin permissions
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'role': 'admin',
                'max_discount': 100.0,  # Admin has unlimited discount
                'is_active': True,
                **kwargs
            }
            
            user_dict = self.db_manager.create_user(**user_data)
            
            # Log the action - user_dict already contains the id
            self.db_manager.log_action(
                user_id=user_dict['id'],
                action='create_admin_user',
                entity_type='user',
                entity_id=user_dict['id'],
                details={'username': username}
            )
            
            self.logger.info(f"Admin user created: {username}")
            
            # Return user dict for session (already a dict)
            return user_dict
            
        except Exception as e:
            self.logger.error(f"Failed to create admin user: {e}")
            raise
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and create session"""
        try:
            with self.db_manager.get_session() as session:
                from database.models import User
                
                # Get user within session context
                user = session.query(User).filter(User.username == username).first()
                
                if not user:
                    self.logger.warning(f"Authentication failed: user not found - {username}")
                    return None
                
                if not user.is_active:
                    self.logger.warning(f"Authentication failed: user inactive - {username}")
                    return None
                
                if not self.verify_password(password, user.password_hash):
                    self.logger.warning(f"Authentication failed: invalid password - {username}")
                    return None
                
                # Update last login within the same session
                user.last_login = datetime.utcnow()
                
                # Convert to dict while user is still attached to session
                user_dict = self._user_to_dict(user)
                user_id = user.id
                
                # Commit the session here to save last_login
                session.commit()
            
            # Create session (outside db session to avoid confusion)
            session_id = secrets.token_urlsafe(32)
            user_dict['session_id'] = session_id
            
            # Store session with expiration
            self.active_sessions[session_id] = {
                'user': user_dict,
                'created_at': datetime.utcnow(),
                'last_activity': datetime.utcnow()
            }
            
            # Log successful login
            self.db_manager.log_action(
                user_id=user_id,
                action='login',
                entity_type='user',
                entity_id=user_id,
                details={'username': username}
            )
            
            self.logger.info(f"User authenticated successfully: {username}")
            return user_dict
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            if session_id in self.active_sessions:
                user_data = self.active_sessions[session_id]['user']
                
                # Log logout
                self.db_manager.log_action(
                    user_id=user_data['id'],
                    action='logout',
                    entity_type='user',
                    entity_id=user_data['id'],
                    details={'username': user_data['username']}
                )
                
                # Remove session
                del self.active_sessions[session_id]
                
                self.logger.info(f"User logged out: {user_data['username']}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return False
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and refresh session"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session_data = self.active_sessions[session_id]
            
            # Check session timeout
            timeout_minutes = self.db_manager.get_setting('session_timeout_minutes', 120)
            timeout_delta = timedelta(minutes=timeout_minutes)
            
            if datetime.utcnow() - session_data['last_activity'] > timeout_delta:
                # Session expired
                del self.active_sessions[session_id]
                self.logger.info(f"Session expired: {session_data['user']['username']}")
                return None
            
            # Update last activity
            session_data['last_activity'] = datetime.utcnow()
            
            return session_data['user']
            
        except Exception as e:
            self.logger.error(f"Session validation error: {e}")
            return None
    
    def create_user(self, username: str, password: str, role: str, max_discount: float = 0.0, **kwargs) -> bool:
        """Create a new user (admin only)"""
        try:
            password_hash = self.hash_password(password)
            
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'role': role,
                'max_discount': max_discount,
                'is_active': True,
                **kwargs
            }
            
            user = self.db_manager.create_user(**user_data)
            
            self.logger.info(f"User created: {username} with role {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create user {username}: {e}")
            return False
    
    def get_role_permissions(self, role: str) -> Dict[str, bool]:
        """Get permissions for a role - Simplified for Version 2.0 (admin/user only)"""
        permissions = {
            'admin': {
                'create_quotes': True,
                'edit_quotes': True,
                'delete_quotes': True,
                'manage_customers': True,
                'manage_users': True,
                'manage_catalog': True,
                'unlimited_discount': True,
                'view_all_quotes': True,
                'view_all_drafts': True,
                'system_settings': True,
                'approve_restricted_items': True
            },
            'user': {
                'create_quotes': True,
                'edit_quotes': True,  # Can edit their own quotes
                'delete_quotes': False,  # Cannot delete quotes
                'manage_customers': True,
                'manage_users': False,
                'manage_catalog': False,
                'unlimited_discount': False,
                'view_all_quotes': False,  # Can only see own quotes
                'view_all_drafts': False,  # Can only see own drafts
                'system_settings': False,
                'approve_restricted_items': False
            }
        }
        
        # Default to 'user' permissions for unknown roles
        return permissions.get(role, permissions['user'])
    
    def has_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Check if user has specific permission"""
        if not user or not user.get('is_active', False):
            return False
        
        role = user.get('role', 'viewer')
        permissions = self.get_role_permissions(role)
        
        return permissions.get(permission, False)
    
    def can_apply_discount(self, user: Dict[str, Any], discount_percent: float) -> bool:
        """Check if user can apply the requested discount"""
        if not user:
            return False
        
        max_discount = user.get('max_discount', 0.0)
        
        # Admin and unlimited discount roles can apply any discount
        if self.has_permission(user, 'unlimited_discount'):
            return True
        
        return discount_percent <= max_discount
    
    def _user_to_dict(self, user) -> Dict[str, Any]:
        """Convert user model to dictionary"""
        return {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'max_discount': user.max_discount,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        try:
            timeout_minutes = self.db_manager.get_setting('session_timeout_minutes', 120)
            timeout_delta = timedelta(minutes=timeout_minutes)
            current_time = datetime.utcnow()
            
            expired_sessions = [
                session_id for session_id, session_data in self.active_sessions.items()
                if current_time - session_data['last_activity'] > timeout_delta
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {e}")
    
    def get_active_users_count(self) -> int:
        """Get count of currently active users"""
        return len(self.active_sessions) 