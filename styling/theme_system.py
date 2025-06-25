# QuoreManager Version 2.0 - Modern Theme System
# Professional dual-theme system with blue and red color schemes

import customtkinter as ctk
from typing import Dict, Any, Literal

# Modern Color Themes - Based on comprehensive design specifications
THEMES = {
    'blue': {
        # Primary Colors - Lighter, more professional
        'primary': '#60A5FA',        # Lighter blue for better UX
        'primary_dark': '#3B82F6',   # Slightly darker for hover
        'primary_hover': '#3B82F6',  # Hover color (alias for primary_dark)
        'primary_light': '#93C5FD',  # Light blue for secondary
        'primary_ultra_light': '#EBF4FF',
        
        # Button Colors - Professional gradients
        'button_primary': '#60A5FA',
        'button_primary_hover': '#3B82F6',
        'button_primary_active': '#2563EB',
        'button_secondary': '#93C5FD',
        'button_secondary_hover': '#60A5FA',
        'button_shadow': '#DBEAFE',  # Light blue shadow
        'button_border': '#BFDBFE',  # Light blue border
        
        # Backgrounds  
        'bg_primary': '#FFFFFF',      # Pure White
        'bg_secondary': '#F8FAFC',    # Very Light Gray
        'bg_tertiary': '#F1F5F9',     # Light Gray
        'bg_card': '#FFFFFF',         # Pure White for cards
        'card_bg': '#FFFFFF',         # Pure White for cards (alias)
        'input_bg': '#F9FAFB',        # Very Light Gray for inputs
        
        # Sidebar - Balanced blue with visible vertical gradient (top to bottom)
        'sidebar_bg': 'linear-gradient(180deg, #3B82F6, #BFDBFE)',  # Stronger gradient contrast
        'sidebar_bg_solid': '#60A5FA',  # Medium blue base (not too light, not too dark)
        'sidebar_bg_gradient_top': '#3B82F6',     # Medium blue for top (more visible)
        'sidebar_bg_gradient_mid': '#60A5FA',     # Light blue for middle
        'sidebar_bg_gradient_bottom': '#BFDBFE',  # Light blue for bottom (good contrast)
        'sidebar_hover': '#93C5FD',               # Even lighter blue for hover
        'sidebar_hover_gradient': '#BFDBFE',      # Beautiful gradient hover effect
        'sidebar_active': '#FFFFFF',
        'sidebar_text': '#E5E7EB',                # Light grey text
        'sidebar_text_active': '#1E40AF',
        
        # Text Colors
        'text_primary': '#111827',    # Near Black
        'text_secondary': '#374151',  # Dark Gray  
        'text_tertiary': '#6B7280',   # Medium Gray (same as muted)
        'text_muted': '#6B7280',      # Medium Gray
        'text_light': '#9CA3AF',      # Light Gray
        
        # Borders and Effects
        'border': '#E5E7EB',          # Light Gray
        'border_light': '#F3F4F6',    # Very Light Gray
        'divider': '#E5E7EB',
        
        # Shadows (hex equivalents)
        'shadow_light': '#F3F4F6',
        'shadow_medium': '#E5E7EB', 
        'shadow_strong': '#D1D5DB',
        
        # Status Colors
        'success': '#10B981',
        'warning': '#F59E0B', 
        'error': '#EF4444',
        'info': '#3B82F6',
        
        # Icon file
        'icon_file': 'version5_blue_icon.ico'
    },
    
    'red': {
        # Primary Colors - Lighter, more professional
        'primary': '#F87171',        # Lighter red for better UX
        'primary_dark': '#EF4444',   # Slightly darker for hover
        'primary_hover': '#EF4444',  # Hover color (alias for primary_dark)
        'primary_light': '#FCA5A5',  # Light red for secondary
        'primary_ultra_light': '#FEF2F2',
        
        # Button Colors - Professional gradients
        'button_primary': '#F87171',
        'button_primary_hover': '#EF4444',
        'button_primary_active': '#DC2626',
        'button_secondary': '#FCA5A5',
        'button_secondary_hover': '#F87171',
        'button_shadow': '#FECACA',  # Light red shadow
        'button_border': '#FED7D7',  # Light red border
        
        # Backgrounds (same as blue theme)
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8FAFC', 
        'bg_tertiary': '#F1F5F9',
        'bg_card': '#FFFFFF',
        'card_bg': '#FFFFFF',         # Pure White for cards (alias)
        'input_bg': '#F9FAFB',        # Very Light Gray for inputs
        
        # Sidebar - Balanced red with visible vertical gradient (top to bottom)
        'sidebar_bg': 'linear-gradient(180deg, #EF4444, #FECACA)',  # Stronger gradient contrast
        'sidebar_bg_solid': '#F87171',  # Medium red base (not too light, not too dark)
        'sidebar_bg_gradient_top': '#EF4444',     # Medium red for top (more visible)
        'sidebar_bg_gradient_mid': '#F87171',     # Light red for middle
        'sidebar_bg_gradient_bottom': '#FECACA',  # Light red for bottom (good contrast)
        'sidebar_hover': '#FCA5A5',               # Even lighter red for hover
        'sidebar_hover_gradient': '#FED7D7',      # Beautiful gradient hover effect
        'sidebar_active': '#FFFFFF',
        'sidebar_text': '#E5E7EB',                # Light grey text
        'sidebar_text_active': '#DC2626',
        
        # Text Colors (same as blue theme)
        'text_primary': '#111827',
        'text_secondary': '#374151',
        'text_tertiary': '#6B7280',   # Medium Gray (same as muted)
        'text_muted': '#6B7280', 
        'text_light': '#9CA3AF',
        
        # Borders and Effects (same as blue theme)
        'border': '#E5E7EB',
        'border_light': '#F3F4F6',
        'divider': '#E5E7EB',
        
        # Shadows (hex equivalents)
        'shadow_light': '#F3F4F6',
        'shadow_medium': '#E5E7EB',
        'shadow_strong': '#D1D5DB',
        
        # Status Colors  
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#EF4444',  # Use red for info in red theme
        
        # Icon file
        'icon_file': 'version5_icon.ico'  # Use version 5 icon for red theme
    }
}

# Typography System - Refined professional hierarchy (more compact)
TYPOGRAPHY = {
    'hero': {'size': 28, 'weight': 'bold', 'family': 'Inter'},      # Much smaller, refined
    'title': {'size': 22, 'weight': 'bold', 'family': 'Inter'},     # Compact section titles
    'heading': {'size': 18, 'weight': 'normal', 'family': 'Inter'}, # Smaller headings
    'card_title': {'size': 16, 'weight': 'normal', 'family': 'Inter'}, # Refined card titles
    'body': {'size': 14, 'weight': 'normal', 'family': 'Inter'},    # Standard body text
    'helper': {'size': 12, 'weight': 'normal', 'family': 'Inter'},  # Small helper text
    'caption': {'size': 11, 'weight': 'normal', 'family': 'Inter'}, # Tiny captions
    'nav_item': {'size': 14, 'weight': 'normal', 'family': 'Inter'}, # Navigation items
    'nav_item_small': {'size': 12, 'weight': 'normal', 'family': 'Inter'},
    'stat_number': {'size': 24, 'weight': 'bold', 'family': 'Inter'}, # Compact stat numbers
    'stat_label': {'size': 13, 'weight': 'normal', 'family': 'Inter'} # Small stat labels
}

# Spacing System - Consistent spacing scale
SPACING = {
    'xs': 4,
    'sm': 8, 
    'md': 12,
    'lg': 16,
    'xl': 24,
    'xxl': 32,
    'xxxl': 48,
    'xxxxl': 64
}

# Component Specifications - Professional design system
COMPONENTS = {
    'card': {
        'corner_radius': 12,
        'padding': 24,
        'margin': 16,
        'border_width': 1,
        'shadow': True
    },
    'button': {
        # Professional button styling
        'height': 40,
        'height_large': 48,
        'height_small': 32,
        'corner_radius': 8,
        'font_size': 14,
        'font_weight': 'normal',
        'border_width': 1,
        'shadow': True,
        'gradient': True,
        'hover_effect': True,
        'active_effect': True
    },
    'sidebar': {
        'width': 240,  # Fixed width as specified
        'corner_radius': 0,  # Full height
        'padding': 16,
        'item_height': 48,
        'item_padding': 16
    }
}

class ModernThemeManager:
    """Professional theme manager for QuoreManager 2.0"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.current_color_theme = settings_manager.get('color_theme', 'blue')  # blue or red
        self.current_mode = settings_manager.get('theme_mode', 'light')  # light or dark
        
    def get_current_theme(self) -> Dict[str, Any]:
        """Get the current theme configuration"""
        return THEMES[self.current_color_theme].copy()
    
    def get_color(self, color_key: str) -> str:
        """Get a specific color from current theme"""
        theme = self.get_current_theme()
        return theme.get(color_key, '#000000')
    
    def get_typography(self, type_key: str) -> Dict[str, Any]:
        """Get typography configuration"""
        return TYPOGRAPHY.get(type_key, TYPOGRAPHY['body']).copy()
    
    def get_spacing(self, size_key: str) -> int:
        """Get spacing value"""
        return SPACING.get(size_key, 16)
    
    def get_component_config(self, component: str) -> Dict[str, Any]:
        """Get component configuration"""
        return COMPONENTS.get(component, {}).copy()
    
    def apply_theme(self):
        """Apply theme to CustomTkinter"""
        # Apply appearance mode (this affects default dark/light)
        ctk.set_appearance_mode(self.current_mode)
        
        # Set color theme - using blue for both since we handle colors manually
        ctk.set_default_color_theme("blue")
    
    def switch_color_theme(self, new_theme: Literal['blue', 'red']):
        """Switch between blue and red color themes"""
        if new_theme in THEMES:
            self.current_color_theme = new_theme
            self.settings_manager.set('color_theme', new_theme)
            return True
        return False
    
    def set_theme(self, new_theme: Literal['blue', 'red']):
        """Set the color theme (alias for switch_color_theme)"""
        return self.switch_color_theme(new_theme)
    
    def toggle_mode(self):
        """Toggle between light and dark mode"""
        new_mode = 'dark' if self.current_mode == 'light' else 'light'
        self.current_mode = new_mode
        self.settings_manager.set('theme_mode', new_mode)
        return new_mode
    
    def create_ctk_font(self, type_key: str) -> ctk.CTkFont:
        """Create a CustomTkinter font from typography specification"""
        typo = self.get_typography(type_key)
        return ctk.CTkFont(
            family=typo['family'],
            size=typo['size'],
            weight=typo['weight']
        )
    
    def create_modern_button(self, parent, text: str, style: str = 'primary', size: str = 'medium', **kwargs) -> ctk.CTkButton:
        """Create a professional styled button with gradients, shadows, and borders"""
        theme = self.get_current_theme()
        button_config = self.get_component_config('button')
        
        # Button heights
        heights = {
            'small': button_config['height_small'],
            'medium': button_config['height'],
            'large': button_config['height_large']
        }
        
        # Professional button styles - only theme colors
        styles = {
            'primary': {
                'fg_color': theme['button_primary'],
                'hover_color': theme['button_primary_hover'],
                'text_color': '#FFFFFF',
                'border_width': button_config['border_width'],
                'border_color': theme['button_border']
            },
            'secondary': {
                'fg_color': theme['button_secondary'],
                'hover_color': theme['button_secondary_hover'],
                'text_color': theme['primary_dark'],
                'border_width': button_config['border_width'],
                'border_color': theme['button_border']
            },
            'outline': {
                'fg_color': 'transparent',
                'hover_color': theme['primary_ultra_light'],
                'text_color': theme['primary'],
                'border_width': button_config['border_width'],
                'border_color': theme['primary']
            },
            'danger': {
                'fg_color': theme['error'],
                'hover_color': '#DC2626',
                'text_color': '#FFFFFF',
                'border_width': button_config['border_width'],
                'border_color': '#FECACA'
            },
            'success': {
                'fg_color': theme['success'],
                'hover_color': '#059669',
                'text_color': '#FFFFFF',
                'border_width': button_config['border_width'],
                'border_color': '#A7F3D0'
            }
        }
        
        style_config = styles.get(style, styles['primary'])
        
        defaults = {
            'font': self.create_ctk_font('body'),
            'corner_radius': button_config['corner_radius'],
            'height': heights.get(size, heights['medium']),
            **style_config
        }
        
        defaults.update(kwargs)
        return ctk.CTkButton(parent, text=text, **defaults)
    
    def create_modern_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """Create a modern card with proper styling"""
        theme = self.get_current_theme()
        card_config = self.get_component_config('card')
        
        defaults = {
            'fg_color': theme['bg_card'],
            'corner_radius': card_config['corner_radius'],
            'border_width': card_config['border_width'],
            'border_color': theme['border_light']
        }
        
        defaults.update(kwargs)
        return ctk.CTkFrame(parent, **defaults)
    
    def get_icon_path(self) -> str:
        """Get the appropriate icon file for current theme"""
        theme = self.get_current_theme()
        return f"resources/{theme['icon_file']}"
    
    def get_button_style_for_action(self, action: str) -> str:
        """Get appropriate button style for common actions"""
        action_styles = {
            'add': 'primary',
            'create': 'primary', 
            'save': 'primary',
            'edit': 'secondary',
            'view': 'secondary',
            'search': 'secondary',
            'refresh': 'secondary',
            'delete': 'danger',
            'remove': 'danger',
            'cancel': 'outline',
            'close': 'outline',
            'continue': 'primary',
            'activate': 'success',
            'deactivate': 'danger'
        }
        return action_styles.get(action.lower(), 'primary') 