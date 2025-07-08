from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class ServiceType(Enum):
    PUMPING = "Septic Pumping"
    INSPECTION = "Septic Inspection"
    REPAIR = "Septic Repair"
    INSTALLATION = "Septic Installation"
    MAINTENANCE = "Preventive Maintenance"
    EMERGENCY = "Emergency Service"
    CLEANING = "Septic Cleaning"
    ROOTER = "Line Cleaning/Rooter"
    GREASE_TRAP = "Grease Trap Service"
    LIFT_STATION = "Lift Station Service"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on-hold"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100), nullable=True)
    customer_type = db.Column(db.String(20), nullable=False, default='residential')  # residential, commercial
    
    # Contact Info
    email = db.Column(db.String(100), nullable=True)
    phone_primary = db.Column(db.String(20), nullable=True)
    phone_secondary = db.Column(db.String(20), nullable=True)
    
    # Address
    street_address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    county = db.Column(db.String(100), nullable=True)
    
    # Billing Address (if different)
    billing_street_address = db.Column(db.String(200), nullable=True)
    billing_city = db.Column(db.String(100), nullable=True)
    billing_state = db.Column(db.String(50), nullable=True)
    billing_zip_code = db.Column(db.String(20), nullable=True)
    
    # Business Info
    preferred_contact_method = db.Column(db.String(20), nullable=True, default='phone')
    payment_terms = db.Column(db.String(50), nullable=True, default='net_30')
    tax_exempt = db.Column(db.Boolean, default=False)
    tax_exempt_number = db.Column(db.String(50), nullable=True)
    
    # Preferences
    service_reminders = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='customer', lazy=True)
    septic_systems = db.relationship('SepticSystem', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'

class SepticSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    
    # System Details
    system_type = db.Column(db.String(50), nullable=True)  # conventional, aerobic, etc.
    tank_size = db.Column(db.Integer, nullable=True)  # gallons
    tank_material = db.Column(db.String(50), nullable=True)  # concrete, plastic, fiberglass
    num_compartments = db.Column(db.Integer, nullable=True)
    
    # Installation Info
    install_date = db.Column(db.Date, nullable=True)
    permit_number = db.Column(db.String(50), nullable=True)
    installer_company = db.Column(db.String(100), nullable=True)
    
    # Maintenance Schedule
    pump_frequency_months = db.Column(db.Integer, nullable=True, default=36)
    last_pumped = db.Column(db.Date, nullable=True)
    next_pump_due = db.Column(db.Date, nullable=True)
    
    # System Status
    system_condition = db.Column(db.String(20), nullable=True, default='good')
    needs_repair = db.Column(db.Boolean, default=False)
    repair_notes = db.Column(db.Text, nullable=True)
    
    # Location Info
    access_notes = db.Column(db.Text, nullable=True)
    gps_coordinates = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='septic_system', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    job_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    septic_system_id = db.Column(db.Integer, db.ForeignKey('septic_system.id'), nullable=True)
    
    # Service Details
    service_type = db.Column(db.String(50), nullable=True)
    service_description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime, nullable=True)
    estimated_duration = db.Column(db.Integer, nullable=True)  # minutes
    route_position = db.Column(db.Integer, nullable=True)
    column_position = db.Column(db.Integer, nullable=True, default=0)  # Position within kanban column
    
    # Assignment
    assigned_technician = db.Column(db.String(100), nullable=True)
    assigned_crew = db.Column(db.String(200), nullable=True)
    
    # Pricing
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)
    parts_cost = db.Column(db.Float, nullable=True)
    labor_cost = db.Column(db.Float, nullable=True)
    disposal_cost = db.Column(db.Float, nullable=True)
    
    # Service Details
    gallons_pumped = db.Column(db.Integer, nullable=True)
    waste_type = db.Column(db.String(50), nullable=True)
    disposal_location = db.Column(db.String(100), nullable=True)
    trip_ticket_number = db.Column(db.String(50), nullable=True)
    
    # Conditions Found
    tank_condition = db.Column(db.String(50), nullable=True)
    sludge_level = db.Column(db.String(50), nullable=True)
    scum_level = db.Column(db.String(50), nullable=True)
    liquid_level = db.Column(db.String(50), nullable=True)
    
    # Issues and Recommendations
    issues_found = db.Column(db.Text, nullable=True)
    recommendations = db.Column(db.Text, nullable=True)
    follow_up_needed = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date, nullable=True)
    follow_up_notes = db.Column(db.Text, nullable=True)
    
    # Completion Info
    work_performed = db.Column(db.Text, nullable=True)
    materials_used = db.Column(db.Text, nullable=True)
    customer_signature = db.Column(db.Text, nullable=True)  # base64 encoded
    technician_signature = db.Column(db.Text, nullable=True)  # base64 encoded
    
    # Payment Info
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(20), nullable=True, default='pending')
    invoice_number = db.Column(db.String(50), nullable=True)
    
    # Time Tracking
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    travel_time = db.Column(db.Integer, nullable=True)  # minutes
    work_time = db.Column(db.Integer, nullable=True)  # minutes
    
    # Notes and Communication
    office_notes = db.Column(db.Text, nullable=True)
    technician_notes = db.Column(db.Text, nullable=True)
    customer_notes = db.Column(db.Text, nullable=True)
    internal_notes = db.Column(db.Text, nullable=True)
    
    # Compliance and Regulations
    permit_required = db.Column(db.Boolean, default=False)
    permit_number = db.Column(db.String(50), nullable=True)
    inspection_required = db.Column(db.Boolean, default=False)
    inspection_passed = db.Column(db.Boolean, nullable=True)
    
    # Equipment Used
    equipment_used = db.Column(db.Text, nullable=True)
    truck_number = db.Column(db.String(20), nullable=True)
    
    # GPS and Photos
    gps_location = db.Column(db.String(100), nullable=True)
    photo_paths = db.Column(db.Text, nullable=True)  # JSON array of photo paths
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Ticket {self.job_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'customer_id': self.customer_id,
            'septic_system_id': self.septic_system_id,
            'service_type': self.service_type,
            'service_description': self.service_description,
            'priority': self.priority,
            'status': self.status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'estimated_duration': self.estimated_duration,
            'column_position': self.column_position,
            'assigned_technician': self.assigned_technician,
            'assigned_crew': self.assigned_crew,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'parts_cost': self.parts_cost,
            'labor_cost': self.labor_cost,
            'disposal_cost': self.disposal_cost,
            'gallons_pumped': self.gallons_pumped,
            'waste_type': self.waste_type,
            'disposal_location': self.disposal_location,
            'trip_ticket_number': self.trip_ticket_number,
            'tank_condition': self.tank_condition,
            'sludge_level': self.sludge_level,
            'scum_level': self.scum_level,
            'liquid_level': self.liquid_level,
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'follow_up_needed': self.follow_up_needed,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'work_performed': self.work_performed,
            'materials_used': self.materials_used,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'invoice_number': self.invoice_number,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'travel_time': self.travel_time,
            'work_time': self.work_time,
            'office_notes': self.office_notes,
            'technician_notes': self.technician_notes,
            'customer_notes': self.customer_notes,
            'internal_notes': self.internal_notes,
            'permit_required': self.permit_required,
            'permit_number': self.permit_number,
            'inspection_required': self.inspection_required,
            'inspection_passed': self.inspection_passed,
            'equipment_used': self.equipment_used,
            'truck_number': self.truck_number,
            'gps_location': self.gps_location,
            'photo_paths': self.photo_paths,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            
            # Include customer info if available
            'customer_name': f"{self.customer.first_name} {self.customer.last_name}" if self.customer else None,
            'customer_phone': self.customer.phone_primary if self.customer else None,
            'customer_address': f"{self.customer.street_address}, {self.customer.city}, {self.customer.state}" if self.customer and self.customer.street_address else None,
        }

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    septic_system_id = db.Column(db.Integer, db.ForeignKey('septic_system.id'), nullable=True)
    
    # Service Summary
    service_date = db.Column(db.Date, nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    technician = db.Column(db.String(100), nullable=False)
    
    # Key Metrics
    gallons_pumped = db.Column(db.Integer, nullable=True)
    cost = db.Column(db.Float, nullable=True)
    
    # Quick Notes
    summary = db.Column(db.Text, nullable=True)
    next_service_due = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    ticket = db.relationship('Ticket', backref='service_history_entry')
    customer = db.relationship('Customer', backref='service_history')
    septic_system = db.relationship('SepticSystem', backref='service_history')