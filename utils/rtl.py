"""
Right-to-Left (RTL) Text Utilities for Hebrew Support
Handles Hebrew text processing and RTL layout
"""

try:
    from bidi.algorithm import get_display
    from arabic_reshaper import reshape
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

def rtl(text: str) -> str:
    """
    Process Hebrew/Arabic text for proper RTL display
    
    Args:
        text: The text to process
        
    Returns:
        Processed text ready for RTL display
    """
    if not text or not isinstance(text, str):
        return str(text) if text is not None else ""
    
    if BIDI_AVAILABLE:
        try:
            # Reshape Arabic characters if needed
            reshaped_text = reshape(text)
            # Apply bidirectional algorithm
            display_text = get_display(reshaped_text)
            return display_text
        except Exception:
            # Fall back to original text if processing fails
            return text
    else:
        # Simple fallback without bidi processing
        return text

def is_hebrew_char(char: str) -> bool:
    """Check if character is Hebrew"""
    if not char:
        return False
    
    hebrew_range = (0x0590, 0x05FF)  # Hebrew Unicode block
    char_code = ord(char)
    return hebrew_range[0] <= char_code <= hebrew_range[1]

def is_hebrew_text(text: str) -> bool:
    """Check if text contains Hebrew characters"""
    if not text:
        return False
    
    hebrew_chars = sum(1 for char in text if is_hebrew_char(char))
    return hebrew_chars > 0

def reverse_parentheses(text: str) -> str:
    """Reverse parentheses direction for RTL text"""
    replacements = {
        '(': ')',
        ')': '(',
        '[': ']',
        ']': '[',
        '{': '}',
        '}': '{'
    }
    
    result = ""
    for char in text:
        result += replacements.get(char, char)
    
    return result

def format_hebrew_number(number: float, decimal_places: int = 2) -> str:
    """Format number for Hebrew RTL display"""
    try:
        formatted = f"{number:,.{decimal_places}f}"
        # Hebrew uses comma as thousands separator and period as decimal
        return formatted
    except (ValueError, TypeError):
        return str(number)

def align_rtl_text(text: str, width: int = 50, fill_char: str = ' ') -> str:
    """Right-align text for RTL display"""
    if len(text) >= width:
        return text
    
    padding = width - len(text)
    return fill_char * padding + text 