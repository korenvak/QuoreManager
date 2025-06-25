"""
Helper Utilities for Kitchen Quote Management System
Common utility functions for file operations, formatting, and validation
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib

def asset_path(filename: str) -> str:
    """Get absolute path to asset file"""
    # Check in resources directory first
    resources_dir = Path(__file__).parent.parent / "resources"
    asset_file = resources_dir / filename
    
    if asset_file.exists():
        return str(asset_file)
    
    # If not found, return the filename (for fallback)
    return filename

def ensure_directory(directory: str) -> Path:
    """Ensure directory exists, create if necessary"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def safe_filename(filename: str) -> str:
    """Generate safe filename by removing/replacing unsafe characters"""
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple consecutive underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Trim underscores from ends
    safe_name = safe_name.strip('_')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed"
    
    return safe_name

def format_currency(amount: float, currency: str = "₪", decimal_places: int = 2) -> str:
    """Format amount as currency"""
    try:
        formatted = f"{amount:,.{decimal_places}f}"
        return f"{formatted}{currency}"
    except (ValueError, TypeError):
        return f"0.00{currency}"

def format_date(date_obj: datetime, format_str: str = "%d/%m/%Y") -> str:
    """Format datetime object as string"""
    try:
        if isinstance(date_obj, datetime):
            return date_obj.strftime(format_str)
        elif isinstance(date_obj, str):
            # Try to parse string date
            parsed_date = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            return parsed_date.strftime(format_str)
        else:
            return str(date_obj)
    except (ValueError, TypeError):
        return ""

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Israeli phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Israeli phone patterns
    patterns = [
        r'^972[5-9]\d{8}$',    # International format: 972-5X-XXXXXXX (mobile) or 972-X-XXXXXXXX (landline)
        r'^05[0-9]\d{7}$',     # Mobile format: 05X-XXXXXXX (10 digits total)
        r'^0[2-489]\d{7}$',    # Landline format: 0X-XXXXXXX (9 digits total, excluding mobile prefixes)
        r'^[5-9]\d{8}$'        # Without leading zero (mobile or landline)
    ]
    
    return any(re.match(pattern, digits_only) for pattern in patterns)

def normalize_phone(phone: str) -> str:
    """Normalize phone number to standard format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Convert to local format
    if digits_only.startswith('972'):
        # International format
        local_part = digits_only[3:]
        if len(local_part) == 9:  # Mobile: 972-5X-XXXXXXX
            return f"0{local_part[:3]}-{local_part[3:]}"
        elif len(local_part) == 8:  # Landline: 972-X-XXXXXXX  
            return f"0{local_part[:2]}-{local_part[2:]}"
    elif digits_only.startswith('05') and len(digits_only) == 10:
        # Mobile format: 05X-XXXXXXX (10 digits)
        return f"{digits_only[:3]}-{digits_only[3:]}"
    elif digits_only.startswith('0') and len(digits_only) == 9:
        # Landline format: 0X-XXXXXXX (9 digits)
        return f"{digits_only[:3]}-{digits_only[3:]}"
    elif digits_only.startswith('5') and len(digits_only) == 9:
        # Mobile without leading zero: 5X-XXXXXXX
        return f"0{digits_only[:2]}-{digits_only[2:]}"
    elif len(digits_only) == 8:
        # Landline without leading zero
        return f"0{digits_only[:2]}-{digits_only[2:]}"
    
    # Return as-is if no pattern matches
    return phone

def calculate_quote_totals(items: List[Dict], regular_discount: float = 0, 
                          contractor_discount: float = 0, vat_rate: float = 17.0) -> Dict[str, float]:
    """Calculate quote totals with discounts and VAT
    Order: Sum of items → × VAT → - Contractor → × Discount
    """
    # Step 1: Sum of items
    subtotal = sum(item.get('כמות', 0) * item.get('מחיר', 0) for item in items)
    
    # Step 2: Apply VAT as multiplier (17% = 1.17)
    vat_multiplier = 1 + (vat_rate / 100)  # 17% becomes 1.17
    after_vat = subtotal * vat_multiplier
    vat_amount = after_vat - subtotal  # Calculate VAT amount for display
    
    # Step 3: Subtract contractor discount (fixed amount)
    contractor_discount_amount = contractor_discount  # Fixed amount, not percentage
    after_contractor = after_vat - contractor_discount_amount
    after_contractor = max(0, after_contractor)  # Can't go below 0
    
    # Step 4: Apply regular discount as reduction factor (18% = 0.82)
    discount_factor = 1 - (regular_discount / 100)  # 18% becomes 0.82
    final_total = after_contractor * discount_factor
    regular_discount_amount = after_contractor - final_total  # Calculate discount amount for display
    
    return {
        'subtotal': subtotal,
        'contractor_discount_val': contractor_discount_amount,
        'discount_val': regular_discount_amount,
        'discount_percent': regular_discount,
        'vat_amount': vat_amount,
        'final_total': final_total
    }

def generate_quote_filename(customer_name: str, quote_number: int, date: Optional[datetime] = None) -> str:
    """Generate standardized quote filename"""
    if date is None:
        date = datetime.now()
    
    safe_customer = safe_filename(customer_name)
    date_str = date.strftime("%Y%m%d")
    
    return f"quote_{safe_customer}_{quote_number:03d}_{date_str}.pdf"

def backup_file(source_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """Create backup of file"""
    try:
        source = Path(source_path)
        
        if not source.exists():
            return None
        
        if backup_dir is None:
            backup_dir_path = source.parent / "backups"
        else:
            backup_dir_path = Path(backup_dir)
        
        backup_path = ensure_directory(str(backup_dir_path))
        
        # Add timestamp to backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source.stem}_{timestamp}{source.suffix}"
        backup_file_path = backup_path / backup_filename
        
        shutil.copy2(source, backup_file_path)
        return str(backup_file_path)
        
    except Exception:
        return None

def get_file_hash(file_path: str) -> Optional[str]:
    """Get MD5 hash of file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def clean_temp_files(temp_dir: str, max_age_hours: int = 24):
    """Clean temporary files older than specified hours"""
    try:
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        for file_path in temp_path.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                
    except Exception:
        pass

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def search_text(text: str, search_term: str, case_sensitive: bool = False) -> bool:
    """Search for term in text"""
    if not search_term:
        return True
    
    if not case_sensitive:
        text = text.lower()
        search_term = search_term.lower()
    
    return search_term in text

def parse_catalog_price(price_str: str) -> float:
    """Parse price string from catalog, handling different formats"""
    try:
        # Remove currency symbols and commas
        clean_price = re.sub(r'[₪$€£,\s]', '', str(price_str))
        
        # Try to convert to float
        return float(clean_price)
        
    except (ValueError, TypeError):
        return 0.0

def validate_discount(discount: float, max_discount: float = 100.0) -> bool:
    """Validate discount percentage"""
    try:
        return 0 <= discount <= max_discount
    except (ValueError, TypeError):
        return False

def hebrew_sort_key(text: str) -> str:
    """Generate sort key for Hebrew text"""
    # This is a simplified version - for proper Hebrew sorting,
    # you might want to use the PyICU library
    return text

def export_to_csv(data: List[Dict], filename: str, encoding: str = 'utf-8-sig') -> bool:
    """Export data to CSV file"""
    try:
        import csv
        
        if not data:
            return False
        
        with open(filename, 'w', newline='', encoding=encoding) as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        return True
        
    except Exception:
        return False 