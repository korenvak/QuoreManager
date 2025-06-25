"""
Database Manager for Kitchen Quote Management System
Handles database initialization, connections, and basic operations
"""

import os
import logging
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from .models import Base, User, Customer, Quote, Draft, AuditLog, SystemSettings

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Set database path
        if db_path is None:
            # Check if running as EXE (bundled by PyInstaller)
            import sys
            is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
            
            if is_exe:
                # Always use AppData directory for EXE to ensure persistence
                import platform, os
                if platform.system() == "Windows":
                    appdata = os.getenv('LOCALAPPDATA') or Path.home()
                    db_dir = Path(appdata) / "KitchenQuoteManager"
                else:
                    db_dir = Path.home() / ".kitchen_quote_manager"
                db_dir.mkdir(exist_ok=True)
                self.logger.info(f"EXE detected, using persistent AppData directory: {db_dir}")
            else:
                # Development mode - try config directory first
                default_dir = Path(__file__).parent.parent / "config"
                try:
                    default_dir.mkdir(exist_ok=True)
                    test_file = default_dir / "_writetest.tmp"
                    with open(test_file, "w") as f:
                        f.write("test")
                    test_file.unlink(missing_ok=True)
                    db_dir = default_dir
                    self.logger.info(f"Development mode, using config directory: {db_dir}")
                except Exception as e:
                    # Fallback to user appdata directory (always writable)
                    import platform, os
                    if platform.system() == "Windows":
                        appdata = os.getenv('LOCALAPPDATA') or Path.home()
                        db_dir = Path(appdata) / "KitchenQuoteManager"
                    else:
                        db_dir = Path.home() / ".kitchen_quote_manager"
                    db_dir.mkdir(exist_ok=True)
                    self.logger.warning(f"Config directory not writable ({e}), using fallback: {db_dir}")
            
            db_path = db_dir / "kitchen_quotes.db"
        
        self.db_path = str(db_path)
        self.logger.info(f"Database path set to: {self.db_path}")
        self.engine = None
        self.Session = None
        
    def initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine with proper SQLite settings
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30
                }
            )
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Initialize default settings
            self._initialize_default_settings()
            
            self.logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        if not self.Session:
            raise RuntimeError("Database not initialized. Call initialize_database() first.")
        
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def _initialize_default_settings(self):
        """Initialize default system settings"""
        default_settings = [
            ('vat_rate', '17.0', 'float', 'Default VAT rate percentage'),
            ('theme_mode', 'light', 'string', 'UI theme mode (light/dark)'),
            ('company_name', 'כיצ\'ן סטודיו', 'string', 'Company name'),
            ('company_phone', '03-1234567', 'string', 'Company phone number'),
            ('company_email', 'info@kitchenstudio.co.il', 'string', 'Company email'),
            ('company_address', 'רחוב הדקל 123, תל אביב', 'string', 'Company address'),
            ('auto_save_interval', '30', 'int', 'Auto-save interval in seconds'),
            ('max_images_per_quote', '2', 'int', 'Maximum images per quote'),
            ('quote_validity_days', '14', 'int', 'Quote validity in days'),
            ('backup_enabled', 'true', 'boolean', 'Enable automatic backups'),
            ('session_timeout_minutes', '120', 'int', 'Session timeout in minutes'),
            ('legal_text', 'הצעת המחיר תקפה ל־14 ימים ממועד הפקתה.\\n\\nההצעה מיועדת ללקוח הספציפי בלבד, ואין להעבירה או להציג אותה בפני חברות אחרות או גורמים חיצוניים.\\n\\nהמחירים עשויים להשתנות, והחברה אינה אחראית לטעויות חישוב או הקלדה. רק הסכום המאושר סופית על ידי החברה הוא המחייב.\\n\\nאישור ההצעה (בחתימה) מהווה התחייבות מצד הלקוח לביצוע העבודה.\\n\\nבמעמד האישור, ישולמו 10% מקדמה מסכום העסקה – תשלום זה אינו ניתן להחזר במקרה של ביטול מכל סיבה שהיא.\\n\\nהלקוח מתחייב לוודא כי מיקום התקנת המטבח יהיה פנוי מכל ריהוט, ציוד או מכשול אחר, וכן שנקודות מים, חשמל וניקוז ימוקמו בהתאם לתכניות שסופקו לו מראש על ידי החברה.\\nכל עיכוב או שינוי הנובע מאי־עמידה בתנאים אלה עשוי לגרור עיכובים בעלויות ולוחות זמנים.', 'string', 'Legal text for quotes')
        ]
        
        try:
            with self.get_session() as session:
                for key, value, data_type, description in default_settings:
                    existing = session.query(SystemSettings).filter_by(key=key).first()
                    if not existing:
                        setting = SystemSettings(
                            key=key,
                            value=value,
                            data_type=data_type,
                            description=description
                        )
                        session.add(setting)
                        
        except Exception as e:
            self.logger.error(f"Failed to initialize default settings: {e}")
    
    # User operations
    def create_user(self, username: str, password_hash: str, role: str, **kwargs) -> Dict[str, Any]:
        """Create a new user and return as dict to avoid session binding issues"""
        with self.get_session() as session:
            user = User(
                username=username,
                password_hash=password_hash,
                role=role,
                **kwargs
            )
            session.add(user)
            session.flush()
            session.refresh(user)
            
            # Convert to dict while session is active
            user_dict = {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'max_discount': user.max_discount,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at,
                'last_login': user.last_login
            }
            
            return user_dict
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.get_session() as session:
            return session.query(User).filter_by(username=username).first()
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        with self.get_session() as session:
            return session.query(User).all()
    
    def get_all_users_dict(self) -> List[Dict]:
        """Get all users as dictionaries to avoid session binding issues"""
        with self.get_session() as session:
            users = session.query(User).all()
            return [{
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'max_discount': user.max_discount,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at,
                'last_login': user.last_login
            } for user in users]
    
    def user_exists(self) -> bool:
        """Check if any users exist in the system"""
        try:
            with self.get_session() as session:
                user_count = session.query(User).count()
                self.logger.info(f"User count in database: {user_count}")
                return user_count > 0
        except Exception as e:
            self.logger.error(f"Error checking if users exist: {e}")
            return False
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            with self.get_session() as session:
                session.query(User).filter(User.id == user_id).update({
                    User.last_login: datetime.utcnow()
                })
                return True
        except Exception as e:
            self.logger.error(f"Failed to update last login for user {user_id}: {e}")
            return False
    
    def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Update user active status"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    user.is_active = is_active
                    session.commit()
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error updating user status: {e}")
            return False
    
    def delete_user(self, user_id: int, force: bool = False) -> bool:
        """Delete user.
        If force=True, attempt permanent deletion (only allowed if no quotes/drafts).
        Otherwise perform soft delete (set inactive). Returns True on success, False on failure."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return False

                # If force deletion requested, ensure user has no dependent records
                if force:
                    has_quotes = session.query(Quote).filter_by(created_by=user_id).count() > 0
                    has_drafts = session.query(Draft).filter_by(created_by=user_id).count() > 0
                    if has_quotes or has_drafts:
                        # Cannot hard delete if dependencies exist
                        self.logger.warning(
                            f"Cannot permanently delete user {user.username}: related quotes or drafts exist"
                        )
                        return False
                    # Safe to delete permanently
                    session.delete(user)
                    session.commit()
                    # Audit log
                    self.log_action(
                        user_id=0,
                        action='delete_user',
                        entity_type='user',
                        entity_id=user_id,
                        details={'permanent': True}
                    )
                    return True

                # Soft delete fallback
                user.is_active = False
                # Audit log
                self.log_action(
                    user_id=0,
                    action='deactivate_user',
                    entity_type='user',
                    entity_id=user_id,
                    details={'permanent': False}
                )
                return True
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return False
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    for key, value in kwargs.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    session.commit()
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return False
    
    # Customer operations
    def create_customer(self, name: str, phone: str, email: str, address: str, **kwargs) -> Optional[Customer]:
        """Create a new customer"""
        try:
            with self.get_session() as session:
                customer = Customer(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address,
                    **kwargs
                )
                session.add(customer)
                session.commit()  # Explicitly commit the transaction
                # Get the ID after commit
                customer_id = customer.id
                self.logger.info(f"Created customer: {name} with ID: {customer_id}")
                
                # Audit log
                self.log_action(
                    user_id=kwargs.get('created_by') or 0,
                    action='create_customer',
                    entity_type='customer',
                    entity_id=customer_id,
                    details={'name': name}
                )
                
                return customer
        except Exception as e:
            self.logger.error(f"Failed to create customer {name}: {e}")
            return None
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID as a plain dict"""
        with self.get_session() as session:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if customer:
                return customer.to_dict()
            return None
    
    def get_all_customers(self) -> List[dict]:
        """Get all customers as plain dicts (for UI use)"""
        with self.get_session() as session:
            session.expire_all()  # Force refresh from DB
            return [customer.to_dict() for customer in session.query(Customer).all()]
    
    def search_customers(self, search_term: str) -> List[Customer]:
        """Search customers by name, phone, or email"""
        with self.get_session() as session:
            search_pattern = f"%{search_term}%"
            return session.query(Customer).filter(
                Customer.name.like(search_pattern) |
                Customer.phone.like(search_pattern) |
                Customer.email.like(search_pattern)
            ).all()
    
    def customer_exists(self, name: str = None, phone: str = None, email: str = None, address: str = None) -> bool:
        """Check if customer exists with any of the unique fields"""
        with self.get_session() as session:
            query = session.query(Customer)
            conditions = []
            
            if name:
                conditions.append(Customer.name == name)
            if phone:
                conditions.append(Customer.phone == phone)
            if email:
                conditions.append(Customer.email == email)
            if address:
                conditions.append(Customer.address == address)
            
            if conditions:
                from sqlalchemy import or_
                return query.filter(or_(*conditions)).first() is not None
            
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete customer and all associated quotes (cascade)"""
        try:
            with self.get_session() as session:
                customer = session.query(Customer).filter_by(id=customer_id).first()
                if customer:
                    session.delete(customer)
                    
                    # Audit log
                    self.log_action(
                        user_id=0,
                        action='delete_customer',
                        entity_type='customer',
                        entity_id=customer_id
                    )
                    
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete customer {customer_id}: {e}")
            return False
    
    def update_customer(self, customer_id: int, **kwargs) -> bool:
        """Update existing customer"""
        try:
            with self.get_session() as session:
                customer = session.query(Customer).filter_by(id=customer_id).first()
                if customer:
                    for key, value in kwargs.items():
                        if hasattr(customer, key):
                            setattr(customer, key, value)
                    session.commit()
                    
                    # Audit log
                    self.log_action(
                        user_id=kwargs.get('acting_user_id') or customer.created_by if hasattr(customer, 'created_by') else 0,
                        action='update_customer',
                        entity_type='customer',
                        entity_id=customer_id,
                        details={key: kwargs.get(key) for key in kwargs}
                    )
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to update customer {customer_id}: {e}")
            return False
    
    # Quote operations
    def create_quote(self, customer_id: int, items: List[Dict], created_by: int, **kwargs) -> Dict:
        """Create a new quote with sequential quote number per customer"""
        with self.get_session() as session:
            # Validate regular discount against user's max allowed (unless unlimited)
            requested_discount = float(kwargs.get('regular_discount', 0.0) or 0.0)

            # Fetch user and check permissions
            user = session.query(User).filter_by(id=created_by).first()
            if not user:
                raise ValueError("Invalid creator user ID")

            has_unlimited_discount = user.role == "admin" or user.max_discount >= 100.0

            if not has_unlimited_discount and requested_discount > (user.max_discount or 0.0):
                raise ValueError(
                    f"Requested discount {requested_discount}% exceeds user's max allowed {user.max_discount}%"
                )

            # Get next quote number for this customer
            last_quote = session.query(Quote).filter_by(customer_id=customer_id)\
                .order_by(Quote.quote_number.desc()).first()
            
            quote_number = (last_quote.quote_number + 1) if last_quote else 1
            
            # Ensure all required fields are present with proper defaults
            quote_data = {
                'customer_id': customer_id,
                'quote_number': quote_number,
                'items': items,
                'created_by': created_by,
                'regular_discount': float(kwargs.get('regular_discount', 0.0) or 0.0),
                'contractor_discount': float(kwargs.get('contractor_discount', 0.0) or 0.0),
                'vat_rate': float(kwargs.get('vat_rate', 17.0) or 17.0),
                'subtotal': float(kwargs.get('subtotal', 0.0) or 0.0),
                'total_amount': float(kwargs.get('total_amount', 0.0) or 0.0),
                'notes': kwargs.get('notes', ''),
                'images': kwargs.get('images'),
                'pdf_path': kwargs.get('pdf_path')
            }
            
            # Calculate and store discount amounts for PDF compatibility
            subtotal = quote_data['subtotal']
            regular_discount = quote_data['regular_discount']
            contractor_discount = quote_data['contractor_discount']
            vat_rate = quote_data['vat_rate']
            
            # Calculate using the correct order: Sum → × VAT → - Contractor → × Discount
            # Step 1: Subtotal (already calculated)
            
            # Step 2: Apply VAT as multiplier (17% = 1.17)
            vat_multiplier = 1 + (vat_rate / 100)
            after_vat = subtotal * vat_multiplier
            vat_amount = after_vat - subtotal
            
            # Step 3: Subtract contractor discount (fixed amount)
            contractor_discount_amount = contractor_discount  # Fixed amount
            after_contractor = after_vat - contractor_discount_amount
            after_contractor = max(0, after_contractor)
            
            # Step 4: Apply regular discount as reduction factor (18% = 0.82)
            discount_factor = 1 - (regular_discount / 100)
            final_total = after_contractor * discount_factor
            regular_discount_amount = after_contractor - final_total
            
            # Add calculated amounts to quote data
            quote_data.update({
                'discount_amount': regular_discount_amount,
                'contractor_discount_amount': contractor_discount_amount,
                'vat_amount': vat_amount,
                'total_amount': final_total  # Update with calculated total
            })
            
            quote = Quote(**quote_data)
            session.add(quote)
            session.flush()
            session.commit()
            
            # Get the quote data before closing session
            quote_dict = {
                'id': quote.id,
                'customer_id': quote.customer_id,
                'quote_number': quote.quote_number,
                'items': quote.items,
                'created_by': quote.created_by,
                'regular_discount': quote.regular_discount,
                'contractor_discount': quote.contractor_discount,
                'vat_rate': quote.vat_rate,
                'subtotal': quote.subtotal,
                'discount_amount': quote.discount_amount,
                'contractor_discount_amount': quote.contractor_discount_amount,
                'vat_amount': quote.vat_amount,
                'total_amount': quote.total_amount,
                'images': quote.images,
                'notes': quote.notes,
                'pdf_path': quote.pdf_path,
                'created_at': quote.created_at
            }
            
            # Audit log
            self.log_action(
                user_id=created_by,
                action='create_quote',
                entity_type='quote',
                entity_id=quote.id,
                details={'quote_number': quote.quote_number, 'customer_id': customer_id}
            )
            
            return quote_dict
    
    def get_quote_by_id(self, quote_id: int) -> Optional[Quote]:
        """Get quote by ID"""
        with self.get_session() as session:
            return session.query(Quote).filter_by(id=quote_id).first()
    
    def get_quotes_by_customer(self, customer_id: int) -> List[Dict]:
        """Get all quotes for a customer as plain dicts"""
        with self.get_session() as session:
            quotes = session.query(Quote).filter_by(customer_id=customer_id)\
                .order_by(Quote.quote_number.desc()).all()
            return [self._quote_to_dict(q) for q in quotes]
    
    def get_recent_quotes(self, limit: int = 10) -> List[Dict]:
        """Get recent quotes as plain dicts"""
        with self.get_session() as session:
            quotes = session.query(Quote).order_by(Quote.created_at.desc()).limit(limit).all()
            return [self._quote_to_dict(q) for q in quotes]
    
    def _quote_to_dict(self, quote) -> Dict:
        """Convert Quote object to dict (no status)"""
        return {
            'id': quote.id,
            'customer_id': quote.customer_id,
            'quote_number': quote.quote_number,
            'items': quote.items,
            'regular_discount': quote.regular_discount,
            'contractor_discount': quote.contractor_discount,
            'vat_rate': quote.vat_rate,
            'subtotal': quote.subtotal,
            'discount_amount': quote.discount_amount,
            'contractor_discount_amount': quote.contractor_discount_amount,
            'vat_amount': quote.vat_amount,
            'total_amount': quote.total_amount,
            'images': quote.images,
            'notes': quote.notes,
            'pdf_path': quote.pdf_path,
            'created_by': quote.created_by,
            'created_at': quote.created_at,
            'updated_at': quote.updated_at,
            'sent_at': quote.sent_at
        }
    
    def get_all_quotes(self) -> List[Dict]:
        """Get all quotes in the system as plain dicts"""
        with self.get_session() as session:
            quotes = session.query(Quote).order_by(Quote.created_at.desc()).all()
            return [self._quote_to_dict(q) for q in quotes]
    
    def get_quotes_by_creator(self, user_id: int) -> List[Dict]:
        """Get quotes created by specific user as plain dicts"""
        with self.get_session() as session:
            quotes = session.query(Quote).filter_by(created_by=user_id).order_by(Quote.created_at.desc()).all()
            return [self._quote_to_dict(q) for q in quotes]
    
    def update_quote(self, quote_id: int, **kwargs) -> bool:
        """Update quote information"""
        try:
            user_id = kwargs.pop('acting_user_id', None)
            with self.get_session() as session:
                quote = session.query(Quote).filter_by(id=quote_id).first()
                if quote:
                    # Permission check if acting_user_id provided
                    if user_id is not None and not self.can_user_edit_quote(user_id, quote_id):
                        self.logger.warning(
                            f"User {user_id} attempted to edit quote {quote_id} without permission"
                        )
                        return False
                    
                    # Update basic fields
                    for key, value in kwargs.items():
                        if hasattr(quote, key):
                            setattr(quote, key, value)
                    
                    # Recalculate discount amounts if pricing fields were updated
                    if any(key in kwargs for key in ['subtotal', 'regular_discount', 'contractor_discount', 'vat_rate']):
                        subtotal = quote.subtotal
                        regular_discount = quote.regular_discount
                        contractor_discount = quote.contractor_discount
                        vat_rate = quote.vat_rate
                        
                        # Calculate using the correct order: Sum → × VAT → - Contractor → × Discount
                        # Step 1: Subtotal (already calculated)
                        
                        # Step 2: Apply VAT as multiplier (17% = 1.17)
                        vat_multiplier = 1 + (vat_rate / 100)
                        after_vat = subtotal * vat_multiplier
                        vat_amount = after_vat - subtotal
                        
                        # Step 3: Subtract contractor discount (fixed amount)
                        contractor_discount_amount = contractor_discount  # Fixed amount
                        after_contractor = after_vat - contractor_discount_amount
                        after_contractor = max(0, after_contractor)
                        
                        # Step 4: Apply regular discount as reduction factor (18% = 0.82)
                        discount_factor = 1 - (regular_discount / 100)
                        final_total = after_contractor * discount_factor
                        regular_discount_amount = after_contractor - final_total
                        
                        # Update calculated amounts
                        quote.discount_amount = regular_discount_amount
                        quote.contractor_discount_amount = contractor_discount_amount
                        quote.vat_amount = vat_amount
                        quote.total_amount = final_total
                    
                    session.commit()
                    
                    # Audit log
                    self.log_action(
                        user_id=user_id if user_id else quote.created_by,
                        action='update_quote',
                        entity_type='quote',
                        entity_id=quote_id,
                        details={key: kwargs.get(key) for key in kwargs}
                    )
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to update quote {quote_id}: {e}")
            return False
    
    def delete_quote(self, quote_id: int) -> bool:
        """Delete a quote from the database"""
        try:
            with self.get_session() as session:
                quote = session.query(Quote).filter_by(id=quote_id).first()
                if quote:
                    session.delete(quote)
                    
                    # Audit log
                    self.log_action(
                        user_id=quote.created_by,
                        action='delete_quote',
                        entity_type='quote',
                        entity_id=quote_id
                    )
                    session.commit()
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete quote {quote_id}: {e}")
            return False
    
    def can_user_edit_quote(self, user_id: int, quote_id: int) -> bool:
        """Check if user can edit a specific quote"""
        try:
            with self.get_session() as session:
                # Get user and quote
                user = session.query(User).filter_by(id=user_id).first()
                quote = session.query(Quote).filter_by(id=quote_id).first()
                
                if not user or not quote:
                    return False
                
                # Admin can edit any quote
                if user.role == 'admin':
                    return True
                
                # Regular users can edit quotes they created that don't exceed their discount limit
                if user.role == 'user':
                    # Check if user created this quote
                    if quote.created_by != user_id:
                        return False
                        
                    # Check if the quote's discount exceeds user's max discount
                    quote_discount = quote.regular_discount or 0
                    user_max_discount = user.max_discount or 0
                    
                    if quote_discount > user_max_discount:
                        self.logger.warning(
                            f"User {user_id} (max_discount={user_max_discount}%) attempted to edit quote {quote_id} "
                            f"with discount {quote_discount}% - permission denied"
                        )
                        return False
                    
                    return True
                
                # Other roles (like viewer) cannot edit quotes
                return False
        except Exception as e:
            self.logger.error(f"Error checking edit permission: {e}")
            return False
    
    def can_user_delete_quote(self, user_id: int, quote_id: int) -> bool:
        """Check if user can delete a specific quote"""
        try:
            with self.get_session() as session:
                # Get user and quote
                user = session.query(User).filter_by(id=user_id).first()
                quote = session.query(Quote).filter_by(id=quote_id).first()
                
                if not user or not quote:
                    return False
                
                # Only admin can delete quotes
                if user.role == 'admin':
                    return True
                
                return False
        except Exception as e:
            self.logger.error(f"Error checking delete permission: {e}")
            return False
    
    # Draft operations
    def save_draft(self, state: Dict, created_by: int, customer_id: int = None, step: int = 1) -> Dict:
        """Save or update draft"""
        with self.get_session() as session:
            # Check if draft already exists for this user
            existing_draft = session.query(Draft).filter_by(created_by=created_by).first()
            
            if existing_draft:
                existing_draft.state = state
                existing_draft.customer_id = customer_id
                existing_draft.step = step
                existing_draft.last_modified = datetime.utcnow()
                session.commit()
                
                # Return draft data as dict to avoid session binding issues
                return {
                    'id': existing_draft.id,
                    'created_by': existing_draft.created_by,
                    'customer_id': existing_draft.customer_id,
                    'step': existing_draft.step,
                    'state': existing_draft.state,
                    'last_modified': existing_draft.last_modified
                }
            else:
                draft = Draft(
                    state=state,
                    created_by=created_by,
                    customer_id=customer_id,
                    step=step
                )
                session.add(draft)
                session.commit()
                
                # Return draft data as dict to avoid session binding issues
                return {
                    'id': draft.id,
                    'created_by': draft.created_by,
                    'customer_id': draft.customer_id,
                    'step': draft.step,
                    'state': draft.state,
                    'last_modified': draft.last_modified
                }
    
    def get_draft_by_user(self, user_id: int) -> Optional[Draft]:
        """Get draft by user ID"""
        with self.get_session() as session:
            return session.query(Draft).filter_by(created_by=user_id).first()
    
    def delete_draft(self, user_id: int) -> bool:
        """Delete draft for user"""
        try:
            with self.get_session() as session:
                draft = session.query(Draft).filter_by(created_by=user_id).first()
                if draft:
                    session.delete(draft)
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete draft for user {user_id}: {e}")
            return False
    
    def get_all_drafts(self) -> List[Dict]:
        """Get all drafts in the system as dictionaries"""
        with self.get_session() as session:
            drafts = session.query(Draft).order_by(Draft.last_modified.desc()).all()
            return [{
                'id': draft.id,
                'created_by': draft.created_by,
                'customer_id': draft.customer_id,
                'step': draft.step,
                'state': draft.state,
                'last_modified': draft.last_modified
            } for draft in drafts]
    
    def get_drafts_by_user(self, user_id: int) -> List[Dict]:
        """Get drafts by specific user as dictionaries"""
        with self.get_session() as session:
            drafts = session.query(Draft).filter_by(created_by=user_id).order_by(Draft.last_modified.desc()).all()
            return [{
                'id': draft.id,
                'created_by': draft.created_by,
                'customer_id': draft.customer_id,
                'step': draft.step,
                'state': draft.state,
                'last_modified': draft.last_modified
            } for draft in drafts]
    
    def delete_draft_by_id(self, draft_id: int) -> bool:
        """Delete draft by ID"""
        try:
            with self.get_session() as session:
                draft = session.query(Draft).filter_by(id=draft_id).first()
                if draft:
                    session.delete(draft)
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete draft {draft_id}: {e}")
            return False
    
    def cleanup_old_drafts(self, days_old: int = 30) -> int:
        """Delete drafts older than specified days"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            with self.get_session() as session:
                old_drafts = session.query(Draft).filter(Draft.last_modified < cutoff_date).all()
                count = len(old_drafts)
                
                for draft in old_drafts:
                    session.delete(draft)
                
                return count
        except Exception as e:
            self.logger.error(f"Failed to cleanup old drafts: {e}")
            return 0
    
    def delete_all_drafts(self) -> int:
        """Delete all drafts from the database"""
        try:
            with self.get_session() as session:
                all_drafts = session.query(Draft).all()
                count = len(all_drafts)
                
                for draft in all_drafts:
                    session.delete(draft)
                
                session.commit()
                self.logger.info(f"Deleted all {count} drafts from database")
                return count
        except Exception as e:
            self.logger.error(f"Failed to delete all drafts: {e}")
            return 0
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID as a dict to avoid session binding issues"""
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'max_discount': user.max_discount,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_active': user.is_active,
                    'created_at': user.created_at,
                    'last_login': user.last_login
                }
            return None
    
    # Settings operations
    def get_setting(self, key: str, default=None):
        """Get system setting value"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter_by(key=key).first()
                if setting:
                    # Convert based on data type
                    if setting.data_type == 'int':
                        return int(setting.value)
                    elif setting.data_type == 'float':
                        return float(setting.value)
                    elif setting.data_type == 'boolean':
                        return setting.value.lower() in ('true', '1', 'yes')
                    elif setting.data_type == 'json':
                        import json
                        return json.loads(setting.value)
                    else:
                        return setting.value
                return default
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {e}")
            return default
    
    def set_setting(self, key: str, value: Any, data_type: str = 'string'):
        """Set system setting value"""
        try:
            with self.get_session() as session:
                setting = session.query(SystemSettings).filter_by(key=key).first()
                
                # Convert value to string for storage
                if data_type in ('int', 'float', 'boolean'):
                    str_value = str(value)
                elif data_type == 'json':
                    import json
                    str_value = json.dumps(value)
                else:
                    str_value = str(value)
                
                if setting:
                    setting.value = str_value
                    setting.data_type = data_type
                else:
                    setting = SystemSettings(
                        key=key,
                        value=str_value,
                        data_type=data_type
                    )
                    session.add(setting)
                    
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {e}")
    
    # Audit logging
    def log_action(self, user_id: int, action: str, entity_type: str = None, 
                   entity_id: int = None, details: Dict = None, ip_address: str = None):
        """Log user action for audit trail"""
        try:
            with self.get_session() as session:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details=details,
                    ip_address=ip_address
                )
                session.add(audit_log)
        except Exception as e:
            self.logger.error(f"Failed to log action: {e}")
    
    # Utility methods
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with self.get_session() as session:
                stats = {
                    'total_customers': session.query(Customer).count(),
                    'total_quotes': session.query(Quote).count(),
                    'quotes_this_month': session.query(Quote).filter(
                        text("strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')")
                    ).count(),
                    'total_users': session.query(User).count(),
                }
                return stats
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {}
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def clear_quotes_data(self) -> bool:
        """Clear all quotes data while keeping catalog and customers"""
        try:
            with self.get_session() as session:
                # Delete all quotes
                session.query(Quote).delete()
                session.commit()
                self.logger.info("All quotes data cleared successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error clearing quotes data: {e}")
            return False
    
    def get_quote_dict_by_id(self, quote_id: int):
        """Get quote by ID as plain dictionary to avoid detached instances"""
        with self.get_session() as session:
            quote = session.query(Quote).filter_by(id=quote_id).first()
            if quote:
                return self._quote_to_dict(quote)
            return None
    
    def get_quotes(self, user_id: int = None, user_role: str = None) -> List[Dict]:
        """Get all quotes with user visibility controls"""
        with self.get_session() as session:
            query = session.query(Quote)
            
            # Apply user visibility filters for non-admin users
            if user_role != 'admin' and user_id is not None:
                # Regular users can only see their own quotes
                query = query.filter(Quote.created_by == user_id)
            
            quotes = query.order_by(Quote.created_at.desc()).all()
            
            result = []
            for quote in quotes:
                quote_dict = self._quote_to_dict(quote)
                result.append(quote_dict)
            
            return result
    
    def get_drafts(self, user_id: int = None, user_role: str = None) -> List[Draft]:
        """Get all drafts with user visibility controls"""
        with self.get_session() as session:
            query = session.query(Draft)
            
            # Apply user visibility filters for non-admin users
            if user_role != 'admin' and user_id is not None:
                # Regular users can only see their own drafts
                query = query.filter(Draft.created_by == user_id)
            
            drafts = query.order_by(Draft.created_at.desc()).all()
            return drafts 