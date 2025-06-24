#!/usr/bin/env python3
"""
Kitchen Quote Management System
Main Entry Point

A comprehensive desktop application for managing kitchen quotes with customer management,
quote creation, PDF generation, and user permissions.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import customtkinter as ctk
    from tkinter import messagebox
    import sqlite3
    from datetime import datetime
    
    # Import application modules
    from database.db_manager import DatabaseManager
    from core.auth import AuthManager
    from ui.login import LoginWindow
    from ui.dashboard import DashboardWindow
    from config.settings import SettingsManager
    from utils.logger import setup_logging
    
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"Missing required dependencies: {e}")
    sys.exit(1)

class KitchenQuoteApp:
    """Main application controller"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Kitchen Quote Management System")
        
        # Initialize core components
        self.settings_manager = SettingsManager()
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        
        # UI components
        self.login_window = None
        self.dashboard_window = None
        self.current_user = None
        
        # Configure customtkinter
        ctk.set_appearance_mode(self.settings_manager.get('theme_mode', 'light'))
        ctk.set_default_color_theme('blue')
        
    def setup_logging(self):
        """Setup application logging"""
        setup_logging()
        
    def run(self):
        """Start the application"""
        try:
            # Initialize database
            self.db_manager.initialize_database()
            
            # Cleanup old drafts (auto-delete drafts older than 30 days)
            try:
                removed_count = self.db_manager.cleanup_old_drafts(days_old=30)
                if removed_count:
                    self.logger.info(f"Auto-cleanup removed {removed_count} old drafts")
            except Exception as cleanup_err:
                self.logger.warning(f"Draft auto-cleanup failed: {cleanup_err}")
            
            # Check if this is first run (no admin user exists)
            if self.auth_manager.is_first_run():
                self.show_first_run_setup()
            else:
                self.show_login()
                
        except Exception as e:
            self.logger.error(f"Failed to start application: {e}")
            messagebox.showerror("Error", f"Failed to start application: {e}")
            sys.exit(1)
    
    def show_first_run_setup(self):
        """Show first-run setup to create admin user"""
        from ui.first_run import FirstRunSetup
        
        def on_setup_complete(admin_user):
            self.logger.info("First run setup completed")
            self.current_user = admin_user
            self.show_dashboard()
        
        setup_window = FirstRunSetup(
            auth_manager=self.auth_manager,
            on_complete=on_setup_complete
        )
        setup_window.show()
    
    def show_login(self):
        """Show login window"""
        def on_login_success(user):
            self.current_user = user
            self.logger.info(f"User {user['username']} logged in successfully")
            if self.login_window:
                self.login_window.destroy()
            self.show_dashboard()
        
        def on_login_error(error):
            self.logger.warning(f"Login failed: {error}")
        
        self.login_window = LoginWindow(
            auth_manager=self.auth_manager,
            settings_manager=self.settings_manager,
            on_success=on_login_success,
            on_error=on_login_error
        )
        self.login_window.show()
    
    def show_dashboard(self):
        """Show main dashboard"""
        if self.dashboard_window and self.dashboard_window.window:
            try:
                self.dashboard_window.window.destroy()
            except Exception:
                pass  # Window might already be destroyed
            
        def on_logout():
            if self.current_user:
                self.logger.info(f"User {self.current_user['username']} logged out")
            self.current_user = None
            if self.dashboard_window and self.dashboard_window.window:
                try:
                    self.dashboard_window.window.destroy()
                except Exception:
                    pass  # Window might already be destroyed
            self.show_login()
        
        def on_switch_user():
            if self.current_user:
                self.logger.info(f"User {self.current_user['username']} switching users")
            self.current_user = None
            if self.dashboard_window and self.dashboard_window.window:
                try:
                    self.dashboard_window.window.destroy()
                except Exception:
                    pass  # Window might already be destroyed
            self.show_login()
        
        # Ensure current_user is not None before creating DashboardWindow
        if self.current_user is None:
            self.logger.error("Cannot show dashboard: current_user is None")
            return
            
        self.dashboard_window = DashboardWindow(
            current_user=self.current_user,
            db_manager=self.db_manager,
            settings_manager=self.settings_manager,
            on_logout=on_logout,
            on_switch_user=on_switch_user
        )
        self.dashboard_window.show()

def main():
    """Application entry point"""
    app = KitchenQuoteApp()
    app.run()

if __name__ == "__main__":
    main() 