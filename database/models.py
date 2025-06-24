"""
Database Models for Kitchen Quote Management System
Defines the schema and relationships for all data entities
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User account model with role-based permissions"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, manager, employee, viewer
    max_discount = Column(Float, default=0.0)  # Maximum discount percentage allowed
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    quotes = relationship("Quote", back_populates="created_by_user")
    drafts = relationship("Draft", back_populates="created_by_user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Customer(Base):
    """Customer information model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    address = Column(Text, unique=True, nullable=False)
    notes = Column(Text)  # Additional customer notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quotes = relationship("Quote", back_populates="customer", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', phone='{self.phone}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Quote(Base):
    """Quote model with items, discounts, and calculations"""
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    quote_number = Column(Integer, nullable=False)  # Sequential per customer
    
    # Quote content
    items = Column(JSON, nullable=False)  # List of items with quantities and prices
    regular_discount = Column(Float, default=0.0)  # Regular discount percentage
    contractor_discount = Column(Float, default=0.0)  # Contractor discount percentage
    vat_rate = Column(Float, default=17.0)  # VAT rate percentage
    
    # Calculated totals
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    contractor_discount_amount = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Optional elements
    images = Column(JSON)  # List of image paths (max 2)
    notes = Column(Text)
    pdf_path = Column(String(255))  # Path to generated PDF
    
    # Tracking
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="quotes")
    created_by_user = relationship("User", back_populates="quotes")
    
    # Ensure unique quote numbers per customer
    __table_args__ = (UniqueConstraint('customer_id', 'quote_number'),)
    
    def __repr__(self):
        return f"<Quote(id={self.id}, customer_id={self.customer_id}, quote_number={self.quote_number})>"

class Draft(Base):
    """Draft quote model for auto-save functionality"""
    __tablename__ = 'drafts'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Draft state (JSON containing all form data)
    state = Column(JSON, nullable=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    step = Column(Integer, default=1)  # Current wizard step
    
    # Relationships
    customer = relationship("Customer", back_populates="drafts")
    created_by_user = relationship("User", back_populates="drafts")
    
    def __repr__(self):
        return f"<Draft(id={self.id}, customer_id={self.customer_id}, step={self.step})>"

class AuditLog(Base):
    """Audit log for tracking important system actions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(50), nullable=False)  # login, logout, create_quote, delete_customer, etc.
    entity_type = Column(String(50))  # customer, quote, user, etc.
    entity_id = Column(Integer)
    details = Column(JSON)  # Additional action details
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user_id={self.user_id}, timestamp={self.timestamp})>"

class SystemSettings(Base):
    """System-wide settings and configuration"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    data_type = Column(String(20), default='string')  # string, int, float, boolean, json
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSettings(key='{self.key}', value='{self.value}')>" 