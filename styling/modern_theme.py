"""
Modern Theme System for Kitchen Quote Management System
Ultra-modern design with gradients, transparency, and smooth animations
"""

import customtkinter as ctk

# Ultra-modern color palette with transparency support
MODERN_COLORS = {
    'light': {
        # Pure white backgrounds with subtle variations
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#FEFEFE', 
        'bg_tertiary': '#F9FAFB',
        'bg_card': '#FFFFFF',
        
        # Sidebar with modern colors
        'bg_sidebar': '#F8FAFC',
        'bg_sidebar_collapsed': '#F1F5F9',
        'bg_sidebar_hover': '#E2E8F0',
        
        # Modern gradient colors
        'gradient_primary': ['#3B82F6', '#6366F1'],
        'gradient_secondary': ['#10B981', '#06B6D4'],
        'gradient_accent': ['#F59E0B', '#EF4444'],
        
        # Accent colors
        'accent_blue': '#3B82F6',
        'accent_purple': '#6366F1', 
        'accent_green': '#10B981',
        'accent_orange': '#F59E0B',
        'accent_red': '#EF4444',
        'accent_indigo': '#8B5CF6',
        'accent_pink': '#EC4899',
        
        # Text with better contrast
        'text_primary': '#111827',
        'text_secondary': '#4B5563',
        'text_muted': '#9CA3AF',
        'text_light': '#D1D5DB',
        
        # Borders and effects
        'border': '#E5E7EB',
        'border_light': '#F3F4F6',
        'shadow_light': 'rgba(0, 0, 0, 0.05)',
        'shadow_medium': 'rgba(0, 0, 0, 0.1)',
        'shadow_strong': 'rgba(0, 0, 0, 0.15)',
        
        # Glass effect (simulated with light colors)
        'glass_bg': '#FEFEFE',
        'glass_border': '#F3F4F6',
    },
    'dark': {
        # Deep dark backgrounds
        'bg_primary': '#0F172A',
        'bg_secondary': '#1E293B',
        'bg_tertiary': '#334155',
        'bg_card': '#1E293B',
        
        # Dark sidebar with modern colors
        'bg_sidebar': '#1E293B',
        'bg_sidebar_collapsed': '#0F172A',
        'bg_sidebar_hover': '#334155',
        
        # Dark gradients
        'gradient_primary': ['#60A5FA', '#A78BFA'],
        'gradient_secondary': ['#34D399', '#22D3EE'],
        'gradient_accent': ['#FBBF24', '#F87171'],
        
        # Light accent colors for dark mode
        'accent_blue': '#60A5FA',
        'accent_purple': '#A78BFA',
        'accent_green': '#34D399',
        'accent_orange': '#FBBF24',
        'accent_red': '#F87171',
        'accent_indigo': '#C4B5FD',
        'accent_pink': '#F472B6',
        
        # Light text colors
        'text_primary': '#F8FAFC',
        'text_secondary': '#CBD5E1',
        'text_muted': '#94A3B8',
        'text_light': '#64748B',
        
        # Dark borders and effects
        'border': '#475569',
        'border_light': '#334155',
        'shadow_light': 'rgba(0, 0, 0, 0.2)',
        'shadow_medium': 'rgba(0, 0, 0, 0.3)',
        'shadow_strong': 'rgba(0, 0, 0, 0.4)',
        
        # Dark glass effect (simulated)
        'glass_bg': '#1E293B',
        'glass_border': '#334155',
    }
}

class ModernTheme:
    """Ultra-modern theme manager with transparency and gradients"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.current_theme = settings_manager.get('theme_mode', 'light')
    
    def get_colors(self):
        """Get colors for current theme"""
        return MODERN_COLORS[self.current_theme]
    
    def apply_theme(self):
        """Apply ultra-modern theme"""
        ctk.set_appearance_mode(self.current_theme)
        
        # Enhanced color themes
        if self.current_theme == 'light':
            ctk.set_default_color_theme("blue")
        else:
            ctk.set_default_color_theme("dark-blue")
    
    def create_modern_button(self, parent, text, icon="", color="accent_blue", **kwargs):
        """Create a modern styled button"""
        colors = self.get_colors()
        
        defaults = {
            'font': ctk.CTkFont(family="Heebo", size=14, weight="bold"),
            'corner_radius': 12,
            'border_width': 0,
            'fg_color': colors[color],
            'hover_color': self._darken_color(colors[color]),
            'text_color': 'white'
        }
        
        defaults.update(kwargs)
        button_text = f"{icon} {text}" if icon else text
        
        return ctk.CTkButton(parent, text=button_text, **defaults)
    
    def create_modern_card(self, parent, **kwargs):
        """Create a modern card with shadow effect"""
        colors = self.get_colors()
        
        defaults = {
            'fg_color': colors['bg_card'],
            'corner_radius': 16,
            'border_width': 1,
            'border_color': colors['border_light']
        }
        
        defaults.update(kwargs)
        return ctk.CTkFrame(parent, **defaults)
    
    def _darken_color(self, color):
        """Darken a color for hover effects"""
        if color.startswith('#'):
            rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        return color 