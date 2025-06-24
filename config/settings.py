"""
Settings Manager for Kitchen Quote Management System
Handles application configuration and user preferences
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class SettingsManager:
    """Manages application settings and configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Set config file path
        if config_file is None:
            config_dir = Path(__file__).parent
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "settings.json"
        
        self.config_file = Path(config_file)
        self.settings = {}
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                self.logger.debug(f"Settings loaded from {self.config_file}")
            else:
                # Initialize with default settings
                self.settings = self.get_default_settings()
                self.save_settings()
                self.logger.info(f"Created default settings file at {self.config_file}")
                
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.settings = self.get_default_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Settings saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            # Application settings
            'app_name': 'מערכת ניהול הצעות מטבח',
            'app_version': '1.0.0',
            'language': 'he',  # Hebrew
            'rtl_mode': True,
            
            # UI settings
            'theme_mode': 'light',  # light, dark
            'window_width': 1400,
            'window_height': 900,
            'window_maximized': False,
            'sidebar_expanded': True,
            'font_family': 'Heebo',
            'font_size': 14,
            
            # Business settings
            'company_info': {
                'name': 'Panel Kitchens',
                'phone': '03-1234567',
                'email': 'info@panelkitchens.co.il',
                'address': 'רחוב הדקל 123, תל אביב',
                'website': 'www.panelkitchens.co.il',
                'tax_id': '123456789'
            },
            
            # Quote settings
            'vat_rate': 17.0,
            'quote_validity_days': 14,
            'default_payment_terms': 'תשלום 50% מראש, יתרה בהתקנה',
            'auto_save_interval': 30,  # seconds
            'max_images_per_quote': 2,
            
            # File paths
            'catalog_path': '',
            'quotes_output_dir': 'quotes',
            'backup_dir': 'backups',
            'temp_dir': 'temp',
            
            # Export settings
            'pdf_settings': {
                'watermark_enabled': True,
                'include_images': True,
                'page_size': 'A4',
                'orientation': 'portrait'
            },
            
            # Security settings
            'session_timeout_minutes': 120,
            'password_min_length': 6,
            'require_password_change': False,
            'max_login_attempts': 5,
            
            # Backup settings
            'auto_backup_enabled': True,
            'backup_interval_days': 1,
            'max_backups_keep': 30,
            
            # Logging settings
            'log_level': 'INFO',
            'log_file_max_size': 10485760,  # 10MB
            'log_files_keep': 5,
            
            # Feature flags
            'features': {
                'email_integration': False,
                'cloud_sync': False,
                'advanced_reporting': True,
                'multi_currency': False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value with dot notation support"""
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            value = self.settings
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting setting {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """Set setting value with dot notation support"""
        try:
            # Support dot notation for nested keys
            keys = key.split('.')
            current = self.settings
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set the value
            current[keys[-1]] = value
            
            if save:
                self.save_settings()
                
            self.logger.debug(f"Setting {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting {key}: {e}")
    
    def update(self, settings_dict: Dict[str, Any], save: bool = True):
        """Update multiple settings"""
        try:
            for key, value in settings_dict.items():
                self.set(key, value, save=False)
            
            if save:
                self.save_settings()
                
        except Exception as e:
            self.logger.error(f"Error updating settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.get_default_settings()
        self.save_settings()
        self.logger.info("Settings reset to defaults")
    
    def get_company_info(self) -> Dict[str, str]:
        """Get company information"""
        return self.get('company_info', {})
    
    def set_company_info(self, info: Dict[str, str]):
        """Set company information"""
        self.set('company_info', info)
    
    def get_theme_settings(self) -> Dict[str, Any]:
        """Get UI theme settings"""
        return {
            'theme_mode': self.get('theme_mode', 'light'),
            'font_family': self.get('font_family', 'Heebo'),
            'font_size': self.get('font_size', 14),
            'sidebar_expanded': self.get('sidebar_expanded', True)
        }
    
    def set_theme_settings(self, theme_settings: Dict[str, Any]):
        """Set UI theme settings"""
        for key, value in theme_settings.items():
            self.set(key, value, save=False)
        self.save_settings()
    
    def get_window_geometry(self) -> Dict[str, Any]:
        """Get window geometry settings"""
        return {
            'width': self.get('window_width', 1400),
            'height': self.get('window_height', 900),
            'maximized': self.get('window_maximized', False)
        }
    
    def set_window_geometry(self, width: int, height: int, maximized: bool):
        """Set window geometry settings"""
        self.update({
            'window_width': width,
            'window_height': height,
            'window_maximized': maximized
        })
    
    def get_business_settings(self) -> Dict[str, Any]:
        """Get business-related settings"""
        return {
            'vat_rate': self.get('vat_rate', 17.0),
            'quote_validity_days': self.get('quote_validity_days', 14),
            'default_payment_terms': self.get('default_payment_terms', ''),
            'max_images_per_quote': self.get('max_images_per_quote', 2)
        }
    
    def set_business_settings(self, business_settings: Dict[str, Any]):
        """Set business-related settings"""
        for key, value in business_settings.items():
            self.set(key, value, save=False)
        self.save_settings()
    
    def get_file_paths(self) -> Dict[str, str]:
        """Get file path settings"""
        return {
            'catalog_path': self.get('catalog_path', ''),
            'quotes_output_dir': self.get('quotes_output_dir', 'quotes'),
            'backup_dir': self.get('backup_dir', 'backups'),
            'temp_dir': self.get('temp_dir', 'temp')
        }
    
    def set_catalog_path(self, path: str):
        """Set catalog XLSX file path"""
        self.set('catalog_path', path)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f'features.{feature}', False)
    
    def enable_feature(self, feature: str, enabled: bool = True):
        """Enable or disable a feature"""
        self.set(f'features.{feature}', enabled)
    
    def export_settings(self, export_path: str) -> bool:
        """Export settings to file"""
        try:
            export_file = Path(export_path)
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """Import settings from file"""
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate imported settings
            if not isinstance(imported_settings, dict):
                self.logger.error("Invalid settings format")
                return False
            
            # Merge with current settings
            self.settings.update(imported_settings)
            self.save_settings()
            
            self.logger.info(f"Settings imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False 